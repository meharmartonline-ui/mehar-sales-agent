import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import os, random, asyncio

st.set_page_config(page_title="MEHAR UGC V79 REAL HUMAN", layout="centered")
st.title("MEHAR UGC V79 - REAL HUMAN VOICE 🎙️")
st.success("V79: Ab ROBOT nahi, REAL HUMAN jaisi awaz ayegi!")

avatar = st.radio(
    "1️⃣ Kaun bolega?",
    ["👩 Larki - Young Girl (Real Human)", "👦 Larka - Young Boy (Real Human)", "👶 Baby", "👩‍👧 Ammi - Real Human", "👳‍♂️ Bearded Bhai - Real Human"],
    index=1
)

# REAL HUMAN NEURAL VOICE - Microsoft ke asli human voice
REAL_VOICE = {
    "👩 Larki - Young Girl (Real Human)": "ur-PK-UzmaNeural",   # Real Larki - Human
    "👦 Larka - Young Boy (Real Human)": "ur-PK-AsadNeural",    # Real Larka - Human
    "👶 Baby": "ur-PK-UzmaNeural",  # Baby ke liye bhi soft
    "👩‍👧 Ammi - Real Human": "ur-PK-UzmaNeural",
    "👳‍♂️ Bearded Bhai - Real Human": "ur-PK-AsadNeural"
}

prompts = {
    "👩 Larki - Young Girl (Real Human)": "beautiful Pakistani girl green dress holding honey jar smiling",
    "👦 Larka - Young Boy (Real Human)": "handsome Pakistani young boy white shalwar kameez holding honey jar smiling",
    "👶 Baby": "cute Pakistani baby with honey jar",
    "👩‍👧 Ammi - Real Human": "Pakistani mother with baby holding honey jar",
    "👳‍♂️ Bearded Bhai - Real Human": "Pakistani bearded man white cap holding honey jar"
}

st.divider()
product_name = st.text_input("Product Name", "Pure Honey 100% Natural")
price = st.text_input("Price", "2975")
offer = st.text_input("Offer", "15% OFF - Free Delivery")
duration = st.selectbox("Duration", [15, 20, 30])

if "Larka" in avatar or "Bearded" in avatar:
    default_voice = f"Assalam-o-Alaikum Bhaiyo! Dekho Main Mehar Mart ka {product_name} use kar raha hun, Yaqeen karo 100 percent khalis hai, Zaiqa bohot zabardast hai, Sirf {price} rupay me {offer}, Abhi order karo 03452352112"
else:
    default_voice = f"Assalam-o-Alaikum guys! Maine Mehar Mart ka {product_name} liya hai, Wallah 100 percent pure hai, Taste bohot zabardast hai, Sirf {price} me {offer}, Aap bhi try karo!"

voice_text = st.text_area("2️⃣ Jo bolegi/bolega - REAL HUMAN me", default_voice, height=110)
st.caption(f"🎙️ Real Voice: {REAL_VOICE[avatar]} - Bilkul human jaisi!")

def gen_image(prompt):
    for _ in range(3):
        try:
            url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=720&height=1280&model=turbo&nologo=true&seed={random.randint(1,999999)}"
            r = requests.get(url, timeout=50)
            if r.status_code == 200 and len(r.content) > 5000:
                return Image.open(BytesIO(r.content)).convert("RGB")
        except:
            continue
    return None

async def gen_real_human_voice(text, voice_name):
    import edge_tts
    os.makedirs("voice", exist_ok=True)
    path = "voice/real_human_voice.mp3"
    # Real human settings - rate, pitch
    # Larka ke liye thora slow, Larki ke liye normal
    communicate = edge_tts.Communicate(text, voice_name, rate="-5%", pitch="+2Hz")
    await communicate.save(path)
    return path

def gen_voice_real_sync(text, voice_name):
    try:
        # REAL HUMAN VOICE - Edge TTS
        return asyncio.run(gen_real_human_voice(text, voice_name))
    except Exception as e:
        st.warning(f"Real voice fail {e}, gTTS backup try...")
        try:
            from gtts import gTTS
            os.makedirs("voice", exist_ok=True)
            path = "voice/backup.mp3"
            gTTS(text=text, lang='ur', slow=False).save(path)
            return path
        except:
            return None

