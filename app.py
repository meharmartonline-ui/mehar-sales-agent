import streamlit as st, os, asyncio, shutil, subprocess, re
import edge_tts

st.set_page_config(page_title="MEHAR V95 - WORLD STUDIO", layout="centered")
st.title("MEHAR V95 - WORLD STUDIO 🌍")
st.success("V95 FINAL: 1-100 Sindhi Ginti Full Fix - Search Based")

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

# SINDHI 1-100 FULL GINTI - Search Based
SINDHI_1_100 = {
    0: "ٻڙي", 1: "هڪ", 2: "ٻه", 3: "ٽي", 4: "چار", 5: "پنج", 6: "ڇهه", 7: "ست", 8: "اٺ", 9: "نو", 10: "ڏهه",
    11: "يارنهن", 12: "ٻارهن", 13: "تيرنهن", 14: "چوڏهن", 15: "پندرهن", 16: "سورنهن", 17: "سترنهن", 18: "ارڙهن", 19: "اُڻويهہ", 20: "ويهہ",
    21: "ايڪويهہ", 22: "ٻاويھ", 23: "ٽاويھ", 24: "چوويھ", 25: "پنجويھ", 26: "ڇويھ", 27: "ستاويھ", 28: "اٺاويھ", 29: "اُڻٽيهہ", 30: "ٽيهہ",
    31: "ايڪٽيهہ", 32: "ٻٽيهہ", 33: "ٽيٽيهہ", 34: "چوٽيهہ", 35: "پنجٽيهہ", 36: "ڇٽيهہ", 37: "ستٽيهہ", 38: "اٺٽيهہ", 39: "اُڻتاليهہ", 40: "چاليهہ",
    41: "ايڪتاليهہ", 42: "ٻتاليهہ", 43: "ٽيتاليهہ", 44: "چواليهہ", 45: "پنجتاليهہ", 46: "ڇتاليهہ", 47: "ستتاليهہ", 48: "اٺتاليهہ", 49: "اُڻپنجاهہ", 50: "پنجاهہ",
    51: "ايڪپنجاهہ", 52: "ٻپنجاهہ", 53: "ٽيپنجاهہ", 54: "چوپنجاهہ", 55: "پنجپنجاهہ", 56: "ڇپنجاهہ", 57: "ستپنجاهہ", 58: "اٺپنجاهہ", 59: "اُڻسٺ", 60: "سٺ",
    61: "ايڪسٺ", 62: "ٻهٺ", 63: "ٽيسٺ", 64: "چوسٺ", 65: "پنجسٺ", 66: "ڇهسٺ", 67: "ستسٺ", 68: "اٺسٺ", 69: "اُڻهتر", 70: "ستر",
    71: "ايڪهتر", 72: "ٻهتر", 73: "ٽيهتر", 74: "چوهتر", 75: "پنجتر", 76: "ڇهتر", 77: "ستهتر", 78: "اٺتر", 79: "اُڻاسي", 80: "اسي",
    81: "ايڪاسي", 82: "ٻاسي", 83: "ٽياسي", 84: "چوراسي", 85: "پنجاسي", 86: "ڇياسي", 87: "ستاسي", 88: "اٺاسي", 89: "اُڻانوي", 90: "نوي",
    91: "ايڪانوي", 92: "ٻانوي", 93: "ٽيانوي", 94: "چورانوي", 95: "پنجانوي", 96: "ڇانوي", 97: "ستانوي", 98: "اٺانوي", 99: "اُڻسئو", 100: "سئو",
}

def sindhi_number_to_words(n):
    if n in SINDHI_1_100:
        return SINDHI_1_100[n]
    if n < 1000:
        # 101-999
        hundreds = n // 100
        rem = n % 100
        if rem == 0:
            return f"{SINDHI_1_100[hundreds]} سئو" if hundreds > 1 else "سئو"
        else:
            h_word = f"{SINDHI_1_100[hundreds]} سئو" if hundreds > 1 else "سئو"
            return f"{h_word} {SINDHI_1_100[rem]}" if rem in SINDHI_1_100 else f"{h_word} {rem}"
    if n < 100000:
        # thousands
        thousands = n // 1000
        rem = n % 1000
        t_word = "هزار" if thousands == 1 else f"{sindhi_number_to_words(thousands)} هزار"
        if rem == 0:
            return t_word
        else:
            return f"{t_word} {sindhi_number_to_words(rem)}"
    return str(n)

TEXTS = {
    "🇵🇰 SINDHI KHALIS - سنڌي": "السلام عليڪم! منهنجا پيارا ڀائرو ۽ ڀينرون! مهر مارٽ جو خالص ماکي هڪ سئو سيڪڙو خالص آهي! صرف ٻه هزار نو سو پنجاهتر روپين ۾! سڄي پاڪستان ۾ فري ڊليوري!",
}

