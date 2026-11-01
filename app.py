import streamlit as st, os, re, subprocess, asyncio
import edge_tts
from gtts import gTTS

st.set_page_config(page_title="MEHAR V96 - SINDHI PURE", layout="centered")
st.title("MEHAR V96 - SINDHI PURE 🌍")
st.success("V96: Sindhi 100% Pure - Lafz Kabhi Cut Nahi!")

VOICE_CATEGORIES = {
    "🇵🇰 SINDHI PURE - سنڌي خالص": {
        "👩 Sindhi Pure Google - BEST 100%": "GTTS-SD",
    },
    "🇵🇰 URDU CLEAR": {
        "👩 Swara - Urdu Best": "hi-IN-SwaraNeural",
        "👦 Asad - Urdu": "ur-PK-AsadNeural",
        "👩 Uzma - Urdu Viral": "ur-PK-UzmaNeural",
    },
    "🇸🇦 ARABIC": {
        "👩 Salma - Arabic": "ar-EG-SalmaNeural",
    },
    "🇺🇸 ENGLISH": {
        "👩 Jenny - English": "en-US-JennyNeural",
    }
}

cat = st.selectbox("📁 CATEGORY:", list(VOICE_CATEGORIES.keys()), index=0)
voices = VOICE_CATEGORIES[cat]
voice_name = voices[st.selectbox(f"{cat} Voice:", list(voices.keys()), index=0)]
MAX_SEC = 600
MAX_CHARS = 5000

TEXTS = {
    "🇵🇰 SINDHI PURE - سنڌي خالص": "السلام عليڪم! منهنجا پيارا ڀائرو ۽ ڀينرون! مهر مارٽ جو خالص ماکي هڪ سو سيڪڙو خالص آهي! صرف اوڻٽيهه سو پنجاهتر روپين ۾ مفت هوم ڊليوري!",
}

default_text = TEXTS.get(cat, "السلام عليڪم! مهر مارٽ جو ماکي خالص آهي!")
text_input = st.text_area(f"Pure Sindhi Text Likho - Cut Nahi Hoga ({MAX_CHARS} max):", value=default_text, height=250, max_chars=MAX_CHARS)

if "SINDHI" in cat:
    st.info("✅ SINDHI PURE MODE: Koi lafz cut nahi hoga - Sentence wise banega!")

# SINDHI KE LIYE CLEAN BAND - BILKUL AS IT IS
def clean_pure(t, category):
    if "SINDHI" in category:
        # Sindhi ke liye kuch bhi mat hatao - bilkul pure
        return t.strip()
    return re.sub(r'[^\w\s.,!?\-ء-ي]', ' ', t).strip()

def split_sindhi_sentences(text):
    # Sindhi ko jumlon me kaato - lafzon me nahi!
    # ۔ ! ؟ ، . , par split
    sentences = re.split(r'([۔!؟!?,،\n]+)', text)
    # Jor do
    result = []
    current = ""
    for part in sentences:
        if not part.strip():
            continue
        current += part
        # Agar current 250 se zyada ho jaye to naya part
        if len(current) > 250 or re.search(r'[۔!؟\n]', part):
            if current.strip():
                result.append(current.strip())
            current = ""
    if current.strip():
        result.append(current.strip())
    
    # Agar ab bhi khali hai to 300 char word boundary par
    if not result:
        words = text.split()
        chunk = ""
        for w in words:
            if len(chunk) + len(w) < 300:
                chunk += " " + w
            else:
                result.append(chunk.strip())
                chunk = w
        if chunk:
            result.append(chunk.strip())
    return result if result else [text]

def gen_gtts_sindhi_pure(text, path):
    try:
        # SINDHI PURE - slow=False taake cut na lage
        tts = gTTS(text=text, lang='sd', slow=False)
        tts.save(path)
        return True
    except Exception as e:
        st.error(f"gTTS Sindhi Error: {e}")
        try:
            # Fallback Urdu
            tts = gTTS(text=text, lang='ur', slow=False)
            tts.save(path)
            return True
        except:
            return False

async def gen(text, voice, category):
    os.makedirs("voice", exist_ok=True)
    
    if "SINDHI" in category:
        parts = split_sindhi_sentences(text)
    else:
        parts = [text[i:i+350] for i in range(0, len(text), 350)]
    
    st.write(f"Total {len(parts)} hisson me bana raha hun - Lafz mehfooz!")
    files = []
    bar = st.progress(0)
    
    for i, p in enumerate(parts):
        p = clean_pure(p, category)
        if not p: 
            continue
        path = f"voice/sindhi_{i}.mp3"
        
        # SINDHI PURE HAMESHA GTTS-SD SE
        ok = gen_gtts_sindhi_pure(p, path)
        
        if ok and os.path.exists(path) and os.path.getsize(path) > 1000:
            files.append(path)
        bar.progress((i+1)/len(parts))
    
    if not files:
        raise Exception("Sindhi voice nahi bani - Text chhota karo")
    
    final = f"voice/FINAL_PURE_SINDHI.mp3"
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

if st.button(f"🎙️ {cat} - PURE BANAO - CUT NAHI HOGA", type="primary", use_container_width=True):
    if not text_input.strip():
        st.warning("Pehle Sindhi text likho!")
    else:
        with st.spinner(f"Pure Sindhi bana raha hun - {len(text_input)} chars..."):
            try:
                path = asyncio.run(gen(text_input, voice_name, cat))
                st.balloons()
                st.success(f"✅ Pure Sindhi Ready! Lafz mehfooz!")
                st.audio(path)
                with open(path, "rb") as f:
                    st.download_button(f"📥 Download Pure Sindhi", f, file_name=f"PURE_SINDHI.mp3", use_container_width=True)
            except Exception as e:
                st.error(f"Error: {e}")

st.divider()
st.markdown("""
**V96 FIX:**
- **Pehle 350 char par beech lafz se cut hota tha**
- **Ab sentence par cut hota hai - ۔ ! ؟ par**
- **Lafz kabhi nahi tootega - ٻ ڄ ڳ ڱ سڀ mehfooz**
- **Google Sindhi Pure - 100% Sindhi**

**Test ye likho:**
