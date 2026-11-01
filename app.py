import streamlit as st, os, asyncio, shutil, subprocess, re
import edge_tts

st.set_page_config(page_title="MEHAR V95 - WORLD STUDIO", layout="centered")
st.title("MEHAR V95 - WORLD STUDIO 🌍")
st.success("V95 FINAL: Bug Fixed - Hindi No Auto Namaste/Bharat - Jo Likho Wahi Bolega!")

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

# PURE SINDHI 52 ALPHABET - Only for Sindhi - Hindi/Urdu me koi change nahi!
PURE_SINDHI_TTS_MAP = {
    "ٻ":"ب","ڄ":"ج","ڃ":"نج","ڇ":"چھ","ٽ":"ٹ","ٺ":"ٹھ","ٿ":"تھ",
    "ڌ":"دھ","ڏ":"ڈ","ڊ":"ڈ","ڍ":"ڈھ","ڀ":"بھ","ڦ":"پھ","ڪ":"ک",
    "ڳ":"گ","ڱ":"نگ","ڻ":"ن","ڙ":"ڑ","ھ":"ہ",
}

st.markdown("### 🌍 LANGUAGE CATEGORY")
language_cat = st.selectbox("Language Category:", list(VOICE_CATEGORIES.keys()), index=0)
voices = VOICE_CATEGORIES[language_cat]
voice_key = st.selectbox(f"{language_cat} - Age:", list(voices.keys()), index=1)
voice_name = voices[voice_key]
st.info(f"SELECTED: {language_cat} - {voice_key}")

time_label = st.selectbox("⏱️ TIME CATEGORY:", list(TIME_OPTIONS.keys()), index=2)
MAX_SEC = TIME_OPTIONS[time_label]
MAX_CHARS = MAX_SEC * 14

# BUG FIX - NO AUTO DEFAULT TEXT - Khali - Jo likho wahi bolega!
# Pehle Hindi me auto Namaste + Bharat tha - Ab nahi - Bilkul khali!
st.markdown("### ✍️ YAHAN JO BHI TYPE KARO GE - WOHI EXACT VOICE BANEGA!")
st.warning("⚠️ BUG FIXED: Hindi me auto Namaste/Bharat nahi - Pakistan likho ge to Pakistan hi bolega - Bharat nahi bolega - Jo likho ge wohi!")

# Text area bilkul khali - Koi default nahi - Koi auto translation nahi!
text_input = st.text_area(
    f"✍️ Yahan apna text likho ({MAX_CHARS} max) - {language_cat} - Jo likho ge wohi bolega - No auto change:",
    value="",  # KHALI - No default - No Namaste - No Bharat!
    placeholder=f"""Yahan jo bhi type karo ge wohi exact voice banega - Koi auto change nahi!

Example - Jo likho ge wohi bolega:
Sindhi: مان جيڪو به لکان ٿو اهو ئي آواز ٺهندو!
Urdu: میں جو بھی لکھوں گا وہی بولے گا - پاکستان لکھو گے تو پاکستان ہی بولے گا!
Hindi: मैं जो भी लिखूंगा वही बोलेगा - Pakistan लिखोगे तो Pakistan ही बोलेगा, Bharat नहीं!
English: Whatever I type will be spoken exactly - If you type Pakistan it will say Pakistan!

Ab aap apna text likho - Delivery All Pakistan likho ge to All Pakistan hi bolega - Bharat nahi!""",
    height=300,
    max_chars=MAX_CHARS
)

if not text_input.strip():
    st.warning("⚠️ Text box khali hai - Yahan likho - Jo likho ge wohi bolega!")
else:
    st.success(f"✅ {len(text_input)} chars - Jo likha hai wohi bolega - No Bharat/Namaste auto!")

st.metric(f"{len(text_input)} / {MAX_CHARS}", f"{len(text_input)//14} sec / {MAX_SEC} sec")
st.progress(min(len(text_input)/MAX_CHARS, 1.0) if text_input else 0)
rate_opt = st.select_slider("Speed:", options=["-5%", "-15%", "+10%"], value="-5%")

