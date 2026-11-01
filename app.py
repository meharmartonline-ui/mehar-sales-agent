import streamlit as st, os, re, subprocess, asyncio, shutil
import edge_tts
from gtts import gTTS

st.set_page_config(page_title="MEHAR V95 - WORLD STUDIO", layout="centered")
st.title("MEHAR V95 - WORLD STUDIO 🌍")
st.success("V95 FINAL: Asad + Uzma Only - Age 10-60 - Khalis Pure")

VOICE_CATEGORIES = {
    "🇵🇰 URDU CLEAR": {
        "10 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "20 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "30 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "50 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "60 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "10 Sal Larka - Asad": "ur-PK-AsadNeural",
        "20 Sal Larka - Asad": "ur-PK-AsadNeural",
        "30 Sal Larka - Asad": "ur-PK-AsadNeural",
        "50 Sal Larka - Asad": "ur-PK-AsadNeural",
        "60 Sal Larka - Asad": "ur-PK-AsadNeural",
    },
    "🇵🇰 SINDHI KHALIS - سنڌي": {
        "10 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "20 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "30 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "50 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "60 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "10 Sal Larka - Asad": "ur-PK-AsadNeural",
        "20 Sal Larka - Asad": "ur-PK-AsadNeural",
        "30 Sal Larka - Asad": "ur-PK-AsadNeural",
        "50 Sal Larka - Asad": "ur-PK-AsadNeural",
        "60 Sal Larka - Asad": "ur-PK-AsadNeural",
    },
    "🇮🇳 HINDI - हिंदी": {
        "10 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "20 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "30 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "50 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "60 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "10 Sal Larka - Asad": "ur-PK-AsadNeural",
        "20 Sal Larka - Asad": "ur-PK-AsadNeural",
        "30 Sal Larka - Asad": "ur-PK-AsadNeural",
        "50 Sal Larka - Asad": "ur-PK-AsadNeural",
        "60 Sal Larka - Asad": "ur-PK-AsadNeural",
    },
    "🇺🇸 ENGLISH CLEAR": {
        "10 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "20 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "30 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "50 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "60 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "10 Sal Larka - Asad": "ur-PK-AsadNeural",
        "20 Sal Larka - Asad": "ur-PK-AsadNeural",
        "30 Sal Larka - Asad": "ur-PK-AsadNeural",
        "50 Sal Larka - Asad": "ur-PK-AsadNeural",
        "60 Sal Larka - Asad": "ur-PK-AsadNeural",
    },
    "🇸🇦 ARABIC - عربي": {
        "10 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "20 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "30 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "50 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "60 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "10 Sal Larka - Asad": "ur-PK-AsadNeural",
        "20 Sal Larka - Asad": "ur-PK-AsadNeural",
        "30 Sal Larka - Asad": "ur-PK-AsadNeural",
        "50 Sal Larka - Asad": "ur-PK-AsadNeural",
        "60 Sal Larka - Asad": "ur-PK-AsadNeural",
    },
}

cat = st.selectbox("📁 CATEGORY:", list(VOICE_CATEGORIES.keys()), index=1)
voices = VOICE_CATEGORIES[cat]
voice_key = st.selectbox(f"{cat} - Asad / Uzma - Age 10-60:", list(voices.keys()), index=6)
voice_name = voices[voice_key]

st.info(f"SELECTED: {cat} - {voice_key} -> {voice_name} - Khalis")

limit_options = {"⚡ 15 Sec":15, "🔥 30 Sec":30, "🎙️ 1 Min":60, "⏰ 2 Min":120, "🚀 10 Min FULL":600}
MAX_SEC = limit_options[st.selectbox("⏱️ LIMIT:", list(limit_options.keys()), index=0)]
MAX_CHARS = MAX_SEC * 15

TEXTS = {
    "🇵🇰 URDU CLEAR": "السلام علیکم! میرے پیارے بھائیوں اور بہنوں! مہر مارٹ کا خالص ماکی ایک سو فیصد خالص ہے!",
    "🇵🇰 SINDHI KHALIS - سنڌي": "السلام عليڪم! منهنجا پيارا ڀائرو ۽ ڀينرون! مهر مارٽ جو خالص ماکي هڪ سئو سيڪڙو خالص آهي! صرف اوڻٽيهه سو پنجاهتر روپين ۾!",
    "🇮🇳 HINDI - हिंदी": "नमस्ते! मेरे प्यारे भाइयों और बहनों! मेहर मार्ट का शुद्ध शहद सौ प्रतिशत खालिस है!",
    "🇺🇸 ENGLISH CLEAR": "Hello friends! Mehar Mart Pure Honey is 100 percent pure!",
    "🇸🇦 ARABIC - عربي": "السلام عليكم! عسل مهر مارت نقي 100 بالمئة!",
}

default_text = TEXTS.get(cat, TEXTS["🇵🇰 SINDHI KHALIS - سنڌي"])
if MAX_SEC >= 120:
    default_text = (default_text + " ") * 20

text_input = st.text_area(f"Text ({MAX_CHARS} max) - {cat} - Khalis Pure:", value=default_text, height=240, max_chars=MAX_CHARS)
st.metric(f"{len(text_input)} chars", f"{len(text_input)//12} sec / {MAX_SEC} sec")
st.progress(min(len(text_input)/MAX_CHARS, 1.0))

rate_opt = st.select_slider("Speed:", options=["-15%", "-10%", "-5%", "+0%", "+10%"], value="-5%")

def clean(t): 
    return t.strip()

def split_no_cut(text, size=400):
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

async def gen_edge_with_retry(text, voice, rate, path):
    for attempt in range(4):
        try:
            if os.path.exists(path):
                os.remove(path)
            await edge_tts.Communicate(text=text, voice=voice, rate=rate).save(path)
            if os.path.exists(path) and os.path.getsize(path) > 800:
                return True
        except Exception as e:
            await asyncio.sleep(1.5)
    return False

def gtts_backup(text, path, category):
    try:
        lang = 'ar' if 'ARABIC' in category else 'en' if 'ENGLISH' in category else 'ur'
        gTTS(text=text, lang=lang, slow=False).save(path)
        return True
    except:
        return False

async def gen(text, voice, rate, category):
    if os.path.exists("voice"):
        shutil.rmtree("voice")
    os.makedirs("voice", exist_ok=True)
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
        ok = await gen_edge_with_retry(p, voice, rate, path)
        if not ok:
            ok = gtts_backup(p, path, category)
        if ok and os.path.exists(path):
            files.append(path)
        bar.progress((i+1)/len(parts))
    if not files:
        raise Exception("Voice nahi bani - Dobara BANAO dabao")
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
    with st.spinner(f"{cat} - {voice_key} - {voice_name} Khalis..."):
        try:
            path = asyncio.run(gen(text_input, voice_name, rate_opt, cat))
            st.balloons()
            st.success(f"✅ Ready! {cat} - {voice_key} - Khalis Pure - No Cut!")
            st.audio(path)
            with open(path, "rb") as f:
                st.download_button(f"📥 Download {voice_key} Khalis", f, file_name=f"{cat[:5]}_{voice_key.replace(' ','_')}_KHALIS_{MAX_SEC}.mp3")
        except Exception as e:
            st.error(f"Error: {e}")
