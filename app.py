import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import os, math, time, random

st.set_page_config(page_title="MEHAR UGC V74", layout="centered")

st.title("MEHAR MART - UGC V74 👩 FIX")
st.success("V74 Stable - No Crash - Avatar Top Pe Hai")

# --- AVATAR TOP PE ---
st.subheader("1️⃣ Kaun dikhega? (Larki / Larka / Baby)")
avatar = st.radio(
    "Select Avatar",
    ["👩 Larki - Young Girl", "👦 Larka - Young Boy", "👶 Baby", "👩‍👧 Ammi with Baby", "👳‍♂️ Bearded Bhai", "👨‍⚕️ Doctor", "👵 Village Amma"],
    index=0
)

prompts = {
    "👩 Larki - Young Girl": "beautiful young Pakistani girl 22 years green dress holding honey jar pointing smiling home UGC realistic photo",
    "👦 Larka - Young Boy": "young Pakistani boy 24 white shalwar kameez holding honey jar smiling home UGC",
    "👶 Baby": "cute Pakistani baby 1 year with honey jar mother hands home UGC",
    "👩‍👧 Ammi with Baby": "Pakistani mother 30 with baby holding honey jar home UGC",
    "👳‍♂️ Bearded Bhai": "Pakistani bearded man 28 white cap holding honey jar UGC",
    "👨‍⚕️ Doctor": "Pakistani doctor white coat holding honey jar UGC",
    "👵 Village Amma": "old Pakistani woman 50 traditional dress holding honey jar UGC"
}

st.divider()
st.subheader("2️⃣ Product")
product_name = st.text_input("Product Name", "Pure Honey 100% Natural")
price = st.text_input("Price", "2975")
offer = st.text_input("Offer", "15% OFF - Free Delivery")

col1, col2 = st.columns(2)
with col1:
    duration = st.selectbox("Duration", [15, 20, 30])
with col2:
    fmt = st.selectbox("Format", ["Instagram Story 9:16", "TikTok 9:16", "FB 1:1"])

st.subheader("3️⃣ Voice Text (Free)")
voice_text = st.text_area("Jo bolega", f"Assalam-o-Alaikum guys! Maine Mehar Mart ka {product_name} liya, 100 percent pure, sirf {price} me {offer}!", height=80)

def gen_image(prompt):
    for i in range(3):
        try:
            url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=720&height=1280&model=flux&nologo=true&seed={random.randint(1,9999999)}"
            r = requests.get(url, timeout=90)
            if r.status_code == 200 and len(r.content) > 10000:
                return Image.open(BytesIO(r.content)).convert("RGB")
        except Exception as e:
            time.sleep(2)
    return None

def gen_voice(text):
    try:
        from gtts import gTTS
        os.makedirs("voice", exist_ok=True)
        p = "voice/voice.mp3"
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(p)
        return p
    except:
        return None

def make_video(img, dur, fmt, voice_path=None):
    W, H = (720, 1280) if "9:16" in fmt else (720, 720)
    fps = 24
    import imageio
    img = img.resize((W, H))
    frames = []
    for i in range(dur * fps):
        frames.append(img)
    os.makedirs("ads", exist_ok=True)
    temp = f"ads/temp_{dur}.mp4"
    final = f"ads/final_{dur}.mp4"
    imageio.mimsave(temp, [f for f in frames], fps=fps, macro_block_size=1)
    
    # Try add voice if exists
    if voice_path and os.path.exists(voice_path):
        try:
            from moviepy.editor import VideoFileClip, AudioFileClip
            v = VideoFileClip(temp)
            a = AudioFileClip(voice_path)
            if a.duration < v.duration:
                a = a.loop(duration=v.duration)
            else:
                a = a.subclip(0, v.duration)
            v = v.set_audio(a)
            v.write_videofile(final, codec='libx264', audio_codec='aac', verbose=False, logger=None)
            return final
        except Exception as e:
            return temp
    return temp

if st.button("🚀 UGC BANAO", type="primary", use_container_width=True):
    full_prompt = f"{prompts[avatar]}, label {product_name}, PURE HONEY jar, realistic, 4k"
    st.info(f"Avatar: {avatar}")
    st.caption(full_prompt)
    
    with st.spinner(f"{avatar} ki image bana raha hai - 40 sec lagega..."):
        img = gen_image(full_prompt)
        if img is None:
            st.error("Bhai Pollinations busy hai! 1 min baad dobara try karo - abhi server slow hai")
            st.stop()
        st.image(img, use_container_width=True)
        st.success("Image ban gayi!")

    with st.spinner("Voice bana raha hai..."):
        vp = gen_voice(voice_text)
        if vp:
            st.audio(vp)

    with st.spinner(f"{dur}s Video bana raha hai..."):
        try:
            vpath = make_video(img, duration, fmt, vp)
            st.success("UGC Video Ready! 🔥")
            st.video(vpath)
            with open(vpath, "rb") as f:
                st.download_button("📥 Download Video", f, file_name=f"UGC_{avatar[:2]}_{duration}s.mp4")
        except Exception as e:
            st.error(f"Video error: {e}")
            st.write("Image download karke CapCut me voice add kar lo Bhai!")
