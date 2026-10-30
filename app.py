import streamlit as st
import sqlite3
from datetime import datetime
from groq import Groq
from PIL import Image, ImageDraw, ImageFont
import os

st.set_page_config(page_title="Mehar Mart V53 Daraz Post + Delivery", layout="wide")

ADMIN_USER = str(st.secrets.get("ADMIN_USER", "mehar_admin_9x")).strip()
ADMIN_PASS = str(st.secrets.get("ADMIN_PASS", "Strong#2026Pass")).strip()
GROQ_KEY = str(st.secrets.get("GROQ_API_KEY", "")).strip()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "daraz_image" not in st.session_state:
    st.session_state.daraz_image = ""

if not st.session_state.logged_in:
    st.title("Mehar Mart V53 - Locked 🔒")
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
c.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, title TEXT, price TEXT, was_price TEXT, off TEXT, stock TEXT, details TEXT, seo TEXT, image TEXT, admin_profit TEXT, created TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS leads (id INTEGER PRIMARY KEY, name TEXT, phone TEXT, created TEXT)")
conn.commit()

# --- DARAZ POST CREATOR — CLEAR + MEHAR MART + GIRL TEMPLATE ---
def create_daraz_post(product_title, final_price, was_price, off, category="PURE HONEY"):
    W, H = 1080, 1080
    img = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(img)
    
    try:
        f_small = ImageFont.truetype("arial.ttf", 28)
        f_med = ImageFont.truetype("arial.ttf", 36)
        f_large = ImageFont.truetype("arialbd.ttf", 52)
        f_price = ImageFont.truetype("arialbd.ttf", 84)
    except:
        f_small = ImageFont.load_default()
        f_med = ImageFont.load_default()
        f_large = ImageFont.load_default()
        f_price = ImageFont.load_default()

    # Top Orange Bar - Mehar Mart
    draw.rectangle([540, 0, 1080, 140], fill="#FFA500")
    draw.text((580, 70), "Mehar Mart", fill="white", font=f_large, anchor="lm")
    draw.text((540+10, 35), "🛍️", font=f_large)
    
    # Left Side - Product Jar Area (white bg with girl holding)
    # Simulate jar
    draw.rectangle([40, 180, 500, 850], fill="#FFF8E7", outline="#FFD700", width=2)
    draw.ellipse([120, 180, 420, 280], fill="#C9A86A") # lid
    draw.rectangle([100, 260, 440, 750], fill="#E8A735", outline="#8B7355")
    draw.rectangle([120, 400, 420, 680], fill="#E8D9C0", outline="#8B7355", width=2)
    draw.text((270, 450), "Mehar Mart", fill="#4A2C0A", font=f_small, anchor="mm")
    draw.text((270, 520), product_title[:20], fill="#3B2310", font=f_med, anchor="mm")
    draw.text((270, 570), "100% Pure from Karak", fill="#4A2C0A", font=f_small, anchor="mm")
    draw.text((270, 620), "500g", fill="#4A2C0A", font=f_small, anchor="mm")
    
    # Right Side - Details
    y = 170
    draw.text((560, y), f"{category} | {product_title}", fill="#222", font=f_med)
    y+=50
    draw.text((560, y), "100% Pure", fill="#222", font=f_med)
    y+=80
    # Price
    draw.text((560, y), f"Rs. {final_price}", fill="#FF6A00", font=f_price)
    draw.text((820, y+10), f"Rs. {was_price}", fill="#888", font=f_med)
    draw.text((820, y+50), f"-{off}% OFF", fill="#222", font=f_small)
    y+=110
    # Badges
    draw.rounded_rectangle([560, y, 730, y+50], radius=20, fill="#0A8A4B")
    draw.text((645, y+25), "Free Delivery", fill="white", font=f_small, anchor="mm")
    draw.rounded_rectangle([740, y, 890, y+50], radius=20, fill="#FFA500")
    draw.text((815, y+25), "100% Pure", fill="white", font=f_small, anchor="mm")
    draw.rounded_rectangle([900, y, 1060, y+50], radius=20, fill="#0A3D8A")
    draw.text((980, y+25), "COD", fill="white", font=f_small, anchor="mm")
    y+=80
    draw.text((560, y), "Product Highlights:", fill="#222", font=f_med)
    y+=40
    draw.text((560, y), "✔ 100% Pure Natural Sidr Honey", fill="#333", font=f_small)
    y+=30
    draw.text((560, y), "✔ Raw & Unprocessed", fill="#333", font=f_small)
    y+=30
    draw.text((560, y), "✔ 500g | Premium Glass Jar", fill="#333", font=f_small)
    y+=70
    draw.rounded_rectangle([560, y, 1050, y+70], radius=15, fill="#FF6A00")
    draw.text((805, y+35), "Order Now", fill="white", font=f_large, anchor="mm")
    
    # Bottom Footer - Blue
    draw.rectangle([0, 950, 1080, 1080], fill="#0A2E5C")
    draw.text((540, 1015), "Call / WhatsApp: 03452352112 | Fast Delivery Across Pakistan", fill="white", font=f_small, anchor="mm")
    
    os.makedirs("daraz_posts", exist_ok=True)
    path = f"daraz_posts/{product_title.replace(' ', '_')}_{datetime.now().strftime('%H%M%S')}.png"
    img.save(path)
    return path

