import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io, pandas as pd, random
from datetime import date, timedelta

st.set_page_config(page_title="Mehar Mart FULL", page_icon="🛒", layout="wide")
st.markdown("<h1 style='text-align:center'>🛒 Mehar Mart - FULL MULTI CATEGORY V8</h1>", unsafe_allow_html=True)
st.success("MASHALLAH - FULL SYSTEM LIVE!")

if 'products' not in st.session_state:
    st.session_state.products = []

# --- SIDEBAR - FULL CATEGORIES ---
st.sidebar.header("📂 FULL CATEGORIES")
ALL_CATEGORIES = [
    "Honey 🍯", 
    "Spices Masala 🌶️", 
    "Dry Fruits", 
    "Kitchen Gadgets 🍳", 
    "Home Decor 🏠", 
    "Beauty Products 💄", 
    "Clothing 👕", 
    "Electronics", 
    "Toys", 
    "Jewelry"
]

new_cat = st.sidebar.text_input("➕ Nayi Category Add Karo")
if st.sidebar.button("Add Category"):
    if new_cat and new_cat not in ALL_CATEGORIES:
        ALL_CATEGORIES.append(new_cat)
        st.sidebar.success(f"{new_cat} Added!")

selected_cats = st.sidebar.multiselect("Categories Select Karo (Multiple)", ALL_CATEGORIES, default=ALL_CATEGORIES[:4])
st.sidebar.markdown("---")
st.sidebar.success(f"Selected: {len(selected_cats)} Categories")

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["📦 ADD PRODUCT", "📋 ALL CATALOGS", "🎨 AD STUDIO"])

with tab1:
    st.header("Product Add - Full System")
    c1, c2 = st.columns(2)
    with c1:
        p_title = st.text_input("Product Title", "Pure Product")
        p_cats = st.multiselect("Product Kahan Jayega? (Multiple)", selected_cats, default=selected_cats[:1])
        col_a, col_b = st.columns(2)
        with col_a:
            p_brand = st.text_input("Brand", "Mehar Mart")
            p_price = st.text_input("Original Price", "Rs. 3000")
            p_weight = st.text_input("Weight / Size", "500g / M,L,XL")
        with col_b:
            p_sku = st.text_input("SKU / Batch", "MM-001")
            p_sale = st.text_input("Sale Price", "Rs. 1999")
            p_color = st.text_input("Color", "All Colors")
        
        # FOOD SPECIFIC FIELDS
        st.markdown("### 🍯🌶️ Food Fields (Honey/Masala ke liye)")
        p_mfg = st.date_input("MFG Date", date.today())
        p_exp = st.date_input("Expire Date 📅", date.today() + timedelta(days=365))
        p_ing = st.text_area("Ingredients / Ajza", "100% Pure, No Mix")
        is_halal = st.checkbox("✅ Halal", True)
        is_pure = st.checkbox("✅ Pure Verified", True)
        is_lab = st.checkbox("✅ Lab Tested", False)
        
        p_img = st.file_uploader("Main Image", type=["jpg","png","jpeg"])

    with c2:
        if p_img:
            img = Image.open(p_img).convert("RGB")
            days_left = (p_exp - date.today()).days
            
            card_h = img.height + 500
            card = Image.new("RGB", (img.width, card_h), "white")
            card.paste(img, (0,0))
            draw = ImageDraw.Draw(card)
            try:
                b36 = ImageFont.truetype("DejaVuSans-Bold.ttf", 34)
                r24 = ImageFont.truetype("DejaVuSans.ttf", 22)
                b30 = ImageFont.truetype("DejaVuSans-Bold.ttf", 30)
            except:
                b36 = ImageFont.load_default()
                r24 = b36
                b30 = b36

            y = img.height + 10
            draw.rectangle([0, y, img.width, y+5], fill="#FF6A00")
            y+=10
            draw.text((10, y), f"{p_title[:50]}", font=b36, fill="black")
            y+=45
            draw.text((10, y), f"Cats: {', '.join(p_cats)}", font=r24, fill="#FF6A00")
            y+=32
            draw.text((10, y), f"{p_sale}", font=b30, fill="#D32F2F")
            draw.text((200, y), f"{p_price}", font=r24, fill="#888")
            y+=38
            draw.text((10, y), f"Size/Weight: {p_weight} | Color: {p_color}", font=r24, fill="black")
            y+=30
            draw.text((10, y), f"SKU: {p_sku} | MFG: {p_mfg} | Exp: {p_exp}", font=r24, fill="green" if days_left>30 else "red")
            y+=30
            draw.text((10, y), f"{'HALAL' if is_halal else ''} | {'PURE' if is_pure else ''} | {'LAB' if is_lab else ''} | Ing: {p_ing[:50]}", font=r24, fill="#333")

            st.image(card, use_column_width=True)
            
            if st.button("💾 Save Karo"):
                st.session_state.products.append({
                    "Title": p_title,
                    "Categories": ", ".join(p_cats),
                    "SKU": p_sku,
                    "Price": p_price,
                    "Sale": p_sale,
                    "Weight/Size": p_weight,
                    "Color": p_color,
                    "MFG": str(p_mfg),
                    "Expire": str(p_exp),
                    "Days Left": days_left,
                    "Brand": p_brand
                })
                st.success(f"Saved in {', '.join(p_cats)}!")

            buf = io.BytesIO()
            card.save(buf, format="PNG")
            st.download_button("⬇️ Poster Download", buf.getvalue(), f"{p_sku}.png", "image/png")
        else:
            st.info("Image upload karo")

with tab2:
    st.header("All Catalogs")
    if st.session_state.products:
        df = pd.DataFrame(st.session_state.products)
        st.dataframe(df, use_container_width=True)
        
        # Category wise download
        for cat in selected_cats:
            cat_df = df[df["Categories"].str.contains(cat.split()[0])]
            if not cat_df.empty:
                b = io.BytesIO()
                cat_df.to_excel(b, index=False)
                st.download_button(f"⬇️ Download {cat} Excel", b.getvalue(), f"{cat}_catalog.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key=cat)
    else:
        st.warning("Koi product nahi")

with tab3:
    st.header("Ad Studio")
    ad_img = st.file_uploader("Ad Image", type=["jpg","png","jpeg"], key="ad")
    if ad_img:
        image = Image.open(ad_img).convert("RGB")
        st.image(image, use_column_width=True)
        buf2 = io.BytesIO()
        image.save(buf2, format="PNG")
        st.download_button("⬇️ Ad Download", buf2.getvalue(), "ad.png", "image/png")
