import streamlit as st, os, asyncio, shutil, subprocess
import edge_tts
from gtts import gTTS

st.set_page_config(page_title="MEHAR V95 - WORLD STUDIO", layout="centered")
st.title("MEHAR V95 - WORLD STUDIO 🌍")
st.success("V95: SINDHI KHALIS FIX - Salam + 2975 Sindhi me bolega")

VOICE_CATEGORIES = {
    "🇵🇰 SINDHI KHALIS - سنڌي": {
        "10 Sal Larki": "ur-PK-UzmaNeural",
        "20 Sal Larki": "ur-PK-UzmaNeural",
        "30 Sal Larki": "ur-PK-UzmaNeural",
        "50 Sal Larki": "ur-PK-UzmaNeural",
        "60 Sal Larki": "ur-PK-UzmaNeural",
        "10 Sal Larka": "ur-PK-AsadNeural",
        "20 Sal Larka": "ur-PK-AsadNeural",
        "30 Sal Larka": "ur-PK-AsadNeural",
        "50 Sal Larka": "ur-PK-AsadNeural",
        "60 Sal Larka": "ur-PK-AsadNeural",
    },
}

cat = st.selectbox("📁 CATEGORY:", list(VOICE_CATEGORIES.keys()), index=0)
voices = VOICE_CATEGORIES[cat]
voice_key = st.selectbox(f"{cat} - Age 10-20-30-50-60:", list(voices.keys()), index=6)
voice_name = voices[voice_key]

st.info(f"SELECTED: {cat} - {voice_key} -> {voice_name} - Khalis Pure")

MAX_SEC = 15
MAX_CHARS = 225

text_input = st.text_area(f"Text (225 max) - {cat} - Khalis Pure:", value="السلام عليڪم! منهنجا پيارا ڀائرو ۽ ڀينرون! مهر مارٽ جو خالص ماکي هڪ سئو سيڪڙو خالص آهي! صرف اوڻٽيهه سو پنجاهتر روپين ۾! سڄي پاڪستان ۾ فري ڊليوري!", height=220, max_chars=MAX_CHARS)
st.metric(f"{len(text_input)} chars", f"{len(text_input)//14} sec")

rate_opt = "-5%"

# SINDHI KHALIS FIX - Salam + Ginti dono Sindhi me!
def fix_sindhi_khalis(text):
    # ! se ruk jata hai - Is ko . banao
    text = text.replace("!", "۔").replace("!", "۔")
    # Ginti fix - 2975 ko Sindhi lafzon me - Ta ke Sindhi me bole
    text = text.replace("اوڻٽيهه سو پنجاهتر", "ٻه هزار نو سو پنجاهتر")
    text = text.replace("اوڻٽيهه سو", "ٻه هزار نو سو")
    # Agar digits hon to bhi Sindhi me
    text = text.replace("2975", "ٻه هزار نو سو پنجاهتر")
    text = text.replace("2975 روپين ۾", "ٻه هزار نو سو پنجاهتر روپين ۾")
    return text.strip()

def clean(t): 
    return fix_sindhi_khalis(t)

def split_no_cut(text, size=1000):
    if len(text) <= size:
        return [text]
    return [text[i:i+size] for i in range(0, len(text), size)]

async def try_edge(text, voice, rate, path):
    is_larka = "Larka" in voice or "Asad" in voice
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

# SINDHI KHALIS - GTTS SD - Salam + Ginti dono Sindhi khalis!
def try_gtts_sindhi_khalis(text, path, voice_key):
    try:
        # Sindhi khalis - sd language - Salam + ginti dono Sindhi me
        gTTS(text=text, lang='sd', slow=False).save(path)
        # LARKA FIX - Asad ke liye awaz mardana karo
        if "Larka" in voice_key or "Asad" in voice_key:
            try:
                import imageio_ffmpeg
                ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
                temp_path = path.replace(".mp3", "_male.mp3")
                # Pitch neeche - Mardana awaz
                subprocess.run([ffmpeg, "-y", "-i", path, "-filter:a", "asetrate=22050*0.85,atempo=1.18,aresample=22050", "-c:a", "libmp3lame", temp_path], check=True, capture_output=True)
                if os.path.exists(temp_path):
                    os.replace(temp_path, path)
            except:
                pass
        return True
    except Exception as e:
        print(f"SD fail {e}")
        try:
            gTTS(text=text, lang='ur', slow=False).save(path)
            return True
        except:
            return False

async def gen(text, voice, rate, voice_key):
    if os.path.exists("voice"):
        shutil.rmtree("voice")
    os.makedirs("voice", exist_ok=True)
    text = fix_sindhi_khalis(text)
    parts = split_no_cut(text, 1000)
    files = []
    is_larka = "Larka" in voice_key or "Asad" in voice_key
    for i, p in enumerate(parts):
        p = clean(p)
        if not p: continue
        safe = "ASAD_LARKA" if is_larka else "UZMA_LARKI"
        path = f"voice/{safe}_{i}.mp3"
        # SINDHI KHALIS - Pehle SD Sindhi - Salam + Ginti dono khalis
        ok = try_gtts_sindhi_khalis(p, path, voice_key)
        if not ok:
            ok = await try_edge(p, voice, rate, path)
        if ok:
            files.append(path)
    if not files:
        raise Exception("Voice fail")
    final = f"voice/FINAL_SINDHI_KHALIS_{safe}.mp3"
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
    with st.spinner(f"{voice_key} - Sindhi Khalis Salam + Ginti..."):
        try:
            path = asyncio.run(gen(text_input, voice_name, rate_opt, voice_key))
            st.balloons()
            if "Larka" in voice_key:
                st.success(f"✅ Ready! LARKA Asad - Sindhi Khalis - السلام عليڪم + ٻه هزار نو سو پنجاهتر - Mardana!")
            else:
                st.success(f"✅ Ready! LARKI Uzma - Sindhi Khalis - السلام عليڪم + ٻه هزار نو سو پنجاهتر - Zanana!")
            st.audio(path)
            st.caption(f"Fixed: {fix_sindhi_khalis(text_input)}")
            with open(path, "rb") as f:
                st.download_button(f"📥 Download {voice_key} Sindhi Khalis", f, file_name=f"{voice_key.replace(' ','_')}_SINDHI_KHALIS.mp3")
        except Exception as e:
            st.error(f"Error: {e}")
