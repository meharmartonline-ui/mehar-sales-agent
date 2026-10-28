import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io, pandas as pd
from datetime import date, timedelta

st.set_page_config(page_title="Mehar Mart Food Verify", page_icon="🍯", layout="wide")
st.markdown("<h1 style='text-align:center'>🍯 Mehar Mart - Honey / Masala Verify System V7</h1>", unsafe_allow_html=True)
st.success("MASHALLAH - Food Verify System Live!")

if 'products' not in st.session_state:
    st.session_state.products = []

st.sidebar.header("📂 CATEGORIES")
default_cats = ["Honey 🍯", "Spices Masala 🌶️", "Dry Fruits", "Kitchen Gadgets", "Home Decor", "Beauty", "All Food Items"]
new_cat = st.sidebar.text_input("➕ Nayi Category")
if st.sidebar.button("Add"):
    if new_cat:
        default_cats.append(new_cat)
        st.sidebar.success(f"{new_cat} Added!")

selected_cats = st.sidebar.multiselect("Multiple Categories (Food)", default_cats, default=["Honey 🍯", "Spices Masala 🌶️"])
filter_cat = st.sidebar.selectbox("Filter Dekho", ["All"] + selected_cats)

tab1, tab2, tab3 = st.tabs(["🍯 FOOD VERIFY ADD", "📋 VERIFIED CATALOG", "🎨 POSTER"])

with tab1:
    st.header("Product Verify - Honey / Masala")
    c1, c2 = st.columns(2)
    with c1:
        p_title = st.text_input("Product Name", "Pure Sidr Honey 🍯 500g")
        p_cats = st.multiselect("Categories", selected_cats, default=selected_cats[:1])
        col_a, col_b = st.columns(2)
        with col_a:
            p_brand = st.text_input("Brand", "Mehar Mart Pure")
            p_price = st.text_input("Price", "Rs. 2500")
            p_weight = st.text_input("Net Weight", "500g / 1KG")
            p_mfg = st.date_input("MFG Date", date.today())
        with col_b:
            p_sku = st.text_input("Batch / SKU", "HONEY-500-001")
            p_sale = st.text_input("Sale Price", "Rs. 1999")
            p_stock = st.text_input("Stock", "50 Bottles")
            p_exp = st.date_input("Expire Date 📅", date.today() + timedelta(days=365))
        
        p_ingredients = st.text_area("Ingredients / Ajza", "100% Pure Sidr Honey, No Sugar, No Mix")
        p_benefits = st.text_area("Benefits / Fawaid", "• Immunity Booster\n• Natural Energy\n• Pure & Halal")
        p_storage = st.text_input("Storage", "Cool & Dry Place, No Fridge")
        
        col_v1, col_v2, col_v3 = st.columns(3)
        with col_v1:
            is_halal = st.checkbox("✅ Halal Certified", True)
        with col_v2:
            is_pure = st.checkbox("✅ 100% Pure Verified", True)
        with col_v3:
            is_lab = st.checkbox("✅ Lab Tested", False)
        
        verify_status = "✅ VERIFIED" if (is_halal and is_pure) else "⚠️ CHECK REQUIRED"
        
        p_img = st.file_uploader("Product Image (Bottle / Packet)", type=["jpg","png","jpeg"])

    with c2:
        if p_img:
            img = Image.open(p_img).convert("RGB")
            # Calculate expire status
            days_left = (p_exp - date.today()).days
            exp_color = "green" if days_left > 90 else "orange" if days_left > 30 else "red"
            exp_text = f"Exp: {p_exp} ({days_left} days left)" if days_left > 0 else "EXPIRED!"

            card_w = img.width
            card_h = img.height + 580
            card = Image.new("RGB", (card_w, card_h), "white")
            card.paste(img, (0,0))
            draw = ImageDraw.Draw(card)
            try:
                b38 = ImageFont.truetype("DejaVuSans-Bold.ttf", 36)
                r26 = ImageFont.truetype("DejaVuSans.ttf", 24)
                b32 = ImageFont.truetype("DejaVuSans-Bold.ttf", 32)
                b28 = ImageFont.truetype("DejaVuSans-Bold.ttf", 26)
            except:
                b38 = ImageFont.load_default()
                r26 = b38
                b32 = b38
                b28 = b38

            y = img.height + 8
            draw.rectangle([0, y, card_w, y+6], fill="#FF6A00")
            y+=14
            draw.text((10, y), f"{p_title[:55]}", font=b38, fill="black")
            y+=50
            draw.text((10, y), f"{verify_status} | {', '.join(p_cats)}", font=b28, fill="green" if "VERIFIED" in verify_status else "red")
            y+=40
            draw.text((10, y), f"{p_sale}", font=b32, fill="#D32F2F")
            draw.text((200, y), f"{p_price}", font=r26, fill="#888")
            draw.text((350, y), f"Stock: {p_stock}", font=r26, fill="black")
            y+=45
            draw.text((10, y), f"Weight: {p_weight} | Batch: {p_sku}", font=r26, fill="black")
            y+=38
            draw.text((10, y), f"MFG: {p_mfg} | {exp_text}", font=r26, fill=exp_color)
            y+=38
            draw.text((10, y), f"Ingredients: {p_ingredients[:70]}", font=r26, fill="#333")
            y+=38
            # Halal pure tags
            tags = []
            if is_halal: tags.append("HALAL")
            if is_pure: tags.append("PURE")
            if is_lab: tags.append("LAB TESTED")
            draw.text((10, y), f"Tags: {' | '.join(tags)} | Storage: {p_storage}", font=r26, fill="#2E7D32")

            st.image(card, use_column_width=True)
            
            if days_left <= 0:
                st.error(f"❌ YE PRODUCT EXPIRE HO GAYA HAI! Exp: {p_exp}")
            elif days_left <= 30:
                st.warning(f"⚠️ Sirf {days_left} din bache hain expire me! Jaldi sale karo!")
            else:
                st.success(f"✅ Fresh Hai - {days_left} din bache hain")

            if st.button("💾 Verify Karke Save Karo"):
                st.session_state.products.append({
                    "Title": p_title,
                    "Categories": ", ".join(p_cats),
                    "SKU/Batch": p_sku,
                    "Price": p_price,
                    "Sale": p_sale,
                    "Weight": p_weight,
                    "MFG": str(p_mfg),
                    "Expire": str(p_exp),
                    "Days Left": days_left,
                    "Ingredients": p_ingredients,
                    "Status": verify_status,
                    "Halal": is_halal,
                    "Pure": is_pure,
                    "Lab Tested": is_lab,
                    "Stock": p_stock
                })
                st.success(f"✅ {p_title} Verified & Saved!")

            buf = io.BytesIO()
            card.save(buf, format="PNG")
            st.download_button("⬇️ Verified Poster Download (Expiry ke sath)", buf.getvalue(), f"VERIFIED_{p_sku}.png", "image/png")
        else:
            st.info("Honey / Masala ki image upload karo")

