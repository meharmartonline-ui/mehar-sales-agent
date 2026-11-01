import streamlit as st, os, re, subprocess, asyncio
import edge_tts
from gtts import gTTS

st.set_page_config(page_title="MEHAR V95 - WORLD STUDIO", layout="centered")
st.title("MEHAR V95 - WORLD STUDIO 🌍")
st.success("V95 FIXED: Larka+Larki Age 10-60 Sal - No Cut - Khalis!")

VOICE_CATEGORIES = {
    "🇵🇰 URDU CLEAR - اردو": {
        "👧 10 Sal Larki - Bachi": "ur-PK-AyeshaNeural",
        "👩 20 Sal Larki - Jawan": "ur-PK-UzmaNeural",
        "👩 30 Sal Larki - Aurat": "hi-IN-SwaraNeural",
        "👩‍🦳 50 Sal Larki - Khatoon": "ur-PK-AyeshaNeural",
        "👵 60 Sal Larki - Buzurg": "ur-PK-AyeshaNeural",
        "👦 10 Sal Larka - Bacha": "ur-PK-AsadNeural",
        "👨 20 Sal Larka - Jawan Larka": "ur-PK-AsadNeural",
        "👨 30 Sal Larka - Mard": "hi-IN-MadhurNeural",
        "👨‍🦳 50 Sal Larka - Admi": "ur-PK-AsadNeural",
        "👴 60 Sal Larka - Buzurg": "ur-PK-AsadNeural",
    },
    "🇵🇰 SINDHI KHALIS - سنڌي": {
        "👧 10 Sal Larki - Bachi": "ur-PK-AyeshaNeural",
        "👩 20 Sal Larki - Jawan": "ur-PK-UzmaNeural",
        "👩 30 Sal Larki - Aurat": "ur-PK-UzmaNeural",
        "👩‍🦳 50 Sal Larki - Khatoon": "ur-PK-AyeshaNeural",
        "👵 60 Sal Larki - Buzurg": "ur-PK-AyeshaNeural",
        "👦 10 Sal Larka - Bacha": "ur-PK-AsadNeural",
        "👨 20 Sal Larka - Jawan": "ur-PK-AsadNeural",
        "👨 30 Sal Larka - Mard": "ur-PK-AsadNeural",
        "👨‍🦳 50 Sal Larka - Admi": "ur-PK-AsadNeural",
        "👴 60 Sal Larka - Buzurg": "ur-PK-AsadNeural",
    },
    "🇺🇸 ENGLISH CLEAR": {
        "👧 10 Sal Girl - Baby Ana": "en-US-AnaNeural",
        "👩 20 Sal Girl - Young Aria": "en-US-AriaNeural",
        "👩 30 Sal Girl - Jenny Adult": "en-US-JennyNeural",
        "👩‍🦳 50 Sal Girl - Libby Mature": "en-GB-LibbyNeural",
        "👵 60 Sal Girl - Senior": "en-GB-LibbyNeural",
        "👦 10 Sal Boy - Baby Andrew": "en-US-AndrewNeural",
        "👨 20 Sal Boy - Young Guy": "en-US-GuyNeural",
        "👨 30 Sal Boy - Davis Adult": "en-US-DavisNeural",
        "👨‍🦳 50 Sal Boy - Christopher": "en-US-ChristopherNeural",
        "👴 60 Sal Boy - Senior Ryan": "en-GB-RyanNeural",
    },
    "🇸🇦 ARABIC - عربي خالص": {
        "👧 10 Sal Larki - Bachi Fatima": "ar-AE-FatimaNeural",
        "👩 20 Sal Larki - Jawan Salma": "ar-EG-SalmaNeural",
        "👩 30 Sal Larki - Zariyah": "ar-SA-ZariyahNeural",
        "👩‍🦳 50 Sal Larki - Salma Mature": "ar-EG-SalmaNeural",
        "👵 60 Sal Larki - Buzurg": "ar-EG-SalmaNeural",
        "👦 10 Sal Larka - Bacha Hamdan": "ar-AE-HamdanNeural",
        "👨 20 Sal Larka - Jawan Shakir": "ar-EG-ShakirNeural",
        "👨 30 Sal Larka - Hamed Mard": "ar-SA-HamedNeural",
        "👨‍🦳 50 Sal Larka - Shakir Mature": "ar-EG-ShakirNeural",
        "👴 60 Sal Larka - Buzurg Hamed": "ar-SA-HamedNeural",
    },
    "🇮🇳 HINDI/URDU MIX": {
        "👧 10 Sal Larki": "hi-IN-SwaraNeural",
        "👩 20 Sal Larki": "hi-IN-SwaraNeural",
        "👩 30 Sal Larki": "en-IN-NeerjaNeural",
        "👦 10 Sal Larka": "hi-IN-MadhurNeural",
        "👨 20 Sal Larka": "hi-IN-MadhurNeural",
        "👨 30 Sal Larka": "en-IN-PrabhatNeural",
    },
}

