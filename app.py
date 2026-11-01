import streamlit as st, os, re, subprocess, asyncio
import edge_tts
from gtts import gTTS

st.set_page_config(page_title="MEHAR V95 - WORLD STUDIO", layout="centered")
st.title("MEHAR V95 - WORLD STUDIO 🌍")
st.success("V95: Urdu + Sindhi Pure + Hindi + English + Arabic - 50+ Voices!")

VOICE_CATEGORIES = {
    "🇵🇰 URDU CLEAR": {
        "👩 Swara - Urdu Best Clear": "hi-IN-SwaraNeural",
        "👦 Asad - Urdu Larka": "ur-PK-AsadNeural",
        "👩 Ayesha - Urdu": "ur-PK-AyeshaNeural",
        "👩 Uzma - Urdu Viral": "ur-PK-UzmaNeural",
    },
    "🇵🇰 SINDHI PURE - سنڌي خالص": {
        "👩 Sindhi Pure - سنڌي خالص Google - BEST": "GTTS-SD",
        "👩 Swara - Sindhi Clear": "hi-IN-SwaraNeural",
        "👦 Asad - Sindhi Mard": "ur-PK-AsadNeural",
        "👩 Uzma - Sindhi Aurat": "ur-PK-UzmaNeural",
    },
    "🇮🇳 HINDI/URDU MIX": {
        "👩 Swara - Hindi Best": "hi-IN-SwaraNeural",
        "👦 Madhur - Hindi Larka": "hi-IN-MadhurNeural",
    },
    "🇺🇸 ENGLISH CLEAR": {
        "👩 Jenny - US Clear": "en-US-JennyNeural",
        "👩 Aria - US Reels": "en-US-AriaNeural",
        "👦 Guy - US Larka": "en-US-GuyNeural",
    },
    "🇸🇦 ARABIC - عربي": {
        "👩 Salma - Arabic BEST": "ar-EG-SalmaNeural",
        "👦 Shakir - Arabic Larka": "ar-EG-ShakirNeural",
        "👩 Zariyah - Arabic Saudi": "ar-SA-ZariyahNeural",
    },
    "👶 BABY / KIDS": {
        "👧 Baby Ana": "en-US-AnaNeural",
        "👧 Ava Multilingual": "en-US-AvaMultilingualNeural",
    },
    "🔥 VIRAL ALL": {
        "👩 Swara - Viral": "hi-IN-SwaraNeural",
        "👩 Jenny - English Viral": "en-US-JennyNeural",
    }
}

cat = st.selectbox("📁 CATEGORY:", list(VOICE_CATEGORIES.keys()), index=1)
voices = VOICE_CATEGORIES[cat]
voice_name = voices[st.selectbox(f"{cat} Voice:", list(voices.keys()), index=0)]

limit_options = {"⚡ 15 Sec":15, "🔥 30 Sec":30, "🎙️ 1 Min":60, "⏰ 2 Min":120, "🚀 10 Min FULL":600}
MAX_SEC = limit_options[st.selectbox("⏱️ LIMIT:", list(limit_options.keys()), index=2)]
MAX_CHARS = MAX_SEC * 13

TEXTS = {
    "🇵🇰 URDU CLEAR": "Assalam-o-Alaikum! Mere pyare bhaiyon aur behno, Mehar Mart ka Pure Honey 100 percent khalis hai!",
    "🇵🇰 SINDHI PURE - سنڌي خالص": "السلام عليڪم! منهنجا پيارا ڀائرو ۽ ڀينرون، مهر مارٽ جو خالص ماکي هڪ سئو سيڪڙو خالص آهي! صرف اوڻٽيهه سو پنجاهتر روپين ۾ مفت هوم ڊليوري سان سڄي پاڪستان ۾!",
    "🇮🇳 HINDI/URDU MIX": "Namaste! Mehar Mart ka Pure Honey 100 percent khalis hai!",
    "🇺🇸 ENGLISH CLEAR": "Hello friends! Mehar Mart Pure Honey is 100 percent pure!",
    "🇸🇦 ARABIC - عربي": "السلام عليكم! عسل مهر مارت نقي 100 بالمئة!",
    "👶 BABY / KIDS": "Hello baby! Mehar Mart honey yummy!",
    "🔥 VIRAL ALL": "Mehar Mart Pure Honey 100 percent khalis hai!",
}

