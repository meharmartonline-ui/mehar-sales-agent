import streamlit as st, requests, os, random, asyncio, subprocess
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="MEHAR UGC V83 ANIMATED", layout="centered")
st.title("MEHAR UGC V83 - ANIMATED ZOOM 🔥")
st.success("V83: Ab Image ZOOM hoga - Video lagega - Static nahi!")

avatar = st.radio("Kaun?", ["👩 Larki - Young Girl", "👦 Larka - Young Boy"], index=0)
REAL_VOICE = {"👩 Larki - Young Girl": "ur-PK-UzmaNeural", "👦 Larka - Young Boy": "ur-PK-AsadNeural"}

uploaded = st.file_uploader("📸 Real Photo Upload Karo (Best Result)", type=["jpg","png","jpeg"])
product_name = st.text_input("Product Name", "Pure Honey 100% Natural")
price = st.text_input("Price", "2975")
offer = st.text_input("Offer", "15% OFF - Free Delivery")
duration = st.selectbox("Duration", [11, 15, 20])

if "Larka" in avatar:
    default_voice = f"Assalam-o-Alaikum Bhaiyo! Ye Mehar Mart ka {product_name} hai, 100 percent khalis, sirf {price} me {offer}, order karo 03452352112"
else:
    default_voice = f"Assalam-o-Alaikum guys! Ye Mehar Mart ka {product_name} hai, 100 percent pure, sirf {price} me {offer}, jaldi order karo!"

voice_text = st.text_area("Voice Text - REAL HUMAN", default_voice, height=90)

def get_ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()

def gen_image(uploaded_file):
    if uploaded_file:
        return Image.open(uploaded_file).convert("RGB")
    try:
        prompt = "beautiful Pakistani girl holding pure honey jar pointing at it, green dress, smiling, realistic, UGC" if "Larki" in avatar else "handsome Pakistani boy white shalwar kameez holding honey jar, smiling, realistic, UGC"
        url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=720&height=1280&model=turbo&nologo=true&seed={random.randint(1,999999)}"
        r = requests.get(url, timeout=20)
        if r.status_code == 200 and len(r.content) > 8000:
            return Image.open(BytesIO(r.content)).convert("RGB")
    except:
        pass
    return Image.new("RGB", (720,1280), "#FFF3E0")

async def gen_voice(text, voice_name):
    import edge_tts
    os.makedirs("voice", exist_ok=True)
    path = "voice/real.mp3"
    await edge_tts.Communicate(text, voice_name, rate="-5%").save(path)
    return path

def gen_voice_sync(text, voice_name):
    try:
        return asyncio.run(gen_voice(text, voice_name))
    except:
        from gtts import gTTS
        path = "voice/backup.mp3"
        gTTS(text=text, lang='ur').save(path)
        return path

def make_animated_video(img, dur, voice_path):
    os.makedirs("ads", exist_ok=True)
    img_path = "ads/input.jpg"
    final_video = "ads/ANIMATED.mp4"
    ffmpeg_exe = get_ffmpeg()
    img.resize((720,1280)).save(img_path, "JPEG", quality=95)
    
    # ANIMATED ZOOM EFFECT - Ab image hilega Bhai!
    # Slow zoom in + slight pan - lagेगा jaise video hai!
    vf_filter = "zoompan=z='if(lte(zoom,1),zoom+0.0015,1.5)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)',scale=720:1280"
    
    if voice_path and os.path.exists(voice_path):
        cmd = [
            ffmpeg_exe, "-y",
            "-loop", "1", "-i", img_path,
            "-i", voice_path,
            "-vf", vf_filter,
            "-c:v", "libx264", "-c:a", "aac",
            "-t", str(dur), "-pix_fmt", "yuv420p",
            "-shortest", final_video
        ]
    else:
        cmd = [ffmpeg_exe,"-y","-loop","1","-i",img_path,"-vf",vf_filter,"-c:v","libx264","-t",str(dur),"-pix_fmt","yuv420p",final_video]
    
    subprocess.run(cmd, capture_output=True, timeout=90)
    return final_video if os.path.exists(final_video) else None

if st.button("🚀 ANIMATED VIDEO BANAO - IMAGE HILEGA", type="primary", use_container_width=True):
    with st.spinner("Image..."):
        img = gen_image(uploaded)
        st.image(img, caption="UGC Photo", use_container_width=True)
    with st.spinner("Real Human Voice..."):
        vp = gen_voice_sync(voice_text, REAL_VOICE[avatar])
        st.audio(vp)
    with st.spinner("Animated Video bana raha - Zoom effect..."):
        vpath = make_animated_video(img, duration, vp)
        if vpath:
            st.success("🔥 ANIMATED VIDEO READY! Ab image zoom hoga - static nahi lagega!")
            st.video(vpath)
            with open(vpath, "rb") as f:
                st.download_button(f"📥 Download ANIMATED - {avatar}", f, file_name=f"ANIMATED_{avatar[:4]}.mp4", mime="video/mp4")

st.divider()
st.markdown("""
### 🤔 Bhai Lipsync wala chahiye - Muh hile?

**V83 me ZOOM animation hai - image hilta hai - Daraz ke liye best hai!**

**Agar bilkul muh hilana hai to:**
1. **CapCut (Free):** Play Store se CapCut > `Talking Photo` > Aapki Larki photo + Ye voice dalo > Lipsync video ban jayega 30 sec me!
2. **HeyGen (Pro):** HeyGen.com > Free credit > Talking Avatar > Real video!

**Aapka ab wala video Daraz ke liye 100% viral hai Bhai - Download karke lagao - sale ayegi!**
""")
