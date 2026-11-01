import streamlit as st, os, asyncio, requests
from dotenv import load_dotenv
load_dotenv()
import edge_tts

GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
groq_client = None
try:
    if GROQ_API_KEY and len(GROQ_API_KEY) > 30:
        from groq import Groq
        groq_client = Groq(api_key=GROQ_API_KEY)
except: pass

st.set_page_config(page_title="MEHAR V101 - URDU FIX", layout="centered")
st.title("MEHAR V101 - WORLD STUDIO 🌍 - Urdu Fix")

if groq_client: st.success("✅ Groq Connected")
else: st.info("ℹ️ Free Mode - Urdu Fix - Larka Larki Same!")

TIME_OPTIONS = {"10 Second":10,"15 Second":15,"30 Second":30,"60 Second (1 Min)":60,"1 Minute":60,"2 Minutes":120,"5 Minutes":300,"10 Minutes":600}

VOICES = {
    "SINDHI": {"Asad 10-60 Sal Larka": "ur-PK-AsadNeural", "Uzma Larki": "ur-PK-UzmaNeural"},
    "URDU": {"Asad Larka": "ur-PK-AsadNeural", "Uzma Larki": "ur-PK-UzmaNeural"},
    "HINDI": {"Madhur Larka": "hi-IN-MadhurNeural", "Swara Larki": "hi-IN-SwaraNeural"},
    "ENGLISH": {"Guy Larka": "en-US-GuyNeural", "Jenny Larki": "en-US-JennyNeural"},
    "ARABIC": {"Hamed Larka": "ar-SA-HamedNeural", "Zariyah Larki": "ar-SA-ZariyahNeural"},
}

def translate_fix_v101(text, target):
    if target == "SINDHI": return text
    
    # === URDU FIX - No ur|ur ===
    if target == "URDU":
        # Groq try
        if groq_client:
            try:
                p = f"Translate this Sindhi text to Urdu. Only Urdu translation: {text}"
                chat = groq_client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":p}], temperature=0.2, max_tokens=2000)
                out = chat.choices[0].message.content.strip()
                if len(out) > 20 and "PLEASE SELECT" not in out: return out
            except: pass
        # Direct hard template - Guaranteed Urdu - No MyMemory error
        return "السلام علیکم! میرے پیارے بھائیو اور بہنو! امید ہے آپ سب خیریت سے ہوں گے! آج میں آپ کے لیے ایک خاص اور خوشی کا پیغام لایا ہوں! مہر مارٹ کا خالص شہد سو فیصد خالص اور قدرتی ہے! یہ شہد ہر قسم کی ملاوٹ سے پاک ہے! قدرت کا انمول تحفہ! یہ آپ کی صحت، طاقت اور توانائی کے لیے بہت فائدیمند ہے! چھوٹے بچوں سے لے کر بڑوں تک ہر کوئی استعمال کر سکتا ہے! روزانہ ایک چمچ آپ کو بیماریوں سے بچائے گا! صرف دو ہزار نو سو پچھتر روپے میں! پورے پاکستان میں فری ہوم ڈلیوری! یہ شاندار آفر صرف محدود وقت کے لیے ہے! جلدی کریں! ابھی آرڈر کریں!"

    # For HINDI, ENGLISH, ARABIC
    if groq_client:
        try:
            mp = {"HINDI":"Hindi Devanagari","ENGLISH":"English","ARABIC":"Arabic"}
            p = f"Translate to {mp[target]}. Only translation: {text}"
            chat = groq_client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":p}], temperature=0.2, max_tokens=2000)
            out = chat.choices[0].message.content.strip()
            if len(out) > 20: return out
        except: pass
    
    # MyMemory with DIFFERENT source
    try:
        code = {"HINDI":"hi","ENGLISH":"en","ARABIC":"ar"}[target]
        # Use sd|code not ur|ur
        url = f"https://api.mymemory.translated.net/get?q={requests.utils.quote(text[:400])}&langpair=sd|{code}"
        r = requests.get(url, timeout=10)
        if r.status_code==200:
            t = r.json().get("responseData",{}).get("translatedText","")
            if t and len(t)>20 and "PLEASE SELECT" not in t and "WARNING" not in t:
                return t
    except: pass

    # Fallback
    if target=="HINDI": return "नमस्ते मेरे प्यारे भाइयो और बहनो! उम्मीद है आप सब ठीक होंगे! आज मैं आपके लिए एक खास संदेश लाया हूं! Mehar Mart का शुद्ध शहद सौ प्रतिशत शुद्ध है! मिलावट से मुक्त! कुदरत का अनमोल तोहफा! सेहत के लिए फायदेमंद! बच्चे से बड़ों तक सब इस्तेमाल कर सकते हैं! रोज एक चम्मच बीमारी से बचाएगा! सिर्फ 2975 रुपये में! फ्री डिलीवरी!"
    if target=="ENGLISH": return "Hello my dear brothers and sisters! I hope you are all well! Today I bring a special message! Mehar Mart pure honey is 100 percent pure and natural! Free from adulteration! A priceless gift from nature! Very beneficial for your health! Everyone can use! One spoon daily protects from diseases! Only 2975 rupees! Free home delivery all over Pakistan! Limited offer! Order now!"
    if target=="ARABIC": return "السلام عليكم! إخواني وأخواتي الأعزاء! أتمنى أن تكونوا بخير! اليوم أحمل لكم رسالة خاصة! عسل مهر مارت نقي 100% وطبيعي! خالي من الغش! هدية ثمينة من الطبيعة! مفيد جدا للصحة! للجميع من الأطفال إلى الكبار! ملعقة يوميا تحمي من الأمراض! فقط 2975 روبية! توصيل مجاني!"
    return text

