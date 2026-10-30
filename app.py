import streamlit as st
import sqlite3
from datetime import datetime
from groq import Groq
from PIL import Image, ImageDraw, ImageFont
import os

st.set_page_config(page_title="MEHAR MART V60 DARAZ POST FIX", layout="wide")

ADMIN_USER = str(st.secrets.get("ADMIN_USER", "mehar_admin_9x")).strip()
ADMIN_PASS = str(st.secrets.get("ADMIN_PASS", "Strong#2026Pass")).strip()
GROQ_KEY = str(st.secrets.get("GROQ_API_KEY", "")).strip()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "last_post" not in st.session_state:
    st.session_state.last_post = ""

if not st.session_state.logged_in:
    st.title("MEHAR MART V60 - Locked 🔒")
    with st.form("login"):
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
c.execute("""CREATE TABLE IF NOT EXISTS products 
(id INTEGER PRIMARY KEY, name TEXT, kharid TEXT, bechne TEXT, final_price TEXT, discount TEXT, stock TEXT, expiry TEXT, highlights TEXT, full_desc TEXT, specs TEXT, image_path TEXT, daraz_post_path TEXT, profit TEXT, created TEXT)""")
conn.commit()

def calc_final(bechne, discount):
    try:
        b = float(bechne)
        d = float(discount)
        final = b - (b * d / 100)
        return str(int(final))
    except:
        return bechne

def calc_profit(final, kharid):
    try:
        return str(int(float(final) - float(kharid)))
    except:
        return "0"

def create_daraz_post_v60(product_name, final_price, was_price, discount, highlights, specs, uploaded_img_path=None):
    W, H = 1080, 1080
    img = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(img)
    try:
        f_small = ImageFont.truetype("arial.ttf", 22)
        f_med = ImageFont.truetype("arial.ttf", 30)
        f_large = ImageFont.truetype("arialbd.ttf", 44)
        f_price = ImageFont.truetype("arialbd.ttf", 72)
        f_tiny = ImageFont.truetype("arial.ttf", 18)
    except:
        f_small = ImageFont.load_default()
        f_med = ImageFont.load_default()
        f_large = ImageFont.load_default()
        f_price = ImageFont.load_default()
        f_tiny = ImageFont.load_default()

    # Top Orange - Mehar Mart
    draw.rectangle([0, 0, 1080, 110], fill="#FF6A00")
    draw.text((30, 55), "Mehar Mart", fill="white", font=f_large, anchor="lm")
    draw.text((750, 55), "Official Store | 4.8 ★ (1.2k)", fill="white", font=f_small, anchor="lm")

    # Left side - Product Image
    left_box = (20, 130, 520, 940)
    draw.rectangle(left_box, fill="#FFFFFF", outline="#E0E0E0", width=2)
    
    if uploaded_img_path and os.path.exists(uploaded_img_path):
        try:
            prod_img = Image.open(uploaded_img_path).convert("RGB")
            prod_img = prod_img.resize((480, 700))
            img.paste(prod_img, (30, 140))
        except:
            draw.text((270, 500), "PURE\nHONEY\n500gm", fill="#8B4513", font=f_large, anchor="mm")
    else:
        draw.text((270, 400), "PURE HONEY", fill="#8B4513", font=f_large, anchor="mm")
        draw.text((270, 500), product_name[:25], fill="#333", font=f_small, anchor="mm")

    # Right side
    y = 140
    draw.text((540, y), product_name, fill="#111", font=f_med)
    y+=70
    # Wrap highlights for subtitle
    sub = highlights.split("\n")[0][:60] if highlights else "100% Pure - No Sugar, No Mix"
    draw.text((540, y), sub, fill="#333", font=f_small)
    y+=40
    draw.text((540, y), "★★★★★  4.8 | 356 Ratings • 120 Sold", fill="#555", font=f_tiny)
    y+=50
    draw.text((540, y), f"Rs. {final_price}", fill="#FF6A00", font=f_price)
    draw.text((780, y+15), f"Rs. {was_price}", fill="#888", font=f_med)
    draw.rounded_rectangle([900, y+10, 1040, y+45], radius=15, fill="#FF6A00")
    draw.text((970, y+27), f"{discount}% OFF", fill="white", font=f_small, anchor="mm")
    y+=80
    # Badges
    draw.rounded_rectangle([540, y, 710, y+40], radius=20, fill="#FFF0E0", outline="#FF6A00")
    draw.text((625, y+20), "Free Delivery", fill="#FF6A00", font=f_tiny, anchor="mm")
    draw.rounded_rectangle([720, y, 870, y+40], radius=20, fill="#FFF0E0", outline="#FF6A00")
    draw.text((795, y+20), "100% Pure", fill="#FF6A00", font=f_tiny, anchor="mm")
    draw.rounded_rectangle([880, y, 1050, y+40], radius=20, fill="#FFF0E0", outline="#FF6A00")
    draw.text((965, y+20), "Cash on Delivery", fill="#FF6A00", font=f_tiny, anchor="mm")
    y+=60
    draw.text((540, y), "Highlights:", fill="#111", font=f_med)
    y+=30
    for line in highlights.split("\n")[:4]:
        if line.strip():
            draw.text((540, y), f"✓ {line.strip()}", fill="#333", font=f_tiny)
            y+=22
    y+=10
    draw.text((540, y), "Specifications:", fill="#111", font=f_small)
    y+=25
    # Specs box
    draw.rectangle([540, y, 1050, y+110], fill="#F5F5F5", outline="#DDD")
    spec_lines = specs.split("\n")[:4]
    sy = y+10
    for line in spec_lines:
        draw.text((550, sy), line.strip(), fill="#333", font=f_tiny)
        sy+=25

    # Bottom Blue Footer
    draw.rectangle([0, 960, 1080, 1080], fill="#0A3D8A")
    draw.text((540, 1020), "Call / WhatsApp: 03452352112 | Fast Delivery Across Pakistan | MEHAR MART - Aapki Sehat Ka Sathi", fill="white", font=f_small, anchor="mm")

    os.makedirs("daraz_posts", exist_ok=True)
    out_path = f"daraz_posts/Daraz_{product_name.replace(' ', '_')[:20]}_{datetime.now().strftime('%H%M%S')}.png"
    img.save(out_path)
    return out_path

