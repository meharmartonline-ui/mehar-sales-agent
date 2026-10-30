"""Local store manager: stores, products, orders/inventory, theme and export in the app's SQLite DB.
Nothing here calls any external store platform. 'Publish' is a local readiness check + JSON export only."""
from __future__ import annotations

import html
import json
import re
import sqlite3

NICHES = ["Kitchen", "Beauty", "Mobile"]
THEMES = {"Minimal White": ("#FFFFFF", "#111111"), "Dark Navy Gold": ("#0A1931", "#FFFFFF"),
          "Classic Default": ("#F4F4F4", "#222222")}
STATUSES = ["new", "confirmed", "shipped", "delivered", "returned", "cancelled"]
RESTOCK = {"returned", "cancelled"}  # these statuses give stock back
LOW_STOCK = 3


def valid_phone(p: str) -> bool:
    return bool(re.fullmatch(r"\+?[0-9 \-]+", p)) and 7 <= len(re.sub(r"\D", "", p)) <= 15


def init_tables(db_session) -> None:
    with db_session() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS stores(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE CHECK(length(name) BETWEEN 1 AND 80),
            niche TEXT NOT NULL, theme TEXT NOT NULL DEFAULT 'Dark Navy Gold',
            primary_color TEXT NOT NULL DEFAULT '#D4AF37',
            status TEXT NOT NULL DEFAULT 'draft' CHECK(status IN ('draft','ready')),
            created_at TEXT NOT NULL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS products(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            store_id INTEGER NOT NULL REFERENCES stores(id) ON DELETE RESTRICT,
            name TEXT NOT NULL CHECK(length(name) BETWEEN 1 AND 120),
            price REAL NOT NULL CHECK(price >= 0),
            stock INTEGER NOT NULL CHECK(stock >= 0),
            created_at TEXT NOT NULL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS orders(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            store_id INTEGER NOT NULL REFERENCES stores(id) ON DELETE RESTRICT,
            product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
            customer TEXT NOT NULL CHECK(length(customer) BETWEEN 1 AND 100),
            phone TEXT NOT NULL CHECK(length(phone) BETWEEN 3 AND 20),
            qty INTEGER NOT NULL CHECK(qty > 0),
            unit_price REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'new' CHECK(status IN ('new','confirmed','shipped','delivered','returned','cancelled')),
            created_at TEXT NOT NULL)""")
        c.execute("CREATE INDEX IF NOT EXISTS idx_products_store ON products(store_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_orders_store ON orders(store_id, status)")


def add_store(db_session, utc_iso, name: str, niche: str):
    if not name.strip():
        return "Store name zaroori hai."
    try:
        with db_session() as c:
            c.execute("INSERT INTO stores(name, niche, created_at) VALUES (?,?,?)", (name.strip(), niche, utc_iso()))
    except sqlite3.IntegrityError:
        return "Is naam ka store pehle se hai."
    return None


def create_order(db_session, utc_iso, store_id, product_id, customer, phone, qty):
    """Atomic: check stock, decrement stock, insert order."""
    customer, phone = customer.strip(), phone.strip()
    if not customer or not valid_phone(phone) or qty < 1:
        return "Customer name, valid phone (7-15 digits) aur qty zaroori hain."
    with db_session() as c:
        c.execute("BEGIN IMMEDIATE")
        try:
            p = c.execute("SELECT price, stock FROM products WHERE id=? AND store_id=?", (product_id, store_id)).fetchone()
            if not p:
                c.execute("ROLLBACK"); return "Product nahi mila."
            if p["stock"] < qty:
                c.execute("ROLLBACK"); return f"Stock kam hai (available {p['stock']})."
            c.execute("UPDATE products SET stock = stock - ? WHERE id=?", (qty, product_id))
            c.execute("INSERT INTO orders(store_id, product_id, customer, phone, qty, unit_price, created_at) VALUES (?,?,?,?,?,?,?)",
                      (store_id, product_id, customer, phone, qty, p["price"], utc_iso()))
            c.execute("COMMIT"); return None
        except Exception:
            c.execute("ROLLBACK"); raise


def set_status(db_session, order_id, new):
    """Atomic status change; returned/cancelled give stock back, leaving those states takes it again."""
    if new not in STATUSES:
        return "Invalid status."
    with db_session() as c:
        c.execute("BEGIN IMMEDIATE")
        try:
            o = c.execute("SELECT product_id, qty, status FROM orders WHERE id=?", (order_id,)).fetchone()
            if not o:
                c.execute("ROLLBACK"); return "Order nahi mila."
            was, will = o["status"] in RESTOCK, new in RESTOCK
            if will and not was:
                c.execute("UPDATE products SET stock = stock + ? WHERE id=?", (o["qty"], o["product_id"]))
            elif was and not will:
                s = c.execute("SELECT stock FROM products WHERE id=?", (o["product_id"],)).fetchone()["stock"]
                if s < o["qty"]:
                    c.execute("ROLLBACK"); return f"Stock kam hai (available {s})."
                c.execute("UPDATE products SET stock = stock - ? WHERE id=?", (o["qty"], o["product_id"]))
            c.execute("UPDATE orders SET status=? WHERE id=?", (new, order_id))
            c.execute("COMMIT"); return None
        except Exception:
            c.execute("ROLLBACK"); raise


def readiness(db_session, store_id):
    with db_session() as c:
        r = c.execute("SELECT COUNT(*) n, COALESCE(SUM(stock),0) s FROM products WHERE store_id=?", (store_id,)).fetchone()
    return {"Kam az kam 1 product": r["n"] > 0, "Kisi product ka stock > 0": r["s"] > 0}


def export_store(db_session, store_id) -> str:
    """Store + products only (no customer/phone data)."""
    with db_session() as c:
        s = dict(c.execute("SELECT name, niche, theme, primary_color, status FROM stores WHERE id=?", (store_id,)).fetchone())
        s["products"] = [dict(r) for r in c.execute("SELECT name, price, stock FROM products WHERE store_id=? ORDER BY id", (store_id,))]
    return json.dumps(s, ensure_ascii=False, indent=2)


def _pick_store(st, db_session, key):
    with db_session() as c:
        rows = c.execute("SELECT id, name, niche, theme, primary_color, status FROM stores ORDER BY id DESC").fetchall()
    if not rows:
        st.info("Pehle 'Store' tab mein ek store plan save karo."); return None
    names = {r["id"]: r["name"] for r in rows}
    sid = st.selectbox("Store", list(names), format_func=names.get, key=key)
    return next(r for r in rows if r["id"] == sid)


def _table(st, pd, rows):
    st.dataframe(pd.DataFrame([dict(r) for r in rows]), use_container_width=True, hide_index=True)


def render(tabs, db_session, utc_iso) -> None:
    import pandas as pd
    import streamlit as st
    t_store, t_prod, t_theme, t_ord, t_pub = tabs

    with t_store:
        st.subheader("🛍️ Store plan")
        st.caption("Plan local database mein save hota hai. Koi external platform call nahi hoti.")
        with st.form("store_form", clear_on_submit=True):
            name = st.text_input("Store name", max_chars=80)
            niche = st.selectbox("Niche", NICHES)
            ok = st.form_submit_button("Save Store Plan")
        if ok:
            err = add_store(db_session, utc_iso, name, niche)
            st.error(err) if err else st.success(f"Store plan '{name.strip()}' local DB mein save ho gaya (draft).")
        with db_session() as c:
            _table(st, pd, c.execute("SELECT id, name, niche, theme, status, created_at FROM stores ORDER BY id DESC").fetchall())

    with t_prod:
        st.subheader("🧺 Products")
        s = _pick_store(st, db_session, "prod_store")
        if s:
            with st.form("prod_form", clear_on_submit=True):
                pn = st.text_input("Product name", max_chars=120)
                pp = st.number_input("Price (Rs)", min_value=0.0, step=50.0, format="%.0f")
                ps = st.number_input("Stock", min_value=0, step=1)
                add = st.form_submit_button("Add Product")
            if add:
                if not pn.strip():
                    st.error("Product name zaroori hai.")
                else:
                    with db_session() as c:
                        c.execute("INSERT INTO products(store_id, name, price, stock, created_at) VALUES (?,?,?,?,?)",
                                  (s["id"], pn.strip(), pp, int(ps), utc_iso()))
                    st.success("Product add ho gaya.")
            with db_session() as c:
                prods = c.execute("SELECT id, name, price, stock FROM products WHERE store_id=? ORDER BY id DESC", (s["id"],)).fetchall()
            _table(st, pd, prods)
            if prods:
                labels = {p["id"]: f"#{p['id']} {p['name']}" for p in prods}
                pid = st.selectbox("Edit / delete product", list(labels), format_func=labels.get)
                cur = next(p for p in prods if p["id"] == pid)
                np_ = st.number_input("New price (Rs)", min_value=0.0, value=float(cur["price"]), step=50.0, format="%.0f", key=f"ep{pid}")
                ns = st.number_input("New stock", min_value=0, value=int(cur["stock"]), step=1, key=f"es{pid}")
                if st.button("Update product"):
                    with db_session() as c:
                        c.execute("UPDATE products SET price=?, stock=? WHERE id=?", (np_, int(ns), pid))
                    st.success("Updated."); st.rerun()
                sure = st.checkbox("Delete confirm (wapas nahi aayega)", key=f"dc{pid}")
                if st.button("Delete product") and sure:
                    try:
                        with db_session() as c:
                            c.execute("DELETE FROM products WHERE id=?", (pid,))
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Is product ke orders hain, delete nahi ho sakta. Stock 0 kar do.")

    with t_theme:
        st.subheader("🎨 Theme")
        s = _pick_store(st, db_session, "theme_store")
        if s:
            names = list(THEMES)
            theme = st.selectbox("Theme", names, index=names.index(s["theme"]) if s["theme"] in names else 1)
            color = st.color_picker("Primary color", s["primary_color"])
            bg, fg = THEMES[theme]
            st.markdown(f"<div style='background:{bg};color:{fg};padding:18px;border-radius:12px;border:1px solid #888'>"
                        f"<h3 style='color:{fg};margin:0'>{html.escape(s['name'])}</h3>"
                        f"<p style='color:{fg}'>Sample product card</p>"
                        f"<span style='background:{color};color:#000;padding:8px 16px;border-radius:8px;font-weight:700'>Order Now</span></div>",
                        unsafe_allow_html=True)
            st.caption("Ye sirf preview hai. Theme local DB mein save hoti hai, kisi live store par apply nahi hoti.")
            if st.button("Save theme (local)"):
                with db_session() as c:
                    c.execute("UPDATE stores SET theme=?, primary_color=? WHERE id=?", (theme, color, s["id"]))
                st.success("Theme save ho gayi.")

    with t_ord:
        st.subheader("📊 Orders & Inventory")
        s = _pick_store(st, db_session, "ord_store")
        if s:
            with db_session() as c:
                prods = c.execute("SELECT id, name, price, stock FROM products WHERE store_id=? ORDER BY name", (s["id"],)).fetchall()
                counts = {r["status"]: r["n"] for r in c.execute("SELECT status, COUNT(*) n FROM orders WHERE store_id=? GROUP BY status", (s["id"],))}
            m1, m2, m3 = st.columns(3)
            m1.metric("Products", len(prods)); m2.metric("Units in stock", sum(p["stock"] for p in prods)); m3.metric("Orders", sum(counts.values()))
            low = [p["name"] for p in prods if p["stock"] <= LOW_STOCK]
            if low: st.warning("Low/zero stock: " + ", ".join(low))
            if prods:
                with st.form("order_form", clear_on_submit=True):
                    lab = {p["id"]: f"{p['name']} (Rs {p['price']:,.0f}, stock {p['stock']})" for p in prods}
                    pid = st.selectbox("Product", list(lab), format_func=lab.get)
                    cu = st.text_input("Customer", max_chars=100); ph = st.text_input("Phone", max_chars=20)
                    q = st.number_input("Qty", min_value=1, value=1, step=1)
                    go = st.form_submit_button("Create COD Order")
                if go:
                    err = create_order(db_session, utc_iso, s["id"], pid, cu, ph, int(q))
                    st.error(err) if err else st.success("Order ban gaya, stock kam ho gaya."); 
            with db_session() as c:
                orders = c.execute("""SELECT o.id, p.name AS product, o.qty, o.unit_price, o.customer, o.phone, o.status, o.created_at
                    FROM orders o JOIN products p ON p.id=o.product_id WHERE o.store_id=? ORDER BY o.id DESC LIMIT 500""", (s["id"],)).fetchall()
            _table(st, pd, orders)
            if orders:
                oid = st.selectbox("Order status badlo", [o["id"] for o in orders], format_func=lambda i: f"Order #{i}")
                new = st.selectbox("Naya status", STATUSES)
                if st.button("Update status"):
                    err = set_status(db_session, oid, new)
                    if err: st.error(err)
                    else: st.rerun()
            st.caption("returned/cancelled par stock wapas aata hai. Customer phone numbers plain text mein hain.")

    with t_pub:
        st.subheader("🚀 Publish")
        st.warning("Koi store platform connected nahi. Yahan publish nahi hota: sirf local readiness check aur JSON export.")
        s = _pick_store(st, db_session, "pub_store")
        if s:
            checks = readiness(db_session, s["id"])
            for k, v in checks.items(): st.write(("✅ " if v else "❌ ") + k)
            st.write(f"Local status: **{s['status']}**")
            if st.button("Mark ready (local)"):
                if all(checks.values()):
                    with db_session() as c: c.execute("UPDATE stores SET status='ready' WHERE id=?", (s["id"],))
                    st.rerun()
                else:
                    st.error("Checklist poori nahi.")
            st.download_button("⬇️ Export store JSON (products only)", export_store(db_session, s["id"]), f"{s['name']}.json", "application/json")
