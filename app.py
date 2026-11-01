import streamlit as st, os, re, subprocess, asyncio, shutil
import edge_tts

st.set_page_config(page_title="MEHAR V95 - WORLD STUDIO", layout="centered")
st.title("MEHAR V95 - WORLD STUDIO 🌍")
st.success("V95 FINAL: Khalis Pure - Alfaz Cut Band - Sindhi + Urdu + Hindi + English + Arabic")

VOICE_CATEGORIES = {
    "🇵🇰 URDU CLEAR": {
        "10 Sal Larki": "ur-PK-AyeshaNeural",
        "20 Sal Larki": "ur-PK-UzmaNeural",
        "30 Sal Larki": "hi-IN-SwaraNeural",
        "50 Sal Larki": "ur-PK-AyeshaNeural",
        "60 Sal Larki": "ur-PK-AyeshaNeural",
        "10 Sal Larka": "ur-PK-AsadNeural",
        "20 Sal Larka": "ur-PK-AsadNeural",
        "30 Sal Larka": "hi-IN-MadhurNeural",
        "50 Sal Larka": "ur-PK-AsadNeural",
        "60 Sal Larka": "ur-PK-AsadNeural",
    },
    "🇵🇰 SINDHI KHALIS - سنڌي": {
        "10 Sal Larki": "ur-PK-AyeshaNeural",
        "20 Sal Larki": "ur-PK-UzmaNeural",
        "30 Sal Larki": "ur-PK-UzmaNeural",
        "50 Sal Larki": "ur-PK-AyeshaNeural",
        "60 Sal Larki": "ur-PK-AyeshaNeural",
        "10 Sal Larka": "ur-PK-AsadNeural",
        "20 Sal Larka": "ur-PK-AsadNeural",
        "30 Sal Larka": "ur-PK-AsadNeural",
        "50 Sal Larka": "ur-PK-AsadNeural",
        "60 Sal Larka": "ur-PK-AsadNeural",
    },
    "🇮🇳 HINDI - हिंदी": {
        "10 Sal Larki": "hi-IN-SwaraNeural",
        "20 Sal Larki": "hi-IN-SwaraNeural",
        "30 Sal Larki": "en-IN-NeerjaNeural",
        "50 Sal Larki": "en-IN-NeerjaNeural",
        "60 Sal Larki": "en-IN-NeerjaNeural",
        "10 Sal Larka": "hi-IN-MadhurNeural",
        "20 Sal Larka": "hi-IN-MadhurNeural",
        "30 Sal Larka": "en-IN-PrabhatNeural",
        "50 Sal Larka": "en-IN-PrabhatNeural",
        "60 Sal Larka": "en-IN-PrabhatNeural",
    },
    "🇺🇸 ENGLISH CLEAR": {
        "10 Sal Larki": "en-US-AnaNeural",
        "20 Sal Larki": "en-US-AriaNeural",
        "30 Sal Larki": "en-US-JennyNeural",
        "50 Sal Larki": "en-GB-LibbyNeural",
        "60 Sal Larki": "en-GB-LibbyNeural",
        "10 Sal Larka": "en-US-AndrewNeural",
        "20 Sal Larka": "en-US-GuyNeural",
        "30 Sal Larka": "en-US-DavisNeural",
        "50 Sal Larka": "en-US-ChristopherNeural",
        "60 Sal Larka": "en-GB-RyanNeural",
    },
    "🇸🇦 ARABIC - عربي": {
        "10 Sal Larki": "ar-AE-FatimaNeural",
        "20 Sal Larki": "ar-EG-SalmaNeural",
        "30 Sal Larki": "ar-SA-ZariyahNeural",
        "50 Sal Larki": "ar-EG-SalmaNeural",
        "60 Sal Larki": "ar-EG-SalmaNeural",
        "10 Sal Larka": "ar-AE-HamdanNeural",
        "20 Sal Larka": "ar-EG-ShakirNeural",
        "30 Sal Larka": "ar-SA-HamedNeural",
        "50 Sal Larka": "ar-EG-ShakirNeural",
        "60 Sal Larka": "ar-SA-HamedNeural",
    },
}

cat = st.selectbox("📁 CATEGORY:", list(VOICE_CATEGORIES.keys()), index=1)
voices = VOICE_CATEGORIES[cat]
voice_key = st.selectbox(f"{cat} - Age 10-20-30-50-60:", list(voices.keys()), index=1)
voice_name = voices[voice_key]

st.info(f"SELECTED: {cat} - {voice_key} -> {voice_name} - Khalis Pure")

limit_options = {"⚡ 15 Sec":15, "🔥 30 Sec":30, "🎙️ 1 Min":60, "⏰ 2 Min":120, "🚀 10 Min FULL":600}
MAX_SEC = limit_options[st.selectbox("⏱️ LIMIT:", list(limit_options.keys()), index=2)]
MAX_CHARS = MAX_SEC * 15