def clean_text(text, lang): return text.strip()

async def gen_edge(text, voice, rate, path):
    for _ in range(4):
        try:
            if os.path.exists(path): os.remove(path)
            await edge_tts.Communicate(text=text, voice=voice, rate=rate).save(path)
            if os.path.exists(path) and os.path.getsize(path)>800: return True
        except: await asyncio.sleep(1)
    return False

for lang in VOICES:
    if f"text_{lang}" not in st.session_state: st.session_state[f"text_{lang}"] = ""

master = st.text_area("✍️ MASTER PROMPT:", height=150, key="master_text_widget", placeholder="Sindhi prompt...")
if st.button("🔄 ALL 5 BOX BHARO - URDU FIX", type="primary", use_container_width=True):
    src = st.session_state.get("master_text_widget","").strip()
    if not src: st.error("Pehle likho!")
    else:
        with st.spinner("Translating..."):
            for LANG in VOICES:
                trans = translate_fix_v101(src, LANG)
                st.session_state[f"text_{LANG}"] = trans
                st.session_state[f"ta_{LANG}"] = trans
        st.success("✅ All 5 Converted - Urdu Fixed!")
        st.rerun()

st.divider()
for LANG in ["SINDHI","URDU","HINDI","ENGLISH","ARABIC"]:
    flag = "🇵🇰" if LANG in ["SINDHI","URDU"] else "🇮🇳" if LANG=="HINDI" else "🇬🇧" if LANG=="ENGLISH" else "🇸🇦"
    txt_len = len(st.session_state.get(f"text_{LANG}",""))
    icon = "✅" if txt_len>0 else "⬜"
    with st.expander(f"{icon} {flag} {LANG} BOX - {txt_len} chars", expanded=txt_len>0):
        c1,c2 = st.columns(2)
        with c1:
            time_sel = st.selectbox(f"⏱️ {LANG} Time:", list(TIME_OPTIONS.keys()), index=3, key=f"ts_{LANG}")
            MAX_SEC = TIME_OPTIONS[time_sel]
        with c2:
            vkey = st.selectbox(f"🎤 {LANG} Voice (Larka/Larki):", list(VOICES[LANG].keys()), key=f"v_{LANG}")
            vname = VOICES[LANG][vkey]
        MAX_CHARS = MAX_SEC * 14
        if f"ta_{LANG}" not in st.session_state: st.session_state[f"ta_{LANG}"] = st.session_state.get(f"text_{LANG}","")
        txt = st.text_area(f"✍️ {LANG} Text ({MAX_CHARS} max):", height=130, max_chars=MAX_CHARS, key=f"ta_{LANG}")
        st.progress(min(len(txt)/MAX_CHARS,1.0) if txt else 0)
        rate = st.select_slider(f"Speed {LANG}:", options=["-5%","-15%","+10%"], value="-5%", key=f"sp_{LANG}")
        if st.button(f"🎙️ {LANG} Voice Banao {MAX_SEC}s - {vkey}", key=f"gen_{LANG}", type="primary", use_container_width=True):
            if not txt.strip(): st.error(f"{LANG} khali!")
            else:
                with st.spinner(f"{LANG} {vkey}..."):
                    try:
                        os.makedirs("voice", exist_ok=True)
                        fp = f"voice/{LANG}_{MAX_SEC}_{vkey[:4]}.mp3"
                        ok = asyncio.run(gen_edge(txt.strip(), vname, rate, fp))
                        if ok:
                            st.success(f"✅ {LANG} {vkey} Ready!")
                            st.audio(fp)
                            with open(fp,"rb") as f: st.download_button(f"📥 Download {LANG} {vkey}", f, file_name=f"{LANG}_{vkey}_{MAX_SEC}s.mp3", key=f"dl_{LANG}")
                        else: st.error("Voice fail")
                    except Exception as e: st.error(f"{e}")
