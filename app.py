import streamlit as st, os, asyncio, shutil, subprocess, re
import edge_tts

st.set_page_config(page_title="MEHAR V95 - Lamba Aahe", layout="centered")
st.title("MEHAR V95 - Lamba Aahe ✅")
st.success("V95 FINAL: Aahe = آآہے - Alif Lamba Khech Ke")

cat = "🇵🇰 SINDHI KHALIS - سنڌي"
voice_key = st.selectbox("Age:", ["10 Sal Larka - Asad", "20 Sal Larka - Asad", "30 Sal Larka - Asad", "50 Sal Larka - Asad", "60 Sal Larka - Asad", "10 Sal Larki - Uzma", "20 Sal Larki - Uzma"], index=2)
VOICE_MAP = {"Larka": "ur-PK-AsadNeural", "Larki": "ur-PK-UzmaNeural"}
voice_name = VOICE_MAP["Larka" if "Larka" in voice_key else "Larki"]

time_label = st.selectbox("Time:", ["15 Second", "20 Second", "30 Second", "60 Second", "2 Minutes", "3 Minutes", "5 Minutes", "10 Minutes"], index=2)
MAX_SEC = {"15 Second":15, "20 Second":20, "30 Second":30, "60 Second":60, "2 Minutes":120, "3 Minutes":180, "5 Minutes":300, "10 Minutes":600}[time_label]
MAX_CHARS = MAX_SEC * 14

SINDHI_1_100 = {0:"ٻڙي",1:"هڪ",2:"ٻه",3:"ٽي",4:"چار",5:"پنج",6:"ڇهه",7:"ست",8:"اٺ",9:"نو",10:"ڏهه",20:"ويهہ",30:"ٽيهہ",40:"چاليهہ",50:"پنجاهہ",60:"سٺ",70:"ستر",80:"اسي",90:"نوي",100:"سئو"}

text_input = st.text_area(f"Text - {MAX_SEC}s - Lamba Aahe:", value="السلام عليڪم! منهنجا پيارا ڀائرو ۽ ڀينرون! مهر مارٽ جو خالص ماکي هڪ سئو سيڪڙو خالص آهي! صرف ٻه هزار نو سو پنجاهتر روپين ۾! سڄي پاڪستان ۾ فري ڊليوري!", height=220, max_chars=MAX_CHARS)
st.metric(f"{len(text_input)} / {MAX_CHARS}", f"{len(text_input)//14} sec / {MAX_SEC} sec")
st.progress(min(len(text_input)/MAX_CHARS, 1.0))
rate_opt = st.select_slider("Speed:", options=["-5%", "-15%", "+10%"], value="-5%")

def clean_lamba_aahe(text):
    t = text.strip().replace("!", "۔")
    
    # LAMBA AAHE - Alif khech ke - FINAL FIX!
    # آهي -> آآہے - Double Alif - Lamba Aahe!
    # آآہے = Alf lamba khech ke - Aa...he
    t = t.replace("آهي", "آآہے")  # LAMBA - Double Alif!
    t = t.replace("آهي", "آآہے")
    t = t.replace("آ ہے", "آآہے")  # Agar pehle wala ho
    t = t.replace("آہے", "آآہے")  # Short ko lamba karo
    t = t.replace("آہی", "آآہے")
    t = t.replace("آهن", "آآہیں")
    
    # Baqi Khalis Sindhi - No Urdu دو!
    t = t.replace("ڀينرون", "بھینرون")
    t = t.replace("ڀائرو", "بھائرو")
    t = t.replace("ٻه", "بہ")  # ٻه -> بہ - Khalis Sindhi - Not دو!
    t = t.replace("ٻہ", "بہ")
    t = t.replace("اوڻٽيهه سو پنجاهتر", "بہ ہزار نو سو پنجاہتر")
    
    # 52 Harf - TTS readable but Khalis sound
    mapping = {"ٻ":"ب","ڄ":"ج","ڃ":"نج","ڳ":"گ","ڱ":"نگ","ڻ":"ن","ٽ":"ٹ","ٺ":"ٹھ","ٿ":"تھ","ڌ":"دھ","ڏ":"ڈ","ڊ":"ڈ","ڍ":"ڈھ","ڀ":"بھ","ڦ":"پھ","ڇ":"چھ","ڪ":"ک","ڙ":"ڑ","ھ":"ہ"}
    for s,u in mapping.items():
        t = t.replace(s,u)
    
    t = t.replace("عليڪم", "علیکم")
    t = t.replace("سڄي", "سجّی")  # سڄي -> سجّی - Khalis
    t = t.replace("سجی", "سجّی")
    t = t.replace("ڊليوري", "ڈلیوری")
    t = t.replace("فري", "فری")
    t = t.replace("100%", "سئو سيڪڙو")
    
    # Numbers 1-100 Khalis Sindhi
    def rep_num(m):
        n=int(m.group())
        return SINDHI_1_100.get(n, f"{n}")
    t = re.sub(r'\b\d+\b', rep_num, t)
    t = t.replace("2975", "بہ ہزار نو سو پنجاہتر")
    
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
    text = clean_lamba_aahe(text)
    parts = split_no_cut(text, 1000)
    files = []
    for i, p in enumerate(parts):
        p = clean_lamba_aahe(p)
        if not p: continue
        path = f"voice/{i}.mp3"
        ok = await gen_edge(p, voice, rate, path)
        if ok:
            files.append(path)
    if not files:
        raise Exception("Voice fail")
    final = f"voice/FINAL_LambaAahe_{MAX_SEC}s.mp3"
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

if st.button(f"🎙️ {voice_key} - {time_label} - Lamba Aahe Banao", type="primary", use_container_width=True):
    with st.spinner(f"Lamba Aahe - Alif khech ke - {voice_key}..."):
        try:
            path = asyncio.run(gen(text_input, voice_name, rate_opt))
            st.balloons()
            st.success(f"✅ Ready! Lamba Aahe - آآہے - Alif Khech Ke!")
            st.audio(path)
            st.caption(f"Lamba Aahe Fixed: {clean_lamba_aahe(text_input)}")
            with open(path, "rb") as f:
                st.download_button(f"📥 Download Lamba Aahe", f, file_name=f"Lamba_Aahe_{MAX_SEC}s.mp3")
        except Exception as e:
            st.error(f"Error: {e}")
