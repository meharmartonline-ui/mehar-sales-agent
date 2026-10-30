import streamlit as st
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os, random, asyncio, subprocess

st.set_page_config(page_title="MEHAR UGC V82 REAL PHOTO", layout="centered")
st.title("MEHAR UGC V82 - REAL LARKA PHOTO 🔥")
st.success("V82: Ab Real Larka + Honey Jar + Real Human Voice + Video!")

avatar = st.radio(
    "1️⃣ Kaun bolega?",
    ["👩 Larki - Young Girl", "👦 Larka - Young Boy", "👶 Baby", "👩‍👧 Ammi", "👳‍♂️ Bearded Bhai"],
    index=1
)

REAL_VOICE = {
    "👩 Larki - Young Girl": "ur-PK-UzmaNeural",
    "👦 Larka - Young Boy": "ur-PK-AsadNeural",
    "👶 Baby": "ur-PK-UzmaNeural",
    "👩‍👧 Ammi": "ur-PK-UzmaNeural",
    "👳‍♂️ Bearded Bhai": "ur-PK-AsadNeural"
}

st.divider()
# NAYA FEATURE: Apni photo upload karo!
st.subheader("📸 Real Photo Option (Best!)")
uploaded = st.file_uploader("Apni Larka/Larki ki Real Photo Upload Karo (Honey Jar ke sath) - Agar hai to", type=["jpg","png","jpeg"])

product_name = st.text_input("Product Name", "Pure Honey 100% Natural")
price = st.text_input("Price", "2975")
offer = st.text_input("Offer", "15% OFF - Free Delivery")
duration = st.selectbox("Duration", [15, 20, 30])

if "Larka" in avatar or "Bearded" in avatar:
    default_voice = f"Assalam-o-Alaikum Bhaiyo! Main Mehar Mart ka {product_name} use kar raha hun, 100 percent khalis hai, sirf {price} rupay me {offer}, order karo 03452352112"
else:
    default_voice = f"Assalam-o-Alaikum guys! Maine Mehar Mart ka {product_name} liya hai, 100 percent pure hai, sirf {price} me {offer}!"

voice_text = st.text_area("Voice Text - REAL HUMAN", default_voice, height=90)

def get_ffmpeg():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except:
        return "ffmpeg"

