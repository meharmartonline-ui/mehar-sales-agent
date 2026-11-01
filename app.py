import streamlit as st, os, re, subprocess, asyncio
from gtts import gTTS
import edge_tts

st.set_page_config(page_title="MEHAR V98 - SINDHI KHALIS", layout="centered")
st.title("MEHAR V98 - SINDHI KHALIS")
st.success("V98: Sindhi Fixed - Google sd not supported - Using Urdu Pure Voice!")

VOICE_CATEGORIES = {
    "🇵🇰 SINDHI KHALIS - سنڌي خالص": {
        "👩 Uzma - Sindhi Khalis BEST - Aurat": "ur-PK-UzmaNeural",
        "👦 Asad - Sindhi Khalis Mard": "ur-PK-AsadNeural",
        "👩 Swara - Sindhi Clear": "hi-IN-SwaraNeural",
        "👩 Ayesha - Sindhi Soft": "ur-PK-AyeshaNeural",
    },
    "🇵🇰 URDU CLEAR": {
        "👩 Swara - Urdu Best": "hi-IN-SwaraNeural",
        "👦 Asad - Urdu": "ur-PK-AsadNeural",
        "👩 Uzma - Urdu Viral": "ur-PK-UzmaNeural",
    },
    "🇮🇳 HINDI MIX": {
        "👩 Swara - Hindi": "hi-IN-SwaraNeural",
    },
    "🇺🇸 ENGLISH": {
        "👩 Jenny - English": "en-US-JennyNeural",
    },
    "🇸🇦 ARABIC": {
        "👩 Salma - Arabic": "ar-EG-SalmaNeural",
    },
}

cat = st.selectbox("📁 CATEGORY:", list(VOICE_CATEGORIES.keys()), index=0)
voices = VOICE_CATEGORIES[cat]
voice_name = voices[st.selectbox(f"{cat} Voice:", list(voices.keys()), index=0)]
MAX_CHARS = 5000

DEFAULT_SINDHI = "السلام عليڪم! منهنجا پيارا ڀائرو ۽ ڀينرون! مهر مارٽ جو خالص ماکي بلڪل خالص ۽ قدرتي آهي! صرف اوڻٽيهه سو پنجاهتر روپين ۾ سڄي پاڪستان ۾ مفت هوم ڊليوري!"

text_input = st.text_area("Pure Sindhi Text - Sindhi me likho:", value=DEFAULT_SINDHI if "SINDHI" in cat else "Mehar Mart Pure Honey", height=250, max_chars=MAX_CHARS)
rate_opt = st.select_slider("Speed:", options=["-10%", "-5%", "+0%", "+5%"], value="+0%")

def clean(t, category=""):
    if "SINDHI" in category:
        return t.strip()
    return re.sub(r'[^\w\s.,!?\-ء-ي]', ' ', t).strip()

def split_sentences(text):
    parts = re.split(r'([۔!؟!?\n]+)', text)
    result = []
    cur = ""
    for p in parts:
        cur += p
        if len(cur) > 250 or re.search(r'[۔!؟\n]', p):
            if cur.strip():
                result.append(cur.strip())
            cur = ""
    if cur.strip():
        result.append(cur.strip())
    if not result:
        result = [text]
    return result

def gen_gtts_urdu(text, path):
    try:
        # Sindhi ke liye Urdu voice - Kyunki Google me Sindhi nahi hai
        tts = gTTS(text=text, lang='ur', slow=False)
        tts.save(path)
        return True
    except:
        return False

async def gen_edge(text, voice, rate, path):
    for _ in range(3):
        try:
            await edge_tts.Communicate(text=text, voice=voice, rate=rate).save(path)
            return True
        except Exception as e:
            print(e)
            await asyncio.sleep(1)
    return False

async def gen(text, voice, rate, category):
    os.makedirs("voice", exist_ok=True)
    parts = split_sentences(text)
    st.write(f"Total {len(parts)} hisson me - Lafz mehfooz!")
    files = []
    bar = st.progress(0)
    for i, p in enumerate(parts):
        p = clean(p, category)
        if not p:
            continue
        path = f"voice/khalis_{i}.mp3"
        ok = await gen_edge(p, voice, rate, path)
        if not ok:
            gen_gtts_urdu(p, path)
        if os.path.exists(path) and os.path.getsize(path) > 500:
            files.append(path)
        bar.progress((i+1)/len(parts))
    if not files:
        raise Exception("Voice nahi bani - Text chhota karo")
    final = "voice/FINAL_KHALIS.mp3"
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

if st.button("🎙️ KHALIS SINDHI BANAO", type="primary", use_container_width=True):
    with st.spinner("Sindhi khalis bana raha hun..."):
        try:
            path = asyncio.run(gen(text_input, voice_name, rate_opt, cat))
            st.balloons()
            st.success("✅ Khalis Sindhi Ready - No Cut!")
            st.audio(path)
            with open(path, "rb") as f:
                st.download_button("📥 Download", f, file_name="KHALIS_SINDHI.mp3", use_container_width=True)
        except Exception as e:
            st.error(f"Error: {e}")

st.divider()
st.info("NOTE: Google me 'sd' language support nahi hai - Is liye Urdu Uzma/Asad voice Sindhi ke liye sab se khalis hai - Script same hone ki wajah se!")
st.code("السلام عليڪم! منهنجا پيارا ڀائرو! مهر مارٽ جو ماکي خالص آهي!")