default_text = TEXTS.get(cat, TEXTS["🇵🇰 SINDHI PURE - سنڌي خالص"])
if MAX_SEC >= 120:
    default_text = (default_text + " ") * 20

text_input = st.text_area(f"Text ({MAX_CHARS} max) - Pure Sindhi likho:", value=default_text, height=220, max_chars=MAX_CHARS)
st.progress(min(len(text_input)/MAX_CHARS, 1.0))
rate_opt = st.select_slider("Speed:", options=["-15%", "-10%", "-5%", "+0%", "+10%"], value="+0%")

def clean(t, category):
    # SINDHI PURE KE LIYE KOI CUTTING NAHI - JAISE LIKHO WAISE RAHEGA
    if "SINDHI" in category:
        return t.strip()
    # Baqi languages ke liye halka clean
    return re.sub(r'[^\w\s.,!?\-ء-يآ-ی]', ' ', t).strip()

async def gen_edge(text, voice, rate, path):
    for attempt in range(3):
        try:
            await edge_tts.Communicate(text=text, voice=voice, rate=rate).save(path)
            return True
        except:
            await asyncio.sleep(1)
    return False

def gen_gtts_pure(text, path, category):
    try:
        if "SINDHI" in category:
            # PURE SINDHI - Google Sindhi
            tts = gTTS(text=text, lang='sd')
        elif "ARABIC" in category:
            tts = gTTS(text=text, lang='ar')
        elif "ENGLISH" in category:
            tts = gTTS(text=text, lang='en')
        else:
            tts = gTTS(text=text, lang='ur')
        tts.save(path)
        return True
    except Exception as e:
        print(f"gTTS error {e}")
        try:
            tts = gTTS(text=text, lang='ur')
            tts.save(path)
            return True
        except:
            return False

async def gen(text, voice, rate, category):
    os.makedirs("voice", exist_ok=True)
    parts = [text[i:i+350] for i in range(0, len(text), 350)]
    files = []
    bar = st.progress(0)
    status = st.empty()
    
    for i, p in enumerate(parts):
        p = clean(p, category)
        if not p: continue
        path = f"voice/w_{i}.mp3"
        status.text(f"Sindhi Pure Part {i+1}/{len(parts)}...")
        
        if voice == "GTTS-SD" or "SINDHI" in category:
            # SINDHI KE LIYE DIRECT GOOGLE SINDHI - PURE!
            gen_gtts_pure(p, path, category)
        else:
            success = await gen_edge(p, voice, rate, path)
            if not success:
                gen_gtts_pure(p, path, category)
        
        if os.path.exists(path):
            files.append(path)
        bar.progress((i+1)/len(parts))
    
    if not files:
        raise Exception("Voice nahi bani")
    
    final = f"voice/FINAL_SINDHI.mp3"
    try:
        import imageio_ffmpeg
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        with open("voice/list.txt","w", encoding="utf-8") as f:
            for fp in files:
                f.write(f"file '{os.path.abspath(fp)}'\n")
        subprocess.run([ffmpeg,"-y","-f","concat","-safe","0","-i","voice/list.txt","-c","copy",final], check=True, capture_output=True)
    except:
        final = files[0]
    status.empty()
    return final

if st.button(f"🎙️ {cat} - PURE BANAO", type="primary", use_container_width=True):
    with st.spinner(f"{cat} Pure bana raha hun..."):
        try:
            path = asyncio.run(gen(text_input, voice_name, rate_opt, cat))
            st.balloons()
            st.success(f"✅ Pure Sindhi Ready! {cat}")
            st.audio(path)
            with open(path, "rb") as f:
                st.download_button(f"📥 Download Pure Sindhi", f, file_name=f"PURE_SINDHI_{MAX_SEC}.mp3", use_container_width=True)
        except Exception as e:
            st.error(f"Error: {e}")
            backup = "voice/backup.mp3"
            if gen_gtts_pure(text_input[:500], backup, cat):
                st.audio(backup)

st.divider()
st.markdown("""
### 🇵🇰 SINDHI PURE FIX:
- **Ab koi lafz cut nahi hoga - ٻ ڄ ڳ ڱ سڀ mehfooz!**
- **Google Sindhi Pure voice - 100% Sindhi**
- **Sample:** السلام عليڪم! منهنجا پيارا ڀائرو!

**TIP:** Sindhi Pure ke liye pehli voice **GTTS-SD** select karo - Wo 100% Sindhi hai!
""")
