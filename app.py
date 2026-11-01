import streamlit as st, os, asyncio, shutil, re
from dotenv import load_dotenv
load_dotenv()
import edge_tts

GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
try:
    from groq import Groq
    groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
except:
    groq_client = None

st.set_page_config(page_title="MEHAR V97 - ALL IN ONE", layout="centered")
st.markdown("<style>textarea{spellcheck:false !important}</style>", unsafe_allow_html=True)

st.title("MEHAR V97 - WORLD STUDIO 🌍")
if groq_client:
    st.success("✅ Groq Connected - 1 Prompt = All 5 Language Auto!")
else:
    st.error("⚠️ GROQ_API_KEY nahi - .env ya Secrets me dalo")

TIME_OPTIONS = {
    "10 Second":10, "15 Second":15, "30 Second":30, "60 Second (1 Min)":60,
    "1 Minute":60, "2 Minutes":120, "5 Minutes":300, "10 Minutes":600
}

# === SINDHI 52 ALFABET RESEARCH - FULL FIX - SYSTEM SAME ===
# Sindhi 52 Harf - Official - Edge TTS bug fix
SINDHI_52_MAP = {
    # 4 Implisive - Main bug
    "ٻ": "ب", "ڄ": "ج", "ڏ": "ڈ", "ڳ": "گ",
    # Heavy letters - TTS fail hote hain
    "ٽ": "ٹ", "ٺ": "ٹھ", "ٿ": "تھ", "ڀ": "بھ", "ڦ": "پھ", 
    "ڌ": "دھ", "ڊ": "ڈ", "ڍ": "ڈھ", "ڙ": "ڑ",
    # Ng sounds
    "ڃ": "نج", "ڱ": "نگ", "ڻ": "ن",
    # Sindhi Kaf Gaf
    "ڪ": "ک", "ک": "کھ", "گ": "گ", 
    # Extra fix - Aahe lamba
    "ھ": "ہ", "۾": "م", "۽": "اور", "ۡ": "",
    # Alif + Wao + Ye forms
    "آ": "آ", "ي": "ی", "ٖ": "", "ٗ": "", "ِ": "", "َ": "", "ُ": ""
}

PROMPTS = {
    "SINDHI": "السلام عليڪم! منهنجا پيارا ڀائرو ۽ ڀينرون! اميد آهي ته توهان سڀ خيريت سان هوندا! اڄ مان توهان لاءِ هڪ خاص پيغام کڻي آيو آهيان! مهر مارٽ جو خالص ماکي هڪ سئو سيڪڙو خالص آهي! قدرت جو تحفو! ڪو به ملاوٽ ناهي! هي ماکي صحت لاءِ تمام گهڻو فائديمند آهي! ٻارن کان وٺي وڏن تائين سڀ استعمال ڪري سگهن ٿا! صرف ٻه هزار نو سو پنجاهتر روپين ۾! سڄي پاڪستان ۾ فري هوم ڊليوري!",
    "URDU": "السلام علیکم! میرے پیارے بھائیو اور بہنو! امید ہے آپ خیریت سے ہوں گے! آج میں خاص پیغام لایا ہوں! مہر مارٹ کا خالص شہد سو فیصد خالص ہے! قدرت کا تحفہ! کوئی ملاوٹ نہیں! صحت کے لیے بہت مفید! بچوں سے بڑوں تک سب استعمال کر سکتے ہیں! صرف 2975 روپے میں! پورے پاکستان میں فری ہوم ڈلیوری!",
    "HINDI": "नमस्ते! मेरे प्यारे भाइयो और बहनो! उम्मीद है आप ठीक होंगे! आज खास संदेश लाया हूं! Mehar Mart का शुद्ध शहद सौ प्रतिशत शुद्ध है! कुदरत का तोहफा! कोई मिलावट नहीं! सेहत के लिए बहुत फायदेमंद! बच्चों से बड़ों तक सब इस्तेमाल कर सकते हैं! सिर्फ 2975 रुपये में! All Pakistan में फ्री होम डिलीवरी!",
    "ENGLISH": "Hello my dear brothers and sisters! I hope you all are well! Today I bring special message! Mehar Mart pure honey is 100 percent pure! Gift from nature! No adulteration! Very beneficial for health! From children to elders everyone can use! Only for 2975 rupees! Free home delivery all over Pakistan!",
    "ARABIC": "السلام عليكم! إخواني وأخواتي الأعزاء! أتمنى أن تكونوا بخير! اليوم أحمل لكم رسالة خاصة! عسل مهر مارت نقي مائة بالمائة! هدية من الطبيعة! لا غش! مفيد جدا للصحة! للجميع من الأطفال إلى الكبار! فقط ب 2975 روبية! توصيل مجاني في جميع أنحاء باكستان!",
}

