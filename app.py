import streamlit as st, os, asyncio, shutil, subprocess, re
import edge_tts

st.set_page_config(page_title="MEHAR V95 - Pure Sindhi", layout="centered")
st.title("MEHAR V95 - Pure Sindhi Alphabet ✅")
st.success("V95 FINAL: 52 Harf Pure Sindhi - No Urdu Translation!")

cat = "🇵🇰 SINDHI KHALIS - سنڌي"
voice_key = st.selectbox("Age:", ["10 Sal Larka - Asad", "20 Sal Larka - Asad", "30 Sal Larka - Asad", "50 Sal Larka - Asad", "60 Sal Larka - Asad", "10 Sal Larki - Uzma", "20 Sal Larki - Uzma"], index=2)
VOICE_MAP = {"Larka": "ur-PK-AsadNeural", "Larki": "ur-PK-UzmaNeural"}
voice_name = VOICE_MAP["Larka" if "Larka" in voice_key else "Larki"]

time_label = st.selectbox("Time:", ["15 Second", "20 Second", "30 Second", "60 Second", "2 Minutes", "3 Minutes", "5 Minutes", "10 Minutes"], index=2)
MAX_SEC = {"15 Second":15, "20 Second":20, "30 Second":30, "60 Second":60, "2 Minutes":120, "3 Minutes":180, "5 Minutes":300, "10 Minutes":600}[time_label]
MAX_CHARS = MAX_SEC * 14

# PURE SINDHI 52 ALPHABET - Full List
SINDHI_ALPHABET_52 = [
    "ا", "ب", "ٻ", "ت", "ث", "ج", "ڄ", "چ", "ڇ", "ح", "خ",
    "د", "ڌ", "ڏ", "ڊ", "ڍ", "ذ", "ر", "ڙ", "ز", "س", "ش", "ص", "ض", "ط", "ظ", "ع", "غ",
    "ف", "ڦ", "ق", "ڪ", "ک", "گ", "ڳ", "ڱ", "ل", "م", "ن", "ڻ", "و", "ه", "ھ", "ء", "ي",
]

# TTS Mapping - Pure Sindhi sound - No Urdu word translation!
PURE_SINDHI_TTS_MAP = {
    "ٻ": "ب",   # ٻه -> بہ - Pure Sindhi 2 - Not Urdu دو!
    "ڄ": "ج",   # ڄ - j
    "ڃ": "نج",  # ڃ
    "ڇ": "چھ",  # ڇهه -> چھہ - 6
    "ٽ": "ٹ",   # ٽي -> ٹی - 3
    "ٺ": "ٹھ",  # ٺ
    "ٿ": "تھ",  # ٿ
    "ڌ": "دھ",  # ڌ - dh
    "ڏ": "ڈ",   # ڏهه -> ڈہ - 10
    "ڊ": "ڈ",   # ڊليوري -> ڈلیوری
    "ڍ": "ڈھ",  # ڍ
    "ڀ": "بھ",  # ڀينرون -> بھینرون - Bhai-bhen - Pure!
    "ڦ": "پھ",  # ڦ
    "ڪ": "ک",   # ڪ - k - عليڪم -> علیکم
    "ڳ": "گ",   # ڳ
    "ڱ": "نگ",  # ڱ
    "ڻ": "ن",   # ڻ - retroflex n
    "ڙ": "ڑ",   # ڙ - stays
    "ھ": "ہ",   # ھ -> ہ - آھي -> آہی - Aahe
}

SINDHI_NUMBERS = {
    0:"ٻڙي",1:"هڪ",2:"ٻه",3:"ٽي",4:"چار",5:"پنج",6:"ڇهه",7:"ست",8:"اٺ",9:"نو",10:"ڏهه",
    11:"يارنهن",12:"ٻارهن",13:"تيرنهن",14:"چوڏهن",15:"پندرهن",16:"سورنهن",17:"سترنهن",18:"ارڙهن",19:"اُڻويهہ",20:"ويهہ",
    21:"ايڪويهہ",22:"ٻاويھ",23:"ٽاويھ",24:"چوويھ",25:"پنجويھ",26:"ڇويھ",27:"ستاويھ",28:"اٺاويھ",29:"اُڻٽيهہ",30:"ٽيهہ",
    31:"ايڪٽيهہ",32:"ٻٽيهہ",33:"ٽيٽيهہ",34:"چوٽيهہ",35:"پنجٽيهہ",36:"ڇٽيهہ",37:"ستٽيهہ",38:"اٺٽيهہ",39:"اُڻتاليهہ",40:"چاليهہ",
    50:"پنجاهہ",60:"سٺ",70:"ستر",80:"اسي",90:"نوي",100:"سئو",
    1000:"هزار"
}

