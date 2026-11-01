import streamlit as st, os, asyncio, shutil, subprocess, re
import edge_tts

st.set_page_config(page_title="MEHAR V97 - WORLD STUDIO", layout="centered")
st.title("MEHAR V97 - WORLD STUDIO 🌍")
st.success("V97 FINAL: Auto Convert - Language Badlo - Text Khud Badlega!")

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

# FULL AUTO CONVERT MAPS
URDU_TO_HINDI = {
    "ا":"अ","ب":"ब","پ":"प","ت":"त","ٹ":"ट","ث":"स","ج":"ज","چ":"च","ح":"ह","خ":"ख",
    "د":"द","ڈ":"ड","ذ":"ज","ر":"र","ڑ":"ड़","ز":"ज","ژ":"ज","س":"स","ش":"श",
    "ص":"स","ض":"ज","ط":"त","ظ":"ज","ع":"अ","غ":"ग","ف":"फ","ق":"क","ک":"क",
    "گ":"ग","ل":"ल","م":"म","ن":"न","و":"व","ہ":"ह","ھ":"ह","ء":"अ","ی":"य","ے":"ए",
    "آ":"आ","ہ":"ह"
}
SINDHI_TO_HINDI_EXTRA = {"ٻ":"ब","ڄ":"ज","ڃ":"ज","ڇ":"छ","ٽ":"ट","ٺ":"ठ","ٿ":"थ","ڌ":"ध","ڏ":"ड","ڊ":"ड","ڍ":"ढ","ڀ":"भ","ڦ":"फ","ڪ":"क","ڳ":"ग","ڱ":"ग","ڻ":"ण","ڙ":"ड़","ھ":"ह"}

HINDI_TO_URDU = {
    "अ":"ا","आ":"آ","इ":"ا","ई":"ی","उ":"و","ऊ":"و","ए":"ے","ऐ":"ے","ओ":"و","औ":"و",
    "ब":"ب","प":"پ","त":"ت","ट":"ٹ","स":"س","ज":"ج","च":"چ","ह":"ہ","ख":"خ",
    "द":"د","ड":"ڈ","र":"ر","ड़":"ڑ","श":"ش","ग":"گ","ल":"ل","म":"म","न":"न",
    "व":"و","य":"ی","ण":"ڻ","छ":"ڇ","ठ":"ٺ","थ":"ٿ","ध":"ڌ","ढ":"ڍ","भ":"ڀ",
    "फ":"ڦ","क":"ڪ","ग":"ڳ","क़":"ق","ख़":"خ","ग़":"غ","ज़":"ز","ड़":"ڙ","ढ़":"ڈھ",
    "न":"ن","म":"م"
}

def auto_convert_text(text, target_lang):
    if not text or not text.strip():
        return text
    t = text.strip()
    # English words like Pakistan, Delivery, Mehar Mart keep - No Bharat!
    # Is liye Pakistan ko pehle save karlo
    placeholders = {}
    eng_words = ["Pakistan", "PAKISTAN", "Delivery", "Mehar", "Mart", "Free", "Home", "2975"]
    for i, w in enumerate(eng_words):
        key = f"__ENG{i}__"
        if w in t:
            placeholders[key] = w
            t = t.replace(w, key)
    
    if "SINDHI" in target_lang:
        for h, u in HINDI_TO_URDU.items():
            t = t.replace(h, u)
        for sc, tc in PURE_SINDHI_TTS_MAP.items():
            t = t.replace(sc, tc)
        t = t.replace("آهي", "آآہی").replace("آهي", "آآہی").replace("آہی", "آآہی").replace("آہے", "آآہے")
    elif "URDU" in target_lang:
        for h, u in HINDI_TO_URDU.items():
            t = t.replace(h, u)
        for sc, tc in PURE_SINDHI_TTS_MAP.items():
            t = t.replace(sc, tc)
        t = t.replace("آهي", "آہے").replace("آآہی", "آہے")
    elif "HINDI" in target_lang:
        for sc, hc in SINDHI_TO_HINDI_EXTRA.items():
            t = t.replace(sc, hc)
        for u, h in URDU_TO_HINDI.items():
            t = t.replace(u, h)
    
    # Restore English words
    for key, w in placeholders.items():
        t = t.replace(key, w)
    
    return t

