import streamlit as st, os, asyncio, shutil, subprocess, re
import edge_tts

st.set_page_config(page_title="MEHAR V95 - WORLD STUDIO", layout="centered")
st.title("MEHAR V95 - WORLD STUDIO 🌍")

# LANGUAGE CATEGORY - FULL SYSTEM - KUCH MISS NAHI!
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

if "text_value" not in st.session_state:
    st.session_state.text_value = ""

st.markdown("### 🌍 LANGUAGE CATEGORY")
language_cat = st.selectbox("Language Category:", list(VOICE_CATEGORIES.keys()), index=0)
voices = VOICE_CATEGORIES[language_cat]
voice_key = st.selectbox(f"{language_cat} - Voice:", list(voices.keys()), index=2)
voice_name = voices[voice_key]

time_label = st.selectbox("⏱️ TIME CATEGORY:", list(TIME_OPTIONS.keys()), index=2)
MAX_SEC = TIME_OPTIONS[time_label]
MAX_CHARS = MAX_SEC * 14

# PASTE FIX - SINGLE BOX - NO DOUBLE BOX!
st.markdown("### ✍️ TEXT - Paste + Type Dono - Single Box!")
st.info(f"📋 Mobile pe paste: Text box me long press karo - Paste ka option aayega - Paste karo! Max {MAX_CHARS} chars - {MAX_SEC} sec")

# Buttons - Clear + Example - No extra paste box!
c1, c2 = st.columns(2)
with c1:
    if st.button("🗑️ CLEAR TEXT", use_container_width=True):
        st.session_state.text_value = ""
        st.rerun()
with c2:
    if st.button("📄 EXAMPLE LOAD", use_container_width=True):
        examples = {
            "🇵🇰 SINDHI KHALIS - سنڌي": "السلام عليڪم! منهنجا پيارا ڀائرو ۽ ڀينرون! مهر مارٽ جو خالص ماکي هڪ سئو سيڪڙو خالص آهي! صرف ٻه هزار نو سو پنجاهتر روپين ۾! سڄي پاڪستان ۾ فري ڊليوري!",
            "🇵🇰 URDU - اردو": "السلام علیکم! میرے پیارے بھائیو اور بہنو! مہر مارٹ کا خالص شہد سو فیصد خالص ہے! پورے پاکستان میں فری ڈلیوری!",
            "🇮🇳 HINDI - हिन्दी": "मैं जो भी लिखूंगा वही बोलेगा! Delivery All Pakistan - Pakistan ही बोलेगा! Bharat नहीं!",
            "🇬🇧 ENGLISH - US": "Hello! Whatever I type will be spoken exactly! Delivery All Pakistan - Not Bharat!",
            "🇬🇧 ENGLISH - UK": "Hello! Whatever I type will be spoken exactly! Delivery All Pakistan!",
            "🇸🇦 ARABIC - عربي": "السلام عليكم! ما أكتبه سيتم التحدث به!",
        }
        st.session_state.text_value = examples.get(language_cat, examples["🇵🇰 SINDHI KHALIS - سنڌي"])
        st.rerun()

# SINGLE TEXT AREA - Paste fix - No max_chars blocking paste!
# max_chars hataya - Manual check karenge - Mobile pe paste block nahi hoga!
text_input = st.text_area(
    f"Yahan Type Ya Paste Karo - {MAX_SEC} sec - Jo likho wahi bolega:",
    value=st.session_state.text_value,
    placeholder="""Yahan long press karke paste karo - Ya type karo!

Mobile:
1. WhatsApp se copy karo
2. Yahan box me long press karo
3. Paste dabao - Ho jayega!

Jo likho ge wahi bolega - Pakistan likho ge to Pakistan hi!""",
    height=280,
    key="single_main_text"
)

# Manual length check - max_chars param nahi - Is liye paste block nahi!
if len(text_input) > MAX_CHARS:
    st.error(f"⚠️ Zyada lamba hai! {len(text_input)} / {MAX_CHARS} - Thoda kam karo - {len(text_input) - MAX_CHARS} chars zyada!")
else:
    if text_input.strip():
        st.success(f"✅ {len(text_input)} / {MAX_CHARS} chars - {len(text_input)//14} sec / {MAX_SEC} sec - Ready!")

st.progress(min(len(text_input)/MAX_CHARS, 1.0) if text_input else 0)
rate_opt = st.select_slider("Speed:", options=["-5%", "-15%", "+10%"], value="-5%")

def clean_no_auto(text, lang_cat):
    if not text.strip():
        return ""
    t = text.strip()
    if "SINDHI" in lang_cat:
        for sc, tc in PURE_SINDHI_TTS_MAP.items():
            t = t.replace(sc, tc)
        t = t.replace("آهي", "آآہی").replace("آهي", "آآہی").replace("آہی", "آآہی").replace("آہے", "آآہے")
        t = t.replace("سجی", "سجّی")
    return t

def split_no_cut(text, size=1000):
    if len(text) <= size:
        return [text]
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

async def gen_edge(text, voice, rate, path):
    for _ in range(5):
        try:
            if os.path.exists(path):
                os.remove(path)
            await edge_tts.Communicate(text=text, voice=voice, rate=rate).save(path)
            if os.path.exists(path) and os.path.getsize(path) > 800:
                return True
        except:
            await asyncio.sleep(1)
    return False

async def gen_exact(text, voice, rate, lang_cat):
    if not text.strip():
        raise Exception("Khali hai!")
    if len(text) > MAX_CHARS:
        raise Exception(f"Text zyada lamba - {len(text)} > {MAX_CHARS}")
    if os.path.exists("voice"):
        shutil.rmtree("voice")
    os.makedirs("voice", exist_ok=True)
    cleaned = clean_no_auto(text, lang_cat)
    parts = split_no_cut(cleaned, 1000)
    files = []
    for i, p in enumerate(parts):
        p = clean_no_auto(p, lang_cat)
        if not p: continue
        path = f"voice/{voice.replace('-','_')}_{i}.mp3"
        ok = await gen_edge(p, voice, rate, path)
        if ok:
            files.append(path)
    if not files:
        raise Exception("Voice fail")
    final = f"voice/FINAL_{MAX_SEC}s.mp3"
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

if st.button(f"🎙️ {voice_key} - {time_label} - VOICE BANAO", type="primary", use_container_width=True):
    if not text_input.strip():
        st.error("⚠️ Khali hai - Type ya Paste karo!")
    elif len(text_input) > MAX_CHARS:
        st.error(f"⚠️ Zyada lamba - {len(text_input) - MAX_CHARS} chars kam karo!")
    else:
        with st.spinner(f"Bana raha - {len(text_input)} chars..."):
            try:
                path = asyncio.run(gen_exact(text_input, voice_name, rate_opt, language_cat))
                st.balloons()
                st.success(f"✅ Ready! {language_cat} - {MAX_SEC}s!")
                st.audio(path)
                with open(path, "rb") as f:
                    st.download_button("📥 Download Voice", f, file_name=f"Voice_{MAX_SEC}s.mp3")
            except Exception as e:
                st.error(f"Error: {e}")

st.divider()
st.caption("V95 - Paste Bug Fixed - Single Box - Mobile pe long press paste - System same - 6 Languages - Hindi Pakistan bug fixed - Jo likho wahi bolega!")