text_input = st.text_area(f"Text ({MAX_CHARS} max) - {cat} - {time_label}:", value=TEXTS.get(cat, "السلام عليڪم! صرف ٻه هزار نو سو پنجاهتر روپين ۾! 1 2 3 4 5 10 20 30 50 100 روپيا!"), height=240, max_chars=MAX_CHARS)
st.metric(f"{len(text_input)} / {MAX_CHARS}", f"{len(text_input)//14} sec / {MAX_SEC} sec")
st.progress(min(len(text_input)/MAX_CHARS, 1.0))

rate_opt = st.select_slider("Speed:", options=["-5%", "-15%", "+10%"], value="-5%")

# FULL FIX - 1-100 Sindhi Ginti + 52 Harf + آهي + ڀينرون
def clean_full_fix(text, category):
    t = text.strip()
    t = t.replace("!", "۔")
    
    if "SINDHI" in category:
        # STEP 1 - Numbers 1-100 ko Sindhi me badlo - Pehle digits
        # 2975 jaise bade numbers
        def replace_numbers(match):
            num = int(match.group())
            if num <= 100:
                return SINDHI_1_100.get(num, str(num))
            elif num <= 5000:
                return sindhi_number_to_words(num)
            return match.group()
        
        # Digits 0-9 and numbers - regex
        t = re.sub(r'\b\d+\b', replace_numbers, t)
        
        # Specific large number - 2975
        t = t.replace("اوڻٽيهه سو پنجاهتر", "ٻه هزار نو سو پنجاهتر")
        
        # STEP 2 - Direct word fix - آهي + ٻه + ڀينرون
        t = t.replace("ڀينرون", "بہینرون")
        t = t.replace("ڀائرو", "بھائرو")
        t = t.replace("آهي", "آہی")
        t = t.replace("آهي", "آہی")
        t = t.replace("آهن", "آہن")
        t = t.replace("ٻه", "ٻہ")
        t = t.replace("ٻہ", "با")
        t = t.replace("با", "دو")  # Final - ٻه -> دو - clear
        
        # 52 HARF MAP
        mapping_52 = {
            "ٻ": "ب", "ڄ": "ج", "ڃ": "نج", "ڳ": "گ", "ڱ": "نگ", "ڻ": "ن",
            "ٽ": "ٹ", "ٺ": "ٹھ", "ٿ": "تھ", "ڌ": "دھ", "ڏ": "ڈ", "ڊ": "ڈ", "ڍ": "ڈھ",
            "ڀ": "بھ", "ڦ": "پھ", "ڇ": "چھ", "ڪ": "ک", "ڙ": "ڑ", "ھ": "ہ",
        }
        for s, u in mapping_52.items():
            t = t.replace(s, u)
        
        t = t.replace("عليڪم", "علیکم")
        t = t.replace("سڄي", "سجی")
        t = t.replace("ڊليوري", "ڈلیوری")
        t = t.replace("فري", "فری")
        t = t.replace("100%", "سئو سيڪڙو")
        t = t.replace("%", " سيڪڙو")
    
    elif "URDU" in category:
        t = re.sub(r'\b2975\b', "دو ہزار نو سو پچھتر", t)
        t = t.replace("100%", "ایک سو فیصد")
    elif "HINDI" in category:
        t = re.sub(r'\b2975\b', "दो हजार नौ सौ पचहत्तर", t)
        t = t.replace("100%", "सौ प्रतिशत")
    elif "ARABIC" in category:
        t = re.sub(r'\b2975\b', "الفان وتسعمائة وخمسة وسبعون", t)
        t = t.replace("100%", "مئة بالمئة")
    elif "ENGLISH" in category:
        t = re.sub(r'\b2975\b', "two thousand nine hundred seventy five", t)
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
    with st.spinner(f"{voice_key} - {time_label} - 1-100 Fix..."):
        try:
            path = asyncio.run(gen(text_input, voice_name, rate_opt, cat))
            st.balloons()
            st.success(f"✅ Ready! 1-100 Ginti Clear - {cat}!")
            st.audio(path)
            st.caption(f"Fixed: {clean_full_fix(text_input, cat)}")
            st.info(f"Sindhi 1-10: {', '.join([f'{k}={v}' for k,v in list(SINDHI_1_100.items())[:11]])}")
            with open(path, "rb") as f:
                st.download_button(f"📥 Download {voice_key} {time_label}", f, file_name=f"{voice_key.replace(' ','_')}_{MAX_SEC}s_100FIX.mp3")
        except Exception as e:
            st.error(f"Error: {e}")
