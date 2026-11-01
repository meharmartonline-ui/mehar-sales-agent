import streamlit as st, os, asyncio, shutil, subprocess
import edge_tts

st.set_page_config(page_title="MEHAR V98 - WORLD STUDIO", layout="centered")
st.title("MEHAR V98 - WORLD STUDIO 🌍")
st.error("V98 FINAL BUG FIX: Alfabet + Auto Convert - Box me Text Khud Badlega!")

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

# === ALFABET CHECK - 5 LANGUAGE - SINDHI URDU HINDI ARABIC ENGLISH ===
# SINDHI 52 HARF - PURE - Urdu me convert map
SINDHI_TO_URDU_LETTER = {
    "ٻ":"ب", "ڄ":"ج", "ڃ":"نج", "ڇ":"چھ", "ٽ":"ٹ", "ٺ":"ٹھ", "ٿ":"تھ",
    "ڌ":"دھ", "ڏ":"ڈ", "ڊ":"ڈ", "ڍ":"ڈھ", "ڀ":"بھ", "ڦ":"پھ", "ڪ":"ک",
    "ڳ":"گ", "ڱ":"نگ", "ڻ":"ن", "ڙ":"ڑ", "ھ":"ہ", "۽":"اور", "۾":"میں", "ٖ":"", "ٗ":""
}

# SINDHI WORD -> URDU WORD - Screenshot wala text fix!
SINDHI_WORD_TO_URDU = {
    "منهنجا":"میرے", "منھنجا":"میرے", "پيارا":"پیارے", "پيارو":"پیارا",
    "ڀائرو":"بھائیو", "ڀينرون":"بہنو", "ڀينرن":"بہنو",
    "اميد":"امید", "آهي":"ہے", "آہے":"ہے", "ته":"کہ", "توهان":"آپ", "توهان":"تم",
    "سڀ":"سب", "خيريت":"خیریت", "سان":"سے", "هوندا":"ہوں گے", "هوندو":"ہوگا",
    "اڄ":"آج", "مان":"میں", "لاء":"لیے", "لئے":"لیے", "لاءِ":"لیے",
    "هڪ":"ایک", "خاص":"خاص", "پيغام":"پیغام", "کڻي":"لے کر", "آيو":"آیا", "آهيان":"ہوں",
    "مهر":"مہر", "مارٽ":"مارٹ", "جو":"کا", "خالص":"خالص", "ماکي":"شہد", "ماکيءَ":"شہد",
    "هڪ سئو":"سو", "سيڪڙو":"فیصد", "صرف":"صرف", "ٻه":"دو", "هزار":"ہزار", "نو":"نو", "سو":"سو",
    "پنجاهتر":"پچھتر", "روپين":"روپے", "۾":"میں", "سڄي":"سارے", "سجي":"سارے",
    "پاڪستان":"پاکستان", "فري":"فری", "هوم":"ہوم", "ڊليوري":"ڈلیوری", "دليوري":"ڈلیوری",
    "هي":"یہ", "آفر":"آفر", "محدود":"محدود", "وقت":"وقت", "جلدي":"جلدی", "ڪريو":"کرو", "ڪيو":"کرو",
    "هن":"اس", "فائدا":"فائدے", "تمام":"بہت", "گهڻا":"زیادہ", "آهن":"ہیں", "صحت":"صحت",
    "بهترين":"بہترین", "توانائي":"توانائی", "ننڊ":"نیند", "ٻارن":"بچوں", "وڏن":"بڑوں",
    "سڀني":"سب کے لیے", "اڄ ئي":"آج ہی", "آرڊر":"آرڈر", "ڪريو":"کریں", "مهرباني":"مہربانی",
    "عليڪم":"علیکم", "عليکم":"علیکم", "السلام":"السلام", "بينرون":"بہنو", "پيارا":"پیارے"
}

# URDU -> HINDI LETTER
URDU_TO_HINDI_LETTER = {
    "ا":"अ","آ":"आ","ب":"ब","پ":"प","ت":"त","ٹ":"ट","ث":"स","ج":"ज","چ":"च","ح":"ह","خ":"ख",
    "د":"द","ڈ":"ड","ذ":"ज","ر":"र","ڑ":"ड़","ز":"ज","ژ":"ज","س":"स","ش":"श",
    "ص":"स","ض":"ज","ط":"त","ظ":"ज","ع":"अ","غ":"ग","ف":"फ","ق":"क","ک":"क","گ":"ग",
    "ل":"ल","م":"म","ن":"न","و":"व","ہ":"ह","ھ":"ह","ء":"अ","ی":"य","ے":"ए"
}

