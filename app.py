import streamlit as st, os, re, subprocess, asyncio
import edge_tts

st.set_page_config(page_title="MEHAR V95 - WORLD STUDIO", layout="centered")
st.title("MEHAR V95 - WORLD STUDIO 🌍")
st.success("V95: Urdu + Hindi + English + Arabic + Baby - 40+ Voices!")

VOICE_CATEGORIES = {
    "🇵🇰 URDU CLEAR": {
        "👩 Swara - Urdu Best Clear": "hi-IN-SwaraNeural",
        "👦 Asad - Urdu Larka": "ur-PK-AsadNeural",
        "👩 Ayesha - Urdu": "ur-PK-AyeshaNeural",
        "👩 Uzma - Urdu Viral": "ur-PK-UzmaNeural",
    },
    "🇮🇳 HINDI/URDU MIX": {
        "👩 Swara - Hindi Best": "hi-IN-SwaraNeural",
        "👦 Madhur - Hindi Larka": "hi-IN-MadhurNeural",
        "👩 Neerja - Hindi Larki": "en-IN-NeerjaNeural",
    },
    "🇺🇸 ENGLISH CLEAR": {
        "👩 Jenny - US Clear Viral": "en-US-JennyNeural",
        "👩 Aria - US Reels": "en-US-AriaNeural",
        "👦 Guy - US Larka": "en-US-GuyNeural",
        "👦 Davis - US Deep Voice": "en-US-DavisNeural",
        "👩 Neerja - Indian English Clear": "en-IN-NeerjaNeural",
        "👦 Prabhat - Indian English Larka": "en-IN-PrabhatNeural",
        "👩 Libby - UK English": "en-GB-LibbyNeural",
    },
    "🇸🇦 ARABIC - عربي": {
        "👩 Salma - Arabic Egypt Clear - BEST": "ar-EG-SalmaNeural",
        "👦 Shakir - Arabic Egypt Larka": "ar-EG-ShakirNeural",
        "👩 Zariyah - Arabic Saudi Clear": "ar-SA-ZariyahNeural",
        "👦 Hamed - Arabic Saudi Larka": "ar-SA-HamedNeural",
        "👩 Amany - Arabic UAE": "ar-AE-FatimaNeural",
        "👦 Hamdan - Arabic UAE Larka": "ar-AE-HamdanNeural",
    },
    "👶 BABY / KIDS": {
        "👧 Baby Ana - US Bachi": "en-US-AnaNeural",
        "👧 Ava - US Bachi Multilingual": "en-US-AvaMultilingualNeural",
        "👧 Baby Ayesha - Hindi Baby": "hi-IN-SwaraNeural",
    },
    "🔥 VIRAL ALL": {
        "👩 Swara - Urdu/Hindi Viral": "hi-IN-SwaraNeural",
        "👩 Jenny - English Viral": "en-US-JennyNeural",
        "👩 Salma - Arabic Viral": "ar-EG-SalmaNeural",
    }
}

cat = st.selectbox("📁 CATEGORY:", list(VOICE_CATEGORIES.keys()), index=0)
voices = VOICE_CATEGORIES[cat]
voice_name = voices[st.selectbox(f"{cat} Voice:", list(voices.keys()), index=0)]

limit_options = {"⚡ 15 Sec":15, "🔥 30 Sec":30, "🎙️ 1 Min":60, "⏰ 2 Min":120, "🚀 10 Min FULL":600}
MAX_SEC = limit_options[st.selectbox("⏱️ LIMIT:", list(limit_options.keys()), index=4)]
MAX_CHARS = MAX_SEC * 13

# TEXTS BY LANGUAGE
TEXTS = {
    "🇵🇰 URDU CLEAR": "Assalam-o-Alaikum! Mere pyare bhaiyon aur behno, Mehar Mart ka Pure Honey 100 percent khalis hai! Sirf 2975 me!",
    "🇮🇳 HINDI/URDU MIX": "Namaste! Mehar Mart ka Pure Honey 100 percent khalis hai! Sirf 2975 me!",
    "🇺🇸 ENGLISH CLEAR": "Hello friends! Mehar Mart Pure Honey is 100 percent pure and natural! Only 2975 with free delivery all over Pakistan!",
    "🇸🇦 ARABIC - عربي": "السلام عليكم! عسل مهر مارت نقي 100 بالمئة! فقط 2975 مع توصيل مجاني في جميع أنحاء باكستان!",
    "👶 BABY / KIDS": "Hello! I am baby! Mehar Mart honey is yummy yummy! So sweet!",
    "🔥 VIRAL ALL": "Mehar Mart Pure Honey 100 percent khalis hai! Sirf 2975 me Free Delivery!"
}

default_text = TEXTS.get(cat, TEXTS["🇵🇰 URDU CLEAR"])
# 10 min full text for Urdu/Hindi/English/Arabic
if MAX_SEC >= 120:
    default_text = default_text * 40

text_input = st.text_area(f"Text ({MAX_CHARS} max) - {cat} ke liye:", value=default_text, height=220, max_chars=MAX_CHARS)
st.metric(f"{len(text_input)} chars", f"{len(text_input)//13} sec / {MAX_SEC} sec")
st.progress(min(len(text_input)/MAX_CHARS, 1.0))

rate_opt = st.select_slider("Speed:", options=["-15%", "-10%", "-5%", "0%", "+10%"], value="-5%")

def clean(t): return re.sub(r'[^\w\s.,!?\-ء-ي]', ' ', t).strip()

async def gen(text, voice, rate):
    os.makedirs("voice", exist_ok=True)
    target = MAX_SEC * 11
    if len(text) < target and MAX_SEC>=60:
        while len(text) < target:
            text += " " + text[:600]
        text = text[:target]
    parts = [text[i:i+350] for i in range(0, len(text), 350)]
    files = []
    bar = st.progress(0)
    for i, p in enumerate(parts):
        p = clean(p)
        if not p: continue
        path = f"voice/w_{i}.mp3"
        try:
            await edge_tts.Communicate(p, voice, rate=rate).save(path)
        except:
            # Fallback
            await edge_tts.Communicate(p, "hi-IN-SwaraNeural", rate=rate).save(path)
        files.append(path)
        bar.progress((i+1)/len(parts))
    final = f"voice/FINAL_{cat[:3]}.mp3"
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

if st.button(f"🎙️ {cat} - {voice_name.split(' - ')[0]} - BANAO", type="primary", use_container_width=True):
    with st.spinner(f"{cat} - {voice_name} se {MAX_SEC} sec..."):
        path = asyncio.run(gen(text_input, voice_name, rate_opt))
        st.balloons()
        st.success(f"✅ Ready! {cat} - {voice_name}")
        st.audio(path)
        with open(path, "rb") as f:
            st.download_button(f"📥 Download {cat}", f, file_name=f"{cat[:5]}_{MAX_SEC}.mp3")

st.divider()
st.markdown("""
**V95 me:**
- 🇵🇰 Urdu: Swara, Asad, Ayesha, Uzma
- 🇮🇳 Hindi: Swara, Madhur
- 🇺🇸 English: Jenny, Aria, Guy, Neerja, Prabhat, Libby
- 🇸🇦 Arabic: Salma, Shakir, Zariyah, Hamed - **عربي clear!**
- 👶 Baby: Ana, Ava
- Speed control - clear ke liye -5%
""")
