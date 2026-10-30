import os
import hmac
import time
import sqlite3
import re
import json
import streamlit as st
import pandas as pd

# ========= 🔒 LOCK 1: FAIL-CLOSED SECRETS =========
def get_secret(key):
    v = os.getenv(key)
    if v:
        return v
    try:
        if key in st.secrets:
            return st.secrets[key]
    except:
        pass
    return None

ADMIN_USER = get_secret("ADMIN_USER")
ADMIN_PASS = get_secret("ADMIN_PASS")
GROQ_API_KEY = get_secret("GROQ_API_KEY")
DB_PATH = get_secret("MEHAR_DB_PATH") or "leads.db"

st.set_page_config(page_title="Mehar Super Agent v2 - Locked", layout="wide")

if not ADMIN_USER or not ADMIN_PASS:
    st.error("🔒 LOCKED — ADMIN_USER / ADMIN_PASS not set in Secrets")
    st.code('ADMIN_USER = "mehar_admin_9x"\nADMIN_PASS = "Strong#2026Pass"\nGROQ_API_KEY = "gsk_xxx"\nMEHAR_DB_PATH = "/mount/data/leads.db"', language="toml")
    st.stop()

# ========= DB — SHORT-LIVED + WAL + BUSY TIMEOUT =========
def get_conn():
    conn = sqlite3.connect(DB_PATH, timeout=10, isolation_level=None, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def init_db():
    conn = get_conn()
    try:
        conn.execute("""CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL CHECK(length(name)>=2),
            phone TEXT NOT NULL CHECK(length(phone)>=7),
            niche TEXT NOT NULL,
            created_at REAL NOT NULL,
            status TEXT DEFAULT 'new')""")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_leads_created ON leads(created_at DESC)")
        conn.execute("""CREATE TABLE IF NOT EXISTS rate_limits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL, username TEXT NOT NULL, ts REAL NOT NULL)""")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_ratelimit_action_ts ON rate_limits(action, ts)")
        conn.execute("""CREATE TABLE IF NOT EXISTS login_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, ts REAL NOT NULL, success INTEGER NOT NULL)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS stores (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, created_at REAL NOT NULL)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, price REAL NOT NULL, stock INTEGER NOT NULL DEFAULT 0, seo_desc TEXT, created_at REAL NOT NULL)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, product_id INTEGER NOT NULL, qty INTEGER NOT NULL, customer_name TEXT, status TEXT DEFAULT 'pending', created_at REAL NOT NULL)""")
    finally:
        conn.close()
init_db()

# ========= RATE LIMIT ATOMIC — SCOPED PER ACTION =========
def is_rate_limited(action, limit=5, window_sec=60):
    now = time.time()
    conn = get_conn()
    try:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("DELETE FROM rate_limits WHERE action=? AND ts < ?", (action, now - window_sec))
        cur = conn.execute("SELECT COUNT(*) FROM rate_limits WHERE action=? AND ts >= ?", (action, now - window_sec))
        count = cur.fetchone()[0]
        if count >= limit:
            conn.execute("COMMIT")
            return True
        conn.execute("INSERT INTO rate_limits(action, username, ts) VALUES(?,?,?)", (action, ADMIN_USER, now))
        conn.execute("COMMIT")
        return False
    except:
        try: conn.execute("ROLLBACK")
        except: pass
        return False
    finally:
        conn.close()

def is_login_throttled(username, limit=5, window_sec=300):
    now = time.time()
    conn = get_conn()
    try:
        conn.execute("DELETE FROM login_attempts WHERE ts < ?", (now - window_sec,))
        cur = conn.execute("SELECT COUNT(*) FROM login_attempts WHERE username=? AND ts >= ? AND success=0", (username, now - window_sec))
        return cur.fetchone()[0] >= limit
    finally:
        conn.close()

def record_login(username, success):
    conn = get_conn()
    try:
        conn.execute("INSERT INTO login_attempts(username, ts, success) VALUES(?,?,?)", (username, time.time(), 1 if success else 0))
    finally:
        conn.close()

# ========= SESSION AUTH — FORM (Enter/Go) =========
if "auth" not in st.session_state:
    st.session_state.auth = False
if "seo_result" not in st.session_state:
    st.session_state.seo_result = ""
    st.session_state.seo_error = ""

if not st.session_state.auth:
    st.title("🔒 Mehar Super Agent v2 — Locked Login")
    st.caption("Hardened prototype — 5 attempts / 5 min throttle — Fail closed")
    with st.form("login_form"):
        u = st.text_input("Admin User")
        p = st.text_input("Admin Pass", type="password")
        submitted = st.form_submit_button("Login — Enter / Go")
        if submitted:
            if is_login_throttled(u):
                st.error("Too many failed — Wait 5 minutes")
            else:
                ok = hmac.compare_digest(u, ADMIN_USER) and hmac.compare_digest(p, ADMIN_PASS)
                record_login(u, ok)
                if ok:
                    st.session_state.auth = True
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    st.stop()

# ========= AUTHENTICATED APP =========
st.sidebar.success(f"Logged: {ADMIN_USER}")
st.sidebar.code(f"DB: {DB_PATH}\nGroq: {'yes' if GROQ_API_KEY else 'no'}")
if st.sidebar.button("Logout — Refresh logs out (session-only)"):
    st.session_state.auth = False
    st.rerun()

st.title("Mehar Super Agent v2 — Fixed Prototype 🔒")
st.caption("Leads + SEO (Groq) + Store Manager — Demo payment only — No real Easypaisa/WhatsApp/PWA")

tab1, tab2, tab3, tab4 = st.tabs(["Leads", "SEO Generator", "Store Manager", "System"])

with tab1:
    st.subheader("Add Lead — Validation 7-15 digits")
    with st.form("lead_form"):
        name = st.text_input("Name * min 2")
        phone = st.text_input("Phone * 7-15 digits")
        niche = st.text_input("Niche * e.g. honey")
        s = st.form_submit_button("Save Lead — Atomic WAL")
        if s:
            phone_clean = re.sub(r"\D", "", phone or "")
            if not name or len(name.strip()) < 2:
                st.error("Name min 2 chars")
            elif not (7 <= len(phone_clean) <= 15):
                st.error("Phone 7-15 digits required")
            elif not niche or len(niche.strip()) < 2:
                st.error("Niche required")
            else:
                conn = get_conn()
                try:
                    conn.execute("INSERT INTO leads(name, phone, niche, created_at) VALUES(?,?,?,?)", (name.strip(), phone_clean, niche.strip(), time.time()))
                    st.success("Lead saved")
                finally:
                    conn.close()
    st.divider()
    st.subheader("Latest 1000 Leads — Bounded read (fix #13)")
    conn = get_conn()
    try:
        df = pd.read_sql_query("SELECT id, name, phone, niche, datetime(created_at,'unixepoch') as created, status FROM leads ORDER BY created_at DESC LIMIT 1000", conn)
        st.dataframe(df, use_container_width=True)
    finally:
        conn.close()

with tab2:
    st.subheader("Groq SEO — Rolling 60s limit — Atomic")
    st.warning("Description sent to Groq when Generate clicked — Demo only — No PWA/Webhook")
    product_title = st.text_input("Product Title *", key="seo_title")
    product_features = st.text_area("Features / Details", key="seo_feat")
    if st.button("Generate SEO — Groq (timeout 30s, 1 retry)"):
        st.session_state.seo_result = ""
        st.session_state.seo_error = ""
        if not GROQ_API_KEY:
            st.session_state.seo_error = "GROQ_API_KEY not set in Secrets"
        elif is_rate_limited("seo_generate", limit=5, window_sec=60):
            st.session_state.seo_error = "Rate limited 60s — Wait"
        elif not product_title:
            st.session_state.seo_error = "Title required"
        else:
            try:
                from groq import Groq
                client = Groq(api_key=GROQ_API_KEY, timeout=30, max_retries=1)
                resp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content": f"Write SEO description max 150 words for: {product_title} - {product_features}"}], max_tokens=300)
                text = (resp.choices[0].message.content or "").strip()
                if not text:
                    st.session_state.seo_error = "Empty Groq result"
                else:
                    st.session_state.seo_result = text[:2000]
            except Exception as e:
                st.session_state.seo_error = f"Groq error: {str(e)[:200]}"
    if st.session_state.seo_error:
        st.error(st.session_state.seo_error)
    if st.session_state.seo_result:
        st.success("Generated — Stale cleared on error (v2.1 fix)")
        st.text_area("SEO Output — Max 2000 chars", st.session_state.seo_result, height=200)

with tab3:
    st.subheader("Store Manager v2.2 — Local SQLite — No external platform call")
    sm_tab1, sm_tab2, sm_tab3, sm_tab4 = st.tabs(["Store", "Products", "Orders", "Publish"])
    with sm_tab1:
        name = st.text_input("Store Name")
        if st.button("Create Store"):
            if not name.strip(): st.error("Name required")
            else:
                c = get_conn()
                try:
                    c.execute("INSERT INTO stores(name, created_at) VALUES(?,?)", (name.strip(), time.time()))
                    st.success("Store created")
                finally: c.close()
        c = get_conn()
        try:
            st.dataframe(pd.read_sql_query("SELECT * FROM stores ORDER BY id DESC LIMIT 20", c), use_container_width=True)
        finally: c.close()
    with sm_tab2:
        title = st.text_input("Product Title")
        price = st.number_input("Price", min_value=0.0)
        stock = st.number_input("Stock", min_value=0, step=1)
        if st.button("Add Product"):
            if not title.strip(): st.error("Title required")
            else:
                c = get_conn()
                try:
                    c.execute("INSERT INTO products(title, price, stock, created_at) VALUES(?,?,?,?)", (title.strip(), price, int(stock), time.time()))
                    st.success("Product added")
                finally: c.close()
        c = get_conn()
        try:
            st.dataframe(pd.read_sql_query("SELECT id, title, price, stock FROM products ORDER BY id DESC LIMIT 50", c), use_container_width=True)
        finally: c.close()
    with sm_tab3:
        st.caption("Orders decrement stock atomically — Cancel restores")
        c = get_conn()
        try:
            prods = pd.read_sql_query("SELECT id, title, stock FROM products", c)
            orders_df = pd.read_sql_query("SELECT * FROM orders ORDER BY id DESC LIMIT 100", c)
        finally: c.close()
        if not prods.empty:
            prod_id = st.selectbox("Product", prods["id"].tolist(), format_func=lambda x: f"{x} - {prods[prods.id==x].iloc[0].title} (stock {prods[prods.id==x].iloc[0].stock})")
            qty = st.number_input("Qty", min_value=1, step=1, key="oqty")
            cust = st.text_input("Customer Name", key="ocust")
            if st.button("Place Order — Atomic"):
                c = get_conn()
                try:
                    c.execute("BEGIN IMMEDIATE")
                    cur = c.execute("SELECT stock FROM products WHERE id=?", (prod_id,))
                    row = cur.fetchone()
                    if not row or row[0] < qty:
                        c.execute("ROLLBACK")
                        st.error("Insufficient stock")
                    else:
                        c.execute("UPDATE products SET stock = stock - ? WHERE id=?", (qty, prod_id))
                        c.execute("INSERT INTO orders(product_id, qty, customer_name, created_at) VALUES(?,?,?,?)", (prod_id, qty, cust.strip(), time.time()))
                        c.execute("COMMIT")
                        st.success("Order placed — Stock decremented")
                except Exception as e:
                    try: c.execute("ROLLBACK")
                    except: pass
                    st.error(f"Failed: {e}")
                finally: c.close()
        st.dataframe(orders_df, use_container_width=True)
        oid = st.number_input("Order ID to cancel/return", min_value=0, step=1)
        if st.button("Cancel/Return — Restore Stock"):
            c = get_conn()
            try:
                c.execute("BEGIN IMMEDIATE")
                cur = c.execute("SELECT product_id, qty, status FROM orders WHERE id=?", (oid,))
                o = cur.fetchone()
                if not o:
                    c.execute("ROLLBACK")
                    st.error("Order not found")
                elif o[2] in ("cancelled","returned"):
                    c.execute("ROLLBACK")
                    st.warning("Already cancelled")
                else:
                    c.execute("UPDATE products SET stock = stock + ? WHERE id=?", (o[1], o[0]))
                    c.execute("UPDATE orders SET status='cancelled' WHERE id=?", (oid,))
                    c.execute("COMMIT")
                    st.success("Cancelled — Stock restored")
            except Exception as e:
                try: c.execute("ROLLBACK")
                except: pass
                st.error(f"Failed: {e}")
            finally: c.close()
    with sm_tab4:
        st.caption("Publish = Checklist + JSON export — No customer data — No external call — Connect real platform only via official docs")
        c = get_conn()
        try:
            stores = pd.read_sql_query("SELECT * FROM stores", c).to_dict(orient="records")
            products = pd.read_sql_query("SELECT id, title, price, stock FROM products", c).to_dict(orient="records")
        finally: c.close()
        checklist = {"stores": len(stores), "products": len(products), "ready": len(products)>0, "db_path": DB_PATH, "note": "Ephemeral hosting may erase DB — Use /mount/data + backup"}
        st.json(checklist)
        export = {"stores": stores, "products": products, "exported_at": time.time()}
        st.download_button("Download JSON Export", json.dumps(export, indent=2), file_name="mehar_publish_export.json", mime="application/json")

with tab4:
    st.subheader("System — Limitations Documented (Honest Prototype)")
    st.info("""
    **Hardened prototype — NOT production marketplace:**
    - Auth: single shared credential, session-only, refresh logs out — expected
    - Rate limit: SQLite per DB, not distributed
    - DB: leads.db may erase on redeploy — set MEHAR_DB_PATH=/mount/data/leads.db + backup
    - Easypaisa: DEMO ONLY — No verification — Use official merchant API for real
    - Webhooks: No endpoint — Needs separate HTTP backend + signature verify
    - PWA: No installable PWA — Needs static hosting + HTTPS + manifest strategy
    - Validation: Python syntax + ZIP check done — Live Streamlit/Groq/mobile/pen-test NOT done
    """)
    st.code(f"DB_PATH={DB_PATH}\nADMIN_USER set={bool(ADMIN_USER)}\nGROQ set={bool(GROQ_API_KEY)}\nStreamlit>=1.41 Groq>=0.13 Pandas>=2.2")
