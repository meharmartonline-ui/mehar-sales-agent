import streamlit as st, os, asyncio, shutil, subprocess
import edge_tts

st.set_page_config(page_title="MEHAR V101 STABLE - V95", layout="centered")
st.title("MEHAR V101 STABLE - V95 WAPAS 🌍")
st.success("V101 STABLE: V95 System - Category Fix - Alfabet Fix - Voice Fix - Sab Stable!")

# === V95 FULL SYSTEM - ASAD UZMA 10-60 SAL - KABHI GAYAB NAHI HOGA ===
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

# === ALFABET CHECK 100% - SINDHI 52 HARF -> URDU TTS KE LIYE ===
# Display ke liye original rahega - TTS ke liye ye map use hoga - Voice bug fix!
SINDHI_TO_URDU_TTS = {
    "ٻ":"ب", "ڄ":"ج", "ڃ":"نج", "ڇ":"چھ", "ٽ":"ٹ", "ٺ":"ٹھ", "ٿ":"تھ",
    "ڌ":"دھ", "ڏ":"ڈ", "ڊ":"ڈ", "ڍ":"ڈھ", "ڀ":"بھ", "ڦ":"پھ", "ڪ":"ک",
    "ڳ":"گ", "ڱ":"نگ", "ڻ":"ن", "ڙ":"ڑ", "ھ":"ہ", "۽":"اور"
}

# === VOICE BUG FIX - JO LIKHO WAHI BOLEGA - PAKISTAN -> PAKISTAN - NO BHARAT ===
def clean_for_voice(text, lang_cat):
    if not text.strip():
        return ""
    t = text.strip()
    # Pakistan, Delivery, Mehar Mart - Kabhi change nahi - Har language me Pakistan hi!
    # Koi Bharat, Namaste auto nahi!
    
    if "SINDHI" in lang_cat:
        # Sindhi 52 Harf -> Urdu for TTS - Lamba Aahe fix
        for s,u in SINDHI_TO_URDU_TTS.items():
            t = t.replace(s, u)
        t = t.replace("آهي", "آآہی").replace("آهي", "آآہی").replace("آہی", "آآہی").replace("آہے", "آآہے")
        t = t.replace("سجی", "سجّی").replace("عليکم","علیکم").replace("عليڪم","علیکم")
    # Urdu, Hindi, English, Arabic - Koi auto change nahi - Jo likha wahi!
    # Hindi me Pakistan likha to Pakistan hi bolega - Bharat nahi!
    # English me jo likha wahi!
    return t

def split_text(text, size=900):
    if len(text) <= size:
        return [text]
    words = text.split(' ')
    parts, cur = [], ""
    for w in words:
        if not w:
            continue
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
    for _ in range(5):
        try:
            if os.path.exists(path):
                os.remove(path)
            await edge_tts.Communicate(text=text, voice=voice, rate=rate).save(path)
            if os.path.exists(path) and os.path.getsize(path) > 800:
                return True
        except Exception as e:
            await asyncio.sleep(0.5)
    return False

async def gen_voice_final(text, voice, rate, lang_cat, max_sec):
    if not text.strip():
        raise Exception("Text khali hai!")
    if len(text) > max_sec*14:
        raise Exception(f"Text zyada lamba - {len(text)} > {max_sec*14}")
    if os.path.exists("voice"):
        shutil.rmtree("voice")
    os.makedirs("voice", exist_ok=True)
    cleaned = clean_for_voice(text, lang_cat)
    parts = split_text(cleaned, 900)
    files = []
    for i, p in enumerate(parts):
        p = clean_for_voice(p, lang_cat)
        if not p.strip():
            continue
        path = f"voice/{voice.replace('-','_')}_{i}.mp3"
        ok = await gen_edge(p, voice, rate, path)
        if ok:
            files.append(path)
    if not files:
        raise Exception("Voice fail - Text check karo!")
    final = f"voice/FINAL_{max_sec}s.mp3"
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

# SESSION - STABLE
if "main_text" not in st.session_state:
    st.session_state.main_text = ""

st.markdown("### 🌍 LANGUAGE CATEGORY - V95 Wapas - Stable")
language_cat = st.selectbox("Language Category:", list(VOICE_CATEGORIES.keys()), index=0)
voices = VOICE_CATEGORIES[language_cat]
voice_key = st.selectbox(f"{language_cat} - Voice - Asad Uzma 10-60 Sal:", list(voices.keys()), index=0)
voice_name = voices[voice_key]

time_label = st.selectbox("⏱️ TIME CATEGORY:", list(TIME_OPTIONS.keys()), index=3)
MAX_SEC = TIME_OPTIONS[time_label]
MAX_CHARS = MAX_SEC * 14

st.info(f"SELECTED: {language_cat} - {voice_key} - {time_label} - Jo likho ge wahi bolega!")

# BUTTONS - STABLE - PASTE FIX
c1, c2, c3 = st.columns(3)
with c1:
    if st.button("🗑️ CLEAR", use_container_width=True):
        st.session_state.main_text = ""
        st.rerun()
