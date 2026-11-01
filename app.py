import streamlit as st, os, asyncio, shutil, subprocess, re
from dotenv import load_dotenv
load_dotenv()
import edge_tts

GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
try:
    from groq import Groq
    groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
except:
    groq_client = None

st.set_page_config(page_title="MEHAR V95 - WORLD STUDIO", layout="centered")
st.markdown("<style>textarea{spellcheck:false !important}</style>", unsafe_allow_html=True)

st.title("MEHAR V95 - WORLD STUDIO 🌍")
if groq_client: st.success("✅ Groq Connected - Auto Convert Ready!")
st.success("V95 FINAL - No Paste Needed - 1 Click Load!")

VOICE_CATEGORIES = {
    "🇵🇰 SINDHI KHALIS - سنڌي": {"30 Sal Larka - Asad": "ur-PK-AsadNeural", "30 Sal Larki - Uzma": "ur-PK-UzmaNeural", "20 Sal Larka - Asad": "ur-PK-AsadNeural", "20 Sal Larki - Uzma": "ur-PK-UzmaNeural"},
    "🇵🇰 URDU - اردو": {"30 Sal Larka - Asad": "ur-PK-AsadNeural", "30 Sal Larki - Uzma": "ur-PK-UzmaNeural"},
    "🇮🇳 HINDI - हिन्दी": {"30 Sal Larka - Madhur": "hi-IN-MadhurNeural", "30 Sal Larki - Swara": "hi-IN-SwaraNeural"},
    "🇬🇧 ENGLISH - US": {"20 Sal Larka - Guy": "en-US-GuyNeural", "20 Sal Larki - Jenny": "en-US-JennyNeural"},
    "🇸🇦 ARABIC - عربي": {"20 Sal Larka - Hamed": "ar-SA-HamedNeural", "20 Sal Larki - Zariyah": "ar-SA-ZariyahNeural"},
}
TIME_OPTIONS = {"15 Second":15,"30 Second":30,"60 Second (1 Minute)":60,"2 Minutes":120,"5 Minutes":300,"10 Minutes":600}
PURE_SINDHI_TTS_MAP = {"ٻ":"ب","ڄ":"ج","ڃ":"نج","ڇ":"چھ","ٽ":"ٹ","ٺ":"ٹھ","ٿ":"تھ","ڌ":"دھ","ڏ":"ڈ","ڊ":"ڈ","ڍ":"ڈھ","ڀ":"بھ","ڦ":"پھ","ڪ":"ک","ڳ":"گ","ڱ":"نگ","ڻ":"ن","ڙ":"ڑ","ھ":"ہ"}

# === 1 MINUTE PROMPTS - NO PASTE NEEDED ===
PROMPTS = {
    "SINDHI 1 MIN": "السلام عليڪم! منهنجا پيارا ڀائرو ۽ ڀينرون! اميد آهي ته توهان سڀ خيريت سان هوندا! اڄ مان توهان لاءِ هڪ خاص پيغام کڻي آيو آهيان! مهر مارٽ جو خالص ماکي هڪ سئو سيڪڙو خالص آهي! قدرت جو تحفو! ڪو به ملاوٽ ناهي! هي ماکي توهان جي صحت لاءِ تمام گهڻو فائديمند آهي! ٻارن کان وٺي وڏن تائين سڀئي استعمال ڪري سگهن ٿا! صرف ٻه هزار نو سو پنجاهتر روپين ۾! سڄي پاڪستان ۾ فري هوم ڊليوري! هي آفر محدود وقت لاءِ آهي! جلدي آرڊر ڪريو! مهرباني!",
    "URDU 1 MIN": "السلام علیکم! میرے پیارے بھائیو اور بہنو! امید ہے آپ سب خیریت سے ہوں گے! آج میں آپ کے لیے ایک خاص پیغام لایا ہوں! مہر مارٹ کا خالص شہد سو فیصد خالص ہے! قدرت کا تحفہ! کوئی ملاوٹ نہیں! یہ شہد آپ کی صحت کے لیے بہت مفید ہے! بچوں سے بڑوں تک سب استعمال کر سکتے ہیں! صرف دو ہزار نو سو پچھتر روپے میں! پورے پاکستان میں فری ہوم ڈلیوری! یہ آفر محدود وقت کے لیے ہے! جلدی آرڈر کریں!",
    "HINDI 1 MIN": "नमस्ते मेरे प्यारे भाइयो और बहनो! उम्मीद है आप सब ठीक होंगे! आज मैं आपके लिए खास संदेश लाया हूं! Mehar Mart का शुद्ध शहद सौ प्रतिशत शुद्ध है! कुदरत का तोहफा! कोई मिलावट नहीं! ये शहद आपकी सेहत के लिए बहुत फायदेमंद है! बच्चों से बड़ों तक सब इस्तेमाल कर सकते हैं! सिर्फ 2975 रुपये में! All Pakistan में फ्री होम डिलीवरी! ये ऑफर सीमित समय के लिए है! जल्दी ऑर्डर करो!",
    "ENGLISH 1 MIN": "Hello my dear brothers and sisters! I hope you all are well! Today I bring a special message! Mehar Mart pure honey is one hundred percent pure! A gift from nature! No adulteration! Very beneficial for your health! From children to elders everyone can use! Only for 2975 rupees! Free home delivery all over Pakistan! Limited time offer! Order quickly! Thank you!",
}