with tab2:
    st.header(f"Verified Catalog - {filter_cat}")
    if st.session_state.products:
        df = pd.DataFrame(st.session_state.products)
        if filter_cat != "All":
            df_f = df[df["Categories"].str.contains(filter_cat.replace(" 🍯","").replace(" 🌶️",""))]
        else:
            df_f = df
        
        # Highlight expire
        def color_exp(val):
            try:
                if val <= 0: return 'background-color: #ffcccc'
                elif val <= 30: return 'background-color: #fff3cd'
                else: return 'background-color: #d4edda'
            except: return ''
        
        st.dataframe(df_f.style.applymap(color_exp, subset=['Days Left']), use_container_width=True)
        
        excel_buf = io.BytesIO()
        df_f.to_excel(excel_buf, index=False)
        st.download_button(f"⬇️ Download {filter_cat} Verified Excel", excel_buf.getvalue(), f"{filter_cat}_verified.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.warning("Koi verified product nahi - Tab 1 me add karo")

with tab3:
    st.header("Food Ad Poster - Expiry ke sath")
    c1, c2 = st.columns(2)
    with c1:
        ad_img = st.file_uploader("Ad Image", type=["jpg","png","jpeg"], key="ad_food")
        ad_title = st.text_input("Ad Title", "Pure Honey Sale 🍯")
        ad_exp = st.date_input("Ad Exp Show", date.today() + timedelta(days=365), key="ad_exp")
        ad_verify = st.checkbox("Show Verified Badge", True)
    with c2:
        if ad_img:
            image = Image.open(ad_img).convert("RGB")
            w,h = image.size
            draw = ImageDraw.Draw(image)
            draw.rectangle([0, h-220, w, h], fill=(0,0,0))
            try:
                f1 = ImageFont.truetype("DejaVuSans-Bold.ttf", 48)
                f2 = ImageFont.truetype("DejaVuSans.ttf", 30)
            except:
                f1 = ImageFont.load_default()
                f2 = f1
            draw.text((15, h-210), ad_title, font=f1, fill="yellow")
            draw.text((15, h-150), f"Exp: {ad_exp} | {'✅ VERIFIED PURE & HALAL' if ad_verify else ''}", font=f2, fill="white")
            draw.text((15, h-110), f"{', '.join(selected_cats[:2])}", font=f2, fill="#90EE90")
            st.image(image, use_column_width=True)
            buf2 = io.BytesIO()
            image.save(buf2, format="PNG")
            st.download_button("⬇️ Food Ad Download", buf2.getvalue(), "food_ad.png", "image/png")

st.markdown("---")
st.markdown("<center>🍯 Mehar Mart Food Verify System - Expire Alert + Halal + Pure</center>", unsafe_allow_html=True)
