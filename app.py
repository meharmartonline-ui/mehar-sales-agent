import streamlit as st
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os, math, random, time

st.set_page_config(page_title="MEHAR UGC V75 DUAL", layout="centered")
st.title("MEHAR UGC V75 - DUAL ENGINE 🔥")
st.success("Fix: Pollinations busy ho to bhi UGC banega - Rukega nahi!")

avatar = st.radio(
    "1️⃣ Kaun dikhega? Select karo",
    ["👩 Larki - Young Girl", "👦 Larka - Young Boy", "👶 Baby", "👩‍👧 Ammi with Baby", "👳‍♂️ Bearded Bhai", "👨‍⚕️ Doctor", "👵 Village Amma"],
    index=0
)

prompts = {
    "👩 Larki - Young Girl": "beautiful young Pakistani girl 22 years green dress holding honey jar pointing smiling home UGC realistic",
    "👦 Larka - Young Boy": "young Pakistani boy 24 white shalwar kameez holding honey jar smiling home UGC",
    "👶 Baby": "cute Pakistani baby with honey jar mother hands home UGC",
    "👩‍👧 Ammi with Baby": "Pakistani mother 30 with baby holding honey jar home UGC",
    "👳‍♂️ Bearded Bhai": "Pakistani bearded man 28 white cap holding honey jar UGC",
    "👨‍⚕️ Doctor": "Pakistani doctor white coat holding honey jar UGC",
    "👵 Village Amma": "old Pakistani woman 50 traditional dress holding honey jar UGC"
}

st.divider()
product_name = st.text_input("Product Name", "Pure Honey 100% Natural")
price = st.text_input("Price", "2975")
offer = st.text_input("Offer", "15% OFF - Free Delivery")
duration = st.selectbox("Duration", [15, 20, 30])
fmt = st.selectbox("Format", ["Instagram Story 9:16", "TikTok 9:16", "FB 1:1"])
voice_text = st.text_area("Voice Text", f"Assalam-o-Alaikum guys! Maine Mehar Mart ka {product_name} liya, 100 percent pure, sirf {price} me {offer}!", height=80)

def create_fallback_ugc_image(avatar_text, product_name):
    # Agar AI image fail ho to ye beautiful UGC card bana dega - taake video rukey nahi
    W, H = 720, 1280
    img = Image.new("RGB", (W, H), "#FFF8E1")
    draw = ImageDraw.Draw(img)
    # Avatar emoji big
    draw.rectangle([0, 0, W, 250], fill="#FF6A00")
    draw.text((W//2, 125), "MEHAR MART", fill="white", anchor="mm", font=ImageFont.load_default())
    draw.rectangle([50, 300, W-50, 800], fill="white", outline="#FF6A00", width=4)
    draw.text((W//2, 400), "🍯", fill="black", anchor="mm", font=ImageFont.load_default())
    draw.text((W//2, 550), product_name[:30], fill="#111", anchor="mm", font=ImageFont.load_default())
    draw.text((W//2, 650), f"Rs. {price}", fill="#FF6A00", anchor="mm", font=ImageFont.load_default())
    draw.text((W//2, 720), offer, fill="#0D47A1", anchor="mm", font=ImageFont.load_default())
    draw.text((W//2, 900), avatar_text, fill="#333", anchor="mm", font=ImageFont.load_default())
    draw.text((W//2, 1000), "100% Pure - Original", fill="#4CAF50", anchor="mm", font=ImageFont.load_default())
    draw.text((W//2, 1100), "03452352112", fill="black", anchor="mm", font=ImageFont.load_default())
    return img

def gen_image_dual(prompt, avatar_text, product_name):
    # 1st try: Pollinations TURBO (fast)
    engines = [
        f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=720&height=1280&model=turbo&nologo=true&seed={random.randint(1,9999999)}",
        f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=720&height=1280&model=flux&nologo=true&seed={random.randint(1,9999999)}"
    ]
    for url in engines:
        try:
            st.caption(f"Trying: {url[:80]}...")
            r = requests.get(url, timeout=60)
            if r.status_code == 200 and len(r.content) > 8000:
                return Image.open(BytesIO(r.content)).convert("RGB")
        except:
            time.sleep(1)
            continue
    # Fallback - khud ka UGC card
    st.warning("AI server busy hai Bhai, ab local UGC card bana raha hun - video to banega!")
    return create_fallback_ugc_image(avatar_text, product_name)

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

def make_video(img, dur, fmt, voice_path):
    W, H = (720, 1280) if "9:16" in fmt else (720, 720)
    import imageio
    img = img.resize((W, H))
    frames = [img for _ in range(dur * 24)]
    os.makedirs("ads", exist_ok=True)
    temp = f"ads/temp_{dur}.mp4"
    final = f"ads/final_{dur}.mp4"
    imageio.mimsave(temp, [f for f in frames], fps=24, macro_block_size=1)
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
        except:
            return temp
    return temp

if st.button("🚀 UGC BANAO - DUAL ENGINE", type="primary", use_container_width=True):
    full_prompt = f"{prompts[avatar]}, {product_name}, PURE HONEY jar, 4k realistic"
    st.info(f"Selected: {avatar}")

    with st.spinner(f"{avatar} ki image bana raha hai..."):
        img = gen_image_dual(full_prompt, avatar, product_name)
        st.image(img, caption=f"UGC - {avatar}", use_container_width=True)
        st.success("Image Ready!")

    with st.spinner("Voice bana raha..."):
        vp = gen_voice(voice_text)
        if vp:
            st.audio(vp)

    with st.spinner("Video bana raha..."):
        vpath = make_video(img, duration, fmt, vp)
        st.success("🔥 UGC Video Ready Bhai!")
        st.video(vpath)
        with open(vpath, "rb") as f:
            st.download_button("📥 Download UGC Video", f, file_name=f"UGC_{duration}s.mp4")
