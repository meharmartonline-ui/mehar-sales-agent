import streamlit as st, os, asyncio, shutil, subprocess, re
import edge_tts

st.set_page_config(page_title="MEHAR V95 - WORLD STUDIO", layout="centered")
st.title("MEHAR V95 - WORLD STUDIO 🌍")
st.success("V95 FINAL: Full System + Hindi Added + Pure Sindhi 52 Harf!")

# LANGUAGE CATEGORY - FULL SYSTEM - HINDI ADDED!
VOICE_CATEGORIES = {
    "🇵🇰 SINDHI KHALIS - سنڌي": {
        "10 Sal Larka - Asad": "ur-PK-AsadNeural",
        "20 Sal Larka - Asad": "ur-PK-AsadNeural",
        "30 Sal Larka - Asad": "ur-PK-AsadNeural",
        "50 Sal Larka - Asad": "ur-PK-AsadNeural",
        "60 Sal Larka - Asad": "ur-PK-AsadNeural",
        "10 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "20 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "30 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "50 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "60 Sal Larki - Uzma": "ur-PK-UzmaNeural",
    },
    "🇵🇰 URDU - اردو": {
        "20 Sal Larka - Asad": "ur-PK-AsadNeural",
        "30 Sal Larka - Asad": "ur-PK-AsadNeural",
        "20 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "30 Sal Larki - Uzma": "ur-PK-UzmaNeural",
    },
    "🇮🇳 HINDI - हिन्दी": {
        "20 Sal Larka - Madhur": "hi-IN-MadhurNeural",
        "30 Sal Larka - Madhur": "hi-IN-MadhurNeural",
        "20 Sal Larki - Swara": "hi-IN-SwaraNeural",
        "30 Sal Larki - Swara": "hi-IN-SwaraNeural",
        "20 Sal Larki - Swara Fast": "hi-IN-SwaraNeural",
    },
    "🇬🇧 ENGLISH - US": {
        "20 Sal Larka - Guy": "en-US-GuyNeural",
        "20 Sal Larki - Jenny": "en-US-JennyNeural",
        "20 Sal Larki - Aria": "en-US-AriaNeural",
    },
    "🇬🇧 ENGLISH - UK": {
        "20 Sal Larka - Ryan": "en-GB-RyanNeural",
        "20 Sal Larki - Sonia": "en-GB-SoniaNeural",
    },
    "🇸🇦 ARABIC - عربي": {
        "20 Sal Larka - Hamed": "ar-SA-HamedNeural",
        "20 Sal Larki - Zariyah": "ar-SA-ZariyahNeural",
    },
}

TIME_OPTIONS = {
    "15 Second": 15,
    "20 Second": 20,
    "30 Second": 30,
    "60 Second (1 Minute)": 60,
    "2 Minutes": 120,
    "3 Minutes": 180,
    "4 Minutes": 240,
    "5 Minutes": 300,
    "6 Minutes": 360,
    "7 Minutes": 420,
    "8 Minutes": 480,
    "9 Minutes": 540,
    "10 Minutes": 600,
}

SINDHI_ALPHABET_52 = ["ا", "ب", "ٻ", "ت", "ث", "ج", "ڄ", "چ", "ڇ", "ح", "خ", "د", "ڌ", "ڏ", "ڊ", "ڍ", "ذ", "ر", "ڙ", "ز", "س", "ش", "ص", "ض", "ط", "ظ", "ع", "غ", "ف", "ڦ", "ق", "ڪ", "ک", "گ", "ڳ", "ڱ", "ل", "م", "ن", "ڻ", "و", "ه", "ھ", "ء", "ي"]
PURE_SINDHI_TTS_MAP = {"ٻ":"ب","ڄ":"ج","ڃ":"نج","ڇ":"چھ","ٽ":"ٹ","ٺ":"ٹھ","ٿ":"تھ","ڌ":"دھ","ڏ":"ڈ","ڊ":"ڈ","ڍ":"ڈھ","ڀ":"بھ","ڦ":"پھ","ڪ":"ک","ڳ":"گ","ڱ":"نگ","ڻ":"ن","ڙ":"ڑ","ھ":"ہ"}

st.markdown("### 🌍 LANGUAGE CATEGORY - زبان / भाषा")
language_cat = st.selectbox("Language Category:", list(VOICE_CATEGORIES.keys()), index=0)
voices = VOICE_CATEGORIES[language_cat]
voice_key = st.selectbox(f"{language_cat} - Age 10-60:", list(voices.keys()), index=2)
voice_name = voices[voice_key]
st.info(f"SELECTED: {language_cat} - {voice_key} - {voice_name}")

time_label = st.selectbox("⏱️ TIME CATEGORY:", list(TIME_OPTIONS.keys()), index=2)
MAX_SEC = TIME_OPTIONS[time_label]
MAX_CHARS = MAX_SEC * 14

