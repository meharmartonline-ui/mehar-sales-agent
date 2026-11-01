import streamlit as st, os, asyncio, shutil, subprocess, re
from dotenv import load_dotenv
load_dotenv()
import edge_tts

# === GROQ SETTING - KEYS ===
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
try:
    from groq import Groq
    groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
except:
    groq_client = None

st.set_page_config(page_title="MEHAR V95 - WORLD STUDIO", layout="centered")

# Red line off
st.markdown("""
<style>textarea{spellcheck:false !important}</style>
<script>setInterval(()=>{document.querySelectorAll('textarea').forEach(t=>t.setAttribute('spellcheck','false'))},500);</script>
""", unsafe_allow_html=True)

st.title("MEHAR V95 - WORLD STUDIO 🌍")

if not GROQ_API_KEY:
    st.warning("⚠️ GROQ_API_KEY nahi mila - .env me dalo ya Streamlit Secrets me - Bina Groq ke bhi chalega - Edge TTS se!")
else:
    st.success(f"✅ Groq Connected - Key: {GROQ_API_KEY[:10]}... - Auto Convert All Ready!")

st.success("V95 FINAL: Dynamic - Jo Type Karo Wohi Voice! + Groq Auto Convert!")

VOICE_CATEGORIES = {
    "🇵🇰 SINDHI KHALIS - سنڌي": {
        "10 Sal Larka - Asad": "ur-PK-AsadNeural",
        "20 Sal Larka - Asad": "ur-PK-AsadNeural",
        "30 Sal Larka - Asad": "ur-PK-AsadNeural",
        "50 Sal Larka - Asad": "ur-PK-AsadNeural",
        "60 Sal Larka - Asad": "ur-PK-AsadNeural",
        "10 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "20 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "30 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "50 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "60 Sal Larki - Uzma": "ur-PK-UzmaNeural",
    },
    "🇵🇰 URDU - اردو": {
        "20 Sal Larka - Asad": "ur-PK-AsadNeural",
        "30 Sal Larka - Asad": "ur-PK-AsadNeural",
        "20 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "30 Sal Larki - Uzma": "ur-PK-UzmaNeural",
    },
    "🇮🇳 HINDI - हिन्दी": {
        "20 Sal Larka - Madhur": "hi-IN-MadhurNeural",
        "30 Sal Larka - Madhur": "hi-IN-MadhurNeural",
        "20 Sal Larki - Swara": "hi-IN-SwaraNeural",
        "30 Sal Larki - Swara": "hi-IN-SwaraNeural",
    },
    "🇬🇧 ENGLISH - US": {
        "20 Sal Larka - Guy": "en-US-GuyNeural",
        "20 Sal Larki - Jenny": "en-US-JennyNeural",
        "20 Sal Larki - Aria": "en-US-AriaNeural",
    },
    "🇬🇧 ENGLISH - UK": {
        "20 Sal Larka - Ryan": "en-GB-RyanNeural",
        "20 Sal Larki - Sonia": "en-GB-SoniaNeural",
    },
    "🇸🇦 ARABIC - عربي": {
        "20 Sal Larka - Hamed": "ar-SA-HamedNeural",
        "20 Sal Larki - Zariyah": "ar-SA-ZariyahNeural",
    },
}

TIME_OPTIONS = {
    "15 Second": 15, "20 Second": 20, "30 Second": 30, "60 Second (1 Minute)": 60,
    "2 Minutes": 120, "3 Minutes": 180, "4 Minutes": 240, "5 Minutes": 300,
    "6 Minutes": 360, "7 Minutes": 420, "8 Minutes": 480, "9 Minutes": 540, "10 Minutes": 600,
}

PURE_SINDHI_TTS_MAP = {
    "ٻ":"ب","ڄ":"ج","ڃ":"نج","ڇ":"چھ","ٽ":"ٹ","ٺ":"ٹھ","ٿ":"تھ",
    "ڌ":"دھ","ڏ":"ڈ","ڊ":"ڈ","ڍ":"ڈھ","ڀ":"بھ","ڦ":"پھ","ڪ":"ک",
    "ڳ":"گ","ڱ":"نگ","ڻ":"ن","ڙ":"ڑ","ھ":"ہ",
}

# === GROQ AUTO CONVERT ALL 5 LANGUAGE ===
def groq_convert(text, target_lang):
    if not groq_client or not text.strip():
        return text
    prompt = f"Translate this text to {target_lang}. Keep 'Pakistan' as 'Pakistan' always, never translate to Bharat. Only give translated text, no explanation. Text: {text}"
    try:
        chat = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role":"user","content":prompt}],
            temperature=0.1,
            max_tokens=2000
        )
        return chat.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Groq Error: {e}")
        return text

st.markdown("### 🌍 LANGUAGE CATEGORY")
language_cat = st.selectbox("Language Category:", list(VOICE_CATEGORIES.keys()), index=0)
voices = VOICE_CATEGORIES[language_cat]
voice_key = st.selectbox(f"{language_cat} - Age 10-60:", list(voices.keys()), index=2)
voice_name = voices[voice_key]

time_label = st.selectbox("⏱️ TIME CATEGORY:", list(TIME_OPTIONS.keys()), index=2)
MAX_SEC = TIME_OPTIONS[time_label]
MAX_CHARS = MAX_SEC * 14

use_groq = st.checkbox("🔄 Groq Auto Convert All Language ON (Sindhi Urdu Hindi English Arabic)", value=False if not groq_client else True)

