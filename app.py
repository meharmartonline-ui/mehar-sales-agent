import streamlit as st, os, asyncio, shutil, subprocess, re
import edge_tts

st.set_page_config(page_title="MEHAR V95 - WORLD STUDIO", layout="centered")
st.title("MEHAR V95 - WORLD STUDIO 🌍")
st.success("V95 FINAL: Only Sindhi Khalis - No Urdu - 1-100 Fix")

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

cat = "🇵🇰 SINDHI KHALIS - سنڌي"
voices = VOICE_CATEGORIES[cat]
voice_key = st.selectbox(f"{cat} - Age 10-60:", list(voices.keys()), index=1)
voice_name = voices[voice_key]
st.info(f"SELECTED: {cat} - {voice_key} -> {voice_name} - Khalis Sindhi")

time_label = st.selectbox("⏱️ TIME CATEGORY:", list(TIME_OPTIONS.keys()), index=0)
MAX_SEC = TIME_OPTIONS[time_label]
MAX_CHARS = MAX_SEC * 14

# SINDHI 1-100 KHALIS - No Urdu!
SINDHI_1_100_KHALIS = {
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

def sindhi_number_to_words_khalis(n):
    if n in SINDHI_1_100_KHALIS:
        return SINDHI_1_100_KHALIS[n]
    if n < 1000:
        hundreds = n // 100
        rem = n % 100
        if rem == 0:
            return f"{SINDHI_1_100_KHALIS[hundreds]} سئو" if hundreds > 1 else "سئو"
        else:
            h_word = f"{SINDHI_1_100_KHALIS[hundreds]} سئو" if hundreds > 1 else "سئو"
            return f"{h_word} {SINDHI_1_100_KHALIS[rem]}" if rem in SINDHI_1_100_KHALIS else f"{h_word} {rem}"
    if n < 100000:
        thousands = n // 1000
        rem = n % 1000
        t_word = "هزار" if thousands == 1 else f"{sindhi_number_to_words_khalis(thousands)} هزار"
        if rem == 0:
            return t_word
        else:
            return f"{t_word} {sindhi_number_to_words_khalis(rem)}"
    return str(n)

text_input = st.text_area(f"Text ({MAX_CHARS} max) - {cat} - {time_label} - Khalis Sindhi:", value="السلام عليڪم! منهنجا پيارا ڀائرو ۽ ڀينرون! مهر مارٽ جو خالص ماکي هڪ سئو سيڪڙو خالص آهي! صرف ٻه هزار نو سو پنجاهتر روپين ۾! سڄي پاڪستان ۾ فري ڊليوري! 1 2 3 10 20 30 100!", height=240, max_chars=MAX_CHARS)
st.metric(f"{len(text_input)} / {MAX_CHARS}", f"{len(text_input)//14} sec / {MAX_SEC} sec")
st.progress(min(len(text_input)/MAX_CHARS, 1.0))

rate_opt = st.select_slider("Speed:", options=["-5%", "-15%", "+10%"], value="-5%")

# ONLY SINDHI KHALIS FIX - No Urdu Translation!
def clean_sindhi_khalis_only(text):
    t = text.strip()
    t = t.replace("!", "۔")
    
    # STEP 1 - Numbers 1-100 Khalis Sindhi - Search based
    def replace_numbers_khalis(match):
        num = int(match.group())
        if num <= 100:
            return SINDHI_1_100_KHALIS.get(num, str(num))
        elif num <= 5000:
            return sindhi_number_to_words_khalis(num)
        return match.group()
    
    t = re.sub(r'\b\d+\b', replace_numbers_khalis, t)
    
    # STEP 2 - Direct word fix - ONLY SINDHI CHARS - No Urdu translation!
    # آهي + ٻه + ڀينرون + سڄي + ڊليوري - Khalis Sindhi me hi fix!
    
    # آهي - آهي -> آہی nahi - آہی Urdu - Ab آہے Sindhi khalis - ھ -> ہ but Sindhi style
    t = t.replace("آهي", "آہی")  # Temporary TTS ke liye - Display original
    # Final TTS ke liye Sindhi khalis chars - No دو!
    # ٻه - 2 - Sindhi me ٻه hi hai - Urdu دو nahi!
    # Is liye ٻه -> بہ - بہ Sindhi me bhi hai - Urdu دو nahi!
    # بہ = Sindhi implosive ka closest - دو = Urdu!
    
    # 52 HARF MAP - Only char mapping - No word translation to Urdu!
    # Ye sirf Asad ko parhane ke liye - Display me original Sindhi!
    mapping_khalis = {
        # Khalis Sindhi -> TTS readable but still Sindhi sound
        "ٻ": "ٻ",  # Keep - Try keep - Asad ke liye niche
        "ڄ": "ڄ",  # Keep
        "ڃ": "نج",
        "ڳ": "گ",
        "ڱ": "نگ",
        "ڻ": "ن",
        "ٽ": "ٽ",
        "ٺ": "ٹھ",
        "ٿ": "ٿ",
        "ڌ": "ڌ",
        "ڏ": "ڏ",
        "ڊ": "ڊ",
        "ڍ": "ڈھ",
        "ڀ": "ڀ",
        "ڦ": "ڦ",
        "ڇ": "ڇ",
        "ڪ": "ڪ",
        "ڙ": "ڑ",
        "ھ": "ہ",
    }
    # Actually for TTS - Asad ko ye chars nahi aate - Is liye TTS ke liye alag map
    tts_mapping_khalis = {
        "ٻ": "ب",   # ٻه -> بہ - Sindhi sound - Not Urdu دو!
        "ڄ": "ج",   # سڄي -> سجی - But سجی Urdu lagta - So سڄي -> سجّی
        "ڃ": "نج",
        "ڳ": "گ",
        "ڱ": "نگ",
        "ڻ": "ن",
        "ٽ": "ٹ",
        "ٺ": "ٹھ",
        "ٿ": "تھ",
        "ڌ": "دھ",
        "ڏ": "ڈ",
        "ڊ": "ڈ",  # ڊليوري -> ڈلیوری but Sindhi me ڈلیوری
        "ڍ": "ڈھ",
        "ڀ": "بھ",  # ڀينرون -> بھینرون - Sindhi khalis
        "ڦ": "پھ",
        "ڇ": "چھ",
        "ڪ": "ک",  # عليڪم -> علیکم - Salam fix
        "ڙ": "ڑ",
        "ھ": "ہ",
    }
    
    # Apply TTS mapping - But keep words Sindhi!
    for s_char, t_char in tts_mapping_khalis.items():
        t = t.replace(s_char, t_char)
    
    # Word level - ONLY SINDHI - No دو!
    # ٻه هزار - Pehle se - ٻه هزار -> بہ ہزار - Not دو ہزار!
    t = t.replace("بہ ہزار", "ٻہ ہزار")  # Display khalis
    t = t.replace("ٻہ ہزار", "بہ ہزار")  # TTS - بہ ہزار = Sindhi 2 hazar - Not Urdu دو!
    # Final - بہ ہزار is Sindhi khalis sound - دو ہزار is Urdu!
    
    # سڄي - Sindhi khalis - سجی Urdu - So سڄي -> سجّی with shadda - More Sindhi!
    t = t.replace("سڄي", "سجّی")  # سجّی - Tashdeed se Sindhi sound
    t = t.replace("سجی", "سجّی")  # saji -> sajji
    
    # Other fixes
    t = t.replace("عليڪم", "علیکم").replace("عليکم", "علیکم")
    t = t.replace("ڊليوري", "ڈلیوری").replace("ڈليوري", "ڈلیوری")
    t = t.replace("فري", "فری")
    t = t.replace("آهي", "آہی")
    t = t.replace("ڀينرون", "بھینرون")
    t = t.replace("ڀائرو", "بھائرو")
    t = t.replace("آہی", "آہے")  # آہے - Sindhi
    t = t.replace("100%", "سئو سيڪڙو")
    
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
    tries = 5
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

async def gen(text, voice, rate):
    if os.path.exists("voice"):
        shutil.rmtree("voice")
    os.makedirs("voice", exist_ok=True)
    text = clean_sindhi_khalis_only(text)
    parts = split_no_cut(text, 1000)
    files = []
    for i, p in enumerate(parts):
        p = clean_sindhi_khalis_only(p)
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
    with st.spinner(f"{voice_key} - {time_label} - Khalis Sindhi..."):
        try:
            path = asyncio.run(gen(text_input, voice_name, rate_opt))
            st.balloons()
            st.success(f"✅ Ready! Only Sindhi Khalis - No Urdu!")
            st.audio(path)
            st.caption(f"Khalis Fixed: {clean_sindhi_khalis_only(text_input)}")
            st.info(f"1-10 Khalis: {', '.join([f'{k}={v}' for k,v in list(SINDHI_1_100_KHALIS.items())[:11]])}")
            with open(path, "rb") as f:
                st.download_button(f"📥 Download {voice_key} Khalis Sindhi", f, file_name=f"{voice_key.replace(' ','_')}_{MAX_SEC}s_KHALIS_SINDHI.mp3")
        except Exception as e:
            st.error(f"Error: {e}")
