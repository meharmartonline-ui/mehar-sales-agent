import streamlit as st
import sqlite3
from datetime import datetime
from groq import Groq
import urllib.parse

st.set_page_config(page_title="Mehar Super Agent V9 - WHITE BG", layout="wide")

ADMIN_USER = str(st.secrets.get("ADMIN_USER", "mehar_admin_9x")).strip()
ADMIN_PASS = str(st.secrets.get("ADMIN_PASS", "Strong#2026Pass")).strip()
GROQ_KEY = str(st.secrets.get("GROQ_API_KEY", "")).strip()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "seo_result" not in st.session_state:
    st.session_state.seo_result = ""
if "image_url" not in st.session_state:
    st.session_state.image_url = ""

if not st.session_state.logged_in:
    st.title("Mehar Super Agent V9 - Locked 🔒")
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

st.title("Mehar Super Agent V9 — WHITE BACKGROUND + SHADOW WALA")
st.success(f"Logged in: {ADMIN_USER} ✅ V9 White BG Fix")

# --- WHITE BACKGROUND IMAGE FUNCTION — Bhai ye new hai ---
def make_image_url_white(product_name):
    prompt = f"Professional e-commerce product photo of {product_name} glass jar with gold lid, label says Mehar Sidr Honey 100% Pure from Karak 500g with bee logo, pure white background #FFFFFF, subtle soft realistic shadow under jar for depth, studio lighting, centered, Amazon Shopify listing style, 4k, high resolution"
    encoded = urllib.parse.quote(prompt)
    # Flux model + enhance = High quality like I made for you Bhai
    return f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&model=flux&enhance=true&nologo=true&seed=7"

tab0, tab1, tab2, tab3 = st.tabs(["🤖 Auto Builder - WHITE BG", "Leads", "Store Manager", "System"])

with tab0:
    st.header("Bhai bolo — White Background + Shadow wala product bana ke do!")
    st.info("1 Click me Description + White BG Picture + Shadow + Store — Sab auto banega jesi maine banayi thi!")
    
    with st.form("auto_builder_v9", clear_on_submit=False):
        auto_title = st.text_input("Product Bolo Bhai *", value="Mehar Sidr Honey 500g")
        auto_features = st.text_area("Features Bolo", value="100% pure, cold extracted, from Karak")
        auto_price = st.text_input("Price Bolo", value="2500")
        auto_stock = st.text_input("Stock Bolo", value="50")
        auto_btn = st.form_submit_button("🚀 WHITE BG PICTURE + SEO BANAO!")
        
        if auto_btn:
            if len(auto_title.strip()) < 2:
                st.error("Product naam likho Bhai!")
            else:
                # 1. SEO
                seo_text = ""
                if GROQ_KEY.startswith("gsk_"):
                    try:
                        client = Groq(api_key=GROQ_KEY)
                        prompt = f"SEO expert Mehar Mart Peshawar. Product: {auto_title}. Features: {auto_features}. Give Title 60 chars, Description 160 chars, 5 Bullets, 10 Tags, 30 word Ad. Never empty."
                        for model_name in ["llama-3.1-8b-instant", "llama-3.3-70b-versatile"]:
                            try:
                                comp = client.chat.completions.create(model=model_name, messages=[{"role": "system", "content": "You are SEO expert. Never empty."},{"role": "user", "content": prompt}], temperature=0.7, max_tokens=1500)
                                seo_text = comp.choices[0].message.content
                                if seo_text and len(seo_text.strip()) > 30:
                                    break
                            except:
                                continue
                    except:
                        seo_text = ""
                if not seo_text or len(seo_text.strip()) < 30:
                    seo_text = f"**SEO Title:** {auto_title} - 100% Pure | Mehar Mart\n**SEO Desc:** Buy {auto_title} - {auto_features} - Fast delivery Pakistan!\n**Bullets:** Pure - Karak - Premium - Fast Delivery - Trusted\n**Tags:** {auto_title}, honey, pure, Mehar Mart\n**Ad:** Discover {auto_title} pure from Karak. Order Mehar Mart!"

                # 2. WHITE BG IMAGE WITH SHADOW
                img_url = make_image_url_white(auto_title)
                
                # 3. SAVE
                c.execute("INSERT INTO products (title,price,stock,details,seo,image,created) VALUES (?,?,?,?,?,?,?)", (auto_title.strip(), auto_price.strip(), auto_stock.strip(), auto_features.strip(), seo_text, img_url, datetime.now().strftime("%Y-%m-%d %H:%M")))
                conn.commit()
                
                st.session_state.seo_result = seo_text
                st.session_state.image_url = img_url
                
                st.success(f"MASHALLAH Bhai! WHITE BG + SHADOW BAN GAYA ✅ — {auto_title}")
                st.balloons()

    # SHOW RESULT
    if st.session_state.seo_result:
        st.divider()
        col1, col2 = st.columns([1,1])
        with col1:
            st.subheader("🖼️ White BG + Subtle Shadow")
            if st.session_state.image_url:
                st.image(st.session_state.image_url, caption="Mehar Mart - White BG Store Listing", use_container_width=True)
                st.link_button("Download White BG Image", st.session_state.image_url)
            else:
                st.write("Image ban rahi hai Bhai...")
        with col2:
            st.subheader("📝 SEO + Description")
            st.text_area("Full SEO", value=st.session_state.seo_result, height=500)
            st.code(st.session_state.seo_result)

with tab1:
    st.subheader("Leads")
    with st.form("lead_form", clear_on_submit=True):
        name = st.text_input("Name * min 2")
        phone = st.text_input("Phone * 7-15 digits")
        niche = st.text_input("Niche *")
        if st.form_submit_button("Add Lead"):
            if len(name.strip()) < 2 or not (7 <= len(phone.strip()) <= 15 and phone.strip().isdigit()):
                st.error("Check Name/Phone!")
            else:
                c.execute("INSERT INTO leads (name,phone,niche,created) VALUES (?,?,?,?)", (name.strip(), phone.strip(), niche.strip(), datetime.now().strftime("%Y-%m-%d %H:%M")))
                conn.commit()
                st.success(f"Lead: {name}")
    st.dataframe(c.execute("SELECT * FROM leads ORDER BY id DESC").fetchall())

with tab2:
    st.subheader("Store Manager - White BG Products")
    prods = c.execute("SELECT id, title, price, stock, details, seo, image, created FROM products ORDER BY id DESC").fetchall()
    if prods:
        st.write(f"Total: {len(prods)} Products")
        for p in prods:
            pid, title, price, stock, details, seo, image, created = p
            with st.container(border=True):
                c1, c2, c3 = st.columns([1,2,1])
                with c1:
                    if image:
                        st.image(image, width=150)
                with c2:
                    st.write(f"**{title}** — Rs.{price} | Stock:{stock}")
                    st.write(f"Details: {details}")
                    with st.expander("SEO Dekho"):
                        st.write(seo)
                with c3:
                    if st.button(f"Delete {pid}", key=f"del_{pid}"):
                        c.execute("DELETE FROM products WHERE id=?", (pid,))
                        conn.commit()
                        st.rerun()
    else:
        st.write("No products yet")

with tab3:
    st.subheader("System V9 - White BG Fix")
    st.write(f"Image Engine: Flux + Enhance + White BG + Subtle Shadow ✅")
    st.write(f"Products: {c.execute('SELECT COUNT(*) FROM products').fetchone()[0]}")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.seo_result = ""
        st.session_state.image_url = ""
        st.rerun()
