import streamlit as st
import requests
from PIL import Image, ImageDraw
from io import BytesIO
import os, random, asyncio

st.set_page_config(page_title="MEHAR UGC V81 FINAL FIX", layout="centered")
st.title("MEHAR UGC V81 - FFMPEG FIX 🔥")
st.success("V81: ffmpeg fix + Image text fix - 100% chalega!")

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

prompts = {
    "👩 Larki - Young Girl": "beautiful Pakistani girl green dress holding honey jar smiling",
    "👦 Larka - Young Boy": "handsome Pakistani young boy white shalwar kameez holding honey jar smiling",
    "👶 Baby": "cute Pakistani baby with honey jar",
    "👩‍👧 Ammi": "Pakistani mother with baby holding honey jar",
    "👳‍♂️ Bearded Bhai": "Pakistani bearded man white cap holding honey jar"
}

st.divider()
product_name = st.text_input("Product Name", "Pure Honey 100% Natural")
price = st.text_input("Price", "2975")
offer = st.text_input("Offer", "15% OFF - Free Delivery")
duration = st.selectbox("Duration", [15, 20, 30])

if "Larka" in avatar or "Bearded" in avatar:
    default_voice = f"Assalam-o-Alaikum Bhaiyo! Main Mehar Mart ka {product_name} use kar raha hun, 100 percent khalis hai, sirf {price} rupay me {offer}, order karo 03452352112"
else:
    default_voice = f"Assalam-o-Alaikum guys! Maine Mehar Mart ka {product_name} liya hai, 100 percent pure hai, sirf {price} me {offer}!"

voice_text = st.text_area("Voice Text - REAL HUMAN", default_voice, height=90)

def get_ffmpeg_path():
    # Streamlit me ffmpeg ka path alag hai - ye fix hai Bhai!
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except:
        return "ffmpeg"

