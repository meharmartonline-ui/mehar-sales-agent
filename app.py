import streamlit as st, os, re, subprocess, asyncio
from gtts import gTTS
import edge_tts

st.set_page_config(page_title="MEHAR V97 - SINDHI KHALIS", layout="centered")
st.title("MEHAR V97 - SINDHI KHALIS سنڌي")
st.success("V97: 100% Khalis Sindhi - No Cut - No Mix!")

VOICE_CATEGORIES = {
    "🇵🇰 SINDHI KHALIS - سنڌي خالص 100%": {
        "👩 Sindhi Khalis - Google Pure - BEST": "GTTS-SD-PURE",
    },
    "🇵🇰 URDU CLEAR": {
        "👩 Swara - Urdu Best": "hi-IN-SwaraNeural",
        "👦 Asad - Urdu": "ur-PK-AsadNeural",
        "👩 Uzma - Urdu Viral": "ur-PK-UzmaNeural",
    },
    "🇮🇳 HINDI/URDU MIX": {
        "👩 Swara - Hindi Best": "hi-IN-SwaraNeural",
        "👦 Madhur - Hindi": "hi-IN-MadhurNeural",
    },
    "🇺🇸 ENGLISH CLEAR": {
        "👩 Jenny - US Clear": "en-US-JennyNeural",
    },
    "🇸🇦 ARABIC - عربي": {
        "👩 Salma - Arabic": "ar-EG-SalmaNeural",
    },
    "👶 BABY / KIDS": {
        "👧 Baby Ana": "en-US-AnaNeural",
    },
    "🔥 VIRAL ALL": {
        "👩 Swara - Viral": "hi-IN-SwaraNeural",
    }
}

cat = st.selectbox("📁 CATEGORY:", list(VOICE_CATEGORIES.keys()), index=0)
voices = VOICE_CATEGORIES[cat]
voice_name = voices[st.selectbox(f"{cat} Voice:", list(voices.keys()), index=0)]

MAX_SEC = 600
MAX_CHARS = 5000

# 100% KHALIS SINDHI TEXT - No English number!
DEFAULT_SINDHI = "السلام عليڪم! منهنجا پيارا ڀائرو ۽ ڀينرون! مهر مارٽ جو خالص ماکي بلڪل خالص ۽ قدرتي آهي! صرف اوڻٽيهه سو پنجاهتر روپين ۾ سڄي پاڪستان ۾ مفت هوم ڊليوري!"

if "SINDHI" in cat:
    default_text = DEFAULT_SINDHI
else:
    default_text = "Assalam-o-Alaikum! Mehar Mart Pure Honey 100 percent khalis hai!"

text_input = st.text_area(f"Pure Sindhi Likho - English mat likho:", value=default_text, height=280, max_chars=MAX_CHARS)
st.metric(f"{len(text_input)} chars", f"{len(text_input)} alfaz")

# Sindhi ke liye speed hamesha Normal
rate_opt = "+0%"

def make_pure_sindhi(text):
    # English numbers ko Sindhi lafzon me badlo - Is se khalis lagega
    text = text.replace("100 percent", "هڪ سئو سيڪڙو")
    text = text.replace("100%", "هڪ سئو سيڪڙو")
    text = text.replace("100", "هڪ سئو")
    text = text.replace("2975", "اوڻٽيهه سو پنجاهتر")
    text = text.replace("Free Delivery", "مفت هوم ڊليوري")
    text = text.replace("Pure Honey", "خالص ماکي")
    return text.strip()

def split_pure(text):
    # Jumlon par kaato - lafz nahi tootega
    parts = re.split(r'([۔!؟\n]+)', text)
    result = []
    cur = ""
    for p in parts:
        cur += p
        if len(cur) > 200 or re.search(r'[۔!؟\n]', p):
            if cur.strip():
                result.append(cur.strip())
            cur = ""
    if cur.strip():
        result.append(cur.strip())
    if not result:
        result = [text]
    return result

def gen_sindhi_khalis(text, path):
    try:
        # PURE SINDHI - Google Sindhi TTS
        tts = gTTS(text=text, lang='sd', slow=False, lang_check=False)
        tts.save(path)
        return True
    except Exception as e:
        st.error(f"Sindhi Error: {e}")
        return False

async def gen(text, category):
    os.makedirs("voice", exist_ok=True)
    
    if "SINDHI" in category:
        text = make_pure_sindhi(text)
        parts = split_pure(text)
        st.info(f"Pure Sindhi ke {len(parts)} jumle bana raha hun - Khalis!")
    else:
        parts = [text[i:i+350] for i in range(0, len(text), 350)]
    
    files = []
    bar = st.progress(0)
    
    for i, p in enumerate(parts):
        if not p.strip():
            continue
        path = f"voice/khalis_{i}.mp3"
        
        if "SINDHI" in category:
            ok = gen_sindhi_khalis(p, path)
        else:
            # Urdu/English ke liye edge-tts
            try:
                await edge_tts.Communicate(text=p, voice="hi-IN-SwaraNeural", rate=rate_opt).save(path)
                ok = True
            except:
                ok = gen_sindhi_khalis(p, path)
        
        if os.path.exists(path) and os.path.getsize(path) > 500:
            files.append(path)
        bar.progress((i+1)/len(parts))
    
    if not files:
        raise Exception("Voice nahi bani")
    
    final = "voice/FINAL_KHALIS_SINDHI.mp3"
    try:
        import imageio_ffmpeg
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        with open("voice/list.txt","w", encoding="utf-8") as f:
            for fp in files:
                f.write(f"file '{os.path.abspath(fp)}'\n")
        subprocess.run([ffmpeg,"-y","-f","concat","-safe","0","-i","voice/list.txt","-c","copy",final], check=True, capture_output=True)
    except:
        final = files[0]
    return final

if st.button("🎙️ KHALIS SINDHI BANAO - 100% PURE", type="primary", use_container_width=True):
    if not text_input.strip():
        st.warning("Text likho!")
    else:
        with st.spinner("100% Khalis Sindhi bana raha hun..."):
            try:
                path = asyncio.run(gen(text_input, cat))
                st.balloons()
                st.success("✅ 100% Khalis Sindhi Ready!")
                st.audio(path)
                with open(path, "rb") as f:
                    st.download_button("📥 Download Khalis Sindhi", f, file_name="KHALIS_SINDHI_100.mp3", use_container_width=True)
            except Exception as e:
                st.error(f"Error: {e}")

st.divider()
st.markdown("### Khalis Sindhi ke liye TIP:")
st.code("السلام عليڪم! منهنجا پيارا ڀائرو! مهر مارٽ جو ماکي خالص آهي! صرف اوڻٽيهه سو پنجاهتر روپين ۾!")

st.warning("English Number 100 / 2975 mat likho - Sindhi lafzon me likho: هڪ سئو / اوڻٽيهه سو پنجاهتر - Tab 100% Khalis lagega!")
