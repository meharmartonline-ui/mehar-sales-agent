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

st.set_page_config(page_title="MEHAR V102 - ALFABET FIX", layout="centered")
st.title("MEHAR V102 - WORLD STUDIO 🌍 - Alfabet Clear Voice")

if groq_client: st.success("✅ Groq Connected")
else: st.info("ℹ️ Free Mode - Alfabet Voice Fix - System Same!")

TIME_OPTIONS = {"10 Second":10,"15 Second":15,"30 Second":30,"60 Second (1 Min)":60,"1 Minute":60,"2 Minutes":120,"5 Minutes":300,"10 Minutes":600}

VOICES = {
    "SINDHI": {"Asad 10-60 Sal Larka": "ur-PK-AsadNeural", "Uzma Larki": "ur-PK-UzmaNeural"},
    "URDU": {"Asad Larka": "ur-PK-AsadNeural", "Uzma Larki": "ur-PK-UzmaNeural"},
    "HINDI": {"Madhur Larka": "hi-IN-MadhurNeural", "Swara Larki": "hi-IN-SwaraNeural"},
    "ENGLISH": {"Guy Larka": "en-US-GuyNeural", "Jenny Larki": "en-US-JennyNeural"},
    "ARABIC": {"Hamed Larka": "ar-SA-HamedNeural", "Zariyah Larki": "ar-SA-ZariyahNeural"},
}

# ===== ALFABET SEARCH - REAL 52 SINDHI, URDU 38, HINDI 52, ARABIC 28 =====

# SINDHI 52 Alfabet - Voice ke liye Urdu readable - Display me original rahega
SINDHI_TTS_MAP = {
    "ٻ":"ب", "ڄ":"ج", "جھ":"جہ", "ڃ":"نج", "ڄھ":"جھ",
    "ڏ":"ڈ", "ڊ":"ڈ", "ڌ":"دھ", "ڍ":"ڈھ", "ڊھ":"ڈھ",
    "ٽ":"ٹ", "ٺ":"ٹھ", "ٿ":"تھ", "ڀ":"بھ", "ٻھ":"بھ",
    "ڦ":"پھ", "پھ":"پھ", "ڳ":"گ", "ڱ":"نگ", "ڻ":"ن", "ڃ":"نچ",
    "ڪ":"ک", "گھ":"گھ", "ھ":"ہ", "ۃ":"ہ",
    "۽":"اور", "۾":"میں", "لا":"لا",
    # Extra Sindhi diacritics saaf
    "آ":"آ", "ء":"", "ً":"", "ٌ":"", "ٍ":"", "َ":"", "ُ":"", "ِ":"", "ّ":"", "ْ":"",
}

# URDU 38 Alfabet + 6 extra - Voice clear
URDU_TTS_MAP = {
    "ٹھ":"ٹھ", "بھ":"بھ", "پھ":"پھ", "تھ":"تھ", "جھ":"جھ",
    "چھ":"چھ", "دھ":"دھ", "ڈھ":"ڈھ", "ڑھ":"ڑھ", "کھ":"کھ", "گھ":"گھ", "لھ":"لھ", "مھ":"مھ", "نھ":"نھ",
    "ھ":"ہ", "ہ":"ہ", "ۃ":"ہ",
    # Arabic char to Urdu
    "ي":"ی", "ك":"ک", "ے":"ے", "ہ":"ہ",
}

# HINDI 52 Alfabet (13 Vowel + 33 Consonant + 2 + 4) - Voice clear
HINDI_TTS_MAP = {
    "ऱ":"र", "ऩ":"न", "फ़":"फ़", "क़":"क़", "ख़":"ख़", "ग़":"ग़", "ज़":"ज़", "ड़":"ड़", "ढ़":"ढ़",
    "ऑ":"ऑ", "ऎ":"ए", "ऒ":"ओ",
    "।":"۔", "॥":"۔",
    # Pakistan English to Hindi for clear voice
    "Pakistan":"पाकिस्तान", "Mehar":"महर", "Mart":"मार्ट",
}

# ARABIC 28 Alfabet - Tashkeel hatana for clear voice
ARABIC_TTS_MAP = {
    "پ":"ب", "چ":"ج", "ژ":"ز", "گ":"ك", "ک":"ك", "ی":"ي", "ے":"ي",
    # Tashkeel remove for clear
    "َ":"", "ُ":"", "ِ":"", "ً":"", "ٌ":"", "ٍ":"", "ّ":"", "ْ":"", "ٰ":"", "ٓ":"", "ٔ":"", "ٕ":"",
    "ـ":"",
}

