import streamlit as st
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os, math
import numpy as np

st.set_page_config(page_title="MEHAR AD MAKER V70", layout="centered")
st.title("MEHAR MART - AI Ad Maker V70 🎬")
st.caption("Image Generator + 15s / 20s / 30s Video Ad for FB / TikTok / Insta Story")

def get_font(size):
    try:
        return ImageFont.truetype("arialbd.ttf", size)
    except:
        return ImageFont.load_default()

def generate_image(prompt):
    url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=1080&height=1080&model=flux&nologo=true&enhance=true"
    r = requests.get(url, timeout=90)
    if r.status_code == 200:
        return Image.open(BytesIO(r.content)).convert("RGB")
    return None

def create_video_ad(product_img, product_name, price, offer, duration, format_type):
    # Format sizes
    if format_type in ["TikTok 9:16", "Instagram Story 9:16"]:
        W, H = 1080, 1920
    else:
        W, H = 1080, 1080

    fps = 24
    total_frames = duration * fps
    frames = []
    
    # Resize product image
    p_size = 700 if W==1080 and H==1080 else 800
    product_img = product_img.resize((p_size, p_size))

    for i in range(total_frames):
        t = i / fps  # seconds
        frame = Image.new("RGB", (W, H), "white")
        draw = ImageDraw.Draw(frame)

        # Background gradient effect
        # 0-3s: Intro, 3-10s: Product, 10-end: Offer + CTA
        progress = i / total_frames
        
        # Zoom animation
        zoom = 1.0 + 0.15 * math.sin(progress * math.pi)
        pw, ph = int(p_size * zoom), int(p_size * zoom)
        p_img_z = product_img.resize((pw, ph))
        
        # Center product
        if W == 1080 and H == 1080: # 1:1
            x = (W - pw)//2
            y = 150 if t < 3 else 100
        else: # 9:16
            x = (W - pw)//2
            y = 300 if t < 3 else 250

        frame.paste(p_img_z, (x, y))

        # Text animations
        if t < 3:
            # Intro - Brand
            draw.rectangle([0, 0, W, 120], fill="#FF6A00")
            draw.text((W//2, 60), "MEHAR MART", fill="white", font=get_font(60), anchor="mm")
            draw.text((W//2, H-200), product_name[:30], fill="#111", font=get_font(40), anchor="mm")
            draw.text((W//2, H-150), "100% Pure - No Mix", fill="#555", font=get_font(30), anchor="mm")
        
        elif t < duration-5:
            # Middle - Product + Price
            draw.rectangle([0, 0, W, 120], fill="#FF6A00")
            draw.text((W//2, 60), "MEHAR MART | Official Store", fill="white", font=get_font(32), anchor="mm")
            
            if W == 1080 and H == 1920:
                draw.text((W//2, 1250), product_name[:35], fill="#111", font=get_font(42), anchor="mm")
                draw.text((W//2, 1350), f"Rs. {price}", fill="#FF6A00", font=get_font(80), anchor="mm")
                draw.text((W//2, 1450), offer, fill="#0D47A1", font=get_font(36), anchor="mm")
            else:
                draw.text((W//2, 850), product_name[:35], fill="#111", font=get_font(36), anchor="mm")
                draw.text((W//2, 920), f"Rs. {price} | {offer}", fill="#FF6A00", font=get_font(50), anchor="mm")

        else:
            # End - CTA
            draw.rectangle([0, 0, W, H], fill="#0D47A1")
            draw.text((W//2, H//2 - 200), "ORDER NOW", fill="white", font=get_font(90), anchor="mm")
            draw.text((W//2, H//2 - 80), f"{product_name[:25]}", fill="#FFC107", font=get_font(40), anchor="mm")
            draw.text((W//2, H//2 + 20), f"Rs. {price} - {offer}", fill="white", font=get_font(50), anchor="mm")
            draw.text((W//2, H//2 + 150), "Call / WhatsApp", fill="white", font=get_font(36), anchor="mm")
            draw.text((W//2, H//2 + 220), "03452352112", fill="white", font=get_font(60), anchor="mm")
            draw.text((W//2, H//2 + 320), "Free Delivery All Pakistan", fill="#FFC107", font=get_font(32), anchor="mm")

        frames.append(np.array(frame))

    # Save video
    os.makedirs("ads", exist_ok=True)
    import imageio
    out_path = f"ads/Mehar_Ad_{duration}s_{format_type.replace(' ','_')}.mp4"
    imageio.mimsave(out_path, frames, fps=fps, macro_block_size=1)
    return out_path

# --- UI ---
st.divider()
product_name = st.text_input("Product Name *", value="Pure Beri Flowers Honey 500gm")
price = st.text_input("Price *", value="2975")
offer = st.text_input("Offer *", value="15% OFF - Free Delivery")
prompt_input = st.text_area("AI Image Prompt (Jo likho ge wahi image banegi) *", value="Pure Beri Flowers Honey jar 500gm, clear glass jar golden honey, white background, studio lighting, MEHAR MART label, honeycomb, beri flowers")

col1, col2 = st.columns(2)
with col1:
    duration = st.selectbox("Ad Duration *", [15, 20, 30])
with col2:
    format_type = st.selectbox("Platform Format *", ["FB Feed 1:1", "TikTok 9:16", "Instagram Story 9:16"])

if st.button("🚀 IMAGE + VIDEO AD BANAO"):
    if not prompt_input.strip():
        st.error("Prompt likho Bhai!")
    else:
        with st.spinner(f"1/2 Image bana raha hai..."):
            img = generate_image(prompt_input)
            if not img:
                st.error("Image fail, dobara try karo")
                st.stop()
            st.image(img, caption="AI Image - Isi se video banegi", use_container_width=True)
            # Save temp
            os.makedirs("temp", exist_ok=True)
            temp_path = "temp/product.png"
            img.save(temp_path)

        with st.spinner(f"2/2 {duration}s Video Ad bana raha hai... {format_type}"):
            video_path = create_video_ad(img, product_name, price, offer, duration, format_type)
            st.success(f"Ho gaya Bhai! {duration}s Ad ready hai!")
            st.video(video_path)
            with open(video_path, "rb") as f:
                st.download_button(f"📥 Download {duration}s Ad - {format_type}", f, file_name=f"Mehar_Ad_{duration}s.mp4", mime="video/mp4")

st.info("💡 Tip: FB ke liye 1:1, TikTok / Insta Story ke liye 9:16 select karo. 15s best hai, 30s detail ke liye.")
