import streamlit as st, os, asyncio, shutil
from dotenv import load_dotenv
load_dotenv()
import edge_tts

GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
try:
    from groq import Groq
    groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
except:
    groq_client = None

st.set_page_config(page_title="MEHAR V97.1 - FIX", layout="centered")
st.title("MEHAR V97.1 - WORLD STUDIO 🌍")

if groq_client:
    st.success(f"✅ Groq Connected - Key: {GROQ_API_KEY[:10]}...")
else:
    st.error("❌ Groq Key nahi - Secrets me GROQ_API_KEY dalo - Phir bhi box copy se bharenge")

TIME_OPTIONS = {"10 Second":10,"15 Second":15,"30 Second":30,"60 Second (1 Min)":60,"1 Minute":60,"2 Minutes":120,"5 Minutes":300,"10 Minutes":600}
SINDHI_52_MAP = {"ٻ":"ب","ڄ":"ج","ڏ":"ڈ","ڳ":"گ","ٽ":"ٹ","ٺ":"ٹھ","ٿ":"تھ","ڀ":"بھ","ڦ":"پھ","ڌ":"دھ","ڊ":"ڈ","ڍ":"ڈھ","ڙ":"ڑ","ڃ":"نج","ڱ":"نگ","ڻ":"ن","ڪ":"ک","ھ":"ہ","۾":"م","۽":"اور"}

VOICES = {
    "SINDHI": {"Asad 10-60 Sal Larka": "ur-PK-AsadNeural", "Uzma Larki": "ur-PK-UzmaNeural"},
    "URDU": {"Asad Larka": "ur-PK-AsadNeural", "Uzma Larki": "ur-PK-UzmaNeural"},
    "HINDI": {"Madhur Larka": "hi-IN-MadhurNeural", "Swara Larki": "hi-IN-SwaraNeural"},
    "ENGLISH": {"Guy Larka": "en-US-GuyNeural", "Jenny Larki": "en-US-JennyNeural"},
    "ARABIC": {"Hamed Larka": "ar-SA-HamedNeural", "Zariyah Larki": "ar-SA-ZariyahNeural"},
}

def groq_convert_fixed(text, target):
    if not groq_client or not text.strip():
        return text # Bina Groq ke same text copy
    try:
        # MODEL FIX - Purana model band - Naya model
        prompt = f"Translate to {target}. Keep Pakistan as Pakistan. Only translation. Text: {text}"
        chat = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # FIXED MODEL
            messages=[{"role":"user","content":prompt}],
            temperature=0.1,
            max_tokens=2500
        )
        out = chat.choices[0].message.content.strip()
        return out if out else text
    except Exception as e:
        st.warning(f"Groq Error {target}: {e} - Same text copy kar raha")
        return text # Fail ho to same text copy - Box khali nahi rahega

def clean_text(text, lang):
    t=text.strip().replace("पाकिस्तान","Pakistan").replace("پاڪستان","Pakistan").replace("پاکستان","Pakistan")
    if "SINDHI" in lang:
        for k,v in SINDHI_52_MAP.items(): t=t.replace(k,v)
        t=t.replace("آهي","آآہی ").replace("تہ","تہہ ")
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

# === MASTER BOX - FIXED ===
st.markdown("### 🌍 MASTER - 1 Bar Likho = All 5 Box Bhar Jayenge!")
st.info("Yahan likho - Button dabao - All box bhar jayenge - Groq ho to translate, nahi to same copy!")

master = st.text_area("✍️ MASTER PROMPT:", value=st.session_state["master_text"], height=150, placeholder="Jaise: السلام علیکم مہر مارٹ کا شہد خالص ہے...", key="master_area")

# Update session on change
if master != st.session_state["master_text"]:
    st.session_state["master_text"] = master