def clean_for_voice(text, lang):
    """Alfabet ke hisab se voice saaf - Display text change nahi"""
    t = text.strip()
    
    if "SINDHI" in lang:
        # Sindhi 52 -> Urdu voice friendly
        for k,v in SINDHI_TTS_MAP.items():
            t = t.replace(k,v)
        # Extra clear - Jumla break
        t = t.replace("!","! ").replace("۔","۔ ").replace("،","، ")
        t = t.replace("  "," ")
        return t
    
    if "URDU" in lang:
        for k,v in URDU_TTS_MAP.items():
            t = t.replace(k,v)
        t = t.replace("!","! ").replace("۔","۔ ").replace("،","، ")
        # 38 alfabet clear - No English
        t = t.replace("Pakistan","پاکستان").replace("Mehar Mart","مہر مارٹ")
        return t
    
    if "HINDI" in lang:
        for k,v in HINDI_TTS_MAP.items():
            t = t.replace(k,v)
        # English to Hindi for ucharan
        t = t.replace("Pakistan","पाकिस्तान").replace("Mehar Mart","महर मार्ट")
        t = t.replace("!","! ").replace("।","। ").replace(", ",", ")
        t = t.replace("  "," ")
        return t
    
    if "ARABIC" in lang:
        for k,v in ARABIC_TTS_MAP.items():
            t = t.replace(k,v)
        t = t.replace("Pakistan","باكستان").replace("Mehar Mart","مهر مارت")
        t = t.replace("!","! ").replace("،","، ").replace("۔","۔ ")
        return t
    
    if "ENGLISH" in lang:
        # English clear
        t = t.replace("۔",". ").replace("،",", ").replace("  "," ")
        return t
    
    return t

def translate_fix(text, target):
    if target == "SINDHI": return text
    if target == "URDU":
        if groq_client:
            try:
                p = f"Translate to Urdu only: {text}"
                chat = groq_client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":p}], temperature=0.2, max_tokens=2000)
                out = chat.choices[0].message.content.strip()
                if len(out)>20 and "PLEASE SELECT" not in out: return out
            except: pass
        return "السلام علیکم! میرے پیارے بھائیو اور بہنو! امید ہے آپ سب خیریت سے ہوں گے! آج میں آپ کے لیے ایک خاص اور خوشی کا پیغام لایا ہوں! مہر مارٹ کا خالص شہد سو فیصد خالص اور قدرتی ہے! یہ شہد ہر قسم کی ملاوٹ سے پاک ہے! قدرت کا انمول تحفہ! یہ آپ کی صحت، طاقت اور توانائی کے لیے بہت فائدیمند ہے! چھوٹے بچوں سے لے کر بڑوں تک ہر کوئی استعمال کر سکتا ہے! روزانہ ایک چمچ آپ کو بیماریوں سے بچائے گا! صرف دو ہزار نو سو پچھتر روپے میں! پورے پاکستان میں فری ہوم ڈلیوری!"
    if groq_client and target in ["HINDI","ENGLISH","ARABIC"]:
        try:
            mp = {"HINDI":"Hindi Devanagari","ENGLISH":"English","ARABIC":"Arabic"}
            p = f"Translate to {mp[target]} only: {text}"
            chat = groq_client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":p}], temperature=0.2, max_tokens=2000)
            out = chat.choices[0].message.content.strip()
            if len(out)>20: return out
        except: pass
    if target=="HINDI": return "नमस्ते मेरे प्यारे भाइयो और बहनो! उम्मीद है आप सब ठीक होंगे! आज मैं आपके लिए एक खास और खुशी का संदेश लाया हूं! महर मार्ट का शुद्ध शहद सौ प्रतिशत शुद्ध है! मिलावट से मुक्त! कुदरत का अनमोल तोहफा! सेहत के लिए बहुत फायदेमंद! बच्चे से बड़ों तक सब इस्तेमाल कर सकते हैं! रोज एक चम्मच बीमारी से बचाएगा! सिर्फ 2975 रुपये में! पूरे पाकिस्तान में फ्री डिलीवरी!"
    if target=="ENGLISH": return "Hello my dear brothers and sisters! I hope you are all well! Today I bring a special and happy message! Mehar Mart pure honey is one hundred percent pure and natural! Free from adulteration! A priceless gift of nature! Very beneficial for health, strength and energy! Everyone from children to elders can use! One spoon daily protects from diseases! Only 2975 rupees! Free home delivery all over Pakistan!"
    if target=="ARABIC": return "السلام عليكم! اخواني واخواتي الاعزاء! اتمنى ان تكونوا بخير! اليوم احمل لكم رسالة خاصة وسعيدة! عسل مهر مارت نقي مائة بالمائة وطبيعي! خالي من الغش! هدية ثمينة من الطبيعة! مفيد جدا للصحة والقوة والطاقة! يمكن للجميع استخدامه من الاطفال الى الكبار! ملعقة يوميا تحمي من الامراض! فقط 2975 روبية! توصيل مجاني في جميع انحاء باكستان!"
    return text

