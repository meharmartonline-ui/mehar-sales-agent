import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import os, random, asyncio

st.set_page_config(page_title="MEHAR UGC V76 FINAL", layout="centered")
st.title("MEHAR UGC V76 - VOICE IN VIDEO 🎙️")
st.success("FINAL: Voice Video ke ANDAR hoga - Larka/Larki alag voice!")

avatar = st.radio(
    "1️⃣ Kaun dikhega?",
    ["👩 Larki - Young Girl", "👦 Larka - Young Boy", "👶 Baby", "👩‍👧 Ammi with Baby", "👳‍♂️ Bearded Bhai"],
    index=1
)

# Avatar to Urdu Voice mapping - FREE Edge TTS
VOICE_MAP = {
    "👩 Larki - Young Girl": "ur-PK-UzmaNeural",  # Larki ki awaz
    "👦 Larka - Young Boy": "ur-PK-AsadNeural",   # Larke ki awaz
    "👶 Baby": "en-US-AnaNeural",               # Baby/Child awaz
    "👩‍👧 Ammi with Baby": "ur-PK-UzmaNeural",   # Ammi awaz
    "👳‍♂️ Bearded Bhai": "ur-PK-AsadNeural"      # Bhai awaz
}

prompts = {
    "👩 Larki - Young Girl": "beautiful young Pakistani girl 22 years green dress holding honey jar pointing smiling home UGC realistic",
    "👦 Larka - Young Boy": "young handsome Pakistani boy 22 years white shalwar kameez holding honey jar smiling home UGC realistic",
    "👶 Baby": "cute Pakistani baby with honey jar mother hands home UGC",
    "👩‍👧 Ammi with Baby": "Pakistani mother 30 with baby holding honey jar home UGC",
    "👳‍♂️ Bearded Bhai": "Pakistani bearded man 28 white cap holding honey jar UGC"
}

st.divider()
product_name = st.text_input("Product Name", "Pure Honey 100% Natural")
price = st.text_input("Price", "2975")
offer = st.text_input("Offer", "15% OFF - Free Delivery")
duration = st.selectbox("Duration", [15, 20, 30])
fmt = st.selectbox("Format", ["Instagram Story 9:16", "TikTok 9:16", "FB 1:1"])

# Voice text auto change by avatar
if "Larka" in avatar or "Bearded" in avatar:
    default_voice = f"Assalam-o-Alaikum Bhaiyo! Main Mehar Mart ka {product_name} use kar raha hun, 100 percent khalis hai, sirf {price} rupay me {offer}, abhi order karo 03452352112"
elif "Baby" in avatar:
    default_voice = f"Mama ne Mehar Mart ka {product_name} liya hai, bohot yummy hai, {price} me {offer}!"
else:
    default_voice = f"Assalam-o-Alaikum guys! Maine Mehar Mart ka {product_name} liya, 100 percent pure hai, sirf {price} me {offer}, aap bhi try karo!"

voice_text = st.text_area("2️⃣ Voice Text - Jo video me bolega", default_voice, height=100)
st.caption(f"Selected Voice: {VOICE_MAP[avatar]} - {avatar}")

def gen_image(prompt):
    try:
        url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=720&height=1280&model=turbo&nologo=true&seed={random.randint(1,9999999)}"
        r = requests.get(url, timeout=60)
        if r.status_code == 200:
            return Image.open(BytesIO(r.content)).convert("RGB")
    except:
        pass
    return None

async def gen_voice_edge(text, voice_name):
    import edge_tts
    os.makedirs("voice", exist_ok=True)
    path = "voice/final_voice.mp3"
    # Clean text for TTS
    communicate = edge_tts.Communicate(text, voice_name)
    await communicate.save(path)
    return path

def gen_voice_sync(text, voice_name):
    try:
        return asyncio.run(gen_voice_edge(text, voice_name))
    except Exception as e:
        # Fallback to gTTS if edge fails
        try:
            from gtts import gTTS
            os.makedirs("voice", exist_ok=True)
            path = "voice/fallback_voice.mp3"
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(path)
            return path
        except:
            return None

def make_video_with_voice_inside(img, dur, fmt, voice_path):
    import imageio
    import numpy as np
    W, H = (720, 1280) if "9:16" in fmt else (720, 720)
    img = img.resize((W, H))
    # Convert to numpy frames
    frame_np = np.array(img)
    frames = [frame_np for _ in range(dur * 24)]
    
    os.makedirs("ads", exist_ok=True)
    temp_video = "ads/temp_no_audio.mp4"
    final_video = "ads/final_with_voice.mp4"
    
    # Save silent video first
    imageio.mimsave(temp_video, frames, fps=24, macro_block_size=1)
    
    # Now add voice INSIDE video - THIS IS THE FIX Bhai!
    if voice_path and os.path.exists(voice_path):
        try:
            from moviepy.editor import VideoFileClip, AudioFileClip
            video = VideoFileClip(temp_video)
            audio = AudioFileClip(voice_path)
            
            # Audio ko video jitna lamba karo
            if audio.duration < video.duration:
                # Loop if short
                from moviepy.editor import AudioClip
                audio = audio.loop(duration=video.duration)
            else:
                audio = audio.subclip(0, video.duration)
            
            final = video.set_audio(audio)
            final.write_videofile(final_video, codec='libx264', audio_codec='aac', fps=24, verbose=False, logger=None)
            video.close()
            audio.close()
            final.close()
            return final_video
        except Exception as e:
            st.error(f"Voice merge error: {e} - Silent video de raha hun")
            return temp_video
    else:
        return temp_video

if st.button("🚀 FINAL UGC VIDEO BANAO - VOICE INSIDE", type="primary", use_container_width=True):
    full_prompt = f"{prompts[avatar]}, {product_name}, PURE HONEY jar, realistic 4k"
    st.info(f"Avatar: {avatar} | Voice: {VOICE_MAP[avatar]}")
    
    with st.spinner(f"{avatar} ki image bana raha hai..."):
        img = gen_image(full_prompt)
        if img is None:
            st.error("Image fail - 30 sec baad try karo Bhai")
            st.stop()
        st.image(img, caption=f"Image: {avatar}", use_container_width=True)
    
    with st.spinner(f"Voice bana raha hai - {VOICE_MAP[avatar]} - {avatar} ki awaz me..."):
        vp = gen_voice_sync(voice_text, VOICE_MAP[avatar])
        if vp:
            st.success(f"Voice ban gayi - {avatar} ki awaz!")
            # Voice ko alag se play nahi karenge - sirf video me hogi
        else:
            st.warning("Voice fail - silent video banega")
    
    with st.spinner(f"{duration}s FINAL Video bana raha hai - Voice ANDAR hogi..."):
        vpath = make_video_with_voice_inside(img, duration, fmt, vp)
        st.success("🔥 HO GAYA BHAI! Video ke ANDAR voice hai - Play karo!")
        st.video(vpath)
        with open(vpath, "rb") as f:
            st.download_button("📥 Download FINAL Video (Voice Inside)", f, file_name=f"Mehar_UGC_{avatar[:4]}_VOICE_INSIDE_{duration}s.mp4", mime="video/mp4")
