import streamlit as st
import sqlite3
from groq import Groq
import os
from datetime import datetime

st.set_page_config(page_title="Mehar Super Agent v2", layout="wide")
st.title("Mehar Super Agent v2 — Fixed Prototype 🔒")
st.caption("Leads + SEO (Groq) + Store Manager — Demo payment only — No real Easypaisa/WhatsApp/PWA")

# --- LOGIN FIX WITH STRIP ---
ADMIN_USER = str(st.secrets.get("ADMIN_USER", "mehar_admin_9x")).strip()
ADMIN_PASS = str(st.secrets.get("ADMIN_PASS", "Strong#2026Pass")).strip()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    u = st.text_input("Username").strip()
    p = st.text_input("Password", type="password").strip()
    if st.button("Login"):
        if u == ADMIN_USER and p == ADMIN_PASS:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Wrong login Bhai!")
    st.stop()

# --- DB ---
conn = sqlite3.connect("mehar.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS leads (id INTEGER PRIMARY KEY, name TEXT, phone TEXT, niche TEXT, created TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, title TEXT, details TEXT)")
conn.commit()

tab1, tab2, tab3, tab4 = st.tabs(["Leads", "SEO Generator", "Store Manager", "System"])

with tab1:
    st.subheader("Add Lead — Validation 7-15 digits")
    with st.form("lead_form"):
        name = st.text_input("Name * min 2")
        phone = st.text_input("Phone * 7-15 digits")
        niche = st.text_input("Niche * e.g. honey")
        submitted = st.form_submit_button("Add Lead")
        if submitted:
            if len(name.strip()) < 2:
                st.error("Name min 2 chars Bhai!")
            elif not (7 <= len(phone.strip()) <= 15 and phone.strip().isdigit()):
                st.error("Phone 7-15 digits only Bhai!")
            elif len(niche.strip()) < 2:
                st.error("Niche likho Bhai!")
            else:
                c.execute("INSERT INTO leads (name,phone,niche,created) VALUES (?,?,?,?)", (name, phone, niche, datetime.now().strftime("%Y-%m-%d %H:%M")))
                conn.commit()
                st.success(f"Lead added Bhai: {name}")
    st.divider()
    st.subheader("All Leads")
    rows = c.execute("SELECT * FROM leads ORDER BY id DESC").fetchall()
    st.write(rows if rows else "No leads yet")

with tab2:
    st.subheader("SEO Generator - Groq AI")
    product_title = st.text_input("Product Title *", value="Mehar Sidr Honey 500g")
    features = st.text_area("Features / Details", value="100% pure, cold extracted, from Karak, for winter", height=120)
    if st.button("Generate SEO — Groq (timeout 30s, 1 retry)"):
        try:
            groq_key = str(st.secrets.get("GROQ_API_KEY","")).strip()
            if not groq_key:
                st.error("GROQ_API_KEY missing in secrets Bhai!")
            else:
                client = Groq(api_key=groq_key)
                prompt = f"You are SEO expert for Mehar Mart Peshawar. Product: {product_title}. Features: {features}. Generate SEO Title (60 chars), SEO Desc (160 chars), 5 Bullets, 10 Tags. Mix Urdu+English."
                with st.spinner("Groq AI soch raha hai..."):
                    completion = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role":"user","content":prompt}],
                        temperature=0.7,
                        max_tokens=900
                    )
                    st.markdown("### Result:")
                    st.write(completion.choices[0].message.content)
                    st.success("Ho gaya Bhai!")
        except Exception as e:
            st.error(f"Groq error: {e}")

with tab3:
    st.subheader("Store Manager — Catalog + Ad Studio V4.1")
    t = st.text_input("Product Title for Store")
    d = st.text_area("Product Details")
    if st.button("Add to Store"):
        if t:
            c.execute("INSERT INTO products (title,details) VALUES (?,?)", (t,d))
            conn.commit()
            st.success("Product added!")
    st.write(c.execute("SELECT * FROM products ORDER BY id DESC").fetchall())

with tab4:
    st.subheader("System Status")
    st.write("ADMIN_USER:", ADMIN_USER)
    st.write("GROQ_KEY present:", "Yes" if st.secrets.get("GROQ_API_KEY") else "No")
    st.write("DB Path:", os.path.abspath("mehar.db"))
    st.write("Leads count:", c.execute("SELECT COUNT(*) FROM leads").fetchone()[0])
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