def create_viral_ugc_card(avatar_text, product_name, price, offer):
    # VIRAL UGC CARD - Bada text, viral design
    W, H = 1080, 1920
    img = Image.new("RGB", (W, H), "#FFF8E1")
    draw = ImageDraw.Draw(img)
    
    # Try big font
    try:
        # Default bada font
        font_title = ImageFont.load_default()
        # Bigger
        font_big = ImageFont.truetype("DejaVuSans.ttf", 80)
        font_med = ImageFont.truetype("DejaVuSans.ttf", 50)
        font_small = ImageFont.truetype("DejaVuSans.ttf", 40)
    except:
        font_big = ImageFont.load_default()
        font_med = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Top gradient
    draw.rectangle([0, 0, W, 300], fill="#FF6F00")
    draw.text((W//2, 80), "MEHAR MART", fill="white", anchor="mm", font=font_big)
    draw.text((W//2, 180), "100% Pure & Original", fill="white", anchor="mm", font=font_med)
    
    # Center white card
    draw.rectangle([40, 350, W-40, 1550], fill="white", outline="#FF6F00", width=8)
    
    # Inside
    y = 400
    draw.text((W//2, y), "🍯", fill="black", anchor="mm", font=font_big)
    y += 120
    draw.text((W//2, y), avatar_text, fill="#333", anchor="mm", font=font_med)
    y += 100
    draw.text((W//2, y), "PRODUCT:", fill="#FF6F00", anchor="mm", font=font_med)
    y += 80
    draw.text((W//2, y), product_name[:32], fill="black", anchor="mm", font=font_med)
    y += 100
    draw.text((W//2, y), f"Rs. {price}", fill="#D32F2F", anchor="mm", font=font_big)
    y += 120
    draw.text((W//2, y), offer, fill="#2E7D32", anchor="mm", font=font_med)
    y += 150
    draw.text((W//2, y), "✓ 100% Pure Natural", fill="black", anchor="mm", font=font_small)
    y += 70
    draw.text((W//2, y), "✓ No Sugar Added", fill="black", anchor="mm", font=font_small)
    y += 70
    draw.text((W//2, y), "✓ Farm Fresh", fill="black", anchor="mm", font=font_small)
    
    # Bottom
    draw.rectangle([0, H-280, W, H], fill="#0D47A1")
    draw.text((W//2, H-180), "Order Now:", fill="white", anchor="mm", font=font_med)
    draw.text((W//2, H-100), "03452352112", fill="white", anchor="mm", font=font_big)
    draw.text((W//2, H-30), "Free Delivery - Peshawar", fill="white", anchor="mm", font=font_small)
    
    return img

def gen_image_smart(uploaded_file, avatar_text, product_name, price, offer):
    # 1. Agar user ne photo upload ki - BEST!
    if uploaded_file is not None:
        st.success("✅ Aapki Real Photo Use Ho Rahi Hai - Best UGC!")
        return Image.open(uploaded_file).convert("RGB")
    
    # 2. Try online AI - 3 engines
    prompts = [
        f"handsome Pakistani young boy white shalwar kameez holding honey jar smiling, UGC style, 4k",
        f"beautiful Pakistani girl holding pure honey jar, smiling, realistic, 4k"
    ]
    prompt = prompts[0] if "Larka" in avatar_text or "Bearded" in avatar_text else prompts[1]
    
    urls = [
        f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=720&height=1280&model=turbo&nologo=true&seed={random.randint(1,999999)}",
        f"https://pollinations.ai/p/{requests.utils.quote(prompt)}?width=720&height=1280"
    ]
    for url in urls:
        try:
            r = requests.get(url, timeout=20)
            if r.status_code == 200 and len(r.content) > 8000:
                st.success("✅ Real AI Photo Ban Gayi!")
                return Image.open(BytesIO(r.content)).convert("RGB")
        except:
            continue
    
    # 3. Fallback - Viral UGC Card (Bada text wala)
    st.warning("Online AI busy Bhai, Viral UGC Card bana raha hun - ye bhi bohot bikta hai Daraz pe!")
    return create_viral_ugc_card(avatar_text, product_name, price, offer)

async def gen_real_voice(text, voice_name):
    import edge_tts
    os.makedirs("voice", exist_ok=True)
    path = "voice/real_human.mp3"
    communicate = edge_tts.Communicate(text, voice_name, rate="-5%")
    await communicate.save(path)
    return path

def gen_voice_sync(text, voice_name):
    try:
        return asyncio.run(gen_real_voice(text, voice_name))
    except:
        try:
            from gtts import gTTS
            os.makedirs("voice", exist_ok=True)
            path = "voice/backup.mp3"
            gTTS(text=text, lang='ur', slow=False).save(path)
            return path
        except:
            return None

def make_video_final(img, dur, voice_path):
    os.makedirs("ads", exist_ok=True)
    img_path = "ads/input.jpg"
    final_video = "ads/final_V82.mp4"
    ffmpeg_exe = get_ffmpeg()
    img = img.resize((720, 1280))
    img.save(img_path, "JPEG", quality=95)
    
    if voice_path and os.path.exists(voice_path):
        cmd = [ffmpeg_exe,"-y","-loop","1","-i",img_path,"-i",voice_path,"-c:v","libx264","-c:a","aac","-b:a","192k","-t",str(dur),"-pix_fmt","yuv420p","-shortest",final_video]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if os.path.exists(final_video) and os.path.getsize(final_video) > 5000:
            return final_video
    # silent
    cmd = [ffmpeg_exe,"-y","-loop","1","-i",img_path,"-c:v","libx264","-t",str(dur),"-pix_fmt","yuv420p",final_video]
    subprocess.run(cmd, capture_output=True, timeout=30)
    return final_video

if st.button("🚀 REAL UGC VIDEO BANAO - V82", type="primary", use_container_width=True):
    with st.spinner("Image bana raha..."):
        img = gen_image_smart(uploaded, avatar, product_name, price, offer)
        st.image(img, caption=f"✅ UGC Ready - {avatar}", use_container_width=True)
    
    with st.spinner(f"🎙️ REAL HUMAN Voice - {REAL_VOICE[avatar]}..."):
        vp = gen_voice_sync(voice_text, REAL_VOICE[avatar])
        if vp:
            st.success("✅ REAL HUMAN Voice Ready! Suno Bhai:")
            st.audio(vp)
    
    with st.spinner(f"{duration}s Video..."):
        vpath = make_video_final(img, duration, vp)
        if vpath and os.path.exists(vpath):
            st.success("🔥 VIDEO READY! 🔊 pe click karo!")
            st.video(vpath)
            st.warning("Download karke gallery me chalao - 100% awaz ayegi!")
            with open(vpath, "rb") as f:
                st.download_button(f"📥 Download - {avatar} - Real Human Voice", f, file_name=f"Mehar_V82_{avatar[:4]}_{duration}s.mp4", mime="video/mp4")

st.divider()
st.info("💡 TIP: Real Larka photo chahiye? Upar apni photo upload karo - Larka honey jar pakde hue - Sabse zyada viral wahi hota hai! Main abhi aapke liye Real Larka photo bhi bana ke dunga neeche 👇")
