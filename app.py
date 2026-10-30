import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import os, math
import numpy as np

st.set_page_config(page_title="MEHAR UGC V72", layout="centered")
st.title("MEHAR MART - UGC AI Agent V72 👩‍👦")
st.caption("Larki / Larka / Baby / Ammi - Jaise real customer ho!")

def generate_image(prompt):
    url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=1080&height=1350&model=flux&nologo=true&enhance=true&seed={np.random.randint(100000)}"
    r = requests.get(url, timeout=90)
    if r.status_code == 200:
        return Image.open(BytesIO(r.content)).convert("RGB")
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

def create_ugc_video(product_img, duration, format_type, voice_path=None):
    W, H = (1080, 1920) if "9:16" in format_type else (1080, 1080)
    fps = 24
    frames = []
    product_img = product_img.resize((W, H))
    total_frames = duration * fps
    
    for i in range(total_frames):
        # Simple zoom UGC effect
        zoom = 1.0 + 0.05 * math.sin(i/total_frames * math.pi * 2)
        w2, h2 = int(W*zoom), int(H*zoom)
        img_z = product_img.resize((w2, h2))
        x = (W - w2)//2
        y = (H - h2)//2
        frame = Image.new("RGB", (W, H), "black")
        frame.paste(img_z, (x, y))
        frames.append(np.array(frame))

    os.makedirs("ads", exist_ok=True)
    temp_video = f"ads/temp_ugc_{duration}s.mp4"
    final_video = f"ads/Mehar_UGC_{duration}s_{format_type.replace(' ','_')}.mp4"
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
        except:
            return temp_video
    return temp_video

# --- Avatar Prompts ---
AVATARS = {
    "👩 Larki - Young Girl (Jaise Screenshot me)": "beautiful young Pakistani girl 22 years old, green traditional dress, holding PURE HONEY jar in hand, pointing at jar with finger, smiling, natural home background, soft lighting, UGC selfie style, realistic, 4k",
    "👦 Larka - Young Boy": "young handsome Pakistani boy 24 years old, white shalwar kameez, holding PURE HONEY jar, smiling, home background, UGC style, realistic",
    "👶 Baby - Cute Baby with Honey": "cute Pakistani baby 1 year old, sitting with small PURE HONEY jar, mother hands holding baby, adorable, home background, UGC style, safe",
    "👩‍👧 Ammi with Baby": "Pakistani mother 30 years old with baby in lap, holding PURE HONEY jar, happy family, home background, UGC mom review style",
    "👳‍♂️ Bearded Bhai - Islamic Look": "Pakistani bearded man 28 years, white cap, holding PURE HONEY jar, sunnah look, smiling, home background, UGC style",
    "👨‍⚕️ Doctor": "Pakistani male doctor in white coat, holding PURE HONEY jar, recommending, clinic background, trustworthy, UGC style",
    "👵 Village Amma": "old Pakistani village woman 50 years, traditional dress, holding PURE HONEY jar, desi background, authentic UGC"
}

st.divider()
product_name = st.text_input("Product Name", value="Pure Honey 100% Natural")
price = st.text_input("Price", value="2975")
offer = st.text_input("Offer", value="15% OFF - Free Delivery")

avatar_choice = st.selectbox("Kaun dikhega UGC me? *", list(AVATARS.keys()))
custom_prompt_add = st.text_input("Extra Detail (Optional)", placeholder="Jaise: kitchen me, roof top pe, etc")

col1, col2 = st.columns(2)
with col1:
    duration = st.selectbox("Video Duration", [15, 20, 30])
with col2:
    format_type = st.selectbox("Format", ["Instagram Story 9:16", "TikTok 9:16", "FB Feed 1:1"])

st.subheader("🎙️ UGC Voice - Jaise real customer bole")
voice_style = st.selectbox("Voice Style", ["Larki ki awaz - Casual", "Larke ki awaz - Friendly", "Ammi ki awaz - Caring"])
default_voice = {
    "Larki ki awaz - Casual": f"Assalam-o-Alaikum guys! Maine Mehar Mart ka {product_name} liya hai, 100 percent pure hai, taste bohot zabardast hai, sirf {price} me {offer}, aap bhi try karo!",
    "Larke ki awaz - Friendly": f"Bhai log, Mehar Mart ka {product_name} check karo, 100 percent original, main khud use kar raha hun, sirf {price} me {offer}, order karo 03452352112",
    "Ammi ki awaz - Caring": f"Mere bachon ko Mehar Mart ka {product_name} bohot pasand hai, khalis aur pure hai, sirf {price} me, free delivery hai"
}
voice_text = st.text_area("Voiceover Text", value=default_voice[voice_style], height=100)

if st.button("🚀 UGC IMAGE + VIDEO BANAO"):
    base_prompt = AVATARS[avatar_choice]
    full_prompt = f"{base_prompt}, jar label says '{product_name}', PURE HONEY 100% Natural with bee and honeycomb, {custom_prompt_add}, high detail, no blur"
    
    with st.spinner(f"{avatar_choice} ki image bana raha hai..."):
        img = generate_image(full_prompt)
        if not img:
            st.error("Image fail, dobara try karo")
            st.stop()
        st.image(img, caption=f"UGC Image - {avatar_choice}", use_container_width=True)
        os.makedirs("temp", exist_ok=True)
        img.save("temp/ugc_product.png")

    with st.spinner("Voice bana raha hai..."):
        voice_path = generate_voice(voice_text)
        if voice_path:
            st.audio(voice_path)

    with st.spinner(f"{duration}s UGC Video bana raha hai..."):
        video_path = create_ugc_video(img, duration, format_type, voice_path)
        st.success("UGC Video Ready Bhai! 🔥")
        st.video(video_path)
        with open(video_path, "rb") as f:
            st.download_button(f"📥 Download UGC Ad - {avatar_choice}", f, file_name=f"UGC_{avatar_choice[:4]}_{duration}s.mp4", mime="video/mp4")

st.info("💡 Tip: Larki wala select karo to bilkul aapke screenshot jaisa banega! Baby wala moms ke liye best hai, Larka wala young audience ke liye viral hota hai!")