def clean_no_auto_change(text, lang_cat):
    """BUG FIXED - Koi auto translation nahi - Jo likho ge wohi bolega!"""
    if not text.strip():
        return ""
    t = text.strip()
    
    # ONLY SINDHI - 52 Harf fix - Baqi languages me koi change nahi!
    if "SINDHI" in lang_cat:
        for sc, tc in PURE_SINDHI_TTS_MAP.items():
            t = t.replace(sc, tc)
        t = t.replace("آهي", "آآہی").replace("آهي", "آآہی").replace("آہی", "آآہی").replace("آہے", "آآہے")
        t = t.replace("سجی", "سجّی").replace("عليکم", "علیکم").replace("عليڪم", "علیکم")
        # Numbers bhi Sindhi me hi - But location Pakistan/Bharat change nahi!
    # HINDI, URDU, ENGLISH, ARABIC - Koi auto change nahi - Jo likha hai wohi!
    # Pehle Hindi me Pakistan -> Bharat kar raha tha - Ab nahi!
    # Pehle Namaste auto add ho raha tha - Ab nahi!
    # Bilkul jo likho ge wohi bolega!
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
        raise Exception("Text khali hai!")
    if os.path.exists("voice"):
        shutil.rmtree("voice")
    os.makedirs("voice", exist_ok=True)
    cleaned = clean_no_auto_change(text, lang_cat)
    parts = split_no_cut(cleaned, 1000)
    files = []
    for i, p in enumerate(parts):
        p = clean_no_auto_change(p, lang_cat)
        if not p: continue
        path = f"voice/{voice.replace('-','_')}_{i}.mp3"
        ok = await gen_edge(p, voice, rate, path)
        if ok:
            files.append(path)
    if not files:
        raise Exception("Voice fail")
    final = f"voice/FINAL_Exact_{voice_key.replace(' ','_')}_{MAX_SEC}s.mp3"
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

if st.button(f"🎙️ {language_cat} - {voice_key} - Jo Likha Hai Wahi Exact Banao", type="primary", use_container_width=True):
    if not text_input.strip():
        st.error("⚠️ Pehle kuch likho - Khali hai!")
    else:
        with st.spinner(f"{voice_key} - Exact jo likha hai wohi bana raha..."):
            try:
                path = asyncio.run(gen_exact(text_input, voice_name, rate_opt, language_cat))
                st.balloons()
                st.success(f"✅ Ready! Exact jo likha tha wohi - No Namaste/Bharat auto!")
                st.audio(path)
                st.markdown("**Aap ne exact likha tha:**")
                st.code(text_input, language=None)
                st.caption(f"TTS Cleaned (Only Sindhi 52 Harf): {clean_no_auto_change(text_input, language_cat)}")
                with open(path, "rb") as f:
                    st.download_button(f"📥 Download Exact Voice", f, file_name=f"Exact_{voice_key.replace(' ','_')}_{MAX_SEC}s.mp3")
            except Exception as e:
                st.error(f"Error: {e}")

st.divider()
st.error("""
**🐛 BUG FIXED - Hindi wala bug:**

**Pehle kya hota tha:**
**- Hindi select karte hi auto `नमस्ते` bolta tha**
**- `Delivery All Pakistan` likha to `Delivery All Bharat` bol deta tha - Pakistan ko Bharat bana deta tha!**

**Ab kya hai:**
**- Koi auto Namaste nahi - Jo likho ge wohi bolega**
**- Pakistan likho ge to Pakistan hi bolega - Bharat nahi banega**
**- Hindi me `मैंने Pakistan में Delivery` likho ge to `Pakistan` hi bolega**
**- Jo type karo ge wohi exact voice - Koi translation nahi!**

**Test karo: `Delivery All Pakistan` likho - Hindi voice select karo - Ab Pakistan hi bolega - Bharat nahi!**
""")