st.markdown("### 🌍 LANGUAGE CATEGORY")
lang = st.selectbox("Language:", list(VOICE_CATEGORIES.keys()), index=0)
voices = VOICE_CATEGORIES[lang]
vkey = st.selectbox(f"{lang} Voice:", list(voices.keys()), index=0)
vname = voices[vkey]
time_label = st.selectbox("⏱️ TIME:", list(TIME_OPTIONS.keys()), index=2)
MAX_SEC = TIME_OPTIONS[time_label]
MAX_CHARS = MAX_SEC * 14

if "main_text" not in st.session_state: st.session_state.main_text = ""

# === PASTE FIX BUTTONS - NO PASTE NEEDED ===
st.markdown("### 📄 1 Click me Prompt Load karo - Paste ki zarurat nahi!")
c1,c2 = st.columns(2)
with c1:
    if st.button("📄 SINDHI 1 MIN", use_container_width=True, type="primary"):
        st.session_state.main_text = PROMPTS["SINDHI 1 MIN"]
        st.rerun()
    if st.button("📄 HINDI 1 MIN", use_container_width=True):
        st.session_state.main_text = PROMPTS["HINDI 1 MIN"]
        st.rerun()
with c2:
    if st.button("📄 URDU 1 MIN", use_container_width=True):
        st.session_state.main_text = PROMPTS["URDU 1 MIN"]
        st.rerun()
    if st.button("📄 ENGLISH 1 MIN", use_container_width=True):
        st.session_state.main_text = PROMPTS["ENGLISH 1 MIN"]
        st.rerun()

# File upload for paste issue
uploaded = st.file_uploader("📁 Ya .txt file upload karo (Paste nahi ho to):", type=["txt"])
if uploaded:
    st.session_state.main_text = uploaded.read().decode("utf-8")
    st.rerun()

if st.button("🗑️ CLEAR", use_container_width=True):
    st.session_state.main_text = ""
    st.rerun()

text_input = st.text_area(f"✍️ Yahan text ({MAX_CHARS} max) - {lang} - {time_label}:", value=st.session_state.main_text, height=220, max_chars=MAX_CHARS)
if text_input != st.session_state.main_text: st.session_state.main_text = text_input

st.progress(min(len(text_input)/MAX_CHARS,1.0) if text_input else 0)
rate_opt = st.select_slider("Speed:", options=["-5%","-15%","+10%"], value="-5%")

def clean_text(text, lang_cat):
    if not text.strip(): return ""
    t=text.strip()
    t=t.replace("पाकिस्तान","Pakistan").replace("پاڪستان","Pakistan").replace("پاکستان","Pakistan")
    if "SINDHI" in lang_cat:
        for sc,tc in PURE_SINDHI_TTS_MAP.items(): t=t.replace(sc,tc)
        t=t.replace("آهي","آآہی ").replace("آهي","آآہی ").replace("سجي","سجّی")
    return t

async def gen_edge(text, voice, rate, path):
    for _ in range(5):
        try:
            if os.path.exists(path): os.remove(path)
            await edge_tts.Communicate(text=text, voice=voice, rate=rate).save(path)
            if os.path.exists(path) and os.path.getsize(path)>800: return True
        except: await asyncio.sleep(1)
    return False

async def gen_dynamic(text, voice, rate, lang_cat):
    if not text.strip(): raise Exception("Khali hai!")
    if os.path.exists("voice"): shutil.rmtree("voice")
    os.makedirs("voice", exist_ok=True)
    cleaned=clean_text(text, lang_cat)
    path=f"voice/{voice.replace('-','_')}.mp3"
    ok=await gen_edge(cleaned, voice, rate, path)
    if not ok: raise Exception("Voice fail")
    return path

if st.button(f"🎙️ {vkey} - Voice Banao", type="primary", use_container_width=True):
    if not text_input.strip(): st.error("⚠️ Pehle button se prompt load karo!")
    else:
        with st.spinner("Bana raha..."):
            try:
                path=asyncio.run(gen_dynamic(text_input, vname, rate_opt, lang))
                st.balloons()
                st.success(f"✅ Ready! {len(text_input)} chars - {MAX_SEC} sec!")
                st.audio(path)
                with open(path,"rb") as f: st.download_button("📥 Download", f, file_name=f"Voice_{MAX_SEC}s.mp3")
            except Exception as e: st.error(f"Error: {e}")
