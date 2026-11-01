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

st.set_page_config(page_title="MEHAR V96 - 5 BOX STUDIO", layout="centered")
st.markdown("<style>textarea{spellcheck:false !important}</style>", unsafe_allow_html=True)
st.title("MEHAR V96 - 5 BOX STUDIO 🌍")
if groq_client: st.success("✅ Groq Connected - All Box Auto Convert!")
else: st.warning("⚠️ Groq Key nahi - Box phir bhi chalenge")

TIME_OPTIONS = {
    "10 Second":10, "15 Second":15, "30 Second":30, "60 Second (1 Min)":60,
    "1 Minute":60, "2 Minutes":120, "5 Minutes":300, "10 Minutes":600
}

PURE_SINDHI_MAP = {"ٻ":"ب","ڄ":"ج","ڃ":"نج","ڇ":"چھ","ٽ":"ٹ","ٺ":"ٹھ","ٿ":"تھ","ڌ":"دھ","ڏ":"ڈ","ڊ":"ڈ","ڍ":"ڈھ","ڀ":"بھ","ڦ":"پھ","ڪ":"ک","ڳ":"گ","ڱ":"نگ","ڻ":"ن","ڙ":"ڑ","ھ":"ہ"}

PROMPTS = {
    "SINDHI": "السلام عليڪم! منهنجا پيارا ڀائرو ۽ ڀينرون! اميد آهي ته توهان سڀ خيريت سان هوندا! اڄ مان توهان لاءِ هڪ خاص پيغام کڻي آيو آهيان! مهر مارٽ جو خالص ماکي هڪ سئو سيڪڙو خالص آهي! قدرت جو تحفو! ڪو به ملاوٽ ناهي! هي ماکي صحت لاءِ تمام گهڻو فائديمند آهي! ٻارن کان وٺي وڏن تائين سڀ استعمال ڪري سگهن ٿا! صرف ٻه هزار نو سو پنجاهتر روپين ۾! سڄي پاڪستان ۾ فري هوم ڊليوري!",
    "URDU": "السلام علیکم! میرے پیارے بھائیو اور بہنو! امید ہے آپ خیریت سے ہوں گے! آج میں خاص پیغام لایا ہوں! مہر مارٹ کا خالص شہد سو فیصد خالص ہے! قدرت کا تحفہ! کوئی ملاوٹ نہیں! صحت کے لیے بہت مفید! بچوں سے بڑوں تک سب استعمال کر سکتے ہیں! صرف 2975 روپے میں! پورے پاکستان میں فری ہوم ڈلیوری!",
    "HINDI": "नमस्ते! मेरे प्यारे भाइयो और बहनो! उम्मीद है आप ठीक होंगे! आज खास संदेश लाया हूं! Mehar Mart का शुद्ध शहद सौ प्रतिशत शुद्ध है! कुदरत का तोहफा! कोई मिलावट नहीं! सेहत के लिए बहुत फायदेमंद! बच्चों से बड़ों तक सब इस्तेमाल कर सकते हैं! सिर्फ 2975 रुपये में! All Pakistan में फ्री होम डिलीवरी!",
    "ENGLISH": "Hello my dear brothers and sisters! I hope you all are well! Today I bring special message! Mehar Mart pure honey is 100 percent pure! Gift from nature! No adulteration! Very beneficial for health! From children to elders everyone can use! Only for 2975 rupees! Free home delivery all over Pakistan!",
    "ARABIC": "السلام عليكم! إخواني وأخواتي الأعزاء! أتمنى أن تكونوا جميعا بخير! اليوم أحمل لكم رسالة خاصة! عسل مهر مارت نقي مائة بالمائة! هدية من الطبيعة! لا يوجد غش! مفيد جدا لصحتكم! يمكن للجميع استخدامه من الأطفال إلى الكبار! فقط ب 2975 روبية! توصيل مجاني في جميع أنحاء باكستان!",
}

VOICES = {
    "SINDHI": {"Asad 10-60 Sal Larka": "ur-PK-AsadNeural", "Uzma 10-60 Sal Larki": "ur-PK-UzmaNeural"},
    "URDU": {"Asad Larka": "ur-PK-AsadNeural", "Uzma Larki": "ur-PK-UzmaNeural"},
    "HINDI": {"Madhur Larka": "hi-IN-MadhurNeural", "Swara Larki": "hi-IN-SwaraNeural"},
    "ENGLISH": {"Guy Larka": "en-US-GuyNeural", "Jenny Larki": "en-US-JennyNeural", "Aria Larki": "en-US-AriaNeural"},
    "ARABIC": {"Hamed Larka": "ar-SA-HamedNeural", "Zariyah Larki": "ar-SA-ZariyahNeural"},
}

def groq_convert(text, target):
    if not groq_client or not text.strip(): return text
    try:
        prompt = f"Translate to {target}. Keep Pakistan as Pakistan. Only translated text. Text: {text}"
        chat = groq_client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":prompt}], temperature=0.1, max_tokens=2000)
        return chat.choices[0].message.content.strip()
    except: return text

