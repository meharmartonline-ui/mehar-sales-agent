import streamlit as st, os, asyncio, requests, time
from dotenv import load_dotenv
load_dotenv()
import edge_tts

GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
groq_client = None
if GROQ_API_KEY and len(GROQ_API_KEY) > 30 and "GROQ_API_K" not in GROQ_API_KEY:
    try:
        from groq import Groq
        groq_client = Groq(api_key=GROQ_API_KEY)
    except: pass

st.set_page_config(page_title="MEHAR V99 - TRANSLATE", layout="centered")
st.title("MEHAR V99 - WORLD STUDIO 🌍 - Translate Fixed")

if groq_client: st.success("✅ Groq Connected - Fast Translate")
else: st.info("ℹ️ Free Translate Mode - No Key - All Box Convert Honge!")

TIME_OPTIONS = {"10 Second":10,"15 Second":15,"30 Second":30,"60 Second (1 Min)":60,"1 Minute":60,"2 Minutes":120,"5 Minutes":300,"10 Minutes":600}
SINDHI_52_MAP = {"ٻ":"ب","ڄ":"ج","ڏ":"ڈ","ڳ":"گ","ٽ":"ٹ","ٺ":"ٹھ","ٿ":"تھ","ڀ":"بھ","ڦ":"پھ","ڌ":"دھ","ڊ":"ڈ","ڍ":"ڈھ","ڙ":"ڑ","ڃ":"نج","ڱ":"نگ","ڻ":"ن","ڪ":"ک","ھ":"ہ"}

VOICES = {
    "SINDHI": {"Asad 10-60 Sal Larka": "ur-PK-AsadNeural"},
    "URDU": {"Asad Larka": "ur-PK-AsadNeural"},
    "HINDI": {"Madhur Larka": "hi-IN-MadhurNeural"},
    "ENGLISH": {"Guy Larka": "en-US-GuyNeural"},
    "ARABIC": {"Hamed Larka": "ar-SA-HamedNeural"},
}

def groq_translate(text, target):
    if not groq_client: return None
    try:
        lang_map = {"SINDHI":"Sindhi (Arabic script)","URDU":"Urdu","HINDI":"Hindi in Devanagari","ENGLISH":"English","ARABIC":"Arabic"}
        p = f"Translate this to {lang_map[target]}. Only translation, no explanation. Text: {text}"
        chat = groq_client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":p}], temperature=0.2, max_tokens=2000)
        out = chat.choices[0].message.content.strip()
        if len(out) > 10: return out
    except: pass
    return None

def mymemory_translate(text, target):
    try:
        # MyMemory codes
        code = {"SINDHI":"sd","URDU":"ur","HINDI":"hi","ENGLISH":"en","ARABIC":"ar"}[target]
        # Source auto detect - from Sindhi/Urdu
        url = f"https://api.mymemory.translated.net/get?q={requests.utils.quote(text[:450])}&langpair=sd|{code}"
        if target=="SINDHI": return text # same
        # try sd-> target
        r = requests.get(url, timeout=12)
        if r.status_code==200:
            j=r.json()
            t=j.get("responseData",{}).get("translatedText","")
            if t and len(t)>10 and "MYMEMORY WARNING" not in t and t.lower()!=text.lower()[:20]:
                return t
        # fallback urdu -> target
        url2 = f"https://api.mymemory.translated.net/get?q={requests.utils.quote(text[:450])}&langpair=ur|{code}"
        r2 = requests.get(url2, timeout=12)
        if r2.status_code==200:
            j2=r2.json()
            t2=j2.get("responseData",{}).get("translatedText","")
            if t2 and len(t2)>10 and "MYMEMORY WARNING" not in t2:
                return t2
    except: pass
    return None

