import streamlit as st, os, asyncio, shutil, subprocess
import edge_tts
from gtts import gTTS

try:
    from google.cloud import texttospeech
    GOOGLE_AVAILABLE = True
except:
    GOOGLE_AVAILABLE = False

st.set_page_config(page_title="MEHAR V95 - WORLD STUDIO", layout="centered")
st.title("MEHAR V95 - WORLD STUDIO 🌍")
st.success("V95: SINDHI KHALIS FIX - Asad/Uzma - No Cut - No WSS")

VOICE_CATEGORIES = {
    "🇵🇰 URDU CLEAR - اردو": {
        "10 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "20 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "30 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "50 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "60 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "10 Sal Larka - Asad": "ur-PK-AsadNeural",
        "20 Sal Larka - Asad": "ur-PK-AsadNeural",
        "30 Sal Larka - Asad": "ur-PK-AsadNeural",
        "50 Sal Larka - Asad": "ur-PK-AsadNeural",
        "60 Sal Larka - Asad": "ur-PK-AsadNeural",
    },
    "🇵🇰 SINDHI KHALIS - سنڌي خالص": {
        "10 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "20 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "30 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "50 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "60 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "10 Sal Larka - Asad": "ur-PK-AsadNeural",
        "20 Sal Larka - Asad": "ur-PK-AsadNeural",
        "30 Sal Larka - Asad": "ur-PK-AsadNeural",
        "50 Sal Larka - Asad": "ur-PK-AsadNeural",
        "60 Sal Larka - Asad": "ur-PK-AsadNeural",
    },
    "🇮🇳 HINDI - हिंदी": {
        "10 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "20 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "30 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "50 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "60 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "10 Sal Larka - Asad": "ur-PK-AsadNeural",
        "20 Sal Larka - Asad": "ur-PK-AsadNeural",
        "30 Sal Larka - Asad": "ur-PK-AsadNeural",
        "50 Sal Larka - Asad": "ur-PK-AsadNeural",
        "60 Sal Larka - Asad": "ur-PK-AsadNeural",
    },
}

cat = st.selectbox("📁 CATEGORY:", list(VOICE_CATEGORIES.keys()), index=1)
voices = VOICE_CATEGORIES[cat]
voice_key = st.selectbox(f"{cat} - Asad/Uzma Age:", list(voices.keys()), index=6)
voice_name = voices[voice_key]

st.info(f"SELECTED: {cat} - {voice_key} - {voice_name}")

MAX_SEC = st.selectbox("⏱️ LIMIT:", [15, 30, 60, 120, 600], index=0)
MAX_CHARS = MAX_SEC * 15

TEXTS = {
    "🇵🇰 URDU CLEAR - اردو": "السلام علیکم! میرے پیارے بھائیوں اور بہنوں! مہر مارٹ کا خالص ماکی ایک سو فیصد خالص ہے!",
    "🇵🇰 SINDHI KHALIS - سنڌي خالص": "السلام عليڪم! منهنجا پيارا ڀائرو ۽ ڀينرون! مهر مارٽ جو خالص ماکي هڪ سئو سيڪڙو خالص آهي! صرف اوڻٽيهه سو پنجاهتر روپين ۾! سڄي پاڪستان ۾ فري ڊليوري!",
    "🇮🇳 HINDI - हिंदी": "नमस्ते! मेरे प्यारे भाइयों और बहनों! मेहर मार्ट का शुद्ध शहद सौ प्रतिशत खालिस है!",
}

text_input = st.text_area(f"Text - {cat} - Khalis Pure - No Cut:", value=TEXTS.get(cat, TEXTS["🇵🇰 SINDHI KHALIS - سنڌي خالص"]), height=240, max_chars=MAX_CHARS)
st.progress(min(len(text_input)/MAX_CHARS, 1.0))

rate_opt = st.select_slider("Speed:", options=["-15%", "-10%", "-5%", "+0%", "+10%"], value="-5%")

def clean(t): return t.strip()

def split_no_cut(text, size=350):
    words = text.split(' ')
    parts, cur = [], ""
    for w in words:
        if not w: continue
        if len(cur) + len(w) + 1 <= size:
            cur = cur + " " + w if cur else w
        else:
            if cur: parts.append(cur)
            cur = w
    if cur: parts.append(cur)
    return parts if parts else [text]

async def try_edge(text, voice, rate, path):
    for _ in range(3):
        try:
            await edge_tts.Communicate(text=text, voice=voice, rate=rate).save(path)
            if os.path.exists(path) and os.path.getsize(path) > 500:
                return True
        except:
            await asyncio.sleep(1)
    return False

# SINDHI KHALIS BUG FIX - sd language!
def try_gtts(text, path, category):
    try:
        if "SINDHI" in category:
            lang = 'sd'  # SINDHI KHALIS FIX
        elif "ARABIC" in category:
            lang = 'ar'
        elif "ENGLISH" in category:
            lang = 'en'
        elif "HINDI" in category:
            lang = 'hi'
        else:
            lang = 'ur'
        gTTS(text=text, lang=lang, slow=False).save(path)
        return True
    except Exception as e:
        print(f"GTTS {lang} fail {e}, trying ur")
        try:
            gTTS(text=text, lang='ur', slow=False).save(path)
            return True
        except:
            return False

async def gen(text, voice, rate, category):
    if os.path.exists("voice"): shutil.rmtree("voice")
    os.makedirs("voice", exist_ok=True)
    parts = split_no_cut(text, 350)
    files = []
    bar = st.progress(0)
    for i, p in enumerate(parts):
        p = clean(p)
        if not p: continue
        path = f"voice/{voice.replace('-','_')}_{i}.mp3"
        ok = await try_edge(p, voice, rate, path)
        if not ok:
            ok = try_gtts(p, path, category)
        if ok:
            files.append(path)
        bar.progress((i+1)/len(parts))
    if not files:
        raise Exception("Voice fail")
    final = f"voice/FINAL_SINDHI_KHALIS.mp3"
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

if st.button(f"🎙️ {cat} - {voice_key} - KHALIS BANAO", type="primary", use_container_width=True):
    with st.spinner(f"{cat} - {voice_key} - Khalis..."):
        try:
            path = asyncio.run(gen(text_input, voice_name, rate_opt, cat))
            st.balloons()
            st.success(f"✅ Ready! {cat} - {voice_key} - Sindhi Khalis Pure!")
            st.audio(path)
            with open(path, "rb") as f:
                st.download_button(f"📥 Download {voice_key}", f, file_name=f"{voice_key.replace(' ','_')}_SINDHI_KHALIS.mp3")
        except Exception as e:
            st.error(f"Error: {e}")
