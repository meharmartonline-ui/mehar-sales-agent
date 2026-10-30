import streamlit as st
import sqlite3
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import os

st.set_page_config(page_title="MEHAR MART V61 SAME POST AUTO", layout="wide")

ADMIN_USER = str(st.secrets.get("ADMIN_USER", "mehar_admin_9x")).strip()
ADMIN_PASS = str(st.secrets.get("ADMIN_PASS", "Strong#2026Pass")).strip()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "last_post" not in st.session_state:
    st.session_state.last_post = ""

if not st.session_state.logged_in:
    st.title("MEHAR MART V61 - Locked 🔒")
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

def create_same_post_as_image(product_name, final_price, was_price, discount, highlights, specs, uploaded_img_path=None):
    W, H = 1080, 1080
    img = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(img)
    try:
        f_small = ImageFont.truetype("arial.ttf", 20)
        f_med = ImageFont.truetype("arial.ttf", 28)
        f_large = ImageFont.truetype("arialbd.ttf", 42)
        f_price = ImageFont.truetype("arialbd.ttf", 68)
        f_tiny = ImageFont.truetype("arial.ttf", 16)
        f_bold_small = ImageFont.truetype("arialbd.ttf", 20)
    except:
        f_small = ImageFont.load_default()
        f_med = ImageFont.load_default()
        f_large = ImageFont.load_default()
        f_price = ImageFont.load_default()
        f_tiny = ImageFont.load_default()
        f_bold_small = ImageFont.load_default()

    # Top Orange - Exactly like your image
    draw.rectangle([0, 0, 1080, 100], fill="#FF6A00")
    draw.text((20, 50), "Mehar Mart", fill="white", font=f_large, anchor="lm")
    draw.text((700, 50), "Official Store | Verified Seller | ★ 4.8 (1.2k Ratings)", fill="white", font=f_small, anchor="lm")

    # Left Side Image Box - White
    draw.rectangle([0, 100, 520, 960], fill="white")
    
    # Paste uploaded image or placeholder jar
    if uploaded_img_path and os.path.exists(uploaded_img_path):
        try:
            prod_img = Image.open(uploaded_img_path).convert("RGB")
            prod_img = prod_img.resize((500, 700))
            img.paste(prod_img, (10, 150))
        except:
            pass
    else:
        # Draw simple jar placeholder with PURE HONEY label - like image
        draw.rectangle([50, 200, 450, 700], fill="#E8A735", outline="#8B7355")
        draw.ellipse([70, 150, 430, 230], fill="#C9A86A")
        draw.rectangle([70, 350, 430, 600], fill="#FFC107")
        draw.text((250, 450), "PURE\nHONEY", fill="#4A2C0A", font=f_large, anchor="mm")
        draw.text((250, 550), "Pure Beri Flowers Honey\n500gm • 100% Natural", fill="white", font=f_small, anchor="mm")

    # Right Side - Same as image
    y = 130
    draw.text((540, y), f"{product_name} | 100% Pure", fill="#111", font=f_med)
    y+=30
    draw.text((540, y), "No Sugar No Mix | Laboratory Tested", fill="#111", font=f_small)
    y+=50
    draw.text((540, y), "★★★★★", fill="#FFC107", font=f_med)
    y+=30
    draw.text((540, y), "4.8 | 356 Ratings • 120 Sold", fill="#555", font=f_tiny)
    y+=50
    # Price line
    draw.text((540, y), f"Rs. {final_price}", fill="#FF6A00", font=f_price)
    draw.text((780, y+15), f"Rs. {was_price}", fill="#888", font=f_med)
    draw.rounded_rectangle([900, y+10, 1020, y+45], radius=15, fill="#FF6A00")
    draw.text((960, y+27), f"{discount}% OFF", fill="white", font=f_small, anchor="mm")
    y+=80
    # Badges - Free Delivery, 100% Pure, COD
    draw.rounded_rectangle([540, y, 710, y+40], radius=20, fill="#FFF0E0", outline="#FF6A00")
    draw.text((625, y+20), "Free Delivery", fill="#E65100", font=f_tiny, anchor="mm")
    draw.rounded_rectangle([720, y, 870, y+40], radius=20, fill="#FFF0E0", outline="#FF6A00")
    draw.text((795, y+20), "100% Pure", fill="#E65100", font=f_tiny, anchor="mm")
    draw.rounded_rectangle([880, y, 1050, y+40], radius=20, fill="#FFF0E0", outline="#FF6A00")
    draw.text((965, y+20), "Cash on Delivery", fill="#E65100", font=f_tiny, anchor="mm")
    y+=70
    draw.text((540, y), "Highlights:", fill="#111", font=f_bold_small)
    y+=25
    for line in highlights.split("\n")[:5]:
        if line.strip():
            draw.text((540, y), f"◉ {line.strip()}", fill="#333", font=f_tiny)
            y+=22
    y+=15
    draw.text((540, y), "Specifications:", fill="#111", font=f_bold_small)
    y+=25
    draw.rectangle([540, y, 1050, y+130], fill="#F8F8F8", outline="#DDD", width=1)
    sy = y+10
    for line in specs.split("\n")[:4]:
        draw.text((550, sy), line.strip(), fill="#333", font=f_tiny)
        sy+=28

    # Bottom Blue Footer - Exactly like image
    draw.rectangle([0, 960, 1080, 1080], fill="#0D47A1")
    draw.text((10, 1020), "Daraz Mall | Authentic", fill="white", font=f_tiny)
    draw.text((540, 1020), "Call / WhatsApp: 03452352112 | Fast Delivery Across Pakistan | MEHAR MART - Aapki Sehat Ka Sathi", fill="white", font=f_tiny, anchor="mm")

    os.makedirs("daraz_posts", exist_ok=True)
    out = f"daraz_posts/SAME_POST_{product_name[:15].replace(' ', '_')}_{datetime.now().strftime('%H%M%S')}.png"
    img.save(out)
    return out

