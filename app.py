import streamlit as st
import sqlite3
from datetime import datetime
from groq import Groq

st.set_page_config(page_title="Mehar Super Agent V7 - SAB BANA KE DE", layout="wide")

ADMIN_USER = str(st.secrets.get("ADMIN_USER", "mehar_admin_9x")).strip()
ADMIN_PASS = str(st.secrets.get("ADMIN_PASS", "Strong#2026Pass")).strip()
GROQ_KEY = str(st.secrets.get("GROQ_API_KEY", "")).strip()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "seo_result" not in st.session_state:
    st.session_state.seo_result = ""

if not st.session_state.logged_in:
    st.title("Mehar Super Agent V7 - Locked 🔒")
    with st.form("login_form"):
        u = st.text_input("Username").strip()
        p = st.text_input("Password", type="password").strip()
        if st.form_submit_button("Login 🔓"):
            if u == ADMIN_USER and p == ADMIN_PASS:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Wrong login Bhai!")
    st.stop()

conn = sqlite3.connect("mehar.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS leads (id INTEGER PRIMARY KEY, name TEXT, phone TEXT, niche TEXT, created TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, title TEXT, price TEXT, stock TEXT, details TEXT, seo TEXT, image TEXT, created TEXT)")
conn.commit()

st.title("Mehar Super Agent V7 — SAB BANA KE DE WALA")
st.success(f"Logged in: {ADMIN_USER} ✅")

tab0, tab1, tab2, tab3, tab4 = st.tabs(["🤖 Auto Builder - SAB BANA KE DE", "Leads", "SEO Generator", "Store Manager", "System"])

# --- NEW TAB — SAB BANA KE DE ---
with tab0:
    st.header("Bhai bas bolo — Ye bana ke do — Main sab bana dunga!")
    st.info("Aap sirf Product ka naam likho — Main SEO + Product + Store me khud add kar dunga!")
    
    with st.form("auto_builder_form", clear_on_submit=False):
        auto_title = st.text_input("Product Bolo Bhai *", value="Mehar Sidr Honey 500g", placeholder="e.g. Mehar Beri Honey 1kg")
        auto_features = st.text_area("Features Bolo (optional)", value="100% pure, cold extracted, from Karak", placeholder="e.g. pure, organic")
        auto_price = st.text_input("Price Bolo", value="2500")
        auto_stock = st.text_input("Stock Bolo", value="50")
        auto_btn = st.form_submit_button("🚀 SAB BANA KE DE — 1 Click Me Sab!")
        
        if auto_btn:
            if len(auto_title.strip()) < 2:
                st.error("Product ka naam to bolo Bhai!")
            else:
                # 1. SEO GENERATE
                seo_text = ""
                if GROQ_KEY.startswith("gsk_"):
                    try:
                        client = Groq(api_key=GROQ_KEY)
                        prompt = f"SEO expert for Mehar Mart Peshawar. Product: {auto_title}. Features: {auto_features}. Give Title 60 chars, Description 160 chars, 5 Bullets, 10 Tags, 30 word Ad. Never empty."
                        for model_name in ["llama-3.1-8b-instant", "llama-3.3-70b-versatile"]:
                            try:
                                comp = client.chat.completions.create(model=model_name, messages=[{"role": "system", "content": "You are SEO expert. Never return empty."},{"role": "user", "content": prompt}], temperature=0.7, max_tokens=1500)
                                seo_text = comp.choices[0].message.content
                                if seo_text and len(seo_text.strip()) > 30:
                                    break
                            except:
                                continue
                    except Exception as e:
                        seo_text = ""
                
                if not seo_text or len(seo_text.strip()) < 30:
                    seo_text = f"""**SEO Title:** {auto_title} - 100% Pure & Original | Mehar Mart Peshawar
**SEO Description:** Buy {auto_title} online. {auto_features}. Fast delivery All Pakistan. Order now at Mehar Mart!
**5 Bullets:** 100% Pure - From Karak - Premium Quality - Fast Delivery - Trusted 5000+ Customers
**10 Tags:** {auto_title}, pure honey, Karak, Mehar Mart, Peshawar, organic, natural, honey, buy honey, Pakistan
**Ad Description:** Discover pure {auto_title} from Karak valleys. 100% natural. Order today from Mehar Mart Peshawar!"""

                # 2. STORE ME ADD
                c.execute("INSERT INTO products (title,price,stock,details,seo,image,created) VALUES (?,?,?,?,?,?,?)", (auto_title.strip(), auto_price.strip(), auto_stock.strip(), auto_features.strip(), seo_text, "", datetime.now().strftime("%Y-%m-%d %H:%M")))
                conn.commit()
                
                st.session_state.seo_result = seo_text
                st.success(f"MASHALLAH Bhai! SAB BAN GAYA ✅ — {auto_title} Store me add ho gaya!")
                st.balloons()
                
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("✅ Product Added")
                    st.write(f"**Title:** {auto_title}")
                    st.write(f"**Price:** Rs. {auto_price}")
                    st.write(f"**Stock:** {auto_stock}")
                with col2:
                    st.subheader("✅ SEO Generated")
                    st.text_area("SEO Result", value=seo_text, height=400)

    # Last auto result show
    if st.session_state.seo_result:
        st.divider()
        st.subheader("Last Generated SEO")
        st.code(st.session_state.seo_result)