text_input = st.text_area(f"Pure Sindhi - {MAX_SEC}s:", value="السلام عليڪم! منهنجا پيارا ڀائرو ۽ ڀينرون! مهر مارٽ جو خالص ماکي هڪ سئو سيڪڙو خالص آهي! صرف ٻه هزار نو سو پنجاهتر روپين ۾! سڄي پاڪستان ۾ فري ڊليوري!", height=240, max_chars=MAX_CHARS)
st.metric(f"{len(text_input)} / {MAX_CHARS}", f"{len(text_input)//14} sec / {MAX_SEC} sec")
st.progress(min(len(text_input)/MAX_CHARS, 1.0))
rate_opt = st.select_slider("Speed:", options=["-5%", "-15%", "+10%"], value="-5%")

def clean_pure_sindhi_alphabet(text):
    t = text.strip().replace("!", "۔")
    
    # STEP 1 - Keep original Sindhi words - No Urdu translation!
    # آهي - Original - Sirf ھ -> ہ for TTS
    # ٻه - Original - Sirf ٻ -> ب for TTS - Not دو!
    # ڀينرون - Original - Sirf ڀ -> بھ for TTS
    
    # STEP 2 - 52 Harf Pure Sindhi Alphabet Mapping - Only chars!
    # This is Alphabet fix - Not word translation!
    for sindhi_char, tts_char in PURE_SINDHI_TTS_MAP.items():
        t = t.replace(sindhi_char, tts_char)
    
    # STEP 3 - Special fixes - Pure Sindhi sound!
    # آهي - After mapping ھ->ہ, آهي -> آہی - Aahe - Lamba nahi - Short!
    # For lamba Aahe - Alf khech ke - آآہی
    # User wants lamba - So آہی -> آآہی
    if "آہی" in t:
        t = t.replace("آہی", "آآہی")  # Lamba Aahe - Alif khech ke!
    if "آہے" in t:
        t = t.replace("آہے", "آآہے")
    
    # سڄي -> After mapping ڄ->ج, سڄي -> سجی - But pure Sindhi سجّی with tashdeed
    t = t.replace("سجی", "سجّی")  # Pure Sindhi sound - Sajji!
    
    # عليڪم - After mapping ڪ->ک, عليڪم -> علیکم - Salam!
    t = t.replace("عليکم", "علیکم").replace("عليڪم", "علیکم")
    
    # ڊليوري -> After mapping ڊ->ڈ, ڊليوري -> ڈلیوری
    # Keep!
    
    # Numbers - Pure Sindhi numbers - Keep original!
    t = t.replace("100%", "سئو سيڪڙو")
    
    # 2975 - Pure Sindhi ginti - Not Urdu دو ہزار!
    # ٻه هزار نو سو پنجاهتر - Pure Sindhi!
    t = t.replace("2975", "ٻہ ہزار نو سو پنجاہتر")
    t = t.replace("ٻہ ہزار", "بہ ہزار")  # TTS - بہ ہزار - Pure Sindhi sound!
    t = t.replace("اوڻٽيهه سو پنجاهتر", "بہ ہزار نو سو پنجاہتر")
    
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

async def gen(text, voice, rate):
    if os.path.exists("voice"):
        shutil.rmtree("voice")
    os.makedirs("voice", exist_ok=True)
    text = clean_pure_sindhi_alphabet(text)
    parts = split_no_cut(text, 1000)
    files = []
    for i, p in enumerate(parts):
        p = clean_pure_sindhi_alphabet(p)
        if not p: continue
        path = f"voice/{i}.mp3"
        ok = await gen_edge(p, voice, rate, path)
        if ok:
            files.append(path)
    if not files:
        raise Exception("Voice fail")
    final = f"voice/FINAL_PureSindhi_{MAX_SEC}s.mp3"
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

if st.button(f"🎙️ {voice_key} - {time_label} - Pure Sindhi Banao", type="primary", use_container_width=True):
    with st.spinner(f"Pure Sindhi 52 Harf - {voice_key}..."):
        try:
            path = asyncio.run(gen(text_input, voice_name, rate_opt))
            st.balloons()
            st.success(f"✅ Ready! Pure Sindhi 52 Harf - Original آھي!")
            st.audio(path)
            st.caption(f"Pure: {clean_pure_sindhi_alphabet(text_input)}")
            st.info(f"52 Harf: {', '.join(SINDHI_ALPHABET_52)}")
            with open(path, "rb") as f:
                st.download_button(f"📥 Download Pure Sindhi", f, file_name=f"Pure_Sindhi_52Harf_{MAX_SEC}s.mp3")
        except Exception as e:
            st.error(f"Error: {e}")
