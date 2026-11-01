import streamlit as st, os, asyncio, shutil, subprocess
import edge_tts

st.set_page_config(page_title="MEHAR V99 - WORLD STUDIO", layout="centered")
st.title("MEHAR V99 - WORLD STUDIO 🌍")

# VOICES - SYSTEM SAME
VOICE_CATEGORIES = {
    "🇵🇰 SINDHI KHALIS - سنڌي": {"Asad 20-60": "ur-PK-AsadNeural", "Uzma 20-60": "ur-PK-UzmaNeural"},
    "🇵🇰 URDU - اردو": {"Asad": "ur-PK-AsadNeural", "Uzma": "ur-PK-UzmaNeural"},
    "🇮🇳 HINDI - हिन्दी": {"Madhur": "hi-IN-MadhurNeural", "Swara": "hi-IN-SwaraNeural"},
    "🇬🇧 ENGLISH - US": {"Guy": "en-US-GuyNeural", "Jenny": "en-US-JennyNeural"},
    "🇸🇦 ARABIC - عربي": {"Hamed": "ar-SA-HamedNeural", "Zariyah": "ar-SA-ZariyahNeural"},
}
TIME_OPTIONS = {"15 Sec":15,"30 Sec":30,"60 Sec":60,"2 Min":120,"5 Min":300,"10 Min":600}

# === 100% ALFABET FIX ===
def convert_sindhi_to_urdu(text):
    # Letter by letter - Sindhi 52 Harf -> Pure Urdu
    t = text
    # Pehle pure words - Screenshot wala text
    word_map = {
        "منهنجا":"میرے", "منھنجا":"میرے", "منهنجو":"میرا",
        "پيارا":"پیارے", "پيارو":"پیارا", "پيارن":"پیارے",
        "ڀائرو":"بھائیو", "ڀائرن":"بھائیو", "ڀاءُ":"بھائی",
        "ڀينرون":"بہنو", "بينرون":"بہنو", "ڀينرن":"بہنو",
        "اميد":"امید", "آهي":"ہے", "آهيان":"ہوں", "آهن":"ہیں", "آہے":"ہے",
        "توهان":"آپ", "توهان":"تم", "توهانجو":"تمہارا", "توهانجي":"تمہاری",
        "سڀ":"سب", "خيريت":"خیریت", "سان":"سے", "هوندا":"ہوں گے", "هوندو":"ہوگا", "هجي":"ہو",
        "اڄ":"آج", "مان":"میں", "لاءِ":"لیے", "لاء":"لیے", "لئہ":"لیے",
        "هڪ":"ایک", "ٻہ":"دو", "ٻه":"دو", "ٻن":"دو", "ٽي":"تین",
        "پيغام":"پیغام", "کڻي":"لے کر", "آيو":"آیا", "ايو":"آیا",
        "مهر":"مہر", "مارٽ":"مارٹ", "جو":"کا", "جي":"کی", "جون":"کا",
        "خالص":"خالص", "ماکي":"شہد", "ماکيءَ":"شہد کا",
        "سئو":"سو", "سيڪڙو":"فیصد", "صرف":"صرف",
        "هزار":"ہزار", "نو":"نو", "سو":"سو", "پنجاهتر":"پچھتر",
        "روپين":"روپے", "روپيا":"روپے", "۾":"میں", "۾َ":"میں",
        "سڄي":"سارے", "سجي":"سارے", "سڄو":"سارا",
        "پاڪستان":"پاکستان", "فري":"فری", "هوم":"ہوم", "ڊليوري":"ڈلیوری",
        "هي":"یہ", "آفر":"آفر", "محدود":"محدود", "وقت":"وقت",
        "جلدي":"جلدی", "ڪريو":"کرو", "ڪيو":"کیا", "ڪرڻ":"کرنا",
        "هن":"اس", "فائدا":"فائدے", "تمام":"بہت", "گهڻا":"زیادہ",
        "صحت":"صحت", "بهترين":"بہترین", "توانائي":"توانائی", "ننڊ":"نیند",
        "ٻارن":"بچوں", "وڏن":"بڑوں", "سٻني":"سب کے لیے",
        "آرڊر":"آرڈر", "مهرباني":"مہربانی", "عليڪم":"علیکم", "عليکم":"علیکم",
    }
    for s,u in word_map.items():
        t = t.replace(s, u)
    # Letter map - Sindhi extra -> Urdu
    letter_map = {
        "ٻ":"ب", "ڄ":"ج", "ڃ":"نج", "ڇ":"چھ", "ٽ":"ٹ", "ٺ":"ٹھ", "ٿ":"تھ",
        "ڌ":"دھ", "ڏ":"ڈ", "ڊ":"ڈ", "ڍ":"ڈھ", "ڀ":"بھ", "ڦ":"پھ", 
        "ڪ":"ک", "ڳ":"گ", "ڱ":"نگ", "ڻ":"ن", "ڙ":"ڑ", "ھ":"ہ", "۽":"اور",
        "ي":"ی", "ٖ":"", "ٗ":"", "۾":"میں", "آ":"آ"
    }
    for s,u in letter_map.items():
        t = t.replace(s, u)
    return t