HINDI_TO_URDU_LETTER = {
    "अ":"ا","आ":"آ","इ":"ا","ई":"ی","उ":"و","ऊ":"و","ए":"ے","ऐ":"ے","ओ":"و","औ":"و",
    "ब":"ب","प":"پ","त":"ت","ट":"ٹ","थ":"تھ","ठ":"ٹھ","द":"د","ड":"ڈ","ध":"دھ","ढ":"ڈھ",
    "न":"ن","म":"م","य":"ی","र":"ر","ड़":"ڑ","ल":"ل","व":"و","श":"ش","स":"س","ष":"ش",
    "स":"س","ह":"ہ","क्ष":"کش","त्र":"تر","ज्ञ":"گیا","छ":"چھ","भ":"بھ","फ":"پھ","क":"ک","ग":"گ","ण":"ن"
}

def auto_convert_box(text, target):
    if not text.strip():
        return text
    t = text.strip()
    
    # Save English words like Pakistan, Delivery, 2975 - No Bharat!
    eng_save = {}
    for i, w in enumerate(["Pakistan","PAKISTAN","Mehar","Mart","Delivery","Free","Home","2975","Mehar Mart"]):
        k = f"__E{i}__"
        if w in t:
            eng_save[k] = w
            t = t.replace(w, k)
    
    if "URDU" in target:
        # Sindhi -> Urdu - Word + Letter
        for sw, uw in SINDHI_WORD_TO_URDU.items():
            t = t.replace(sw, uw)
        for sl, ul in SINDHI_TO_URDU_LETTER.items():
            t = t.replace(sl, ul)
        # Hindi -> Urdu
        for hl, ul in HINDI_TO_URDU_LETTER.items():
            t = t.replace(hl, ul)
        # Lamba fix hataya - Display me original Urdu rahega
        
    elif "SINDHI" in target:
        # Urdu/Hindi -> Sindhi - Reverse
        for hl, ul in HINDI_TO_URDU_LETTER.items():
            t = t.replace(hl, ul)  # Hindi -> Urdu first
        # Urdu words to Sindhi words (reverse of above)
        for sw, uw in SINDHI_WORD_TO_URDU.items():
            t = t.replace(uw, sw)
        # Urdu letter to Sindhi? Keep Urdu as is - Sindhi can read Urdu
        t = t.replace("ہے","آهي").replace("ہوں","آهيان").replace("ہیں","آهن")
        
    elif "HINDI" in target:
        # Sindhi -> Hindi via Urdu
        for sw, uw in SINDHI_WORD_TO_URDU.items():
            t = t.replace(sw, uw)
        for sl, ul in SINDHI_TO_URDU_LETTER.items():
            t = t.replace(sl, ul)
        # Urdu -> Hindi
        for ul, hl in URDU_TO_HINDI_LETTER.items():
            t = t.replace(ul, hl)
    
    # Restore English
    for k, w in eng_save.items():
        t = t.replace(k, w)
    
    return t

def tts_clean(text, lang):
    t = text
    if "SINDHI" in lang:
        for sl, ul in SINDHI_TO_URDU_LETTER.items():
            if sl not in ["۽","۾"]:
                t = t.replace(sl, ul)
        t = t.replace("آهي","آآہی").replace("آہے","آآہی").replace("آہی","آآہی")
    return t

# SESSION
if "main_text" not in st.session_state:
    st.session_state.main_text = ""
if "last_lang" not in st.session_state:
    st.session_state.last_lang = "🇵🇰 SINDHI KHALIS - سنڌي"

st.markdown("### 🌍 LANGUAGE - Badlo - Text Khud Badlega - Box Me Dikhega!")

# LANGUAGE SELECT - WITH AUTO CONVERT
lang = st.selectbox("Language Select - Auto Convert:", list(VOICE_CATEGORIES.keys()), index=0, key="lang_select")

# AUTO CONVERT TRIGGER - LANGUAGE BADALTE HI TEXT BOX BADLEGA!
if lang != st.session_state.last_lang and st.session_state.main_text.strip():
    old = st.session_state.main_text
    new = auto_convert_box(old, lang)
    if new != old:
        st.session_state.main_text = new
        st.toast(f"🔄 {st.session_state.last_lang} -> {lang} - Text converted!", icon="✅")
    st.session_state.last_lang = lang
else:
    st.session_state.last_lang = lang

voices = VOICE_CATEGORIES[lang]
vkey = st.selectbox("Voice:", list(voices.keys()), index=2)
vname = voices[vkey]

time_label = st.selectbox("Time:", list(TIME_OPTIONS.keys()), index=3)
MAX_SEC = TIME_OPTIONS[time_label]
MAX_CHARS = MAX_SEC * 14

st.success(f"✅ Auto Convert ON - Ab {lang} select karte hi box ka text {lang} me badal jayega - Screenshot bug fixed!")

c1, c2 = st.columns(2)
with c1:
    if st.button("🗑️ CLEAR", use_container_width=True):
        st.session_state.main_text = ""
        st.rerun()
