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

st.set_page_config(page_title="MEHAR V102 FIXED - ASALAM", layout="centered")
st.title("MEHAR V102 FIXED 🌍 - Asalam + Jo Likha Wahi")

if groq_client: st.success("✅ Groq Connected - Asalam Fix Active")
else: st.info("ℹ️ Free Mode - Asalam Fix Active - No Namaste!")

TIME_OPTIONS = {"10 Second":10,"15 Second":15,"30 Second":30,"60 Second (1 Min)":60,"1 Minute":60,"2 Minutes":120,"5 Minutes":300,"10 Minutes":600}

VOICES = {
    "SINDHI": {"Asad 10-60 Sal Larka": "ur-PK-AsadNeural", "Uzma Larki": "ur-PK-UzmaNeural"},
    "URDU": {"Asad Larka": "ur-PK-AsadNeural", "Uzma Larki": "ur-PK-UzmaNeural"},
    "HINDI": {"Madhur Larka": "hi-IN-MadhurNeural", "Swara Larki": "hi-IN-SwaraNeural", "Uzma Larki (Asalam Best)": "ur-PK-UzmaNeural"},
    "ENGLISH": {"Guy Larka": "en-US-GuyNeural", "Jenny Larki": "en-US-JennyNeural"},
    "ARABIC": {"Hamed Larka": "ar-SA-HamedNeural", "Zariyah Larki": "ar-SA-ZariyahNeural"},
}

# ===== ALFABET FIX + ASALAM FIX + 0:01 FIX =====

SINDHI_TTS_MAP = {
    "ٻ":"ب", "ڄ":"ج", "جھ":"جہ", "ڃ":"نج", "ڏ":"ڈ", "ڊ":"ڈ", "ڌ":"دھ", "ڍ":"ڈھ", "ٽ":"ٹ", "ٺ":"ٹھ", "ٿ":"تھ", "ڀ":"بھ", "ڦ":"پھ", "ڳ":"گ", "ڱ":"نگ", "ڻ":"ن", "ڪ":"ک", "گھ":"گھ", "ھ":"ہ", "۽":"اور", "۾":"میں", "ً":"", "ٌ":"", "ٍ":"", "َ":"", "ُ":"", "ِ":"", "ّ":"", "ْ":"",
}

URDU_TTS_MAP = {
    "ٹھ":"ٹھ", "بھ":"بھ", "پھ":"پھ", "تھ":"تھ", "جھ":"جھ", "چھ":"چھ", "دھ":"دھ", "ڈھ":"ڈھ", "کھ":"کھ", "گھ":"گھ", "ھ":"ہ", "ي":"ی", "ك":"ک",
}

HINDI_TTS_MAP = {
    "ऱ":"र", "ऩ":"न", "फ़":"फ़", "क़":"क़", "ख़":"ख़", "ग़":"ग़", "ज़":"ज़", "ड़":"ड़", "ढ़":"ढ़", "।":"۔",
    "Pakistan":"पाकिस्तान", "Mehar":"महर", "Mart":"मार्ट", "Bharat":"पाकिस्तान", "Namaste":"अस्सलाम ओ अलैकुम",
}

ARABIC_TTS_MAP = {
    "پ":"ب", "چ":"ج", "ژ":"ز", "گ":"ك", "ک":"ك", "ی":"ي", "ے":"ي",
    "َ":"", "ُ":"", "ِ":"", "ً":"", "ٌ":"", "ٍ":"", "ّ":"", "ْ":"", "ـ":"",
}

def clean_for_voice(text, lang):
    t = text.strip()
    # 0:01 FIX - 100% se 1 sec banta hai
    t = t.replace("100%", "100 percent")
    t = t.replace("100 %", "100 percent")
    t = t.replace("%", " percent ")
    t = t.replace("  ", " ")
    
    if "SINDHI" in lang:
        for k,v in SINDHI_TTS_MAP.items():
            t = t.replace(k,v)
        t = t.replace("!","! ").replace("۔","۔ ").replace("،","، ")
        return t
    if "URDU" in lang:
        for k,v in URDU_TTS_MAP.items():
            t = t.replace(k,v)
        t = t.replace("Pakistan","پاکستان").replace("Mehar Mart","مہر مارٹ")
        return t
    if "HINDI" in lang:
        for k,v in HINDI_TTS_MAP.items():
            t = t.replace(k,v)
        # ASALAM FIX - Namaste -> Asalam, Bharat -> Pakistan - Jo Likha Wahi
        t = t.replace("नमस्ते", "अस्सलाम ओ अलैकुम")
        t = t.replace("नमस्कार", "अस्सलाम ओ अलैकुम")
        t = t.replace("भारत", "पाकिस्तान")
        t = t.replace("Bharat", "पाकिस्तान")
        t = t.replace("Pakistan","पाकिस्तान").replace("Mehar Mart","महर मार्ट")
        t = t.replace("!","! ").replace("।","। ")
        return t
    if "ARABIC" in lang:
        for k,v in ARABIC_TTS_MAP.items():
            t = t.replace(k,v)
        t = t.replace("Pakistan","باكستان")
        return t
    if "ENGLISH" in lang:
        t = t.replace("۔",". ").replace("،",", ")
        return t
    return t