with tab1:
    st.subheader("Leads")
    with st.form("lead_form", clear_on_submit=True):
        name = st.text_input("Name * min 2")
        phone = st.text_input("Phone * 7-15 digits")
        niche = st.text_input("Niche *")
        if st.form_submit_button("Add Lead"):
            if len(name.strip()) < 2 or not (7 <= len(phone.strip()) <= 15 and phone.strip().isdigit()):
                st.error("Check Name/Phone Bhai!")
            else:
                c.execute("INSERT INTO leads (name,phone,niche,created) VALUES (?,?,?,?)", (name.strip(), phone.strip(), niche.strip(), datetime.now().strftime("%Y-%m-%d %H:%M")))
                conn.commit()
                st.success(f"Lead added: {name}")
    st.dataframe(c.execute("SELECT id, name, phone, niche, created FROM leads ORDER BY id DESC").fetchall())

with tab2:
    st.subheader("SEO Generator Manual")
    product_title = st.text_input("Product Title *", value="Mehar Sidr Honey 500g", key="p_title")
    features = st.text_area("Features", value="100% pure, cold extracted, from Karak", height=120, key="p_feat")
    if st.button("Generate SEO"):
        # reuse same logic
        client = Groq(api_key=GROQ_KEY)
        prompt = f"SEO for {product_title} - {features}"
        try:
            comp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}], max_tokens=1500)
            st.session_state.seo_result = comp.choices[0].message.content
            st.success("SEO Done")
        except Exception as e:
            st.error(f"{e}")
    if st.session_state.seo_result:
        st.text_area("SEO", value=st.session_state.seo_result, height=500)

with tab3:
    st.subheader("Store Manager - All Products")
    prods = c.execute("SELECT id, title, price, stock, details, seo, image, created FROM products ORDER BY id DESC").fetchall()
    if prods:
        st.write(f"Total: {len(prods)} Products")
        for p in prods:
            pid, title, price, stock, details, seo, image, created = p
            with st.container(border=True):
                st.write(f"**{title}** — Rs.{price} | Stock:{stock} | {created}")
                st.write(f"Details: {details}")
                with st.expander("SEO Dekho"):
                    st.write(seo)
                if st.button(f"Delete {pid}", key=f"del_{pid}"):
                    c.execute("DELETE FROM products WHERE id=?", (pid,))
                    conn.commit()
                    st.rerun()
    else:
        st.write("No products yet — Auto Builder se banao Bhai!")

with tab4:
    st.subheader("System")
    st.write(f"Products: {c.execute('SELECT COUNT(*) FROM products').fetchone()[0]}")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