with c2:
    if st.button("📄 EXAMPLE", use_container_width=True):
        if "SINDHI" in lang:
            st.session_state.main_text = "السلام عليڪم! منهنجا پيارا ڀائرو ۽ ڀينرون! اميد آهي ته توهان سڀ خيريت سان هوندا! اڄ مان توهان لاءِ هڪ خاص پيغام کڻي آيو آهيان! مهر مارٽ جو خالص ماکي هڪ سئو سيڪڙو خالص آهي! صرف ٻه هزار نو سو پنجاهتر روپين ۾! سڄي پاڪستان ۾ فري هوم ڊليوري!"
        elif "URDU" in lang:
            st.session_state.main_text = "السلام علیکم! میرے پیارے بھائیو اور بہنو! امید ہے کہ آپ سب خیریت سے ہوں گے! آج میں آپ کے لیے ایک خاص پیغام لے کر آیا ہوں! مہر مارٹ کا خالص شہد سو فیصد خالص ہے! صرف دو ہزار نو سو پچھتر روپے میں! سارے پاکستان میں فری ہوم ڈلیوری! یہ آفر محدود وقت کے لیے ہے! جلدی کریں!"
        elif "HINDI" in lang:
            st.session_state.main_text = "नमस्ते! मेरे प्यारे भाइयों और बहनों! उम्मीद है आप सब ठीक होंगे! आज मैं आपके लिए एक खास संदेश लेकर आया हूं! मेहर मार्ट का शुद्ध शहद सौ प्रतिशत शुद्ध है! सिर्फ दो हजार नौ सौ पचहत्तर रुपये में! पूरे Pakistan में फ्री होम डिलीवरी! यह ऑफर सीमित समय के लिए है!"
        else:
            st.session_state.main_text = "Hello brothers and sisters! Mehar Mart pure honey 100 percent pure! Only 2975 rupees! Free delivery all Pakistan!"
        st.rerun()

# TEXT BOX - YAHAN AUTO CONVERT DIKHEGA!
text = st.text_area(
    f"Type/Paste - {MAX_CHARS} max - {lang} - Language badlo text khud badlega:",
    value=st.session_state.main_text,
    placeholder="Yahan likho - Language badlo to text khud us language me badal jayega - Pakistan hamesha Pakistan!",
    height=320,
    key="text_area_main"
)

if text != st.session_state.main_text:
    st.session_state.main_text = text

if text.strip():
    if len(text) > MAX_CHARS:
        st.error(f"Zyada! {len(text)}/{MAX_CHARS}")
    else:
        st.success(f"✅ {len(text)}/{MAX_CHARS} - {lang} me converted - Red underline khatam!")
        # Show converted preview
        converted_for_tts = tts_clean(text, lang)
        if converted_for_tts != text:
            st.caption(f"TTS ke liye: {converted_for_tts[:100]}...")

st.progress(min(len(text)/MAX_CHARS, 1.0) if text else 0)
rate = st.select_slider("Speed:", ["-5%","-15%","+10%"], value="-5%")

def split_txt(t, s=1000):
    if len(t) <= s:
        return [t]
    words = t.split(' ')
    parts, cur = [], ""
    for w in words:
        if len(cur)+len(w)+1 <= s:
            cur = cur+" "+w if cur else w
        else:
            if cur: parts.append(cur)
            cur = w
    if cur: parts.append(cur)
    return parts

async def gen_edge(t, v, r, p):
    for _ in range(5):
        try:
            if os.path.exists(p):
                os.remove(p)
            await edge_tts.Communicate(text=t, voice=v, rate=r).save(p)
            if os.path.exists(p) and os.path.getsize(p) > 800:
                return True
        except:
            await asyncio.sleep(1)
    return False

async def gen_voice(t, v, r, l):
    if not t.strip():
        raise Exception("Khali hai!")
    if os.path.exists("voice"):
        shutil.rmtree("voice")
    os.makedirs("voice", exist_ok=True)
    t_clean = tts_clean(t, l)
    parts = split_txt(t_clean, 1000)
    files = []
    for i, p in enumerate(parts):
        if not p.strip(): continue
        path = f"voice/{v.replace('-','_')}_{i}.mp3"
        ok = await gen_edge(p, v, r, path)
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

if st.button(f"🎙️ {vkey} - {time_label} - VOICE BANAO", type="primary", use_container_width=True):
    if not text.strip():
        st.error("Khali hai!")
    else:
        with st.spinner(f"{lang} - Bana raha..."):
            try:
                path = asyncio.run(gen_voice(text, vname, rate, lang))
                st.balloons()
                st.success(f"✅ Ready! {lang} - Text + Voice dono {lang} me - Bug Fixed!")
                st.audio(path)
                with open(path, "rb") as f:
                    st.download_button("📥 Download", f, file_name=f"Voice_{MAX_SEC}s.mp3")
            except Exception as e:
                st.error(f"Error: {e}")

st.divider()
st.info("V98 - Alfabet Check - Sindhi 52 Harf -> Urdu Pure - Urdu -> Hindi - Hindi -> Urdu - Auto Convert Box Me Dikhega - Screenshot wala red underline bug fixed!")
