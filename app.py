import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import os, math, time
import numpy as np

st.set_page_config(page_title="MEHAR UGC V73 FIX", layout="centered")
st.title("MEHAR MART - UGC V73 FIX 👩‍👦")
st.success("✅ FIX: Avatar option sab se upar hai + Image retry system!")

# --- 1. AVATAR SELECTION SAB SE UPAR ---
st.subheader("1️⃣ Kaun dikhega? Select karo *")
avatar_choice = st.radio(
    "Avatar:",
    [
        "👩 Larki - Young Girl (Screenshot jaisi)",
        "👦 Larka - Young Boy",
        "👶 Baby - Cute Baby",
        "👩‍👧 Ammi with Baby",
        "👳‍♂️ Bearded Bhai",
        "👨‍⚕️ Doctor",
        "👵 Village Amma"
    ],
    index=0
)

# Avatar to prompt mapping
PROMPTS = {
    "👩 Larki - Young Girl (Screenshot jaisi)": "beautiful young Pakistani girl 22yo green dress holding honey jar pointing at jar smiling home background UGC selfie realistic",
    "👦 Larka - Young Boy": "handsome Pakistani young boy 24yo white shalwar kameez holding honey jar smiling home UGC realistic",
    "👶 Baby - Cute Baby": "cute Pakistani baby 1yo with honey jar mother hands adorable home UGC",
    "👩‍👧 Ammi with Baby": "Pakistani mother 30yo with baby holding honey jar happy family home UGC",
    "👳‍♂️ Bearded Bhai": "Pakistani bearded man 28yo white cap holding honey jar sunnah look UGC",
    "👨‍⚕️ Doctor": "Pakistani doctor white coat holding honey jar clinic trustworthy UGC",
    "👵 Village Amma": "old Pakistani village woman 50yo traditional dress holding honey jar desi UGC"
}

st.divider()
st.subheader("2️⃣ Product Details")
product_name = st.text_input("Product Name", value="Pure Honey 100% Natural")
price = st.text_input("Price", value="2975")
offer = st.text_input("Offer", value="15% OFF - Free Delivery")
extra = st.text_input("Extra Background (optional)", placeholder="Jaise: kitchen me")

col1, col2 = st.columns(2)
with col1:
    duration = st.selectbox("Duration", [15, 20, 30])
with col2:
    format_type = st.selectbox("Format", ["Instagram Story 9:16", "TikTok 9:16", "FB Feed 1:1"])

st.subheader("3️⃣ Voiceover")
voice_style = st.selectbox("Voice Style", ["Larki ki awaz - Casual", "Larke ki awaz - Friendly", "Ammi ki awaz - Caring"])
default_voice = {
    "Larki ki awaz - Casual": f"Assalam-o-Alaikum guys! Maine Mehar Mart ka {product_name} liya hai, 100 percent pure hai, sirf {price} me {offer}!",
    "Larke ki awaz - Friendly": f"Bhai log, Mehar Mart ka {product_name} check karo, 100 percent original, sirf {price} me {offer}, order karo 03452352112",
    "Ammi ki awaz - Caring": f"Mere bachon ko Mehar Mart ka {product_name} bohot pasand hai, khalis hai, sirf {price} me"
}
voice_text = st.text_area("Voice Text", value=default_voice[voice_style], height=80)

def generate_image_with_retry(prompt):
    # 3 baar try karega Bhai
    for attempt in range(3):
        try:
            encoded = requests.utils.quote(prompt)
            url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1350&model=flux&nologo=true&seed={np.random.randint(1000000)}"
            st.write(f"Try {attempt+1}: Image bana raha hai...")
            r = requests.get(url, timeout=120)
            if r.status_code == 200 and len(r.content) > 5000:
                return Image.open(BytesIO(r.content)).convert("RGB")
        except Exception as e:
            st.warning(f"Try {attempt+1} fail: {e}")
            time.sleep(2)
    return None

def generate_voice(text):
    try:
        from gtts import gTTS
        os.makedirs("voice", exist_ok=True)
        path = "voice/ugc_voice.mp3"
        try:
            tts = gTTS(text=text, lang='ur', slow=False)
        except:
            tts = gTTS(text=text, lang='en', slow=False)
        tts.save(path)
        return path
    except:
        return None

def create_video(product_img, duration, format_type, voice_path=None):
    W, H = (1080, 1920) if "9:16" in format_type else (1080, 1080)
    fps = 24
    frames = []
    product_img = product_img.resize((W, H))
    for i in range(duration * fps):
        zoom = 1.0 + 0.04 * math.sin(i / (duration*fps) * math.pi * 2)
        w2, h2 = int(W*zoom), int(H*zoom)
        img_z = product_img.resize((w2, h2))
        x = (W - w2)//2
        y = (H - h2)//2
        frame = Image.new("RGB", (W, H), "black")
        frame.paste(img_z, (x, y))
        frames.append(np.array(frame))
    os.makedirs("ads", exist_ok=True)
    temp_video = f"ads/temp_{duration}s.mp4"
    final_video = f"ads/Mehar_UGC_{duration}s.mp4"
    import imageio
    imageio.mimsave(temp_video, frames, fps=fps, macro_block_size=1)
    if voice_path and os.path.exists(voice_path):
        try:
            from moviepy.editor import VideoFileClip, AudioFileClip
            video = VideoFileClip(temp_video)
            audio = AudioFileClip(voice_path)
            if audio.duration < video.duration:
                audio = audio.loop(duration=video.duration)
            else:
                audio = audio.subclip(0, video.duration)
            video = video.set_audio(audio)
            video.write_videofile(final_video, codec='libx264', audio_codec='aac', verbose=False, logger=None)
            return final_video
        except Exception as e:
            st.warning(f"Voice add error: {e}")
            return temp_video
    return temp_video

if st.button("🚀 UGC IMAGE + VIDEO BANAO", type="primary"):
    base = PROMPTS[avatar_choice]
    full_prompt = f"{base}, jar label PURE HONEY 100% Natural with bee logo, {product_name}, {extra}, high quality, realistic skin"
    
    st.info(f"Selected: {avatar_choice}")
    st.code(full_prompt)
    
    with st.spinner(f"{avatar_choice} ki image bana raha hai... 30 sec lagega"):
        img = generate_image_with_retry(full_prompt)
        if not img:
            st.error("Bhai 3 baar fail hua! 1 min ruk ke dobara try karo - Pollinations busy hai. Ya prompt thora short karo.")
            st.stop()
        st.image(img, caption=f"✅ UGC Ready - {avatar_choice}", use_container_width=True)

    with st.spinner("Voice bana raha hai..."):
        voice_path = generate_voice(voice_text)
        if voice_path:
            st.audio(voice_path)

    with st.spinner(f"{duration}s Video bana raha hai..."):
        video_path = create_video(img, duration, format_type, voice_path)
        st.success("Ho gaya Bhai! 🔥")
        st.video(video_path)
        with open(video_path, "rb") as f:
            st.download_button(f"📥 Download {avatar_choice} - {duration}s", f, file_name=f"UGC_{duration}s.mp4", mime="video/mp4")
