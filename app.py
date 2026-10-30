import streamlit as st
import sqlite3
from datetime import datetime
from groq import Groq

st.set_page_config(page_title="Mehar Super Agent v2", layout="wide", initial_sidebar_state="collapsed")

# --- SECRETS ---
ADMIN_USER = str(st.secrets.get("ADMIN_USER", "mehar_admin_9x")).strip()
ADMIN_PASS = str(st.secrets.get("ADMIN_PASS", "Strong#2026Pass")).strip()
GROQ_KEY = str(st.secrets.get("GROQ_API_KEY", "")).strip()

# --- LOGIN PERSISTENT FIX — Bar bar login khatam ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "seo_result" not in st.session_state:
    st.session_state.seo_result = ""

if not st.session_state.logged_in:
    st.title("Mehar Super Agent v2 - Locked 🔒")
    st.info("Bhai login karo — Ek bar login to bar bar nahi ayega ✅")
    with st.form("login_form_v5"):
        u = st.text_input("Username").strip()
        p = st.text_input("Password", type="password").strip()
        login_btn = st.form_submit_button("Login 🔓")
        if login_btn:
            if u == ADMIN_USER and p == ADMIN_PASS:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error(f"Wrong login Bhai! Aapne likha: {u}")
    st.stop()

# --- DB ---
conn = sqlite3.connect("mehar.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS leads (id INTEGER PRIMARY KEY, name TEXT, phone TEXT, niche TEXT, created TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, title TEXT, details TEXT, created TEXT)")
conn.commit()

st.title("Mehar Super Agent v2 · Streamlit")
st.success(f"Logged in: {ADMIN_USER} — Login Permanent Fix ✅")
st.caption(f"GROQ_KEY Status: {'OK ✅ ' + GROQ_KEY[:10] + '...' if GROQ_KEY.startswith('gsk_') else 'INVALID ❌ Secrets check karo'}")

tab1, tab2, tab3, tab4 = st.tabs(["Leads", "SEO Generator", "Store Manager", "System"])

with tab1:
    with st.form("lead_form", clear_on_submit=True):
        name = st.text_input("Name * min 2")
        phone = st.text_input("Phone * 7-15 digits")
        niche = st.text_input("Niche *")
        submit = st.form_submit_button("Add Lead")
        if submit:
            if len(name.strip()) < 2 or not (7 <= len(phone.strip()) <= 15 and phone.strip().isdigit()):
                st.error("Check Name/Phone Bhai!")
            else:
                c.execute("INSERT INTO leads (name,phone,niche,created) VALUES (?,?,?,?)", (name.strip(), phone.strip(), niche.strip(), datetime.now().strftime("%Y-%m-%d %H:%M")))
                conn.commit()
                st.success(f"Lead added: {name}")
    leads = c.execute("SELECT id, name, phone, niche, created FROM leads ORDER BY id DESC").fetchall()
    st.write(leads if leads else "No leads")

with tab2:
    st.subheader("SEO Generator - Groq AI (FINAL FIXED)")
    product_title = st.text_input("Product Title *", value="Mehar Sidr Honey 500g", key="p_title")
    features = st.text_area("Features / Details", value="100% pure, cold extracted, from Karak", height=120, key="p_feat")

    if st.button("Generate SEO — Groq", type="primary"):
        if not GROQ_KEY.startswith("gsk_"):
            st.error("Bhai Secrets me GROQ_API_KEY galat hai! console.groq.com se nayi key banao!")
        else:
            client = Groq(api_key=GROQ_KEY)
            prompt = f"""You are SEO expert for Mehar Mart Peshawar, Pakistan.
Product: {product_title}
Features: {features}
Write in simple English:
1. SEO Title - 60 chars max
2. SEO Description - 160 chars max
3. 5 Bullet Points
4. 10 Tags comma separated
5. 30 words Ad Description
No empty response. Must give full result."""

            result = ""
            error_msg = ""
            with st.spinner("Groq soch raha hai Bhai... 10 sec..."):
                for model_name in ["llama-3.1-8b-instant", "llama-3.3-70b-versatile", "mixtral-8x7b-32768"]:
                    try:
                        comp = client.chat.completions.create(
                            model=model_name,
                            messages=[{"role": "system", "content": "You are helpful SEO assistant. Never return empty."},
                                      {"role": "user", "content": prompt}],
                            temperature=0.7,
                            max_tokens=1500
                        )
                        result = comp.choices[0].message.content
                        if result and len(result.strip()) > 30:
                            break
                    except Exception as e:
                        error_msg = str(e)
                        continue
            
            # FALLBACK - Kabhi khali nahi ayega Bhai
            if not result or len(result.strip()) < 30:
                st.warning(f"Groq busy hai ({error_msg[:100]}), Fallback SEO de raha hon Bhai!")
                result = f"""**SEO Title (60 chars):** {product_title} - 100% Pure & Original | Mehar Mart Peshawar

**SEO Description (160 chars):** Buy {product_title} online in Pakistan. {features}. 100% pure, fast delivery across Peshawar, Lahore, Karachi. Order now at Mehar Mart!

**5 Bullets:**
- 100% Pure & Natural - {features}
- Direct from Karak - No mixing
- Premium Quality Guaranteed
- Fast Delivery All Pakistan
- Trusted by 5000+ Customers - Mehar Mart

**10 Tags:** {product_title}, pure honey, sidr honey, Karak honey, Mehar Mart, Peshawar, organic honey, natural honey, honey 500g, buy honey Pakistan

**Ad Description (30 words):** Discover pure {product_title} from Karak valleys. Cold extracted, 100% natural, packed with health benefits. Order today from Mehar Mart Peshawar and taste real purity!
"""
            
            st.session_state.seo_result = result
            st.success("SEO Ho gaya Bhai! MASHALLAH ✅")

    # PERSISTENT RESULT — Login se bhi nahi jayega
    if st.session_state.seo_result:
        st.text_area("Full SEO Result - Copy Karo", value=st.session_state.seo_result, height=600, key="seo_box")
        st.code(st.session_state.seo_result, language="text")

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
    st.write(prods if prods else "No products")

with tab4:
    st.subheader("System Status")
    st.write(f"Login: Permanent ✅")
    st.write(f"GROQ_KEY: {GROQ_KEY[:15]}... ({len(GROQ_KEY)} chars)")
    st.write(f"Leads: {c.execute('SELECT COUNT(*) FROM leads').fetchone()[0]}")
    st.write(f"Products: {c.execute('SELECT COUNT(*) FROM products').fetchone()[0]}")
    if st.button("Logout — Bar bar login fix ke liye logout"):
        st.session_state.logged_in = False
        st.session_state.seo_result = ""
        st.rerun()
