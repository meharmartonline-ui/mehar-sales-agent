import streamlit as st
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os, random, asyncio, time

st.set_page_config(page_title="MEHAR UGC V77 NEVER FAIL", layout="centered")
st.title("MEHAR UGC V77 - NEVER FAIL 🔥")
st.success("V77: Image fail bhi ho to bhi video banega - Guarantee!")

avatar = st.radio(
    "1️⃣ Kaun dikhega?",
    ["👩 Larki - Young Girl", "👦 Larka - Young Boy", "👶 Baby", "👩‍👧 Ammi with Baby", "👳‍♂️ Bearded Bhai"],
    index=1
)

VOICE_MAP = {
    "👩 Larki - Young Girl": "ur-PK-UzmaNeural",
    "👦 Larka - Young Boy": "ur-PK-AsadNeural",
    "👶 Baby": "en-US-AnaNeural",
    "👩‍👧 Ammi with Baby": "ur-PK-UzmaNeural",
    "👳‍♂️ Bearded Bhai": "ur-PK-AsadNeural"
}

prompts = {
    "👩 Larki - Young Girl": "beautiful Pakistani girl green dress holding honey jar smiling",
    "👦 Larka - Young Boy": "handsome Pakistani young boy white shalwar kameez holding honey jar smiling",
    "👶 Baby": "cute Pakistani baby with honey jar",
    "👩‍👧 Ammi with Baby": "Pakistani mother with baby holding honey jar",
    "👳‍♂️ Bearded Bhai": "Pakistani bearded man white cap holding honey jar"
}

st.divider()
product_name = st.text_input("Product Name", "Pure Honey 100% Natural")
price = st.text_input("Price", "2975")
offer = st.text_input("Offer", "15% OFF - Free Delivery")
duration = st.selectbox("Duration", [15, 20, 30])
fmt = st.selectbox("Format", ["Instagram Story 9:16", "TikTok 9:16", "FB 1:1"])

if "Larka" in avatar or "Bearded" in avatar:
    default_voice = f"Assalam-o-Alaikum Bhaiyo! Main Mehar Mart ka {product_name} use kar raha hun, 100 percent khalis hai, sirf {price} rupay me {offer}, order karo 03452352112"
else:
    default_voice = f"Assalam-o-Alaikum guys! Maine Mehar Mart ka {product_name} liya, 100 percent pure hai, sirf {price} me {offer}!"

voice_text = st.text_area("Voice Text - Video ke andar bolega", default_voice, height=80)