def translate_fix(text, target):
    if target == "SINDHI": return text
    if target == "URDU":
        if groq_client:
            try:
                p = f"Translate to Urdu only - Use Asalam O Alaikum, not Salam, keep Pakistan: {text}"
                chat = groq_client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":p}], temperature=0.2, max_tokens=2000)
                out = chat.choices[0].message.content.strip()
                if len(out)>20 and "PLEASE SELECT" not in out: return out
            except: pass
        return "السلام علیکم! میرے پیارے بھائیو اور بہنو! امید ہے آپ سب خیریت سے ہوں گے! آج میں آپ کے لیے ایک خاص اور خوشی کا پیغام لایا ہوں! مہر مارٹ کا خالص شہد سو فیصد خالص اور قدرتی ہے! یہ شہد ہر قسم کی ملاوٹ سے پاک ہے! قدرت کا انمول تحفہ! یہ آپ کی صحت، طاقت اور توانائی کے لیے بہت فائدیمند ہے! چھوٹے بچوں سے لے کر بڑوں تک ہر کوئی استعمال کر سکتا ہے! روزانہ ایک چمچ آپ کو بیماریوں سے بچائے گا! صرف دو ہزار نو سو پچھتر روپے میں! پورے پاکستان میں فری ہوم ڈلیوری!"

    if groq_client and target in ["HINDI","ENGLISH","ARABIC"]:
        try:
            mp = {"HINDI":"Hindi Devanagari - IMPORTANT: Use Asalam O Alaikum not Namaste, use Pakistan not Bharat","ENGLISH":"English","ARABIC":"Arabic"}
            p = f"Translate to {mp[target]} only - Must use Asalam O Alaikum, never Namaste, must use Pakistan never Bharat: {text}"
            chat = groq_client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":p}], temperature=0.2, max_tokens=2000)
            out = chat.choices[0].message.content.strip()
            if target=="HINDI":
                out = out.replace("नमस्ते", "अस्सलाम ओ अलैकुम").replace("नमस्कार", "अस्सलाम ओ अलैकुम").replace("भारत", "पाकिस्तान").replace("Bharat", "पाकिस्तान")
            if len(out)>20: return out
        except: pass
    
    # HINDI FALLBACK - YAHAN BUG THA - AB ASALAM FIX
    if target=="HINDI": return "अस्सलाम ओ अलैकुम! मेरे प्यारे भाइयो और बहनो! उम्मीद है आप सब ठीक होंगे! आज मैं आपके लिए एक खास और खुशी का संदेश लाया हूं! महर मार्ट का शुद्ध शहद सौ प्रतिशत शुद्ध है! मिलावट से मुक्त! कुदरत का अनमोल तोहफा! सेहत के लिए बहुत फायदेमंद! बच्चे से बड़ों तक सब इस्तेमाल कर सकते हैं! रोज एक चम्मच बीमारी से बचाएगा! सिर्फ 2975 रुपये में! पूरे पाकिस्तान में फ्री डिलीवरी!"
    if target=="ENGLISH": return "Asalam O Alaikum! My dear brothers and sisters! I hope you are all well! Today I bring a special and happy message! Mehar Mart pure honey is one hundred percent pure and natural! Free from adulteration! A priceless gift of nature! Very beneficial for health, strength and energy! Everyone from children to elders can use! One spoon daily protects from diseases! Only 2975 rupees! Free home delivery all over Pakistan!"
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