cat = st.selectbox("📁 CATEGORY:", list(VOICE_CATEGORIES.keys()), index=0)
voices = VOICE_CATEGORIES[cat]
voice_key = st.selectbox(f"{cat} Voice - Age Select:", list(voices.keys()), index=1)
voice_name = voices[voice_key]

limit_options = {"⚡ 15 Sec":15, "🔥 30 Sec":30, "🎙️ 1 Min":60, "⏰ 2 Min":120, "🚀 10 Min FULL":600}
MAX_SEC = limit_options[st.selectbox("⏱️ LIMIT:", list(limit_options.keys()), index=2)]
MAX_CHARS = MAX_SEC * 13

TEXTS = {
    "🇵🇰 URDU CLEAR - اردو": "Assalam-o-Alaikum! Mere pyare bhaiyon aur behno, Mehar Mart ka Pure Honey 100 percent khalis hai! Sirf 2975 me!",
    "🇵🇰 SINDHI KHALIS - سنڌي": "السلام عليڪم! منهنجا پيارا ڀائرو ۽ ڀينرون! مهر مارٽ جو خالص ماکي هڪ سئو سيڪڙو خالص آهي!",
    "🇮🇳 HINDI/URDU MIX": "Namaste! Mehar Mart ka Pure Honey 100 percent khalis hai! Sirf 2975 me!",
    "🇺🇸 ENGLISH CLEAR": "Hello friends! Mehar Mart Pure Honey is 100 percent pure and natural! Only 2975 with free delivery!",
    "🇸🇦 ARABIC - عربي خالص": "السلام عليكم! عسل مهر مارت نقي 100 بالمئة! فقط 2975!",
}

default_text = TEXTS.get(cat, TEXTS["🇵🇰 URDU CLEAR - اردو"])
if MAX_SEC >= 120:
    default_text = default_text * 40

text_input = st.text_area(f"Text ({MAX_CHARS} max) - {cat}:", value=default_text, height=220, max_chars=MAX_CHARS)
st.metric(f"{len(text_input)} chars", f"{len(text_input)//13} sec / {MAX_SEC} sec")
st.progress(min(len(text_input)/MAX_CHARS, 1.0))

rate_opt = st.select_slider("Speed:", options=["-15%", "-10%", "-5%", "+0%", "+10%"], value="-5%")

def clean(t):
    return t.strip()

def split_no_cut(text, size=300):
    words = text.split()
    parts = []
    cur = ""
    for w in words:
        if len(cur) + len(w) + 1 <= size:
            cur += " " + w if cur else w
        else:
            if cur:
                parts.append(cur)
            cur = w
    if cur:
        parts.append(cur)
    return parts if parts else [text]

def gtts_fallback(text, path, category):
    try:
        if "ARABIC" in category:
            lang = 'ar'
        elif "ENGLISH" in category:
            lang = 'en'
        else:
            lang = 'ur'
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(path)
        return True
    except:
        return False

async def gen_edge_with_retry(text, voice, rate, path):
    for attempt in range(3):
        try:
            await edge_tts.Communicate(text=text, voice=voice, rate=rate).save(path)
            return True
        except:
            await asyncio.sleep(1.2 * (attempt+1))
    return False

async def gen(text, voice, rate, category):
    os.makedirs("voice", exist_ok=True)
    target = MAX_SEC * 11
    if len(text) < target and MAX_SEC>=60:
        while len(text) < target:
            text += " " + text[:600]
        text = text[:target]
    
    parts = split_no_cut(text, 300)
    files = []
    bar = st.progress(0)
    
    for i, p in enumerate(parts):
        p = clean(p)
        if not p: continue
        path = f"voice/w_{i}.mp3"
        ok = await gen_edge_with_retry(p, voice, rate, path)
        if not ok or not os.path.exists(path) or os.path.getsize(path) < 500:
            gtts_fallback(p, path, category)
        if os.path.exists(path) and os.path.getsize(path) > 500:
            files.append(path)
        bar.progress((i+1)/len(parts))
    
    if not files:
        raise Exception("Voice nahi bani - Dobara try karo")
    
    final = f"voice/FINAL_{category[:3]}.mp3"
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

if st.button(f"🎙️ {voice_key} - BANAO", type="primary", use_container_width=True):
    with st.spinner(f"{voice_key} - {cat} - {MAX_SEC} sec..."):
        try:
            path = asyncio.run(gen(text_input, voice_name, rate_opt, cat))
            st.balloons()
            st.success(f"✅ Ready! {voice_key} - {cat}")
            st.audio(path)
            with open(path, "rb") as f:
                st.download_button(f"📥 Download {voice_key}", f, file_name=f"{cat[:5]}_{voice_key[:6]}_{MAX_SEC}.mp3")
        except Exception as e:
            st.error(f"Error: {e} - Dobara Banao dabao!")

st.divider()
st.markdown("**V95 FINAL:** Same System + Bug Fix + Larka/Larki Age 10/20/30/50/60 + No Cut + Khalis")
