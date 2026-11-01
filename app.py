import streamlit as st, os, asyncio, shutil, subprocess
import edge_tts
from gtts import gTTS

st.set_page_config(page_title="MEHAR V95 - WORLD STUDIO", layout="centered")
st.title("MEHAR V95 - WORLD STUDIO 🌍")
st.success("V95: GINTI FIX - 2975 Sahi Bolega - Sindhi Khalis")

VOICE_CATEGORIES = {
    "🇵🇰 URDU CLEAR - اردو": {
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
    "🇵🇰 SINDHI KHALIS - سنڌي خالص": {
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
voice_key = st.selectbox(f"{cat} - Asad/Uzma:", list(voices.keys()), index=6)
voice_name = voices[voice_key]

st.info(f"SELECTED: {cat} - {voice_key} -> {voice_name}")

MAX_SEC = st.selectbox("⏱️ LIMIT:", [15, 30, 60, 120, 600], index=0)
MAX_CHARS = MAX_SEC * 14

# GINTI FIX - Sahi Sindhi text
TEXTS = {
    "🇵🇰 URDU CLEAR - اردو": "السلام علیکم! میرے پیارے بھائیوں اور بہنوں! مہر مارٹ کا خالص ماکی صرف 2975 روپے میں! سارے پاکستان میں فری ڈلیوری!",
    "🇵🇰 SINDHI KHALIS - سنڌي خالص": "السلام عليڪم! منهنجا پيارا ڀائرو ۽ ڀينرون! مهر مارٽ جو خالص ماکي صرف 2975 روپين ۾! سڄي پاڪستان ۾ فري ڊليوري!",
}

text_input = st.text_area(f"Text - {cat} - Khalis:", value=TEXTS.get(cat, TEXTS["🇵🇰 SINDHI KHALIS - سنڌي خالص"]), height=240, max_chars=MAX_CHARS)

char_count = len(text_input)
sec_count = char_count / 14
st.metric(f"{char_count} / {MAX_CHARS}", f"{sec_count:.1f} sec / {MAX_SEC} sec")
st.progress(min(char_count/MAX_CHARS, 1.0))

rate_opt = st.select_slider("Speed:", options=["-15%", "-10%", "-5%", "+0%", "+10%"], value="-5%")

# GINTI FIX FUNCTION - Asal bug fix!
def fix_ginti_khalis(text):
    # اوڻٽيهه سو پنجاهتر - Ye TTS sahi nahi parhta - Is ko 2975 banao
    replacements = {
        "اوڻٽيهه سو پنجاهتر": "2975",
        "اوڻٽيهه سو پنجاهتر روپين ۾": "2975 روپين ۾",
        "اوڻٽيهه سو": "2900",
        "اونٹيہہ سو پچھتر": "2975",
        "انتیس سو پچھتر": "2975",
        "انتیس سو": "2900",
        "2975 روپين ۾!": "2975 روپين ۾",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

def clean(t): 
    t = t.strip()
    t = fix_ginti_khalis(t)  # GINTI FIX YAHAN!
    return t

def split_no_cut_khalis(text, category):
    size = 1000 if "SINDHI" in category else 600
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

async def try_edge_khalis(text, voice, rate, path, is_larka):
    tries = 5 if is_larka else 3
    for _ in range(tries):
        try:
            if os.path.exists(path):
                os.remove(path)
            await edge_tts.Communicate(text=text, voice=voice, rate=rate).save(path)
            if os.path.exists(path) and os.path.getsize(path) > 800:
                return True
        except:
            await asyncio.sleep(1.2)
    return False

def try_gtts_backup(text, path, category):
    try:
        lang = 'sd' if "SINDHI" in category else 'ur'
        gTTS(text=text, lang=lang, slow=False).save(path)
        return True
    except:
        try:
            gTTS(text=text, lang='ur', slow=False).save(path)
            return True
        except:
            return False

async def gen(text, voice, rate, category, voice_key):
    if os.path.exists("voice"): shutil.rmtree("voice")
    os.makedirs("voice", exist_ok=True)
    is_larka = "Larka" in voice_key or "Asad" in voice_key
    text = fix_ginti_khalis(text)  # GINTI FIX
    parts = split_no_cut_khalis(text, category)
    files = []
    bar = st.progress(0)
    for i, p in enumerate(parts):
        p = clean(p)
        if not p: continue
        safe = "ASAD_LARKA" if is_larka else "UZMA_LARKI"
        path = f"voice/{safe}_{i}.mp3"
        ok = await try_edge_khalis(p, voice, rate, path, is_larka)
        if not ok:
            ok = try_gtts_backup(p, path, category)
        if ok:
            files.append(path)
        bar.progress((i+1)/len(parts))
    if not files:
        raise Exception("Voice fail")
    final = f"voice/FINAL_{safe}_KHALIS.mp3"
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
    with st.spinner(f"Bana raha hun..."):
        try:
            path = asyncio.run(gen(text_input, voice_name, rate_opt, cat, voice_key))
            st.balloons()
            st.success(f"✅ Ready! Ginti 2975 sahi bolega! {voice_key}")
            st.audio(path)
            st.caption(f"Fixed Text: {fix_ginti_khalis(text_input)}")
            with open(path, "rb") as f:
                st.download_button(f"📥 Download {voice_key}", f, file_name=f"{voice_key.replace(' ','_')}_2975_KHALIS.mp3")
        except Exception as e:
            st.error(f"Error: {e}")