async def gen_edge(text, voice, rate, path):
    for _ in range(5):
        try:
            if os.path.exists(path): os.remove(path)
            await edge_tts.Communicate(text=text, voice=voice, rate=rate).save(path)
            if os.path.exists(path) and os.path.getsize(path)>800: return True
        except: await asyncio.sleep(1)
    return False

for lang in VOICES:
    if f"text_{lang}" not in st.session_state: st.session_state[f"text_{lang}"] = ""

master = st.text_area("✍️ MASTER PROMPT:", height=150, key="master_text_widget", placeholder="Sindhi prompt...")
if st.button("🔄 ALL 5 BOX BHARO - ALFABET FIX", type="primary", use_container_width=True):
    src = st.session_state.get("master_text_widget","").strip()
    if not src: st.error("Pehle likho!")
    else:
        with st.spinner("Converting..."):
            for LANG in VOICES:
                trans = translate_fix(src, LANG)
                st.session_state[f"text_{LANG}"] = trans
                st.session_state[f"ta_{LANG}"] = trans
        st.success("✅ All Converted - Alfabet Fixed!")
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
        # Alfabet info
        if LANG=="SINDHI": st.caption("Sindhi 52 Alfabet: ٻ ڄ ڏ ڳ ٽ ٺ ٿ ڀ ڦ ڌ ڊ ڍ ڙ ڃ ڱ ڻ ڪ - Voice clear map")
        if LANG=="URDU": st.caption("Urdu 38 Alfabet: ٹھ بھ پھ تھ جھ چھ دھ ڈھ کھ گھ - Voice clear")
        if LANG=="HINDI": st.caption("Hindi 52 Alfabet: अ-ह + क्ष त्र ज्ञ + फ़ क़ ख़ ग़ ज़ ड़ ढ़ - Voice clear")
        if LANG=="ARABIC": st.caption("Arabic 28 Alfabet: ا ب ت ث ج ح خ د ذ ر ز س ش ص ض ط ظ ع غ ف ق ك ل م ن ه و ي - Tashkeel clear")
        rate = st.select_slider(f"Speed {LANG}:", options=["-5%","-15%","+10%"], value="-5%", key=f"sp_{LANG}")
        if st.button(f"🎙️ {LANG} Voice Banao {MAX_SEC}s - {vkey}", key=f"gen_{LANG}", type="primary", use_container_width=True):
            if not txt.strip(): st.error(f"{LANG} khali!")
            else:
                with st.spinner(f"{LANG} {vkey}... Alfabet clear..."):
                    try:
                        # Alfabet search ke hisab se voice clear
                        cleaned = clean_for_voice(txt, LANG)
                        os.makedirs("voice", exist_ok=True)
                        fp = f"voice/{LANG}_{MAX_SEC}_{vkey[:4]}.mp3"
                        ok = asyncio.run(gen_edge(cleaned, vname, rate, fp))
                        if ok:
                            st.success(f"✅ {LANG} {vkey} Clear Voice Ready! Alfabet Fixed!")
                            st.audio(fp)
                            with open(fp,"rb") as f: st.download_button(f"📥 Download {LANG} {vkey}", f, file_name=f"{LANG}_{vkey}_{MAX_SEC}s_Clear.mp3", key=f"dl_{LANG}")
                        else: st.error("Voice fail")
                    except Exception as e: st.error(f"{e}")

st.caption("V102 - Alfabet Fix: Sindhi 52, Urdu 38, Hindi 52, Arabic 28 - Ucharan Clear - System Same")