default_texts = {
    "🇵🇰 SINDHI KHALIS - سنڌي": "السلام عليڪم! منهنجا پيارا ڀائرو ۽ ڀينرون! مهر مارٽ جو خالص ماکي هڪ سئو سيڪڙو خالص آهي! صرف ٻه هزار نو سو پنجاهتر روپين ۾! سڄي پاڪستان ۾ فري ڊليوري!",
    "🇵🇰 URDU - اردو": "السلام علیکم! میرے پیارے بھائیوں اور بہنوں! مہر مارٹ کا خالص شہد سو فیصد خالص ہے! صرف دو ہزار نو سو پچھتر روپے میں!",
    "🇮🇳 HINDI - हिन्दी": "नमस्ते! मेरे प्यारे भाइयों और बहनों! मेहर मार्ट का शुद्ध शहद सौ प्रतिशत शुद्ध है! सिर्फ दो हजार नौ सौ पचहत्तर रुपये में! पूरे भारत में फ्री डिलीवरी!",
    "🇬🇧 ENGLISH - US": "Hello! My dear brothers and sisters! Mehar Mart pure honey is 100 percent pure! Only for 2975 rupees! Free delivery!",
    "🇬🇧 ENGLISH - UK": "Hello! My dear brothers and sisters! Mehar Mart pure honey is 100 percent pure! Only for 2975 rupees!",
    "🇸🇦 ARABIC - عربي": "السلام عليكم! إخواني وأخواتي الأعزاء! عسل مهر مارت نقي 100 بالمائة!",
}

text_input = st.text_area(f"Text ({MAX_CHARS} max) - {language_cat} - {time_label}:", value=default_texts.get(language_cat, default_texts["🇵🇰 SINDHI KHALIS - سنڌي"]), height=240, max_chars=MAX_CHARS)
st.metric(f"{len(text_input)} / {MAX_CHARS}", f"{len(text_input)//14} sec / {MAX_SEC} sec")
st.progress(min(len(text_input)/MAX_CHARS, 1.0))
rate_opt = st.select_slider("Speed:", options=["-5%", "-15%", "+10%"], value="-5%")

def clean_pure_sindhi_alphabet(text, lang_cat):
    t = text.strip().replace("!", "۔" if "SINDHI" in lang_cat or "URDU" in lang_cat else "!")
    if "SINDHI" in lang_cat:
        for sc, tc in PURE_SINDHI_TTS_MAP.items():
            t = t.replace(sc, tc)
        if "آہی" in t:
            t = t.replace("آہی", "آآہی")
        if "آہے" in t:
            t = t.replace("آہے", "آآہے")
        if "آهي" in t:
            t = t.replace("آهي", "آآہی")
        t = t.replace("سجی", "سجّی").replace("عليکم", "علیکم").replace("عليڪم", "علیکم").replace("100%", "سئو سيڪڙو").replace("2975", "ٻہ ہزار نو سو پنجاہتر").replace("ٻہ ہزار", "بہ ہزار").replace("اوڻٽيهه سو پنجاهتر", "بہ ہزار نو سو پنجاہتر")
    return t

def split_no_cut(text, size=1000):
    if len(text) <= size:
        return [text]
    words = text.split(' ')
    parts, cur = [], ""
    for w in words:
        if not w: continue
        if len(cur) + len(w) + 1 <= size:
            cur = cur + " " + w if cur else w
        else:
            if cur: parts.append(cur)
            cur = w
    if cur: parts.append(cur)
    return parts if parts else [text]

async def gen_edge(text, voice, rate, path):
    for _ in range(5):
        try:
            if os.path.exists(path):
                os.remove(path)
            await edge_tts.Communicate(text=text, voice=voice, rate=rate).save(path)
            if os.path.exists(path) and os.path.getsize(path) > 800:
                return True
        except:
            await asyncio.sleep(1)
    return False

async def gen(text, voice, rate, lang_cat):
    if os.path.exists("voice"):
        shutil.rmtree("voice")
    os.makedirs("voice", exist_ok=True)
    text = clean_pure_sindhi_alphabet(text, lang_cat)
    parts = split_no_cut(text, 1000)
    files = []
    for i, p in enumerate(parts):
        p = clean_pure_sindhi_alphabet(p, lang_cat)
        if not p: continue
        path = f"voice/{voice.replace('-','_')}_{i}.mp3"
        ok = await gen_edge(p, voice, rate, path)
        if ok:
            files.append(path)
    if not files:
        raise Exception("Voice fail")
    final = f"voice/FINAL_{voice_key.replace(' ','_')}_{MAX_SEC}s.mp3"
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

if st.button(f"🎙️ {language_cat} - {voice_key} - {time_label} - KHALIS BANAO", type="primary", use_container_width=True):
    with st.spinner(f"{voice_key} - {time_label}..."):
        try:
            path = asyncio.run(gen(text_input, voice_name, rate_opt, language_cat))
            st.balloons()
            st.success(f"✅ Ready! {language_cat} - {voice_key} - {time_label}!")
            st.audio(path)
            st.caption(f"Cleaned: {clean_pure_sindhi_alphabet(text_input, language_cat)}")
            if "SINDHI" in language_cat:
                st.info(f"52 Harf Pure Sindhi: {', '.join(SINDHI_ALPHABET_52)}")
            with open(path, "rb") as f:
                st.download_button(f"📥 Download {voice_key} - {time_label}", f, file_name=f"{voice_key.replace(' ','_')}_{MAX_SEC}s.mp3")
        except Exception as e:
            st.error(f"Error: {e}")