with c2:
    if st.button("📄 EXAMPLE", use_container_width=True):
        ex = {
            "🇵🇰 SINDHI KHALIS - سنڌي": "السلام عليڪم! منهنجا پيارا ڀائرو ۽ ڀينرون! اميد آهي ته توهان سڀ خيريت سان هوندا! اڄ مان توهان لاءِ هڪ خاص پيغام کڻي آيو آهيان! مهر مارٽ جو خالص ماکي هڪ سئو سيڪڙو خالص آهي! صرف ٻه هزار نو سو پنجاهتر روپين ۾! سڄي پاڪستان ۾ فري هوم ڊليوري!",
            "🇵🇰 URDU - اردو": "السلام علیکم! میرے پیارے بھائیو اور بہنو! امید ہے آپ سب خیریت سے ہوں گے! آج میں آپ کے لیے ایک خاص پیغام لے کر آیا ہوں! مہر مارٹ کا خالص شہد سو فیصد خالص ہے! صرف دو ہزار نو سو پچھتر روپے میں! پورے پاکستان میں فری ڈلیوری!",
            "🇮🇳 HINDI - हिन्दी": "मैं जो भी लिखूंगा वही बोलेगा! Delivery All Pakistan - Pakistan ही बोलेगा! Bharat नहीं बोलेगा!",
            "🇬🇧 ENGLISH - US": "Hello! Whatever I type will be spoken exactly! Delivery All Pakistan - Not Bharat!",
            "🇬🇧 ENGLISH - UK": "Hello! Whatever I type will be spoken exactly! Delivery All Pakistan!",
            "🇸🇦 ARABIC - عربي": "السلام عليكم! ما أكتبه سيتم التحدث به بالضبط! Delivery All Pakistan!",
        }
        st.session_state.main_text = ex.get(language_cat, ex["🇵🇰 SINDHI KHALIS - سنڌي"])
        st.rerun()
with c3:
    if st.button("📋 COPY", use_container_width=True):
        st.toast("Text select karke copy karo!")

# SINGLE BOX - PASTE + TYPE - MOBILE LONG PRESS PASTE
text_input = st.text_area(
    f"Yahan Type Ya Paste Karo - {MAX_CHARS} max - {language_cat} - Jo likho wahi bolega - Pakistan = Pakistan:",
    value=st.session_state.main_text,
    placeholder="Yahan long press karke paste karo - Ya type karo - Jo likho ge wahi voice banega - Pakistan likho ge to Pakistan hi bolega - Koi Bharat Namaste auto nahi!",
    height=300,
    key="text_box_v101"
)

if text_input != st.session_state.main_text:
    st.session_state.main_text = text_input

if not text_input.strip():
    st.warning("⚠️ Khali hai - Type ya Paste karo!")
elif len(text_input) > MAX_CHARS:
    st.error(f"⚠️ Zyada lamba - {len(text_input)}/{MAX_CHARS} - {len(text_input)-MAX_CHARS} chars kam karo!")
else:
    st.success(f"✅ {len(text_input)}/{MAX_CHARS} - {len(text_input)//14}s/{MAX_SEC}s - Ready - Jo hai wahi bolega!")

st.progress(min(len(text_input)/MAX_CHARS, 1.0) if text_input else 0)
rate_opt = st.select_slider("Speed:", options=["-5%", "-15%", "+10%"], value="-5%")

if st.button(f"🎙️ {voice_key} - {time_label} - VOICE BANAO - Jo Hai Wahi", type="primary", use_container_width=True):
    if not text_input.strip():
        st.error("⚠️ Khali hai!")
    elif len(text_input) > MAX_CHARS:
        st.error(f"⚠️ Zyada lamba!")
    else:
        with st.spinner(f"{voice_key} - Bana raha - Jo hai wahi - {len(text_input)} chars..."):
            try:
                path = asyncio.run(gen_voice_final(text_input, voice_name, rate_opt, language_cat, MAX_SEC))
                st.balloons()
                st.success(f"✅ Ready! {language_cat} - {voice_key} - Jo likha tha wahi bana!")
                st.audio(path)
                st.code(text_input, language=None)
                with open(path, "rb") as f:
                    st.download_button("📥 Download Voice", f, file_name=f"Voice_{voice_key.replace(' ','_')}_{MAX_SEC}s.mp3")
            except Exception as e:
                st.error(f"Error: {e}")

st.divider()
st.caption("""
V101 STABLE - V95 Wapas - Final - Stable:

✅ Category Fix: Asad Uzma 10-60 Sal Larka Larki - Sindhi me 10,20,30,50,60 Sal - Kabhi gayab nahi hoga!
✅ Alfabet Fix: Sindhi 52 Harf `ٻ ڄ ٽ ڪ ڙ ھ` -> Urdu `ب ج ٹ ک ڑ ہ` - TTS ke liye - Display original - Red underline nahi!
✅ Voice Bug Fix: Jo likho wahi bolega - Pakistan = Pakistan - Hindi me bhi Pakistan hi - Bharat Namaste auto nahi!
✅ Paste Fix: Single box - Mobile long press paste - Type + Paste dono!
✅ System Same: 6 Language, 10-60 Sal, 15 Sec-10 Min - V95 jaisa - Kuch miss nahi!

Commit > Reboot > Stable!
""")
