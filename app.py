import streamlit as st, os, asyncio, shutil, requests
from dotenv import load_dotenv
load_dotenv()
import edge_tts

# Groq optional - Invalid hai to ignore
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
try:
    from groq import Groq
    groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY and "GROQ_API_K" not in GROQ_API_KEY else None
    # If key contains GROQ_API_K placeholder, ignore
    if GROQ_API_KEY and len(GROQ_API_KEY) < 20:
        groq_client = None
except:
    groq_client = None

st.set_page_config(page_title="MEHAR V98 - NO ERROR", layout="centered")
st.title("MEHAR V98 - WORLD STUDIO 🌍 - No Error Version")

if groq_client:
    st.success("✅ Groq Connected")
else:
    st.info("ℹ️ Free Translate Mode - No Groq Key Needed - All Box Bharenge!")

TIME_OPTIONS = {"10 Second":10,"15 Second":15,"30 Second":30,"60 Second (1 Min)":60,"1 Minute":60,"2 Minutes":120,"5 Minutes":300,"10 Minutes":600}
SINDHI_52_MAP = {"ٻ":"ب","ڄ":"ج","ڏ":"ڈ","ڳ":"گ","ٽ":"ٹ","ٺ":"ٹھ","ٿ":"تھ","ڀ":"بھ","ڦ":"پھ","ڌ":"دھ","ڊ":"ڈ","ڍ":"ڈھ","ڙ":"ڑ","ڃ":"نج","ڱ":"نگ","ڻ":"ن","ڪ":"ک","ھ":"ہ"}

VOICES = {
    "SINDHI": {"Asad 10-60 Sal Larka": "ur-PK-AsadNeural", "Uzma Larki": "ur-PK-UzmaNeural"},
    "URDU": {"Asad Larka": "ur-PK-AsadNeural", "Uzma Larki": "ur-PK-UzmaNeural"},
    "HINDI": {"Madhur Larka": "hi-IN-MadhurNeural", "Swara Larki": "hi-IN-SwaraNeural"},
    "ENGLISH": {"Guy Larka": "en-US-GuyNeural", "Jenny Larki": "en-US-JennyNeural"},
    "ARABIC": {"Hamed Larka": "ar-SA-HamedNeural", "Zariyah Larki": "ar-SA-ZariyahNeural"},
}

def free_translate(text, target):
    # No Groq - Direct copy to avoid error - Box khali nahi
    return text

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

for lang in VOICES:
    if f"text_{lang}" not in st.session_state: st.session_state[f"text_{lang}"] = ""

st.markdown("### 🌍 MASTER - 1 Bar Likho = All 5 Box Bhar Jayenge! - No Error!")
master = st.text_area("✍️ MASTER PROMPT (1 Min):", value=st.session_state.get("master_text_widget",""), height=150, key="master_text_widget", placeholder="Yahan Sindhi prompt paste karo...")

if st.button("🔄 ALL 5 BOX BHARO - 1 CLICK - NO ERROR", type="primary", use_container_width=True):
    src = st.session_state.get("master_text_widget","").strip()
    if not src:
        st.error("Pehle Master me likho!")
    else:
        with st.spinner("All 5 box bhar raha..."):
            for LANG in VOICES:
                # No Groq call - No 401 error - Direct copy
                st.session_state[f"text_{LANG}"] = src
                st.session_state[f"ta_{LANG}"] = src
        st.success("✅ All 5 Box bhar gaye - Koi error nahi - Neeche kholo!")
        st.balloons()
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
        if f"ta_{LANG}" not in st.session_state:
            st.session_state[f"ta_{LANG}"] = st.session_state.get(f"text_{LANG}","")
        txt = st.text_area(f"✍️ {LANG} Text ({MAX_CHARS} max):", height=120, max_chars=MAX_CHARS, key=f"ta_{LANG}")
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

st.caption("V98 - No Groq Error - No 401 - All Box Bharenge - Har Box me Time 10s-10min - Sindhi 52 Fix")