TEXTS = {
    "🇵🇰 URDU CLEAR": "السلام علیکم! میرے پیارے بھائیوں اور بہنوں! مہر مارٹ کا خالص ماکی ایک سو فیصد خالص ہے! صرف انتیس سو پچھتر روپے میں فری ڈیلیوری!",
    "🇵🇰 SINDHI KHALIS - سنڌي": "السلام عليڪم! منهنجا پيارا ڀائرو ۽ ڀينرون! مهر مارٽ جو خالص ماکي هڪ سئو سيڪڙو خالص آهي! صرف اوڻٽيهه سو پنجاهتر روپين ۾! سڄي پاڪستان ۾ فري ڊليوري!",
    "🇮🇳 HINDI - हिंदी": "नमस्ते! मेरे प्यारे भाइयों और बहनों! मेहर मार्ट का शुद्ध शहद सौ प्रतिशत खालिस है! सिर्फ 2975 में!",
    "🇺🇸 ENGLISH CLEAR": "Hello friends! Mehar Mart Pure Honey is 100 percent pure and natural! Only 2975 with free delivery all over Pakistan!",
    "🇸🇦 ARABIC - عربي": "السلام عليكم ورحمة الله! اخواني واخواتي الاعزاء! عسل مهر مارت نقي 100 بالمئة وطبيعي! فقط 2975 مع توصيل مجاني!",
}

default_text = TEXTS.get(cat, TEXTS["🇵🇰 SINDHI KHALIS - سنڌي"])
if MAX_SEC >= 120:
    default_text = (default_text + " ") * 20

text_input = st.text_area(f"Text ({MAX_CHARS} max) - {cat} - Khalis Pure:", value=default_text, height=240, max_chars=MAX_CHARS)
st.metric(f"{len(text_input)} chars", f"{len(text_input)//12} sec / {MAX_SEC} sec")
st.progress(min(len(text_input)/MAX_CHARS, 1.0))

rate_opt = st.select_slider("Speed:", options=["-15%", "-10%", "-5%", "+0%", "+10%"], value="-5%")

# KHALIS PURE FIX - Alfaz cut band!
def clean(t): 
    # Koi lafz cut nahi - Khalis as it is!
    return t.strip()

# KHALIS PURE FIX - Lafz beech se kabhi cut nahi hoga!
def split_no_cut(text, size=400):
    # Harf ba harf cut band - Sirf space se cut - Khalis pure!
    words = text.split(' ')
    parts = []
    cur = ""
    for w in words:
        if w == "":
            continue
        if len(cur) + len(w) + 1 <= size:
            cur = cur + " " + w if cur else w
        else:
            if cur:
                parts.append(cur)
            cur = w
    if cur:
        parts.append(cur)
    return parts if parts else [text]

async def gen(text, voice, rate):
    if os.path.exists("voice"):
        shutil.rmtree("voice")
    os.makedirs("voice", exist_ok=True)
    # Khalis pure text - No change
    target = MAX_SEC * 12
    if len(text) < target and MAX_SEC>=60:
        while len(text) < target:
            text += " " + text[:500]
        text = text[:target]
    parts = split_no_cut(text, 400)
    files = []
    bar = st.progress(0)
    for i, p in enumerate(parts):
        p = clean(p)
        if not p: continue
        safe = voice.replace("-", "_")
        path = f"voice/{safe}_{i}.mp3"
        # Khalis voice - Pure language
        try:
            await edge_tts.Communicate(text=p, voice=voice, rate=rate).save(path)
        except:
            await asyncio.sleep(1)
            try:
                await edge_tts.Communicate(text=p, voice=voice, rate=rate).save(path)
            except:
                await edge_tts.Communicate(text=p, voice="hi-IN-SwaraNeural", rate=rate).save(path)
        files.append(path)
        bar.progress((i+1)/len(parts))
    final = f"voice/FINAL_{cat[:3]}_KHALIS.mp3"
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

if st.button(f"🎙️ {cat} - {voice_key} - KHALIS BANAO", type="primary", use_container_width=True):
    with st.spinner(f"{cat} - {voice_key} - Khalis Pure bana raha hun..."):
        path = asyncio.run(gen(text_input, voice_name, rate_opt))
        st.balloons()
        st.success(f"✅ Ready! {cat} - {voice_key} - Khalis Pure - No Cut!")
        st.audio(path)
        with open(path, "rb") as f:
            st.download_button(f"📥 Download {voice_key} Khalis", f, file_name=f"{cat[:5]}_{voice_key.replace(' ','_')}_KHALIS_{MAX_SEC}.mp3")
