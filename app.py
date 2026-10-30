import streamlit as st
import sqlite3
import os
from datetime import datetime
from groq import Groq

st.set_page_config(page_title="Mehar Super Agent v2", layout="wide")

ADMIN_USER = str(st.secrets.get("ADMIN_USER", "mehar_admin_9x")).strip()
ADMIN_PASS = str(st.secrets.get("ADMIN_PASS", "Strong#2026Pass")).strip()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("Mehar Super Agent v2 - Locked 🔒")
    u = st.text_input("Username").strip()
    p = st.text_input("Password", type="password").strip()
    if st.button("Login"):
        if u == ADMIN_USER and p == ADMIN_PASS:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Wrong login Bhai!")
    st.stop()

conn = sqlite3.connect("mehar.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS leads (id INTEGER PRIMARY KEY, name TEXT, phone TEXT, niche TEXT, created TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, title TEXT, details TEXT, created TEXT)")
conn.commit()

st.title("Mehar Super Agent v2 · Streamlit")
st.success(f"Logged in Bhai! {ADMIN_USER}")

tab1, tab2, tab3, tab4 = st.tabs(["Leads", "SEO Generator", "Store Manager", "System"])

with tab1:
    st.subheader("Add Lead — Validation 7-15 digits")
    with st.form("lead_form", clear_on_submit=True):
        name = st.text_input("Name * min 2")
        phone = st.text_input("Phone * 7-15 digits")
        niche = st.text_input("Niche * e.g. honey")
        submit = st.form_submit_button("Add Lead")
        if submit:
            if len(name.strip()) < 2:
                st.error("Name min 2 chars Bhai!")
            elif not (7 <= len(phone.strip()) <= 15 and phone.strip().isdigit()):
                st.error("Phone 7-15 digits only Bhai!")
            elif len(niche.strip()) < 2:
                st.error("Niche likho Bhai!")
            else:
                c.execute("INSERT INTO leads (name,phone,niche,created) VALUES (?,?,?,?)", (name.strip(), phone.strip(), niche.strip(), datetime.now().strftime("%Y-%m-%d %H:%M")))
                conn.commit()
                st.success(f"Lead added Bhai: {name}")
    leads = c.execute("SELECT id, name, phone, niche, created FROM leads ORDER BY id DESC").fetchall()
    st.write(leads if leads else "No leads yet")

with tab2:
    st.subheader("SEO Generator - Groq AI (FIXED BOX)")
    product_title = st.text_input("Product Title *", value="Mehar Sidr Honey 500g")
    features = st.text_area("Features / Details", value="100% pure, cold extracted, from Karak", height=120)
    if st.button("Generate SEO — Groq"):
        try:
            groq_key = str(st.secrets.get("GROQ_API_KEY", "")).strip()
            client = Groq(api_key=groq_key)
            prompt = f"SEO expert for Mehar Mart Peshawar. Product: {product_title}. Features: {features}. Give SEO Title (60 chars), SEO Description (160 chars), 5 Bullets, 10 Tags, Ad Description 30 words."
            with st.spinner("Groq soch raha hai Bhai..."):
                completion = client.chat.completions.create(model="openai/gpt-oss-20b", messages=[{"role": "user", "content": prompt}], temperature=0.7, max_tokens=1200)
                result = completion.choices[0].message.content
                st.success("SEO Ho gaya Bhai! MASHALLAH")
                st.text_area("Full SEO Result - Copy Karo", value=result, height=450)
                st.code(result, language="text")
        except Exception as e:
            st.error(f"Groq error Bhai: {e}")

with tab3:
    st.subheader("Store Manager")
    with st.form("product_form", clear_on_submit=True):
        t = st.text_input("Product Title *")
        d = st.text_area("Product Details")
        add_p = st.form_submit_button("Add to Store")
        if add_p:
            c.execute("INSERT INTO products (title,details,created) VALUES (?,?,?)", (t.strip(), d.strip(), datetime.now().strftime("%Y-%m-%d %H:%M")))
            conn.commit()
            st.success("Product added Bhai!")
    prods = c.execute("SELECT id, title, details, created FROM products ORDER BY id DESC").fetchall()
    st.write(prods if prods else "No products yet")

with tab4:
    st.subheader("System Status")
    st.write(f"Leads: {c.execute('SELECT COUNT(*) FROM leads').fetchone()[0]}")
    st.write(f"Products: {c.execute('SELECT COUNT(*) FROM products').fetchone()[0]}")
    st.write(f"Model: openai/gpt-oss-20b (Free)")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