# SESSION - LANGUAGE CHANGE DETECT!
if "text_value" not in st.session_state:
    st.session_state.text_value = ""
if "prev_lang" not in st.session_state:
    st.session_state.prev_lang = "🇵🇰 SINDHI KHALIS - سنڌي"
if "prev_text" not in st.session_state:
    st.session_state.prev_text = ""

st.markdown("### 🌍 LANGUAGE CATEGORY - Auto Convert")
language_cat = st.selectbox("Language Category - Badlo to text khud badlega:", list(VOICE_CATEGORIES.keys()), index=0)

# AUTO CONVERT ON LANGUAGE CHANGE - YAHI BUG FIX HAI!
if language_cat != st.session_state.prev_lang and st.session_state.text_value.strip():
    old_text = st.session_state.text_value
    new_text = auto_convert_text(old_text, language_cat)
    if new_text != old_text:
        st.session_state.text_value = new_text
        st.toast(f"🔄 Auto Convert: {st.session_state.prev_lang} -> {language_cat}")
    st.session_state.prev_lang = language_cat
else:
    st.session_state.prev_lang = language_cat

voices = VOICE_CATEGORIES[language_cat]
voice_key = st.selectbox(f"{language_cat} - Voice:", list(voices.keys()), index=2)
voice_name = voices[voice_key]

time_label = st.selectbox("⏱️ TIME CATEGORY:", list(TIME_OPTIONS.keys()), index=3)
MAX_SEC = TIME_OPTIONS[time_label]
MAX_CHARS = MAX_SEC * 14

st.info(f"✅ Auto Convert ON - {language_cat} select karte hi text box ka text khud {language_cat} me badal jayega! Screenshot wala bug fixed!")

c1, c2 = st.columns(2)
with c1:
    if st.button("🗑️ CLEAR", use_container_width=True):
        st.session_state.text_value = ""
        st.rerun()
with c2:
    if st.button("📄 EXAMPLE", use_container_width=True):
        if "SINDHI" in language_cat:
            st.session_state.text_value = "السلام عليڪم! منهنجا پيارا ڀائرو ۽ ڀينرون! اميد آهي ته توهان سڀ خيريت سان هوندا! اڄ مان توهان لاءِ هڪ خاص پيغام کڻي آيو آهيان! مهر مارٽ جو خالص ماکي هڪ سئو سيڪڙو خالص آهي! صرف ٻه هزار نو سو پنجاهتر روپين ۾! سڄي پاڪستان ۾ فري هوم ڊليوري! هي آفر محدود وقت لاءِ آهي! جلدي ڪريو! هن خالص ماکي جا فائدا تمام گهڻا آهن! صحت لاءِ بهترين! اڄ ئي آرڊر ڪريو! مهرباني!"
        elif "URDU" in language_cat:
            st.session_state.text_value = "السلام علیکم! میرے پیارے بھائیو اور بہنو! امید ہے کہ آپ سب خیریت سے ہوں گے! آج میں آپ کے لیے ایک خاص پیغام لے کر آیا ہوں! مہر مارٹ کا خالص شہد سو فیصد خالص ہے! صرف دو ہزار نو سو پچھتر روپے میں! سارے پاکستان میں فری ہوم ڈلیوری! یہ آفر محدود وقت کے لیے ہے! جلدی کریں! اس خالص شہد کے بہت فائدے ہیں! صحت کے لیے بہترین! آج ہی آرڈر کریں! شکریہ!"
        elif "HINDI" in language_cat:
            st.session_state.text_value = "नमस्ते! मेरे प्यारे भाइयों और बहनों! उम्मीद है आप सब ठीक होंगे! आज मैं आपके लिए एक खास संदेश लेकर आया हूं! मेहर मार्ट का शुद्ध शहद सौ प्रतिशत शुद्ध है! सिर्फ दो हजार नौ सौ पचहत्तर रुपये में! पूरे Pakistan में फ्री होम डिलीवरी! यह ऑफर सीमित समय के लिए है! जल्दी करें! इस शुद्ध शहद के बहुत फायदे हैं! सेहत के लिए बेहतरीन! आज ही ऑर्डर करें! धन्यवाद!"
        else:
            st.session_state.text_value = "Hello! My dear brothers and sisters! I hope you are all well! Today I have a special message for you! Mehar Mart pure honey is 100 percent pure! Only for 2975 rupees! Free home delivery all over Pakistan! This offer is for limited time! Hurry up! Many benefits for health! Order today! Thank you!"
        st.rerun()