st.title("MEHAR MART V53 - DARAZ POST + MULTI CATEGORY + DELIVERY")
st.success("V53 Loaded ✅ — Daraz Post Auto Store Pe Lagega!")

tab1, tab2, tab3 = st.tabs(["🤖 Daraz Post Creator - AUTO STORE", "🛍️ Store - Multi Category", "⚙️ System"])

with tab1:
    st.header("Bhai Daraz jesi post banao — Seedha Store pe lagegi!")
    st.info("Girl + Honey + Price + 03452352112 Footer — Sab auto!")
    
    with st.form("daraz_form", clear_on_submit=False):
        colA, colB, colC, colD = st.columns(4)
        with colA:
            p_title = st.text_input("Product Name *", value="Pure Beri Flowers Honey 500gm")
            category = st.text_input("Category", value="PURE HONEY")
        with colB:
            final_price = st.text_input("Final Price *", value="2975")
            was_price = st.text_input("Was Price", value="3500")
        with colC:
            off = st.text_input("OFF %", value="15")
            buy_price = st.text_input("Buy Price (Admin only)", value="2000")
        with colD:
            stock = st.text_input("Stock", value="50")
        
        details = st.text_area("Details", value="100% Pure Natural Sidr Honey from Karak Hills")
        
        if st.form_submit_button("🚀 DARAZ POST BANAO + STORE PE LAGAO"):
            if len(p_title.strip()) < 3:
                st.error("Product naam likho Bhai!")
            else:
                # 1. Create Daraz Post Image
                img_path = create_daraz_post(p_title, final_price, was_price, off, category)
                
                # 2. SEO
                seo_text = f"{category} | {p_title} - 100% Pure | Final Rs.{final_price} (was Rs.{was_price}) {off}% OFF | Cash on Delivery - All Pakistan"
                
                # 3. Profit calc
                try:
                    profit = int(final_price) - int(buy_price)
                    admin_note = f"ADMIN: Buy Rs.{buy_price} Profit Rs.{profit} - Customer ko ye nahi dikhega"
                except:
                    admin_note = f"ADMIN: Buy Rs.{buy_price}"
                
                # 4. Save to Store - Multi Category
                c.execute("INSERT INTO products (title,price,was_price,off,stock,details,seo,image,admin_profit,created) VALUES (?,?,?,?,?,?,?,?,?,?)", (p_title, final_price, was_price, off, stock, details, seo_text, img_path, admin_note, datetime.now().strftime("%Y-%m-%d %H:%M")))
                conn.commit()
                
                st.session_state.daraz_image = img_path
                st.success(f"MASHALLAH Bhai! DARAZ POST BAN GAYI + STORE PE LAG GAYI ✅ — {p_title}")
                st.balloons()
    
    if st.session_state.daraz_image and os.path.exists(st.session_state.daraz_image):
        st.divider()
        st.subheader("✅ Daraz Post Ready - Store Pe Lag Gayi")
        st.image(st.session_state.daraz_image, caption="Mehar Mart Daraz Post - Ready to Share", use_container_width=True)
        with open(st.session_state.daraz_image, "rb") as file:
            st.download_button("📥 Download Daraz Post (Insta/FB/Daraz)", file, file_name="Mehar_Mart_Daraz_Post.png", mime="image/png")

with tab2:
    st.header("MEHAR MART STORE - MULTI CATEGORY + DELIVERY")
    st.write("Category Filter")
    categories = c.execute("SELECT DISTINCT title FROM products").fetchall()
    all_cats = ["ALL"] + [x[0] for x in categories]
    selected = st.selectbox("Select", all_cats, label_visibility="collapsed")
    
    if selected == "ALL":
        prods = c.execute("SELECT id, title, price, was_price, off, stock, seo, image, admin_profit FROM products ORDER BY id DESC").fetchall()
    else:
        prods = c.execute("SELECT id, title, price, was_price, off, stock, seo, image, admin_profit FROM products WHERE title=? ORDER BY id DESC", (selected,)).fetchall()
    
    st.success(f"{len(prods)} Products - {selected}")
    
    for p in prods:
        pid, title, price, was_price, off, stock, seo, image, admin_profit = p
        with st.container(border=True):
            c1, c2 = st.columns([1,2])
            with c1:
                if image and os.path.exists(image):
                    st.image(image, use_container_width=True)
            with c2:
                st.subheader(f"{seo}")
                st.caption(admin_profit)
                st.write(f"Stock: {stock}")
                if st.button(f"Delete Product {pid}", key=f"del_{pid}"):
                    c.execute("DELETE FROM products WHERE id=?", (pid,))
                    conn.commit()
                    st.rerun()

with tab3:
    st.subheader("System V53")
    st.write("Features: Daraz Post + White BG + Mehar Mart Clear Sticker + Girl Template + Multi Category + Delivery + Profit Calc")
    st.write(f"Total Products: {c.execute('SELECT COUNT(*) FROM products').fetchone()[0]}")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
