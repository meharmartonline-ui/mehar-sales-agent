import streamlit as st, os, re, subprocess, asyncio
from gtts import gTTS
import edge_tts

st.set_page_config(page_title="MEHAR V100 - LARKA LARKI", layout="centered")
st.title("MEHAR V100 - LARKA + LARKI KHALIS")
st.success("V100: Har Language me Larka + Larki - Dono Awaz!")

VOICE_CATEGORIES = {
    "🇵🇰 SINDHI - سنڌي": {
        "👩 LARKI - Uzma - Aurat": "ur-PK-UzmaNeural",
        "👦 LARKA - Asad - Mard": "ur-PK-AsadNeural",
    },
    "🇵🇰 URDU - اردو": {
        "👩 LARKI - Uzma - Aurat Viral": "ur-PK-UzmaNeural",
        "👦 LARKA - Asad - Mard Best": "ur-PK-AsadNeural",
    },
    "🇸🇦 ARABIC - عربي": {
        "👩 LARKI - Salma - Aurat": "ar-EG-SalmaNeural",
        "👦 LARKA - Shakir - Mard": "ar-EG-ShakirNeural",
    },
    "🇺🇸 ENGLISH - Clear": {
        "👩 LARKI - Jenny - Aurat Best": "en-US-JennyNeural",
        "👦 LARKA - Guy - Mard Best": "en-US-GuyNeural",
    },
    "🇮🇳 HINDI": {
        "👩 LARKI - Swara - Aurat": "hi-IN-SwaraNeural",
        "👦 LARKA - Madhur - Mard": "hi-IN-MadhurNeural",
    },
}

cat = st.selectbox("CATEGORY:", list(VOICE_CATEGORIES.keys()), index=0)
voices = VOICE_CATEGORIES[cat]
voice_key = st.selectbox(f"{cat} - LARKA / LARKI SELECT KARO:", list(voices.keys()), index=0)
voice_name = voices[voice_key]

MAX_SEC = 600
DEFAULT_TEXTS = {
    "🇵🇰 SINDHI - سنڌي": "السلام عليڪم! منهنجا پيارا ڀائرو ۽ ڀينرون! مهر مارٽ جو ماکي خالص آهي!",
    "🇵🇰 URDU - اردو": "السلام علیکم! میرے پیارے بھائیوں اور بہنوں! مہر مارٹ کا شہد خالص ہے!",
    "🇸🇦 ARABIC - عربي": "السلام عليكم! عسل مهر مارت نقي!",
    "🇺🇸 ENGLISH - Clear": "Hello friends! Mehar Mart honey is pure!",
    "🇮🇳 HINDI": "Namaste! Mehar Mart honey pure hai!",
}

text_input = st.text_area("Text:", value=DEFAULT_TEXTS.get(cat, "Hello"), height=200)
rate_opt = "+0%"

def clean(t, cat=""):
    if "SINDHI" in cat or "URDU" in cat or "ARABIC" in cat:
        return t.strip()
    return re.sub(r'[^\w\s.,!?\-ء-ي]', ' ', t).strip()

def split_sent(text):
    parts = re.split(r'([۔!؟.!?\n]+)', text)
    res = []
    cur = ""
    for p in parts:
        cur += p
        if len(cur) > 250 or re.search(r'[۔!؟.!?\n]', p):
            if cur.strip():
                res.append(cur.strip())
            cur = ""
    if cur.strip():
        res.append(cur.strip())
    return res if res else [text]

async def gen_edge(text, voice, rate, path):
    for _ in range(3):
        try:
            await edge_tts.Communicate(text=text, voice=voice, rate=rate).save(path)
            return True
        except:
            await asyncio.sleep(0.5)
    return False

async def gen(text, voice, rate, category):
    os.makedirs("voice", exist_ok=True)
    parts = split_sent(text)
    files = []
    bar = st.progress(0)
    for i, p in enumerate(parts):
        p = clean(p, category)
        if not p:
            continue
        path = f"voice/v_{i}.mp3"
        await gen_edge(p, voice, rate, path)
        if os.path.exists(path):
            files.append(path)
        bar.progress((i+1)/len(parts))
    final = "voice/FINAL.mp3"
    try:
        import imageio_ffmpeg
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        with open("voice/list.txt","w", encoding="utf-8") as f:
            for fp in files:
                f.write(f"file '{os.path.abspath(fp)}'\n")
        subprocess.run([ffmpeg,"-y","-f","concat","-safe","0","-i","voice/list.txt","-c","copy",final], check=True, capture_output=True)
    except:
        final = files[0]
    return final

if st.button(f"🎙️ {voice_key} - BANAO", type="primary", use_container_width=True):
    with st.spinner(f"{voice_key} ki awaz bana raha hun..."):
        path = asyncio.run(gen(text_input, voice_name, rate_opt, cat))
        st.balloons()
        st.success(f"Ready! {voice_key}")
        st.audio(path)
        with open(path, "rb") as f:
            st.download_button("📥 Download", f, file_name=f"{cat}_{voice_key}.mp3")

st.divider()
st.markdown("**LARKA / LARKI Dono:**")
st.markdown("SINDHI: Uzma = Larki, Asad = Larka")
st.markdown("URDU: Uzma = Larki, Asad = Larka")
st.markdown("ARABIC: Salma = Larki, Shakir = Larka")
st.markdown("ENGLISH: Jenny = Larki, Guy = Larka")