if "main_text" not in st.session_state:
    st.session_state.main_text = ""
if "last_lang" not in st.session_state:
    st.session_state.last_lang = language_cat

# Auto convert on change if Groq ON
if use_groq and st.session_state.main_text.strip() and language_cat != st.session_state.last_lang:
    with st.spinner(f"Groq {st.session_state.last_lang} -> {language_cat}..."):
        st.session_state.main_text = groq_convert(st.session_state.main_text, language_cat)
st.session_state.last_lang = language_cat

st.markdown("### ✍️ YAHAN JO BHI TYPE KARO GE - WOHI VOICE BANEGA!")

col1, col2 = st.columns(2)
with col1:
    if st.button("🗑️ CLEAR", use_container_width=True):
        st.session_state.main_text = ""
        st.rerun()
with col2:
    if st.button("🔄 Groq Convert Now", type="primary", use_container_width=True, disabled=not groq_client):
        st.session_state.main_text = groq_convert(st.session_state.main_text, language_cat)
        st.rerun()

text_input = st.text_area(
    f"✍️ Yahan text likho ({MAX_CHARS} max) - {language_cat}:",
    value=st.session_state.main_text,
    placeholder="Sindhi: السلام عليڪم! منهنجا پيارا ڀائرو...\nUrdu: السلام علیکم! میرے پیارے بھائیو...\nHindi: नमस्ते! मैं जो भी लिखूंगा...\nEnglish: Hello! Whatever I type...",
    height=260,
    max_chars=MAX_CHARS,
    key="main_input"
)

if text_input != st.session_state.main_text:
    st.session_state.main_text = text_input

if not text_input.strip():
    st.warning("⚠️ Khali hai - Kuch likho!")
else:
    st.success(f"✅ {len(text_input)} chars - Ready!")

st.progress(min(len(text_input)/MAX_CHARS, 1.0) if text_input else 0)
rate_opt = st.select_slider("Speed:", options=["-5%", "-15%", "+10%"], value="-5%")

def clean_dynamic_any_text(text, lang_cat):
    if not text.strip(): return ""
    t = text.strip()
    # Pakistan protect - Bharat bug fix
    t = t.replace("पाकिस्तान", "Pakistan").replace("پاڪستان", "Pakistan").replace("پاکستان", "Pakistan")
    if "SINDHI" in lang_cat:
        for sc, tc in PURE_SINDHI_TTS_MAP.items():
            t = t.replace(sc, tc)
        t = t.replace("آهي", "آآہی ").replace("آهي", "آآہی ").replace("آہی", "آآہی ")
        t = t.replace("سجي", "سجّی").replace("عليکم", "علیکم")
        t = t.replace("100%", "سئو سيڪڙو")
        t = re.sub(r'\b2975\b', "بہ ہزار نو سو پنجاہتر", t)
    return t

def split_no_cut(text, size=1000):
    if len(text) <= size: return [text]
    words = text.split(' ')
    parts, cur = [], ""
    for w in words:
        if not w: continue
        if len(cur) + len(w) + 1 <= size: cur = cur + " " + w if cur else w
        else:
            if cur: parts.append(cur)
            cur = w
    if cur: parts.append(cur)
    return parts if parts else [text]

async def gen_edge(text, voice, rate, path):
    for _ in range(5):
        try:
            if os.path.exists(path): os.remove(path)
            await edge_tts.Communicate(text=text, voice=voice, rate=rate).save(path)
            if os.path.exists(path) and os.path.getsize(path) > 800: return True
        except: await asyncio.sleep(1)
    return False

async def gen_dynamic(text, voice, rate, lang_cat):
    if not text.strip(): raise Exception("Khali hai!")
    if os.path.exists("voice"): shutil.rmtree("voice")
    os.makedirs("voice", exist_ok=True)
    cleaned = clean_dynamic_any_text(text, lang_cat)
    parts = split_no_cut(cleaned, 1000)
    files = []
    for i, p in enumerate(parts):
        p = clean_dynamic_any_text(p, lang_cat)
        if not p: continue
        path = f"voice/{voice.replace('-','_')}_{i}.mp3"
        ok = await gen_edge(p, voice, rate, path)
        if ok: files.append(path)
    if not files: raise Exception("Voice fail")
    final = f"voice/FINAL_{MAX_SEC}s.mp3"
    try:
        import imageio_ffmpeg
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        with open("voice/list.txt","w", encoding="utf-8") as f:
            for fp in files: f.write(f"file '{os.path.abspath(fp)}'\n")
        subprocess.run([ffmpeg,"-y","-f","concat","-safe","0","-i","voice/list.txt","-c","copy",final], check=True, capture_output=True)
    except: final = files[0]
    return final

if st.button(f"🎙️ {language_cat} - {voice_key} - Voice Banao", type="primary", use_container_width=True):
    if not text_input.strip():
        st.error("⚠️ Pehle kuch likho!")
    else:
        with st.spinner(f"{voice_key} bana raha..."):
            try:
                path = asyncio.run(gen_dynamic(text_input, voice_name, rate_opt, language_cat))
                st.balloons()
                st.success(f"✅ Ready! {language_cat} - {len(text_input)} chars!")
                st.audio(path)
                with open(path, "rb") as f:
                    st.download_button(f"📥 Download", f, file_name=f"Voice_{MAX_SEC}s.mp3")
            except Exception as e: st.error(f"Error: {e}")

st.divider()
st.caption("V95 + Groq - Requirements + .env + app.py - 3 file - Full system!")
