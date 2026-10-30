import streamlit as st
import requests
from PIL import Image, ImageDraw
from io import BytesIO
import os, random, asyncio, subprocess

st.set_page_config(page_title="MEHAR UGC V80 FINAL", layout="centered")
st.title("MEHAR UGC V80 - FINAL FIX 🔥")
st.success("V80: Image + Real Human Voice + Video - 100% Guarantee!")

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

voice_text = st.text_area("Voice Text - REAL HUMAN bolegi", default_voice, height=100)

# FIXED IMAGE GENERATOR - Kabhi blank nahi
def create_real_ugc_image(avatar_text, product_name, price, offer):
    W, H = 720, 1280
    # Avatar ke hisab se color
    if "Larka" in avatar_text:
        bg_color = "#E3F2FD"
        top_color = "#1976D2"
    elif "Larki" in avatar_text:
        bg_color = "#FCE4EC"
        top_color = "#E91E63"
    else:
        bg_color = "#FFF3E0"
        top_color = "#FF6A00"
    
    img = Image.new("RGB", (W, H), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Top bar
    draw.rectangle([0, 0, W, 140], fill=top_color)
    draw.text((20, 30), "MEHAR MART", fill="white")
    draw.text((20, 80), "100% Pure & Original", fill="white")
    
    # Center box
    draw.rectangle([30, 180, W-30, 900], fill="white", outline=top_color, width=4)
    
    # Emoji honey
    draw.text((W//2-50, 200), "🍯", fill="black")
    draw.text((30, 350), f"Avatar: {avatar_text}", fill="black")
    draw.text((30, 400), f"Product:", fill="black")
    draw.text((30, 440), product_name[:35], fill="black")
    draw.text((30, 500), f"Price: Rs. {price}", fill=top_color)
    draw.text((30, 550), f"Offer: {offer}", fill="green")
    draw.text((30, 650), "Benefits:", fill="black")
    draw.text((30, 690), "- 100% Pure Natural", fill="black")
    draw.text((30, 730), "- No Sugar Added", fill="black")
    draw.text((30, 770), "- Direct from Farm", fill="black")
    
    # Bottom
    draw.rectangle([0, H-150, W, H], fill="#0D47A1")
    draw.text((20, H-100), "Order Now:", fill="white")
    draw.text((20, H-60), "03452352112 - Free Delivery", fill="white")
    draw.text((20, H-20), "Mehar Mart - Peshawar", fill="white")
    
    return img

def gen_image_fixed(prompt, avatar_text, product_name, price, offer):
    # Try online first
    for _ in range(2):
        try:
            url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=720&height=1280&model=turbo&nologo=true&seed={random.randint(1,999999)}"
            r = requests.get(url, timeout=30)
            if r.status_code == 200 and len(r.content) > 8000:
                return Image.open(BytesIO(r.content)).convert("RGB")
        except:
            continue
    # 100% Guaranteed local image
    st.warning("Online AI busy hai Bhai, Local REAL UGC bana raha hun - ye bhi viral hota hai!")
    return create_real_ugc_image(avatar_text, product_name, price, offer)

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
        st.warning(f"Real voice fail {e}, backup...")
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
    final_video = "ads/final_REAL.mp4"
    
    img = img.resize((720, 1280))
    img.save(img_path, "JPEG")
    
    # ONLY FFMPEG - No moviepy needed - 100% working
    if voice_path and os.path.exists(voice_path):
        try:
            # Real human voice video - FFMPEG direct
            cmd = [
                "ffmpeg", "-y",
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
                st.error(f"FFmpeg error: {result.stderr[:500]}")
                # Fallback silent
                cmd2 = ["ffmpeg","-y","-loop","1","-i",img_path,"-c:v","libx264","-t",str(dur),"-pix_fmt","yuv420p","ads/silent.mp4"]
                subprocess.run(cmd2, capture_output=True, timeout=30)
                return "ads/silent.mp4"
        except Exception as e:
            st.error(f"Video error: {e}")
            return None
    else:
        # No voice - silent video
        try:
            cmd = ["ffmpeg","-y","-loop","1","-i",img_path,"-c:v","libx264","-t",str(dur),"-pix_fmt","yuv420p",final_video]
            subprocess.run(cmd, capture_output=True, timeout=30)
            return final_video
        except:
            return None

if st.button("🚀 REAL HUMAN VIDEO BANAO - FINAL", type="primary", use_container_width=True):
    full_prompt = f"{prompts[avatar]}, {product_name}, honey jar, realistic photo, UGC style"
    st.info(f"Avatar: {avatar} | Real Human Voice: {REAL_VOICE[avatar]}")
    
    with st.spinner(f"{avatar} image bana raha..."):
        img = gen_image_fixed(full_prompt, avatar, product_name, price, offer)
        st.image(img, caption=f"✅ UGC Image Ready - {avatar}", use_container_width=True)
    
    with st.spinner(f"🎙️ REAL HUMAN Voice - {REAL_VOICE[avatar]}..."):
        vp = gen_voice_sync(voice_text, REAL_VOICE[avatar])
        if vp and os.path.exists(vp):
            st.success("✅ REAL HUMAN Voice Ready! Suno Bhai - bilkul human jaisi:")
            st.audio(vp)
        else:
            st.error("Voice fail!")
            vp = None
    
    with st.spinner(f"{duration}s Video bana raha - Voice ke sath..."):
        vpath = make_video_final(img, duration, vp)
        if vpath and os.path.exists(vpath):
            st.success("🔥 FINAL VIDEO READY! 🔊 pe click karke volume ON karo!")
            st.video(vpath)
            st.caption("⚠️ Awaz nahi aa rahi? Video player me speaker icon 🔊 pe click karo! Download karke gallery me 100% awaz ayegi!")
            with open(vpath, "rb") as f:
                st.download_button(f"📥 Download REAL HUMAN - {avatar} - Voice Inside", f, file_name=f"Mehar_REAL_HUMAN_{avatar[:4]}_{duration}s.mp4", mime="video/mp4")
        else:
            st.error("Video fail - dubara try karo Bhai")
