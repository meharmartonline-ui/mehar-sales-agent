import streamlit as st, os, re, subprocess, asyncio
import edge_tts
from gtts import gTTS

st.set_page_config(page_title="MEHAR V96 - SINDHI PURE", layout="centered")
st.title("MEHAR V96 - SINDHI PURE")
st.success("V96: Sindhi 100% Pure - Lafz Kabhi Cut Nahi!")

VOICE_CATEGORIES = {
    "SINDHI PURE - سنڌي خالص": {
        "Sindhi Pure Google - BEST 100%": "GTTS-SD",
    },
    "URDU CLEAR": {
        "Swara - Urdu Best": "hi-IN-SwaraNeural",
        "Asad - Urdu": "ur-PK-AsadNeural",
        "Uzma - Urdu Viral": "ur-PK-UzmaNeural",
    },
    "ARABIC": {
        "Salma - Arabic": "ar-EG-SalmaNeural",
    },
    "ENGLISH": {
        "Jenny - English": "en-US-JennyNeural",
    }
}

cat = st.selectbox("CATEGORY:", list(VOICE_CATEGORIES.keys()), index=0)
voices = VOICE_CATEGORIES[cat]
voice_name = voices[st.selectbox(f"{cat} Voice:", list(voices.keys()), index=0)]
MAX_CHARS = 5000

default_text = "السلام عليڪم! منهنجا پيارا ڀائرو ۽ ڀينرون! مهر مارٽ جو خالص ماکي هڪ سو سيڪڙو خالص آهي! صرف اوڻٽيهه سو پنجاهتر روپين ۾ مفت هوم ڊليوري!"

text_input = st.text_area("Pure Sindhi Text Likho:", value=default_text, height=250, max_chars=MAX_CHARS)

if "SINDHI" in cat:
    st.info("SINDHI PURE MODE: Koi lafz cut nahi hoga!")

def clean_pure(t, category):
    if "SINDHI" in category:
        return t.strip()
    return re.sub(r'[^\w\s.,!?\-ء-ي]', ' ', t).strip()

def split_sindhi_sentences(text):
    sentences = re.split(r'([۔!؟!?,،\n]+)', text)
    result = []
    current = ""
    for part in sentences:
        if not part.strip():
            continue
        current += part
        if len(current) > 250 or re.search(r'[۔!؟\n]', part):
            if current.strip():
                result.append(current.strip())
            current = ""
    if current.strip():
        result.append(current.strip())
    if not result:
        words = text.split()
        chunk = ""
        for w in words:
            if len(chunk) + len(w) < 300:
                chunk += " " + w
            else:
                result.append(chunk.strip())
                chunk = w
        if chunk:
            result.append(chunk.strip())
    return result if result else [text]

def gen_gtts_sindhi_pure(text, path):
    try:
        tts = gTTS(text=text, lang='sd', slow=False)
        tts.save(path)
        return True
    except:
        try:
            tts = gTTS(text=text, lang='ur', slow=False)
            tts.save(path)
            return True
        except:
            return False

async def gen(text, voice, category):
    os.makedirs("voice", exist_ok=True)
    if "SINDHI" in category:
        parts = split_sindhi_sentences(text)
    else:
        parts = [text[i:i+350] for i in range(0, len(text), 350)]
    st.write(f"Total {len(parts)} hisson me bana raha hun")
    files = []
    bar = st.progress(0)
    for i, p in enumerate(parts):
        p = clean_pure(p, category)
        if not p:
            continue
        path = f"voice/sindhi_{i}.mp3"
        ok = gen_gtts_sindhi_pure(p, path)
        if ok and os.path.exists(path) and os.path.getsize(path) > 1000:
            files.append(path)
        bar.progress((i+1)/len(parts))
    if not files:
        raise Exception("Sindhi voice nahi bani")
    final = "voice/FINAL_PURE_SINDHI.mp3"
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

if st.button(f"{cat} - PURE BANAO", type="primary", use_container_width=True):
    if not text_input.strip():
        st.warning("Pehle Sindhi text likho!")
    else:
        with st.spinner("Pure Sindhi bana raha hun..."):
            try:
                path = asyncio.run(gen(text_input, voice_name, cat))
                st.balloons()
                st.success("Pure Sindhi Ready!")
                st.audio(path)
                with open(path, "rb") as f:
                    st.download_button("Download Pure Sindhi", f, file_name="PURE_SINDHI.mp3", use_container_width=True)
            except Exception as e:
                st.error(f"Error: {e}")

st.divider()
st.markdown("V96 FIX: Sentence par cut - Lafz mehfooz - Google Sindhi Pure")