def create_big_text_image(avatar_text, product_name, price, offer):
    W, H = 720, 1280
    # Big colors
    if "Larka" in avatar_text:
        top_color = "#1976D2"
    elif "Larki" in avatar_text:
        top_color = "#C2185B"
    else:
        top_color = "#EF6C00"
    
    img = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(img)
    
    # Top - BIG
    draw.rectangle([0, 0, W, 200], fill=top_color)
    draw.text((W//2, 50), "MEHAR MART", fill="white", anchor="mm", align="center")
    draw.text((W//2, 120), "100% Pure Honey", fill="white", anchor="mm")
    
    # Middle box - BIG TEXT
    y = 250
    draw.text((40, y), f"{avatar_text}", fill="black")
    y += 80
    draw.text((40, y), f"PRODUCT:", fill=top_color)
    y += 60
    draw.text((40, y), product_name[:30], fill="black")
    y += 80
    draw.text((40, y), f"PRICE: Rs. {price}", fill=top_color)
    y += 80
    draw.text((40, y), f"{offer}", fill="green")
    y += 100
    draw.text((40, y), "BENEFITS:", fill="black")
    y += 60
    draw.text((40, y), "✓ 100% Pure Natural", fill="black")
    y += 60
    draw.text((40, y), "✓ No Sugar Added", fill="black")
    y += 60
    draw.text((40, y), "✓ Direct from Farm", fill="black")
    y += 100
    draw.text((40, y), "🍯 PURE HONEY JAR", fill=top_color)
    
    # Bottom - BIG
    draw.rectangle([0, H-200, W, H], fill="#0D47A1")
    draw.text((W//2, H-120), "Order Now: 03452352112", fill="white", anchor="mm")
    draw.text((W//2, H-60), "Free Delivery - Peshawar", fill="white", anchor="mm")
    
    return img

def gen_image_fixed(prompt, avatar_text, product_name, price, offer):
    # Try 1: Pollinations
    try:
        url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=720&height=1280&model=turbo&nologo=true&seed={random.randint(1,999999)}"
        r = requests.get(url, timeout=25)
        if r.status_code == 200 and len(r.content) > 8000:
            return Image.open(BytesIO(r.content)).convert("RGB")
    except:
        pass
    st.warning("Online AI busy Bhai, Local BIG UGC bana raha hun!")
    return create_big_text_image(avatar_text, product_name, price, offer)

async def gen_real_human_voice(text, voice_name):
    import edge_tts
    os.makedirs("voice", exist_ok=True)
    path = "voice/real_human.mp3"
    communicate = edge_tts.Communicate(text, voice_name, rate="-5%")
    await communicate.save(path)
    return path

def gen_voice_sync(text, voice_name):
    try:
        return asyncio.run(gen_real_human_voice(text, voice_name))
    except Exception as e:
        try:
            from gtts import gTTS
            os.makedirs("voice", exist_ok=True)
            path = "voice/backup.mp3"
            gTTS(text=text, lang='ur', slow=False).save(path)
            return path
        except:
            return None

def make_video_ffmpeg_fixed(img, dur, voice_path):
    import subprocess
    os.makedirs("ads", exist_ok=True)
    img_path = "ads/input.jpg"
    final_video = "ads/final_REAL.mp4"
    
    ffmpeg_exe = get_ffmpeg_path()
    st.caption(f"Using ffmpeg: {ffmpeg_exe}")
    
    img = img.resize((720, 1280))
    img.save(img_path, "JPEG", quality=95)
    
    if voice_path and os.path.exists(voice_path):
        try:
            cmd = [
                ffmpeg_exe, "-y",
                "-loop", "1",
                "-i", img_path,
                "-i", voice_path,
                "-c:v", "libx264",
                "-c:a", "aac",
                "-b:a", "192k",
                "-t", str(dur),
                "-pix_fmt", "yuv420p",
                "-shortest",
                final_video
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if os.path.exists(final_video) and os.path.getsize(final_video) > 5000:
                return final_video
            else:
                st.error(f"FFmpeg log: {result.stderr[:800]}")
                return None
        except Exception as e:
            st.error(f"Video error: {e}")
            return None
    else:
        try:
            cmd = [ffmpeg_exe,"-y","-loop","1","-i",img_path,"-c:v","libx264","-t",str(dur),"-pix_fmt","yuv420p",final_video]
            subprocess.run(cmd, capture_output=True, timeout=30)
            return final_video
        except Exception as e:
            st.error(f"Silent video error: {e}")
            return None

if st.button("🚀 REAL HUMAN VIDEO BANAO - V81", type="primary", use_container_width=True):
    full_prompt = f"{prompts[avatar]}, {product_name}, honey jar, realistic, UGC"
    st.info(f"Avatar: {avatar} | Voice: {REAL_VOICE[avatar]}")
    
    with st.spinner(f"{avatar} image..."):
        img = gen_image_fixed(full_prompt, avatar, product_name, price, offer)
        st.image(img, caption=f"✅ UGC Ready - {avatar}", use_container_width=True)
    
    with st.spinner(f"🎙️ REAL HUMAN Voice - {REAL_VOICE[avatar]}..."):
        vp = gen_voice_sync(voice_text, REAL_VOICE[avatar])
        if vp and os.path.exists(vp):
            st.success("✅ REAL HUMAN Voice Ready! Suno:")
            st.audio(vp)
        else:
            st.error("Voice fail!")
            vp = None
    
    with st.spinner(f"{duration}s Video me voice dal raha hu..."):
        vpath = make_video_ffmpeg_fixed(img, duration, vp)
        if vpath and os.path.exists(vpath):
            st.success("🔥 FINAL VIDEO READY! 🔊 pe click karke suno!")
            st.video(vpath)
            st.warning("⚠️ Video me awaz nahi? 🔊 icon pe click karo! Download karke gallery me 100% ayegi!")
            with open(vpath, "rb") as f:
                st.download_button(f"📥 Download REAL HUMAN - {avatar}", f, file_name=f"Mehar_REAL_{avatar[:4]}_{duration}s.mp4", mime="video/mp4")
        else:
            st.error("Video fail - lekin image aur voice to ban gaye! Neeche download karo")
            if vp:
                with open(vp, "rb") as f:
                    st.download_button("📥 Download Voice Only (Real Human)", f, file_name="real_human_voice.mp3")