st.title("MEHAR MART V60 — DARAZ POST + PASS FIX")
st.success(f"Logged in: {ADMIN_USER} ✅ V60 Daraz Auto")

tab1, tab2 = st.tabs(["➕ Add Product - Daraz Post Auto", "🛍️ MEHAR MART STORE - V59"])

with tab1:
    st.subheader("Add Product — Same as V59 + Auto Daraz Post")
    with st.form("v60_form", clear_on_submit=False):
        st.write("**Product Name * **")
        name = st.text_input("Product Name *", value="Pure Beri Flowers Honey 500gm - 100% Pure", label_visibility="collapsed")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("Kharid Rate *")
            kharid = st.number_input("Kharid Rate *", value=2000, min_value=1, step=1, label_visibility="collapsed")
        with col2:
            st.write("Bechne Rate *")
            bechne = st.number_input("Bechne Rate *", value=3500, min_value=1, step=1, label_visibility="collapsed")
        
        col3, col4 = st.columns(2)
        with col3:
            st.write("Discount %")
            discount = st.number_input("Discount %", value=15, min_value=0, max_value=90, step=1, label_visibility="collapsed")
        with col4:
            st.write("Stock Qty *")
            stock = st.number_input("Stock Qty *", value=50, min_value=1, step=1, label_visibility="collapsed")

        st.write("Expiry Date *")
        expiry = st.date_input("Expiry Date *", value=datetime(2027,4,28), label_visibility="collapsed")

        # Live profit calc
        final_price_live = calc_final(bechne, discount)
        profit_live = calc_profit(final_price_live, kharid)
        st.success(f"Kharid Rs.{kharid} | Bechne Rs.{bechne} | Discount {discount}% = Final Rs.{final_price_live} | PROFIT Rs.{profit_live}")
        
        st.write("Highlights *")
        highlights = st.text_area("Highlights *", value="100% Pure - No Sugar, No Mix\nOriginal Beri Flowers Honey\nLaboratory Tested\nFor Health, Energy & Immunity", label_visibility="collapsed", height=120)
        
        st.write("Full Description *")
        full_desc = st.text_area("Full Description *", value="MEHAR MART - Aapki Sehat Ka Sathi\nCash on Delivery All Pakistan", label_visibility="collapsed", height=100)
        
        st.write("Specifications *")
        specs = st.text_area("Specifications *", value="Weight: 500gm\nType: Beri Honey\nBrand: MEHAR MART\nExpiry: 2 Years", label_visibility="collapsed", height=100)
        
        st.write("Photo *")
        uploaded_file = st.file_uploader("Photo *", type=["jpg","jpeg","png"], label_visibility="collapsed")

        submit = st.form_submit_button("🚀 SAVE + DARAZ POST BANAO + STORE PE LAGAO")

        if submit:
            if len(name.strip()) < 3:
                st.error("Product Name likho Bhai!")
            else:
                # Save uploaded photo
                img_path = ""
                if uploaded_file is not None:
                    os.makedirs("uploads", exist_ok=True)
                    img_path = f"uploads/{uploaded_file.name}_{datetime.now().strftime('%H%M%S')}.png"
                    with open(img_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                
                final_price = calc_final(bechne, discount)
                profit = calc_profit(final_price, kharid)
                
                # Create Daraz Post
                daraz_path = create_daraz_post_v60(name, final_price, str(bechne), str(discount), highlights, specs, img_path if img_path else None)
                
                c.execute("INSERT INTO products (name,kharid,bechne,final_price,discount,stock,expiry,highlights,full_desc,specs,image_path,daraz_post_path,profit,created) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                          (name, str(kharid), str(bechne), final_price, str(discount), str(stock), str(expiry), highlights, full_desc, specs, img_path, daraz_path, profit, datetime.now().strftime("%Y-%m-%d %H:%M")))
                conn.commit()
                
                st.session_state.last_post = daraz_path
                st.success(f"MASHALLAH Bhai! Product + Daraz Post + Store ✅ Final Rs.{final_price} Profit Rs.{profit}")
                st.balloons()

    if st.session_state.last_post and os.path.exists(st.session_state.last_post):
        st.divider()
        st.subheader("✅ Daraz Post Ready - Same as you wanted Bhai!")
        st.image(st.session_state.last_post, caption="Daraz Post - Mehar Mart V60", use_container_width=True)
        with open(st.session_state.last_post, "rb") as f:
            st.download_button("📥 Download Daraz Post", f, file_name="Mehar_Mart_Daraz_Post.png", mime="image/png")

with tab2:
    st.header("MEHAR MART STORE - V59")
    st.write("🔍 Search Product")
    search = st.text_input("Search", placeholder="Beri Honey search...", label_visibility="collapsed")
    
    st.write("Sort By")
    sort = st.selectbox("Sort By", ["Default", "Price Low to High", "Price High to Low"], label_visibility="collapsed")
    
    query = "SELECT * FROM products"
    params = []
    if search.strip():
        query += " WHERE name LIKE ?"
        params.append(f"%{search.strip()}%")
    
    if sort == "Price Low to High":
        query += " ORDER BY CAST(final_price AS INTEGER) ASC"
    elif sort == "Price High to Low":
        query += " ORDER BY CAST(final_price AS INTEGER) DESC"
    else:
        query += " ORDER BY id DESC"
    
    prods = c.execute(query, params).fetchall()
    st.success(f"{len(prods)} Products - {search if search else 'ALL'}")
    
    for p in prods:
        # id, name, kharid, bechne, final_price, discount, stock, expiry, highlights, full_desc, specs, image_path, daraz_post_path, profit, created
        with st.container(border=True):
            colA, colB = st.columns([1,2])
            with colA:
                if p[12] and os.path.exists(p[12]): # daraz post
                    st.image(p[12], use_container_width=True)
                elif p[11] and os.path.exists(p[11]):
                    st.image(p[11], width=200)
            with colB:
                st.write(f"**{p[1]}**")
                st.write(f"PURE HONEY | {p[1]} | Final Rs.{p[4]} (was Rs.{p[3]}) {p[5]}% OFF | 💵 Cash on Delivery - All Pakistan")
                st.caption(f"ADMIN: Buy Rs.{p[2]} Profit Rs.{p[13]} - Customer ko ye nahi dikhega")
                st.write(f"Stock: {p[6]} | Expiry: {p[7]}")
                if st.button(f"Delete {p[0]}", key=f"del_{p[0]}"):
                    c.execute("DELETE FROM products WHERE id=?", (p[0],))
                    conn.commit()
                    st.rerun()