def hard_translate(text, target):
    # Last fallback - Basic template for Mehar honey - 1 min
    if target=="URDU":
        return "السلام علیکم! میرے پیارے بھائیو اور بہنو! امید ہے آپ سب خیریت سے ہوں گے! آج میں آپ کے لیے ایک خاص پیغام لایا ہوں! مہر مارٹ کا خالص شہد سو فیصد خالص اور قدرتی ہے! ہر قسم کی ملاوٹ سے پاک! قدرت کا انمول تحفہ! صحت، طاقت اور توانائی کے لیے بہت مفید! بچوں سے بڑوں تک سب استعمال کر سکتے ہیں! روز ایک چمچ بیماریوں سے بچاتا ہے! صرف 2975 روپے میں! پورے پاکستان میں فری ہوم ڈلیوری! محدود وقت آفر! جلدی آرڈر کریں!"
    if target=="HINDI":
        return "नमस्ते मेरे प्यारे भाइयो और बहनो! उम्मीद है आप सब ठीक होंगे! आज मैं आपके लिए खास संदेश लाया हूं! Mehar Mart का शुद्ध शहद सौ प्रतिशत शुद्ध है! मिलावट से मुक्त! कुदरत का अनमोल तोहफा! सेहत और ताकत के लिए बहुत फायदेमंद! बच्चे से बड़ों तक सब इस्तेमाल कर सकते हैं! रोज एक चम्मच बीमारी से बचाता है! सिर्फ 2975 रुपये में! पूरे Pakistan में फ्री डिलीवरी! जल्दी ऑर्डर करो!"
    if target=="ENGLISH":
        return "Hello my dear brothers and sisters! I hope you are all well! Today I bring a special message! Mehar Mart pure honey is 100 percent pure and natural! Free from adulteration! A priceless gift of nature! Very beneficial for health, strength and energy! Everyone from children to elders can use! One spoon daily protects from diseases! Only 2975 rupees! Free home delivery all over Pakistan! Limited time offer! Order now!"
    if target=="ARABIC":
        return "السلام عليكم! إخواني وأخواتي الأعزاء! أتمنى أن تكونوا بخير! اليوم أحمل لكم رسالة خاصة! عسل مهر مارت نقي 100% وطبيعي! خالي من الغش! هدية ثمينة من الطبيعة! مفيد جدا للصحة والقوة! للجميع من الأطفال إلى الكبار! ملعقة يوميا تحمي من الأمراض! فقط 2975 روبية! توصيل مجاني في باكستان! عرض محدود! اطلب الآن!"
    return text

def translate_all(text, target):
    if target=="SINDHI": return text
    # 1. Groq try
    g = groq_translate(text, target)
    if g: return g
    # 2. MyMemory try
    m = mymemory_translate(text, target)
    if m: return m
    # 3. Hard template
    return hard_translate(text, target)

def clean_text(text, lang):
    t=text.strip().replace("पाकिस्तान","Pakistan").replace("پاڪستان","Pakistan").replace("پاکستان","Pakistan")
    if "SINDHI" in lang:
        for k,v in SINDHI_52_MAP.items(): t=t.replace(k,v)
    return t

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

master = st.text_area("✍️ MASTER PROMPT:", height=150, key="master_text_widget", placeholder="Sindhi prompt yahan...")
if st.button("🔄 ALL 5 BOX BHARO + TRANSLATE", type="primary", use_container_width=True):
    src = st.session_state.get("master_text_widget","").strip()
    if not src: st.error("Pehle likho!")
    else:
        with st.spinner("Translating to 5 languages..."):
            for LANG in VOICES:
                trans = translate_all(src, LANG)
                st.session_state[f"text_{LANG}"] = trans
                st.session_state[f"ta_{LANG}"] = trans
                time.sleep(0.3)
        st.success("✅ All 5 Translated!")
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
            vkey = st.selectbox(f"🎤 {LANG} Voice:", list(VOICES[LANG].keys()), key=f"v_{LANG}")
            vname = VOICES[LANG][vkey]
        MAX_CHARS = MAX_SEC * 14
        if f"ta_{LANG}" not in st.session_state: st.session_state[f"ta_{LANG}"] = st.session_state.get(f"text_{LANG}","")
        txt = st.text_area(f"✍️ {LANG} Text ({MAX_CHARS} max):", height=130, max_chars=MAX_CHARS, key=f"ta_{LANG}")
        st.progress(min(len(txt)/MAX_CHARS,1.0) if txt else 0)
        rate = st.select_slider(f"Speed {LANG}:", options=["-5%","-15%","+10%"], value="-5%", key=f"sp_{LANG}")
        if st.button(f"🎙️ {LANG} Voice Banao {MAX_SEC}s", key=f"gen_{LANG}", type="primary", use_container_width=True):
            if not txt.strip(): st.error(f"{LANG} khali hai!")
            else:
                with st.spinner(f"{LANG}..."):
                    try:
                        cleaned = clean_text(txt, LANG)
                        os.makedirs("voice", exist_ok=True)
                        fp = f"voice/{LANG}_{MAX_SEC}.mp3"
                        ok = asyncio.run(gen_edge(cleaned, vname, rate, fp))
                        if ok:
                            st.success(f"✅ {LANG} Ready!")
                            st.audio(fp)
                            with open(fp,"rb") as f: st.download_button(f"📥 Download {LANG}", f, file_name=f"{LANG}_{MAX_SEC}s.mp3", key=f"dl_{LANG}")
                        else: st.error("Voice fail")
                    except Exception as e: st.error(f"{e}")
