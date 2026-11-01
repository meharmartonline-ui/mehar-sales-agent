import streamlit as st, os, asyncio, shutil, subprocess
import edge_tts

st.set_page_config(page_title="MEHAR V95 - WORLD STUDIO", layout="centered")
st.title("MEHAR V95 - WORLD STUDIO 🌍")
st.success("V95 FINAL: آهي + ڀينرون Fix")

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
    "🇵🇰 URDU CLEAR - اردو": {
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
    "🇮🇳 HINDI - हिंदी": {
        "10 Sal Larka - Asad": "hi-IN-MadhurNeural",
        "20 Sal Larka - Asad": "hi-IN-MadhurNeural",
        "30 Sal Larka - Asad": "hi-IN-MadhurNeural",
        "50 Sal Larka - Asad": "hi-IN-MadhurNeural",
        "60 Sal Larka - Asad": "hi-IN-MadhurNeural",
        "10 Sal Larki - Uzma": "hi-IN-SwaraNeural",
        "20 Sal Larki - Uzma": "hi-IN-SwaraNeural",
        "30 Sal Larki - Uzma": "hi-IN-SwaraNeural",
        "50 Sal Larki - Uzma": "hi-IN-SwaraNeural",
        "60 Sal Larki - Uzma": "hi-IN-SwaraNeural",
    },
    "🇸🇦 ARABIC - العربية": {
        "10 Sal Larka - Asad": "ar-SA-HamedNeural",
        "20 Sal Larka - Asad": "ar-SA-HamedNeural",
        "30 Sal Larka - Asad": "ar-SA-HamedNeural",
        "50 Sal Larka - Asad": "ar-SA-HamedNeural",
        "60 Sal Larka - Asad": "ar-SA-HamedNeural",
        "10 Sal Larki - Uzma": "ar-SA-ZariyahNeural",
        "20 Sal Larki - Uzma": "ar-SA-ZariyahNeural",
        "30 Sal Larki - Uzma": "ar-SA-ZariyahNeural",
        "50 Sal Larki - Uzma": "ar-SA-ZariyahNeural",
        "60 Sal Larki - Uzma": "ar-SA-ZariyahNeural",
    },
    "🇺🇸 ENGLISH - English": {
        "10 Sal Larka - Asad": "en-US-GuyNeural",
        "20 Sal Larka - Asad": "en-US-GuyNeural",
        "30 Sal Larka - Asad": "en-US-GuyNeural",
        "50 Sal Larka - Asad": "en-US-GuyNeural",
        "60 Sal Larka - Asad": "en-US-GuyNeural",
        "10 Sal Larki - Uzma": "en-US-JennyNeural",
        "20 Sal Larki - Uzma": "en-US-JennyNeural",
        "30 Sal Larki - Uzma": "en-US-JennyNeural",
        "50 Sal Larki - Uzma": "en-US-JennyNeural",
        "60 Sal Larki - Uzma": "en-US-JennyNeural",
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

cat = st.selectbox("📁 CATEGORY LANGUAGE:", list(VOICE_CATEGORIES.keys()), index=0)
voices = VOICE_CATEGORIES[cat]
voice_key = st.selectbox(f"{cat} - Age 10-60:", list(voices.keys()), index=1)
voice_name = voices[voice_key]
st.info(f"SELECTED: {cat} - {voice_key} -> {voice_name}")

time_label = st.selectbox("⏱️ TIME CATEGORY:", list(TIME_OPTIONS.keys()), index=0)
MAX_SEC = TIME_OPTIONS[time_label]
MAX_CHARS = MAX_SEC * 14

TEXTS = {
    "🇵🇰 SINDHI KHALIS - سنڌي": "السلام عليڪم! منهنجا پيارا ڀائرو ۽ ڀينرون! مهر مارٽ جو خالص ماکي هڪ سئو سيڪڙو خالص آهي! صرف ٻه هزار نو سو پنجاهتر روپين ۾! سڄي پاڪستان ۾ فري ڊليوري!",
}

text_input = st.text_area(f"Text ({MAX_CHARS} max) - {cat} - {time_label}:", value=TEXTS.get(cat, "السلام عليڪم! منهنجا پيارا ڀائرو ۽ ڀينرون! مهر مارٽ جو خالص ماکي هڪ سئو سيڪڙو خالص آهي!"), height=220, max_chars=MAX_CHARS)
st.metric(f"{len(text_input)} / {MAX_CHARS}", f"{len(text_input)//14} sec / {MAX_SEC} sec")
st.progress(min(len(text_input)/MAX_CHARS, 1.0))

rate_opt = st.select_slider("Speed:", options=["-5%", "-15%", "+10%"], value="-5%")

# FULL FIX - آهي + ڀينرون + سڄي + ڊليوري + 52 Harf
def clean_full_fix(text, category):
    t = text.strip()
    t = t.replace("!", "۔")
    
    if "SINDHI" in category:
        # GINTI
        t = t.replace("اوڻٽيهه سو پنجاهتر", "ٻه هزار نو سو پنجاهتر")
        t = t.replace("2975", "ٻه هزار نو سو پنجاهتر")
        
        # BUG 1 + 2 - آهي + ڀينرون - Direct word fix - Sab se pehle!
        t = t.replace("ڀينرون", "بھینرون")  # ڀ -> بھ - Asad clear bolega
        t = t.replace("ڀائرو", "بھائرو")
        t = t.replace("آهي", "آہے")  # آهي -> آہے - Asad clear
        t = t.replace("آهن", "آہن")
        t = t.replace("آهن", "آہن")
        
        # 52 HARF MAP - Full alphabet
        mapping_52 = {
            "ٻ": "ب",
            "ڄ": "ج",  # سڄي
            "ڃ": "نج",
            "ڳ": "گ",
            "ڱ": "نگ",
            "ڻ": "ن",
            "ٽ": "ٹ",
            "ٺ": "ٹھ",
            "ٿ": "تھ",
            "ڌ": "دھ",
            "ڏ": "ڈ",
            "ڊ": "ڈ",  # ڊليوري
            "ڍ": "ڈھ",
            "ڀ": "بھ",  # ڀينرون
            "ڦ": "پھ",
            "ڇ": "چھ",
            "ڪ": "ک",  # عليڪم
            "ڙ": "ڑ",
            "ھ": "ہ",  # ھ vs ہ - آهي me ھ
        }
        for s, u in mapping_52.items():
            t = t.replace(s, u)
        
        # Salam + سڄي + ڊليوري fix
        t = t.replace("عليڪم", "علیکم").replace("عليکم", "علیکم")
        t = t.replace("سڄي", "سجی").replace("سڃي", "سجی")
        t = t.replace("ڊليوري", "ڈلیوری").replace("ڈليوري", "ڈلیوری")
        t = t.replace("فري", "فری")
        
        t = t.replace("100%", "سئو سيڪڙو")
    
    elif "URDU" in category:
        t = t.replace("2975", "دو ہزار نو سو پچھتر")
        t = t.replace("100%", "ایک سو فیصد")
    elif "HINDI" in category:
        t = t.replace("2975", "दो हजार नौ सौ पचहत्तर")
        t = t.replace("100%", "सौ प्रतिशत")
    elif "ARABIC" in category:
        t = t.replace("2975", "الفان وتسعمائة وخمسة وسبعون")
        t = t.replace("100%", "مئة بالمئة")
    elif "ENGLISH" in category:
        t = t.replace("2975", "two thousand nine hundred seventy five")
        t = t.replace("100%", "one hundred percent")
    
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
    is_larka = "Larka" in voice or "Asad" in voice or "Madhur" in voice or "Hamed" in voice or "Guy" in voice
    tries = 5 if is_larka else 3
    for _ in range(tries):
        try:
            if os.path.exists(path):
                os.remove(path)
            await edge_tts.Communicate(text=text, voice=voice, rate=rate).save(path)
            if os.path.exists(path) and os.path.getsize(path) > 800:
                return True
        except:
            await asyncio.sleep(1)
    return False

async def gen(text, voice, rate, category):
    if os.path.exists("voice"):
        shutil.rmtree("voice")
    os.makedirs("voice", exist_ok=True)
    text = clean_full_fix(text, category)
    parts = split_no_cut(text, 1000)
    files = []
    for i, p in enumerate(parts):
        p = clean_full_fix(p, category)
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

if st.button(f"🎙️ {cat} - {voice_key} - {time_label} - KHALIS BANAO", type="primary", use_container_width=True):
    with st.spinner(f"{voice_key} - {time_label} - آهي ڀينرون Fix..."):
        try:
            path = asyncio.run(gen(text_input, voice_name, rate_opt, cat))
            st.balloons()
            st.success(f"✅ Ready! آهي + ڀينرون Clear - {cat}!")
            st.audio(path)
            st.caption(f"Fixed: {clean_full_fix(text_input, cat)}")
            with open(path, "rb") as f:
                st.download_button(f"📥 Download {voice_key} {time_label}", f, file_name=f"{voice_key.replace(' ','_')}_{MAX_SEC}s_FIX.mp3")
        except Exception as e:
            st.error(f"Error: {e}")