master = st.text_area("✍️ MASTER PROMPT:", height=150, key="master_text_widget", placeholder="Sindhi prompt likho... Jo likha wahi sab me jayega...")
if st.button("🔄 ALL 5 BOX BHARO - ASALAM FIX - JO LIKHA WAHI", type="primary", use_container_width=True):
    src = st.session_state.get("master_text_widget","").strip()
    if not src: st.error("Pehle likho!")
    else:
        with st.spinner("Converting - Asalam Fix - Jo Likha Wahi..."):
            for LANG in VOICES:
                trans = translate_fix(src, LANG)
                st.session_state[f"text_{LANG}"] = trans
                st.session_state[f"ta_{LANG}"] = trans
        st.success("✅ All Converted - Asalam Fix - No Namaste! Jo Likha Wahi!")
        st.rerun()

st.divider()
for LANG in ["SINDHI","URDU","HINDI","ENGLISH","ARABIC"]:
    flag = "🇵🇰" if LANG in ["SINDHI","URDU"] else "🇮🇳" if LANG=="HINDI" else "🇬🇧" if LANG=="ENGLISH" else "🇸🇦"
    txt_len = len(st.session_state.get(f"text_{LANG}",""))
    icon = "✅" if txt_len>0 else "⬜"
    with st.expander(f"{icon} {flag} {LANG} BOX - {txt_len} chars", expanded=txt_len>0 or LANG=="HINDI"):
        c1,c2 = st.columns(2)
        with c1:
            time_sel = st.selectbox(f"⏱️ {LANG} Time:", list(TIME_OPTIONS.keys()), index=3, key=f"ts_{LANG}")
            MAX_SEC = TIME_OPTIONS[time_sel]
        with c2:
            vkey = st.selectbox(f"🎤 {LANG} Voice (Larka/Larki):", list(VOICES[LANG].keys()), key=f"v_{LANG}")
            vname = VOICES[LANG][vkey]
        MAX_CHARS = MAX_SEC * 14
        if f"ta_{LANG}" not in st.session_state: st.session_state[f"ta_{LANG}"] = st.session_state.get(f"text_{LANG}","")
        txt = st.text_area(f"✍️ {LANG} Text ({MAX_CHARS} max) - Jo Likha Wahi Bolega:", height=130, max_chars=MAX_CHARS, key=f"ta_{LANG}")
        st.progress(min(len(txt)/MAX_CHARS,1.0) if txt else 0)
        if LANG=="SINDHI": st.caption("Sindhi 52 Alfabet - Voice clear")
        if LANG=="URDU": st.caption("Urdu 38 Alfabet - Voice clear")
        if LANG=="HINDI": st.caption("Hindi 52 Alfabet - Asalam Fix - No Namaste - Bharat -> Pakistan - Jo Likha Wahi")
        if LANG=="ARABIC": st.caption("Arabic 28 Alfabet - Tashkeel clear")
        rate = st.select_slider(f"Speed {LANG}:", options=["-5%","-15%","+10%"], value="-5%", key=f"sp_{LANG}")
        if st.button(f"🎙️ {LANG} Voice Banao {MAX_SEC}s - {vkey} - Jo Likha Wahi", key=f"gen_{LANG}", type="primary", use_container_width=True):
            if not txt.strip(): st.error(f"{LANG} khali!")
            else:
                with st.spinner(f"{LANG} {vkey}... Asalam Fix... Jo Likha Wahi..."):
                    try:
                        cleaned = clean_for_voice(txt, LANG)
                        os.makedirs("voice", exist_ok=True)
                        fp = f"voice/{LANG}_{MAX_SEC}_{vkey[:4]}.mp3"
                        ok = asyncio.run(gen_edge(cleaned, vname, rate, fp))
                        if ok:
                            st.success(f"✅ {LANG} {vkey} Ready! Asalam Fix! Jo Likha Wahi Bola! No Namaste!")
                            st.audio(fp)
                            with open(fp,"rb") as f: st.download_button(f"📥 Download {LANG} {vkey} - {MAX_SEC}s", f, file_name=f"{LANG}_{vkey}_{MAX_SEC}s_ASALAM_FIX.mp3", key=f"dl_{LANG}")
                        else: st.error("Voice fail - Dobara try karo")
                    except Exception as e: st.error(f"{e}")

st.caption("V102 FIXED - Asalam Fix - Hindi me Asalam O Alaikum, No Namaste, Bharat->Pakistan, 0:01 Fix, Jo Likha Wahi, Time Box 10-15-30+1-2-5-10 Min")