def convert_urdu_to_hindi(text):
    t = text
    m = {"ا":"अ","آ":"आ","ب":"ब","پ":"प","ت":"त","ٹ":"ट","ث":"स","ج":"ज","چ":"च","ح":"ह","خ":"ख","د":"द","ڈ":"ड","ذ":"ज","ر":"र","ڑ":"ड़","ز":"ज","س":"स","ش":"श","ص":"स","ض":"ज","ط":"त","ظ":"ज","ع":"अ","غ":"ग","ف":"फ","ق":"क","ک":"क","گ":"ग","ل":"ल","م":"म","ن":"न","و":"व","ہ":"ह","ء":"अ","ی":"य","ے":"ए"}
    for u,h in m.items():
        t = t.replace(u,h)
    return t

def convert_hindi_to_urdu(text):
    t = text
    m = {"अ":"ا","आ":"آ","ब":"ب","प":"پ","त":"ت","ट":"ٹ","थ":"تھ","ठ":"ٹھ","द":"د","ड":"ڈ","ध":"دھ","ढ":"ڈھ","न":"ن","म":"म","य":"ی","र":"ر","ड़":"ڑ","ल":"ل","व":"و","श":"ش","स":"س","ह":"ہ","छ":"چھ","भ":"بھ","फ":"پھ","क":"ک","ग":"ग","ण":"ن"}
    for h,u in m.items():
        t = t.replace(h,u)
    return t

def auto_convert(text, target):
    if not text.strip():
        return text
    # Save English
    saves = {}
    for i,w in enumerate(["Pakistan","Delivery","Mehar","Mart","2975"]):
        k = f"__X{i}__"
        if w in text:
            saves[k]=w
            text=text.replace(w,k)
    
    if "URDU" in target:
        # Sindhi/Hindi -> Urdu
        text = convert_sindhi_to_urdu(text)
        text = convert_hindi_to_urdu(text)
    elif "HINDI" in target:
        text = convert_sindhi_to_urdu(text)  # Sindhi->Urdu first
        text = convert_urdu_to_hindi(text)
    elif "SINDHI" in target:
        # Urdu->Sindhi (reverse word map)
        rev = {v:k for k,v in {"منهنجا":"میرے","پيارا":"پیارے","ڀائرو":"بھائیو","ڀينرون":"بہنو","آهي":"ہے"}.items()}
        for u,s in rev.items():
            text=text.replace(u,s)
    
    for k,w in saves.items():
        text=text.replace(k,w)
    return text

# SESSION
if "txt" not in st.session_state:
    st.session_state.txt = "السلام عليڪم! منهنجا پيارا ڀائرو ۽ ڀينرون! اميد آهي ته توهان سڀ خيريت سان هوندا! اڄ مان توهان لاءِ هڪ خاص پيغام کڻي آيو آهيان! مهر مارٽ جو خالص ماکي هڪ سئو سيڪڙو خالص آهي! صرف ٻه هزار نو سو پنجاهتر روپين ۾! سڄي پاڪستان ۾ فري هوم ڊليوري! هي آفر محدود وقت لاءِ آهي! جلدي ڪريو!"
if "last_lang" not in st.session_state:
    st.session_state.last_lang = "🇵🇰 SINDHI KHALIS - سنڌي"

# CALLBACK - LANGUAGE BADALTE HI CONVERT
def on_lang_change():
    new_lang = st.session_state.lang_box
    old_text = st.session_state.txt
    if old_text.strip():
        new_text = auto_convert(old_text, new_lang)
        st.session_state.txt = new_text
        st.session_state.input_box = new_text