VOICES = {
    "SINDHI": {"Asad 10-60 Sal Larka": "ur-PK-AsadNeural", "Uzma 10-60 Sal Larki": "ur-PK-UzmaNeural"},
    "URDU": {"Asad Larka": "ur-PK-AsadNeural", "Uzma Larki": "ur-PK-UzmaNeural"},
    "HINDI": {"Madhur Larka": "hi-IN-MadhurNeural", "Swara Larki": "hi-IN-SwaraNeural"},
    "ENGLISH": {"Guy Larka": "en-US-GuyNeural", "Jenny Larki": "en-US-JennyNeural"},
    "ARABIC": {"Hamed Larka": "ar-SA-HamedNeural", "Zariyah Larki": "ar-SA-ZariyahNeural"},
}

def groq_convert(text, target):
    if not groq_client or not text.strip(): return text
    try:
        prompt = f"Translate this to {target} language. Keep 'Pakistan' as 'Pakistan' always, never translate to Bharat/India. Only give translated text, no explanation. Text: {text}"
        chat = groq_client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":prompt}], temperature=0.1, max_tokens=2500)
        return chat.choices[0].message.content.strip()
    except Exception as e:
        return text

def clean_text(text, lang):
    t=text.strip()
    t=t.replace("पाकिस्तान","Pakistan").replace("پاڪستان","Pakistan").replace("پاکستان","Pakistan").replace("باكستان","Pakistan")
    if "SINDHI" in lang:
        for k,v in SINDHI_52_MAP.items(): t=t.replace(k,v)
        # Lamba Aahe bug fix - Voice me chhota bolta tha
        t=t.replace("آهي","آآہی ").replace("آهي","آآہی ").replace("آہے","آآہے ").replace("تہ","تہہ ")
    return t

async def gen_edge(text, voice, rate, path):
    for _ in range(5):
        try:
            if os.path.exists(path): os.remove(path)
            await edge_tts.Communicate(text=text, voice=voice, rate=rate).save(path)
            if os.path.exists(path) and os.path.getsize(path)>800: return True
        except: await asyncio.sleep(1)
    return False

# Init
for lang in VOICES:
    if f"text_{lang}" not in st.session_state: st.session_state[f"text_{lang}"] = ""
    if f"time_{lang}" not in st.session_state: st.session_state[f"time_{lang}"] = "60 Second (1 Min)"
if "master_text" not in st.session_state: st.session_state["master_text"] = ""

# ===== MASTER BOX - 1 PROMPT = ALL LANGUAGE - PEHLE WALA SYSTEM SAME =====
st.markdown("### 🌍 MASTER PROMPT - 1 BAR LIKHO = ALL 5 BOX ME AUTO CONVERT!")
st.info("💡 Yahan ek bar likho - Neeche wala button dabao - Sindhi Urdu Hindi English Arabic sab me khud convert ho jayega - Pehle wala system!")

master = st.text_area("✍️ MASTER PROMPT (Koi bhi language me likho - Sindhi/Urdu/Hindi/English):", value=st.session_state["master_text"], height=150, placeholder="Yahan ek bar likho... Jaise: السلام علیکم! مہر مارٹ کا شہد... Ya Hello Mehar Mart honey...")
if master != st.session_state["master_text"]: st.session_state["master_text"] = master

colM1, colM2 = st.columns(2)
with colM1:
    if st.button("🔄 1 PROMPT = ALL 5 BOX AUTO CONVERT (Groq)", type="primary", use_container_width=True, disabled=not groq_client):
        if not st.session_state["master_text"].strip():
            st.error("Pehle Master me kuch likho!")
        else:
            with st.spinner("Groq All 5 Language me convert kar raha... 10 sec"):
                src = st.session_state["master_text"]
                for LANG in VOICES:
                    # Sindhi ke liye Sindhi, Urdu ke liye Urdu...
                    converted = groq_convert(src, LANG)
                    st.session_state[f"text_{LANG}"] = converted
                st.success("✅ All 5 Box me convert ho gaya - Neeche check karo!")
                st.rerun()