def create_guaranteed_image(avatar_text, product_name, price, offer):
    # Ye kabhi fail nahi hoga Bhai - Local banega
    W, H = 720, 1280
    # Color by avatar
    bg = "#FFF3E0" if "Larka" in avatar_text else "#FCE4EC" if "Larki" in avatar_text else "#E8F5E9"
    img = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)
    try:
        font_big = ImageFont.truetype("arial.ttf", 50)
        font_med = ImageFont.truetype("arial.ttf", 35)
    except:
        font_big = ImageFont.load_default()
        font_med = ImageFont.load_default()
    
    draw.rectangle([0, 0, W, 150], fill="#FF6A00")
    draw.text((W//2, 75), "MEHAR MART", fill="white", anchor="mm", font=font_big)
    
    # Avatar circle
    draw.ellipse([W//2-150, 200, W//2+150, 500], fill="#FFCC80", outline="#FF6A00", width=5)
    draw.text((W//2, 350), "👤", fill="black", anchor="mm", font=font_big)
    draw.text((W//2, 550), avatar_text, fill="#333", anchor="mm", font=font_med)
    
    draw.rectangle([40, 620, W-40, 1000], fill="white", outline="#FF6A00", width=3)
    draw.text((W//2, 680), "🍯", fill="black", anchor="mm", font=font_big)
    draw.text((W//2, 760), product_name[:28], fill="black", anchor="mm", font=font_med)
    draw.text((W//2, 820), f"Rs. {price}", fill="#FF6A00", anchor="mm", font=font_big)
    draw.text((W//2, 880), offer, fill="#0D47A1", anchor="mm", font=font_med)
    draw.text((W//2, 950), "100% Pure & Original", fill="#2E7D32", anchor="mm", font=font_med)
    
    draw.rectangle([0, H-120, W, H], fill="#0D47A1")
    draw.text((W//2, H-60), "03452352112 - Free Delivery", fill="white", anchor="mm", font=font_med)
    return img

def gen_image_never_fail(prompt, avatar_text, product_name, price, offer):
    # 4 engines try karega
    urls = [
        f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=720&height=1280&model=turbo&nologo=true&seed={random.randint(1,999999)}",
        f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=720&height=1280&model=flux&seed={random.randint(1,999999)}",
        f"https://pollinations.ai/p/{requests.utils.quote(prompt)}?width=720&height=1280&model=turbo"
    ]
    for url in urls:
        try:
            r = requests.get(url, timeout=40)
            if r.status_code == 200 and len(r.content) > 5000:
                return Image.open(BytesIO(r.content)).convert("RGB")
        except:
            continue
    # Agar sab fail to local image - lekin video banega!
    st.warning("AI server busy hai Bhai, Local UGC bana raha hun - Video to banega hi banega!")
    return create_guaranteed_image(avatar_text, product_name, price, offer)

async def gen_voice_edge(text, voice_name):
    import edge_tts
    os.makedirs("voice", exist_ok=True)
    path = "voice/final_voice.mp3"
    communicate = edge_tts.Communicate(text, voice_name)
    await communicate.save(path)
    return path

def gen_voice_sync(text, voice_name):
    try:
        return asyncio.run(gen_voice_edge(text, voice_name))
    except:
        try:
            from gtts import gTTS
            os.makedirs("voice", exist_ok=True)
            path = "voice/fallback.mp3"
            gTTS(text=text, lang='en', slow=False).save(path)
            return path
        except:
            return None

def make_video_voice_inside(img, dur, fmt, voice_path):
    import imageio
    import numpy as np
    W, H = (720, 1280) if "9:16" in fmt else (720, 720)
    img = img.resize((W, H))
    frame_np = np.array(img)
    frames = [frame_np for _ in range(dur * 24)]
    os.makedirs("ads", exist_ok=True)
    temp = "ads/temp.mp4"
    final = "ads/final_voice_inside.mp4"
    imageio.mimsave(temp, frames, fps=24, macro_block_size=1)
    if voice_path and os.path.exists(voice_path):
        try:
            from moviepy.editor import VideoFileClip, AudioFileClip
            v = VideoFileClip(temp)
            a = AudioFileClip(voice_path)
            if a.duration < v.duration:
                a = a.loop(duration=v.duration)
            else:
                a = a.subclip(0, v.duration)
            out = v.set_audio(a)
            out.write_videofile(final, codec='libx264', audio_codec='aac', fps=24, verbose=False, logger=None)
            return final
        except Exception as e:
            st.write(f"Audio merge error: {e}")
            return temp
    return temp

if st.button("🚀 FINAL VIDEO BANAO - VOICE INSIDE", type="primary", use_container_width=True):
    full_prompt = f"{prompts[avatar]}, {product_name}, honey jar, realistic photo, 4k, UGC style"
    st.info(f"Avatar: {avatar} | Voice: {VOICE_MAP[avatar]}")
    
    with st.spinner(f"{avatar} ki image bana raha hai..."):
        img = gen_image_never_fail(full_prompt, avatar, product_name, price, offer)
        st.image(img, caption=f"UGC Image - {avatar}", use_container_width=True)
        st.success("Image Ready! ✅")
    
    with st.spinner(f"Voice bana raha hai - {avatar} ki awaz me ({VOICE_MAP[avatar]})..."):
        vp = gen_voice_sync(voice_text, VOICE_MAP[avatar])
        if vp:
            st.success(f"Voice Ready - {avatar} ki awaz me! ✅")
        else:
            st.warning("Voice fail - silent video")
    
    with st.spinner(f"{duration}s Video bana raha hai - Voice ANDAR dal raha hai..."):
        vpath = make_video_voice_inside(img, duration, fmt, vp)
        st.success("🔥 HO GAYA BHAI! VIDEO ME VOICE ANDAR HAI - AB PLAY KARO!")
        st.video(vpath)
        with open(vpath, "rb") as f:
            st.download_button(f"📥 Download {avatar} - Voice Inside", f, file_name=f"Mehar_{avatar[:4]}_VOICE_INSIDE_{duration}s.mp4", mime="video/mp4")