def make_video_real_voice(img, dur, voice_path):
    import imageio, numpy as np, subprocess
    os.makedirs("ads", exist_ok=True)
    img_path = "ads/input.jpg"
    temp_video = "ads/temp.mp4"
    final_video = "ads/final_REAL_HUMAN.mp4"
    img = img.resize((720, 1280))
    img.save(img_path)
    
    # Silent video
    frame = np.array(img)
    frames = [frame for _ in range(dur * 24)]
    imageio.mimsave(temp_video, frames, fps=24, macro_block_size=1)
    
    if voice_path and os.path.exists(voice_path):
        try:
            cmd = ["ffmpeg","-y","-loop","1","-i",img_path,"-i",voice_path,"-c:v","libx264","-c:a","aac","-b:a","192k","-t",str(dur),"-pix_fmt","yuv420p","-shortest",final_video]
            subprocess.run(cmd, capture_output=True, timeout=60)
            if os.path.exists(final_video):
                return final_video
        except:
            pass
        try:
            from moviepy.editor import VideoFileClip, AudioFileClip
            v = VideoFileClip(temp_video)
            a = AudioFileClip(voice_path)
            if a.duration < v.duration:
                a = a.loop(duration=v.duration)
            else:
                a = a.subclip(0, v.duration)
            out = v.set_audio(a)
            out.write_videofile(final_video, codec='libx264', audio_codec='aac', fps=24, verbose=False, logger=None)
            return final_video
        except Exception as e:
            st.error(f"Merge error {e}")
            return temp_video
    return temp_video

if st.button("🚀 REAL HUMAN VOICE VIDEO BANAO", type="primary", use_container_width=True):
    full_prompt = f"{prompts[avatar]}, {product_name}, honey jar, realistic, UGC"
    st.info(f"Avatar: {avatar} | Real Human Voice: {REAL_VOICE[avatar]}")
    
    with st.spinner(f"{avatar} image..."):
        img = gen_image(full_prompt)
        if img is None:
            img = Image.new("RGB", (720, 1280), "#FFF3E0")
        st.image(img, use_container_width=True)
    
    with st.spinner(f"🎙️ REAL HUMAN Voice bana raha hu - {REAL_VOICE[avatar]}... 10 sec lagega"):
        vp = gen_voice_real_sync(voice_text, REAL_VOICE[avatar])
        if vp and os.path.exists(vp):
            st.success("✅ REAL HUMAN Voice ban gayi! Suno Bhai:")
            st.audio(vp)
            st.caption("Ye awaz dekho Bhai - bilkul real human jaisi hai na? Robot nahi!")
        else:
            st.error("Voice fail!")
            vp = None
    
    with st.spinner(f"{duration}s Video me REAL HUMAN voice dal raha hu..."):
        vpath = make_video_real_voice(img, duration, vp)
        if vpath:
            st.success("🔥 HO GAYA! REAL HUMAN VOICE VIDEO READY! 🔊 pe click karke suno!")
            st.video(vpath)
            st.warning("⚠️ Video me awaz kam lage to 🔊 pe click karo aur volume full karo! Download karke gallery me 100% awaz ayegi!")
            with open(vpath, "rb") as f:
                st.download_button(f"📥 Download REAL HUMAN - {avatar}", f, file_name=f"REAL_HUMAN_{avatar[:4]}_{duration}s.mp4", mime="video/mp4")

st.divider()
st.subheader("💡 Aur zyada REAL chahiye Bhai?")
st.markdown("""
**Level 1 (FREE - Abhi wala):** `ur-PK-Uzma / Asad` - Microsoft Real Human Neural - 95% human jaisa ✅

**Level 2 (ULTRA REAL - 99% human):**
1.  ElevenLabs.io pe free account banao
2.  Voice Library me `Urdu Female` / `Aadam` search karo
3.  API Key leke Streamlit Secrets me dalo - Main code de dunga!

**Level 3 (Aapki apni awaz clone):**
- Aap 1 min apni awaz record karo
- ElevenLabs usi awaz me bolega - Bilkul aap jaisa!

**Abhi ke liye V79 ka voice suno Bhai - ye bhi real human jaisa hai - Robot nahi!**
""")