with colM2:
    if st.button("🗑️ All Clear", use_container_width=True):
        st.session_state["master_text"] = ""
        for LANG in VOICES: st.session_state[f"text_{LANG}"] = ""
        st.rerun()

st.divider()

# ===== 5 BOX - HAR BOX ME APNA TIME DROPDOWN - SYSTEM SAME =====
for LANG in ["SINDHI", "URDU", "HINDI", "ENGLISH", "ARABIC"]:
    flag = "🇵🇰" if LANG in ["SINDHI","URDU"] else "🇮🇳" if LANG=="HINDI" else "🇬🇧" if LANG=="ENGLISH" else "🇸🇦"
    with st.expander(f"{flag} {LANG} BOX - {st.session_state[f'time_{LANG}']} - {len(st.session_state[f'text_{LANG}'])} chars", expanded=(LANG=="SINDHI")):
        
        c1,c2 = st.columns(2)
        with c1:
            time_sel = st.selectbox(f"⏱️ {LANG} Time Limit:", list(TIME_OPTIONS.keys()), index=3, key=f"ts_{LANG}")
            st.session_state[f"time_{LANG}"] = time_sel
            MAX_SEC = TIME_OPTIONS[time_sel]
        with c2:
            vkey = st.selectbox(f"🎤 {LANG} Voice (10-60 Sal):", list(VOICES[LANG].keys()), key=f"v_{LANG}")
            vname = VOICES[LANG][vkey]
        
        MAX_CHARS = MAX_SEC * 14
        
        b1,b2 = st.columns(2)
        with b1:
            if st.button(f"📄 {LANG} Example Load", key=f"load_{LANG}", use_container_width=True):
                st.session_state[f"text_{LANG}"] = PROMPTS[LANG]
                st.rerun()
        with b2:
            if st.button(f"🗑️ Clear {LANG}", key=f"cl_{LANG}", use_container_width=True):
                st.session_state[f"text_{LANG}"] = ""
                st.rerun()
        
        # Text box - Auto converted text yahan ayega
        txt = st.text_area(f"✍️ {LANG} Text ({MAX_CHARS} max) - {time_sel}:", value=st.session_state[f"text_{LANG}"], height=130, max_chars=MAX_CHARS, key=f"ta_{LANG}")
        if txt != st.session_state[f"text_{LANG}"]: st.session_state[f"text_{LANG}"] = txt
        
        st.progress(min(len(txt)/MAX_CHARS,1.0) if txt else 0)
        rate = st.select_slider(f"Speed {LANG}:", options=["-5%","-15%","+10%"], value="-5%", key=f"sp_{LANG}")
        
        if st.button(f"🎙️ {LANG} Voice Banao - {MAX_SEC}s - {vkey}", key=f"gen_{LANG}", type="primary", use_container_width=True):
            if not txt.strip(): st.error(f"{LANG} box khali hai - Upar Master se convert karo!")
            else:
                with st.spinner(f"{LANG} bana raha..."):
                    try:
                        cleaned = clean_text(txt, LANG)
                        if os.path.exists("voice"): shutil.rmtree("voice")
                        os.makedirs("voice", exist_ok=True)
                        fp = f"voice/{LANG}_{MAX_SEC}.mp3"
                        ok = asyncio.run(gen_edge(cleaned, vname, rate, fp))
                        if ok:
                            st.balloons()
                            st.success(f"✅ {LANG} Ready! {MAX_SEC} sec!")
                            st.audio(fp)
                            with open(fp,"rb") as f: st.download_button(f"📥 {LANG} Download {MAX_SEC}s", f, file_name=f"{LANG}_{MAX_SEC}s.mp3", key=f"dl_{LANG}")
                        else: st.error("Voice fail")
                    except Exception as e: st.error(f"Error: {e}")

st.caption("V97 - System Same - 1 Master Prompt = All 5 Box Auto - Har Box me Time 10s-10min - Sindhi 52 Harf Fix - Arabic Added")
