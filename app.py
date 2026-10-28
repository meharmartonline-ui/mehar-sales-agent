import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(page_title="Mehar Mart V5", page_icon="🛒", layout="wide")

st.markdown("<h1 style='text-align:center'>🛒 Mehar Mart V5 FINAL JOINT</h1>", unsafe_allow_html=True)
st.success("MASHALLAH BOSS APP LIVE HO GAYI! 💯")

tab1, tab2 = st.tabs(["📦 CATALOG MAKER", "🎨 AD STUDIO"])

with tab1:
    st.header("Catalog Maker")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Product Name", "Mehar Kurta")
        price = st.text_input("Price", "Rs. 2500")
        img = st.file_uploader("Product Image Upload karo", type=["jpg","png","jpeg"])
    with col2:
        if img:
            image = Image.open(img)
            st.image(image, caption=f"{name} - {price}", use_column_width=True)
            if st.button("📄 PDF Catalog Banao"):
                st.success("Catalog Ready! Screenshot le lo BOSS!")
        else:
            st.info("Image upload karo to preview ayega")

with tab2:
    st.header("Ad Studio - Price Wala Poster")
    col1, col2 = st.columns(2)
    with col1:
        ad_img = st.file_uploader("Ad ke liye Image", type=["jpg","png","jpeg"], key="ad")
        ad_text = st.text_input("Offer Text", "EID SALE 50% OFF")
        ad_price = st.text_input("Price", "Rs. 1999 Only")
    with col2:
        if ad_img:
            image = Image.open(ad_img)
            # Simple poster draw
            draw = ImageDraw.Draw(image)
            # Add text box at bottom
            w, h = image.size
            draw.rectangle([0, h-120, w, h], fill=(0,0,0,180))
            draw.text((20, h-100), ad_text, fill="white")
            draw.text((20, h-60), ad_price, fill="yellow")
            st.image(image, caption="Your Ad Poster", use_column_width=True)
            
            buf = io.BytesIO()
            image.save(buf, format="PNG")
            st.download_button("⬇️ Poster Download Karo", buf.getvalue(), "mehar_ad.png", "image/png")

st.markdown("---")
st.markdown("<center>Made with ❤️ for Mehar Mart by BOSS</center>", unsafe_allow_html=True)