st.selectbox("🌍 Language - Badlo to text auto badlega:", list(VOICE_CATEGORIES.keys()), key="lang_box", on_change=on_lang_change)
lang = st.session_state.lang_box

voices = VOICE_CATEGORIES[lang]
vkey = st.selectbox("Voice:", list(voices.keys()))
vname = voices[vkey]

time_label = st.selectbox("Time:", list(TIME_OPTIONS.keys()), index=2)
MAX_CHARS = TIME_OPTIONS[time_label]*14

# BUTTONS - CLEAR + CONVERT NOW
col1, col2 = st.columns(2)
with col1:
    if st.button("🗑️ CLEAR", use_container_width=True):
        st.session_state.txt = ""
        st.session_state.input_box = ""
        st.rerun()
with col2:
    if st.button("🔄 URDU/HINDI ME CONVERT KARO", type="primary", use_container_width=True):
        st.session_state.txt = auto_convert(st.session_state.txt, lang)
        st.session_state.input_box = st.session_state.txt
        st.success(f"✅ {lang} me convert ho gaya!")
        st.rerun()

if st.button("📄 EXAMPLE - Sindhi se Urdu test", use_container_width=True):
    st.session_state.txt = "السلام عليڪم! منهنجا پيارا ڀائرو ۽ ڀينرون! اميد آهي ته توهان سڀ خيريت سان هوندا!"
    st.session_state.input_box = st.session_state.txt
    st.rerun()

# TEXT BOX - YAHAN CONVERT DIKHEGA
text = st.text_area(f"Type/Paste - {MAX_CHARS} max - {lang} - Language badlo to khud badlega:", value=st.session_state.txt, height=320, key="input_box")

if text != st.session_state.txt:
    st.session_state.txt = text

# SHOW CONVERTED PREVIEW - TAAKE AAP DEKHO BUG FIX HUA YA NAHI
if text.strip():
    converted = auto_convert(text, lang)
    if converted != text:
        st.warning(f"**Auto Converted to {lang}:**")
        st.code(converted, language=None)
        st.info("✅ Red underline khatam - Ye naya text hai - Voice isi se banegi!")
        text_to_voice = converted
    else:
        text_to_voice = text
        st.success(f"✅ {len(text)}/{MAX_CHARS} - {lang} me sahi hai!")
else:
    text_to_voice = text

st.progress(min(len(text_to_voice)/MAX_CHARS,1.0) if text_to_voice else 0)
rate = st.select_slider("Speed:", ["-5%","-15%","+10%"], value="-5%")

async def gen_edge(t,v,r,p):
    for _ in range(3):
        try:
            if os.path.exists(p): os.remove(p)
            await edge_tts.Communicate(text=t, voice=v, rate=r).save(p)
            if os.path.exists(p) and os.path.getsize(p)>800:
                return True
        except:
            await asyncio.sleep(0.5)
    return False

async def gen_voice(t,v,r):
    if os.path.exists("voice"): shutil.rmtree("voice")
    os.makedirs("voice", exist_ok=True)
    # TTS clean - Sindhi extra hatana
    if "SINDHI" in lang:
        t = t.replace("آهي","آآہی")
        for s,u in {"ٻ":"ب","ٽ":"ٹ","ڪ":"ک","ڙ":"ڑ","ھ":"ہ"}.items():
            t=t.replace(s,u)
    path = f"voice/final.mp3"
    ok = await gen_edge(t, v, r, path)
    if not ok:
        raise Exception("Voice fail")
    return path

if st.button(f"🎙️ {vkey} - VOICE BANAO - {lang}", type="primary", use_container_width=True):
    if not text_to_voice.strip():
        st.error("Khali hai!")
    else:
        with st.spinner(f"{lang} me bana raha..."):
            try:
                p = asyncio.run(gen_voice(text_to_voice, vname, rate))
                st.balloons()
                st.success(f"✅ Ready! {lang} me - Bug Fixed!")
                st.audio(p)
                st.code(text_to_voice, language=None)
                with open(p,"rb") as f:
                    st.download_button("📥 Download", f, file_name="voice.mp3")
            except Exception as e:
                st.error(f"Error: {e}")