col1, col2 = st.columns(2)
with col1:
    if st.button("🔄 ALL 5 BOX BHARO - 1 CLICK", type="primary", use_container_width=True):
        src = st.session_state["master_text"] or master
        if not src.strip():
            st.error("⚠️ Pehle upar Master me kuch likho!")
        else:
            with st.spinner("All 5 box bhar raha..."):
                # FIX: Bina Groq ke bhi bharenge - Same text copy
                for LANG in VOICES:
                    if groq_client:
                        converted = groq_convert_fixed(src, LANG)
                    else:
                        converted = src # No Groq = same copy - Khali nahi
                    st.session_state[f"text_{LANG}"] = converted
                st.success("✅ All 5 Box bhar gaye - Neeche kholo - Sab me text hai!")
                st.balloons()
                # Force rerun nahi - same page pe dikhega
with col2:
    if st.button("🗑️ All Clear", use_container_width=True):
        st.session_state["master_text"] = ""
        for LANG in VOICES: st.session_state[f"text_{LANG}"] = ""
        st.rerun()

# Quick test - Direct load without Groq
st.markdown("**Agar Master kaam na kare to direct example:**")
if st.button("📄 Test: All 5 Box me Example Bharo (Bina Groq)", use_container_width=True):
    st.session_state["text_SINDHI"] = "السلام عليڪم! مهر مارٽ جو خالص ماکي تمام سٺو آهي! صرف 2975 ۾! فري ڊليوري!"
    st.session_state["text_URDU"] = "السلام علیکم! مہر مارٹ کا خالص شہد بہت اچھا ہے! صرف 2975 میں! فری ڈلیوری!"
    st.session_state["text_HINDI"] = "नमस्ते! Mehar Mart का शुद्ध शहद बहुत अच्छा है! सिर्फ 2975 में! फ्री डिलीवरी!"
    st.session_state["text_ENGLISH"] = "Hello! Mehar Mart pure honey is very good! Only 2975! Free delivery!"
    st.session_state["text_ARABIC"] = "السلام عليكم! عسل مهر مارت نقي جيد جدا! فقط 2975! توصيل مجاني!"
    st.success("✅ Test example bhar gaya - Neeche box kholo!")
    st.rerun()

st.divider()

# 5 BOX
for LANG in ["SINDHI","URDU","HINDI","ENGLISH","ARABIC"]:
    flag = "🇵🇰" if LANG in ["SINDHI","URDU"] else "🇮🇳" if LANG=="HINDI" else "🇬🇧" if LANG=="ENGLISH" else "🇸🇦"
    has_text = len(st.session_state[f"text_{LANG}"].strip()) > 0
    icon = "✅" if has_text else "⬜"
    with st.expander(f"{icon} {flag} {LANG} BOX - {st.session_state[f'time_{LANG}']} - {len(st.session_state[f'text_{LANG}'])} chars", expanded=has_text):
        c1,c2 = st.columns(2)
        with c1:
            time_sel = st.selectbox(f"⏱️ {LANG} Time:", list(TIME_OPTIONS.keys()), index=3, key=f"ts_{LANG}")
            st.session_state[f"time_{LANG}"] = time_sel
            MAX_SEC = TIME_OPTIONS[time_sel]
        with c2:
            vkey = st.selectbox(f"🎤 {LANG} Voice:", list(VOICES[LANG].keys()), key=f"v_{LANG}")
            vname = VOICES[LANG][vkey]
        MAX_CHARS = MAX_SEC * 14
        
        txt = st.text_area(f"✍️ {LANG} Text ({MAX_CHARS} max):", value=st.session_state[f"text_{LANG}"], height=120, max_chars=MAX_CHARS, key=f"ta_{LANG}")
        if txt != st.session_state[f"text_{LANG}"]: st.session_state[f"text_{LANG}"] = txt
        
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
                            st.success(f"✅ {LANG} {MAX_SEC}s Ready!")
                            st.audio(fp)
                            with open(fp,"rb") as f: st.download_button(f"📥 Download {LANG}", f, file_name=f"{LANG}_{MAX_SEC}s.mp3", key=f"dl_{LANG}")
                        else: st.error("Fail")
                    except Exception as e: st.error(f"{e}")

st.caption("V97.1 FIX - 1 Prompt = All 5 Box Bharenge - Groq Model Fixed - Khali Bug Fixed")