st.title("MEHAR MART V61 — SAME POST AUTO AGENT")
st.success("V61 Loaded ✅ — Ab aapke jaisa poster agent khud banayega!")

tab1, tab2 = st.tabs(["➕ Add Product - SAME POST AUTO", "🛍️ STORE"])

with tab1:
    st.header("Same Post Banao — Jaise Upar Wali Image")
    with st.form("v61_form", clear_on_submit=False):
        name = st.text_input("Product Name *", value="Pure Beri Flowers Honey 500gm - 100% Pure")
        col1, col2 = st.columns(2)
        with col1:
            kharid = st.number_input("Kharid Rate *", value=2000, min_value=1)
        with col2:
            bechne = st.number_input("Bechne Rate *", value=3500, min_value=1)
        col3, col4 = st.columns(2)
        with col3:
            discount = st.number_input("Discount %", value=15, min_value=0, max_value=90)
        with col4:
            stock = st.number_input("Stock Qty *", value=50, min_value=1)
        expiry = st.date_input("Expiry Date *", value=datetime(2027,4,28))
        
        final_price_live = calc_final(bechne, discount)
        profit_live = calc_profit(final_price_live, kharid)
        st.success(f"Kharid Rs.{kharid} | Bechne Rs.{bechne} | Discount {discount}% = Final Rs.{final_price_live} | PROFIT Rs.{profit_live}")

        highlights = st.text_area("Highlights *", value="100% Pure - No Sugar No Mix\nOriginal Beri Flowers Honey\nLaboratory Tested\nFor Health • Energy • Immunity", height=100)
        full_desc = st.text_area("Full Description *", value="MEHAR MART - Aapki Sehat Ka Sathi\nCash on Delivery All Pakistan", height=80)
        specs = st.text_area("Specifications *", value="Weight: 500gm | Type: Beri Honey\nBrand: MEHAR MART | Expiry: 2 Years", height=80)
        uploaded_file = st.file_uploader("Photo * (Upload karo to wahi lagegi)", type=["jpg","jpeg","png"])

        if st.form_submit_button("🚀 SAME POST BANAO + STORE PE LAGAO"):
            img_path = ""
            if uploaded_file is not None:
                os.makedirs("uploads", exist_ok=True)
                img_path = f"uploads/{uploaded_file.name}_{datetime.now().strftime('%H%M%S')}.png"
                with open(img_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            
            final_price = calc_final(bechne, discount)
            profit = calc_profit(final_price, kharid)
            daraz_path = create_same_post_as_image(name, final_price, str(bechne), str(discount), highlights, specs, img_path if img_path else None)
            
            c.execute("INSERT INTO products (name,kharid,bechne,final_price,discount,stock,expiry,highlights,full_desc,specs,image_path,daraz_post_path,profit,created) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                      (name, str(kharid), str(bechne), final_price, str(discount), str(stock), str(expiry), highlights, full_desc, specs, img_path, daraz_path, profit, datetime.now().strftime("%Y-%m-%d %H:%M")))
            conn.commit()
            st.session_state.last_post = daraz_path
            st.success(f"MASHALLAH Bhai! SAME POST BAN GAYI ✅ Final Rs.{final_price} Profit Rs.{profit}")
            st.balloons()

    if st.session_state.last_post and os.path.exists(st.session_state.last_post):
        st.divider()
        st.image(st.session_state.last_post, caption="Same Post - Ready", use_container_width=True)
        with open(st.session_state.last_post, "rb") as f:
            st.download_button("📥 Download Same Post", f, file_name="Mehar_Mart_Same_Post.png", mime="image/png")

with tab2:
    st.header("MEHAR MART STORE - V61")
    search = st.text_input("Search Product", placeholder="Beri Honey search...")
    sort = st.selectbox("Sort By", ["Default", "Price Low to High", "Price High to Low"])
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
    st.success(f"{len(prods)} Products")
    for p in prods:
        with st.container(border=True):
            c1, c2 = st.columns([1,2])
            with c1:
                if p[12] and os.path.exists(p[12]):
                    st.image(p[12], use_container_width=True)
            with c2:
                st.write(f"**{p[1]}** — Rs.{p[4]} (was Rs.{p[3]}) {p[5]}% OFF")
                st.caption(f"Buy Rs.{p[2]} Profit Rs.{p[13]}")
                if st.button(f"Delete {p[0]}", key=f"del_{p[0]}"):
                    c.execute("DELETE FROM products WHERE id=?", (p[0],))
                    conn.commit()
                    st.rerun()