def clean_text(text, lang):
    t=text.strip()
    t=t.replace("पाकिस्तान","Pakistan").replace("پاڪستان","Pakistan").replace("پاکستان","Pakistan")
    if "SINDHI" in lang:
        for k,v in PURE_SINDHI_MAP.items(): t=t.replace(k,v)
        t=t.replace("آهي","آآہی ").replace("سجي","سجّی")
    return t

async def gen_edge(text, voice, rate, path):
    for _ in range(5):
        try:
            if os.path.exists(path): os.remove(path)
            await edge_tts.Communicate(text=text, voice=voice, rate=rate).save(path)
            if os.path.exists(path) and os.path.getsize(path)>800: return True
        except: await asyncio.sleep(1)
    return False

# Init session for 5 boxes
for lang in VOICES:
    if f"text_{lang}" not in st.session_state: st.session_state[f"text_{lang}"] = ""
    if f"time_{lang}" not in st.session_state: st.session_state[f"time_{lang}"] = "60 Second (1 Min)"

# === 5 BOXES ===
for LANG in ["SINDHI", "URDU", "HINDI", "ENGLISH", "ARABIC"]:
    with st.expander(f"{'🇵🇰' if LANG in ['SINDHI','URDU'] else '🇮🇳' if LANG=='HINDI' else '🇬🇧' if LANG=='ENGLISH' else '🇸🇦'} {LANG} BOX - {st.session_state[f'time_{LANG}']}", expanded=(LANG=="SINDHI")):
        
        col1, col2 = st.columns(2)
        with col1:
            time_sel = st.selectbox(f"⏱️ {LANG} Time:", list(TIME_OPTIONS.keys()), index=3, key=f"time_sel_{LANG}")
            st.session_state[f"time_{LANG}"] = time_sel
            MAX_SEC = TIME_OPTIONS[time_sel]
        with col2:
            vkey = st.selectbox(f"🎤 {LANG} Voice:", list(VOICES[LANG].keys()), key=f"voice_{LANG}")
            vname = VOICES[LANG][vkey]
        
        MAX_CHARS = MAX_SEC * 14
        
        c1,c2,c3 = st.columns(3)
        with c1:
            if st.button(f"📄 {LANG} Prompt Load", key=f"load_{LANG}", use_container_width=True, type="primary" if LANG=="SINDHI" else "secondary"):
                st.session_state[f"text_{LANG}"] = PROMPTS[LANG]
                st.rerun()
        with c2:
            if st.button(f"🔄 Groq To {LANG}", key=f"groq_{LANG}", use_container_width=True, disabled=not groq_client):
                # Take text from any other box that has text
                source_text = ""
                for other in VOICES:
                    if st.session_state[f"text_{other}"].strip():
                        source_text = st.session_state[f"text_{other}"]
                        break
                if source_text:
                    st.session_state[f"text_{LANG}"] = groq_convert(source_text, LANG)
                    st.rerun()
        with c3:
            if st.button(f"🗑️ Clear {LANG}", key=f"clear_{LANG}", use_container_width=True):
                st.session_state[f"text_{LANG}"] = ""
                st.rerun()
        
        text_val = st.text_area(f"✍️ {LANG} Text ({MAX_CHARS} max) - {time_sel}:", value=st.session_state[f"text_{LANG}"], height=150, max_chars=MAX_CHARS, key=f"area_{LANG}")
        if text_val != st.session_state[f"text_{LANG}"]: st.session_state[f"text_{LANG}"] = text_val
        
        st.progress(min(len(text_val)/MAX_CHARS,1.0) if text_val else 0)
        rate = st.select_slider(f"Speed {LANG}:", options=["-5%","-15%","+10%"], value="-5%", key=f"rate_{LANG}")
        
        if st.button(f"🎙️ {LANG} - {vkey} - Voice Banao ({MAX_SEC}s)", key=f"gen_{LANG}", type="primary", use_container_width=True):
            if not text_val.strip(): st.error("⚠️ Pehle prompt load karo!")
            else:
                with st.spinner(f"{LANG} {vkey} bana raha..."):
                    try:
                        cleaned = clean_text(text_val, LANG)
                        path = f"voice_{LANG}.mp3"
                        if os.path.exists("voice"): shutil.rmtree("voice")
                        os.makedirs("voice", exist_ok=True)
                        full_path = f"voice/{path}"
                        ok = asyncio.run(gen_edge(cleaned, vname, rate, full_path))
                        if ok:
                            st.balloons()
                            st.success(f"✅ {LANG} Ready! {len(text_val)} chars - {MAX_SEC}s!")
                            st.audio(full_path)
                            with open(full_path,"rb") as f: st.download_button(f"📥 {LANG} Download {MAX_SEC}s", f, file_name=f"{LANG}_{MAX_SEC}s.mp3", key=f"dl_{LANG}")
                        else: st.error("Voice fail")
                    except Exception as e: st.error