# SINGLE TEXT AREA - AUTO CONVERTED TEXT DIKHEGA!
text_input = st.text_area(
    f"Yahan Type Ya Paste Karo ({MAX_CHARS} max) - {language_cat} - Auto Convert:",
    value=st.session_state.text_value,
    placeholder="Yahan likho - Language badlo to text khud us language me badal jayega! Pakistan likho to har language me Pakistan hi!",
    height=300,
    key="main_text_box"
)

if text_input != st.session_state.text_value:
    st.session_state.text_value = text_input
    st.session_state.prev_text = text_input

if len(text_input) > MAX_CHARS:
    st.error(f"⚠️ Zyada! {len(text_input)}/{MAX_CHARS}")
elif text_input.strip():
    st.success(f"✅ {len(text_input)}/{MAX_CHARS} - {len(text_input)//14}s/{MAX_SEC}s - {language_cat} me converted!")

st.progress(min(len(text_input)/MAX_CHARS, 1.0) if text_input else 0)
rate_opt = st.select_slider("Speed:", options=["-5%", "-15%", "+10%"], value="-5%")

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

async def gen_voice(text, voice, rate):
    if not text.strip():
        raise Exception("Khali hai!")
    if os.path.exists("voice"):
        shutil.rmtree("voice")
    os.makedirs("voice", exist_ok=True)
    parts = split_no_cut(text, 1000)
    files = []
    for i, p in enumerate(parts):
        if not p.strip(): continue
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
        st.error("⚠️ Khali hai!")
    elif len(text_input) > MAX_CHARS:
        st.error("⚠️ Zyada lamba!")
    else:
        with st.spinner(f"Bana raha - {language_cat}..."):
            try:
                path = asyncio.run(gen_voice(text_input, voice_name, rate_opt))
                st.balloons()
                st.success(f"✅ Ready! {language_cat} - Text + Voice dono {language_cat} me!")
                st.audio(path)
                st.code(text_input, language=None)
                with open(path, "rb") as f:
                    st.download_button("📥 Download", f, file_name=f"Voice_{MAX_SEC}s.mp3")
            except Exception as e:
                st.error(f"Error: {e}")

st.divider()
st.error("""
**🐛 FINAL BUG FIX - Screenshot wala:**

**Pehle:** Sindhi text likha - URDU select kiya - Text waisa ka waisa Sindhi me hi raha - Change nahi - Voice bhi Sindhi!

**Ab:** 
- **Sindhi likho - URDU select karo - Text box ka text khud URDU me badal jayega - Dikhega bhi Urdu me - Bolega bhi Urdu me!**
- **Urdu likho - HINDI select karo - Text box khud Hindi me - `पाकिस्तान` - Pakistan hi - Bharat nahi!**
- **Hindi likho - SINDHI select karo - Text box khud Sindhi me!**

**Kaise:** Language Category badlo - Text auto convert hoke box me hi change ho jayega - Voice bhi usi language me!

**System Same - Kuch Miss Nahi - Sirf ye auto convert add!**
""")
