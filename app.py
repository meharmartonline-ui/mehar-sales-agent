import streamlit as st, os, re, subprocess, asyncio, shutil
import edge_tts
from gtts import gTTS

st.set_page_config(page_title="MEHAR V95 - WORLD STUDIO", layout="centered")
st.title("MEHAR V95 - WORLD STUDIO")
st.success("V98 FIXED: Syntax Error Fix - Larka Larki Age Change!")

VOICE_CATEGORIES = {
    "URDU CLEAR": {
        "20 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "20 Sal Larka - Asad": "ur-PK-AsadNeural",
        "30 Sal Larki - Ayesha": "ur-PK-AyeshaNeural",
        "20 Sal Larki - Swara": "hi-IN-SwaraNeural",
    },
    "SINDHI KHALIS": {
        "20 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "20 Sal Larka - Asad": "ur-PK-AsadNeural",
        "30 Sal Larki - Ayesha": "ur-PK-AyeshaNeural",
        "20 Sal Larki - Swara": "hi-IN-SwaraNeural",
    },
    "ENGLISH CLEAR": {
        "20 Sal Larki - Jenny": "en-US-JennyNeural",
        "20 Sal Larka - Guy": "en-US-GuyNeural",
        "20 Sal Larki - Aria": "en-US-AriaNeural",
        "30 Sal Larka - Davis": "en-US-DavisNeural",
    },
    "ARABIC": {
        "20 Sal Larki - Salma": "ar-EG-SalmaNeural",
        "20 Sal Larka - Shakir": "ar-EG-ShakirNeural",
        "30 Sal Larki - Zariyah": "ar-SA-ZariyahNeural",
        "30 Sal Larka - Hamed": "ar-SA-HamedNeural",
    },
}

cat = st.selectbox("CATEGORY:", list(VOICE_CATEGORIES.keys()), index=0)
voices = VOICE_CATEGORIES[cat]
voice_key = st.selectbox(f"{cat} - LARKA LARKI Age:", list(voices.keys()), index=0)
voice_name = voices[voice_key]

st.info(f"SELECTED: {voice_key} -> {voice_name}")

limit_options = {"15 Sec":15, "30 Sec":30, "1 Min":60, "2 Min":120, "10 Min FULL":600}
MAX_SEC = limit_options[st.selectbox("LIMIT:", list(limit_options.keys()), index=2)]
MAX_CHARS = MAX_SEC * 13

TEXTS = {
    "URDU CLEAR": "Assalam-o-Alaikum! Mere pyare bhaiyon aur behno, Mehar Mart ka Pure Honey khalis hai!",
    "SINDHI KHALIS": "Assalam-o-Alaikum! Mehar Mart jo makhi khalis aahe!",
    "ENGLISH CLEAR": "Hello friends! Mehar Mart honey is pure!",
    "ARABIC": "Assalam-o-Alaikum! Asal Mehar Mart naqi!",
}

default_text = TEXTS.get(cat, TEXTS["URDU CLEAR"])
if MAX_SEC >= 120:
    default_text = (default_text + " ") * 20

text_input = st.text_area(f"Text ({MAX_CHARS} max):", value=default_text, height=180, max_chars=MAX_CHARS)
st.progress(min(len(text_input)/MAX_CHARS, 1.0))

rate_opt = st.select_slider("Speed:", options=["-15%", "-10%", "-5%", "+0%", "+10%"], value="-5%")

def clean(t):
    return t.strip()

def split_no_cut(text, size=280):
    words = text.split()
    parts = []
    cur = ""
    for w in words:
        if len(cur) + len(w) + 1 <= size:
            cur = cur + " " + w if cur else w
        else:
            if cur:
                parts.append(cur)
            cur = w
    if cur:
        parts.append(cur)
    return parts if parts else [text]

async def gen_edge(text, voice, rate, path):
    for attempt in range(4):
        try:
            if os.path.exists(path):
                os.remove(path)
            await edge_tts.Communicate(text=text, voice=voice, rate=rate).save(path)
            if os.path.exists(path) and os.path.getsize(path) > 800:
                return True
        except Exception as e:
            print(f"Attempt {attempt} fail: {e}")
            await asyncio.sleep(1)
    return False

async def gen(text, voice, rate, category):
    if os.path.exists("voice"):
        shutil.rmtree("voice")
    os.makedirs("voice", exist_ok=True)
    parts = split_no_cut(text, 280)
    files = []
    bar = st.progress(0)
    for i, p in enumerate(parts):
        p = clean(p)
        if not p:
            continue
        safe_voice = voice.replace("-", "_")
        path = f"voice/{safe_voice}_{i}.mp3"
        ok = await gen_edge(p, voice, rate, path)
        if not ok:
            try:
                lang = 'ar' if 'ARABIC' in category else 'en' if 'ENGLISH' in category else 'ur'
                gTTS(text=p, lang=lang, slow=False).save(path)
                ok = True
            except:
                ok = False
        if ok and os.path.exists(path):
            files.append(path)
        bar.progress((i+1)/len(parts))
    if not files:
        raise Exception(f"{voice} se voice nahi bani")
    final = f"voice/FINAL_{safe_voice}.mp3"
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

if st.button(f"BANAO - {voice_key}", type="primary", use_container_width=True):
    with st.spinner(f"{voice_key} - {voice_name} bana raha hun..."):
        try:
            path = asyncio.run(gen(text_input, voice_name, rate_opt, cat))
            st.balloons()
            st.success(f"Ready! {voice_key} - {voice_name}")
            st.audio(path)
            with open(path, "rb") as f:
                st.download_button(f"Download {voice_key}", f, file_name=f"{voice_key}_{MAX_SEC}.mp3")
        except Exception as e:
            st.error(f"Error: {e}")

st.divider()
st.markdown("V98 FINAL - Syntax Fix - Larka Larki Age Change - Khalis No Cut")
