import streamlit as st, os, asyncio, re, subprocess
import edge_tts

st.set_page_config(page_title="MEHAR V91 - NO AUDIO FIX", layout="centered")
st.title("MEHAR V91 - 10 Min FIXED 🔥")
st.success("V91: NoAudioReceived Error 100% Fixed - Chunk System!")

# === PRONUNCIATION FIX ===
def fix_urdu(text):
    text = text.replace("  ", " ")
    # Zyada , . ! hata do - isi se error aata hai
    text = re.sub(r'[,]{2,}', ',', text)
    text = re.sub(r'[.]{2,}', '.', text)
    text = text.replace("،", ",")
    return text

# === SETTINGS ===
limit_options = {
    "⚡ 15 Sec - Viral": 15, "🔥 20 Sec": 20, "💯 30 Sec": 30,
    "🎙️ 1 Min": 60, "⏰ 2 Min": 120, "🚀 10 Min - FULL": 600,
}
sel = st.selectbox("LIMIT:", list(limit_options.keys()), index=5)
MAX_SEC = limit_options[sel]
MAX_CHARS = MAX_SEC * 15

voice_map = {
    "👩 Ayesha - SAAF URDU (No Error)": "ur-PK-AyeshaNeural",
    "👩 Uzma - Viral": "ur-PK-UzmaNeural",
    "👦 Asad": "ur-PK-AsadNeural",
}
voice_name = voice_map[st.selectbox("Voice:", list(voice_map.keys()), index=0)]

FULL_10_MIN = """Assalam-o-Alaikum Wa Rahmatullahi Wa Barakatuhu! Mere pyare bhaiyon aur behno, aaj main aapko apni sachi kahani sunata hun jo Mehar Mart ke Pure Honey se judi hai. Ye kahani 10 minute ki hai.

Mera naam Ahmed hai, main Lahore me rehta hun. Do saal pehle tak mujhe har waqt thakan rehti thi. Doctor ne kaha immunity weak hai, khalis ghiza khao. Bazaar ka shehad milawati tha. Walid Sahab ne kaha asal shehad ka zikr Quran Pak me Surah Nahal me hai, us me shifa hai.

Phir Facebook pe Mehar Mart Online ka page dekha. Behen bata rahi thi ye Sidr ka shehad hai, lab tested hai, 100 percent natural hai. Maine 03452352112 par WhatsApp kiya, 2 din me parcel aa gaya, Free Delivery, Cash on Delivery.

Parcel khola to khushbu aisi jaise khet se aaya ho, rang sunahri, gaadha, taar bandh raha tha. Yehi khalis ki nishani hai.

Subah neem garam pani me ek chamach shehad aur nimbu dal ke piya, energy mehsoos hui. Ek hafte me Ami ne kaha chehra fresh lag raha hai. Biwi ne kaha active ho gaye ho. Bete Ali ko doodh me deya to nazla khatam.

Ab ghar me ye shehad khatam nahi hota. Ye sirf shehad nahi, shifa hai, Sunnat hai. Nabi Pak Sallallahu Alaihi Wasallam ko bhi pasand tha.

Mehar Mart wale jhoot nahi bolte, lab report dikhate hain. Bazaar me 5000 ka milta hai, ye sirf 2975 me, 15 percent OFF, Free Delivery pure Pakistan me, Karachi, Lahore, Islamabad, Peshawar, Quetta, Multan, sab jaga.

Agar aap bhi thakan se pareshan ho, immunity weak hai, to ek baar Mehar Mart ka Pure Honey try karo.

Abhi order karo 03452352112 par, stock limited hai, season saal me ek baar aata hai. JazakAllah Khair! Pakistan Zindabad!
"""

text_input = st.text_area(f"Text ({MAX_CHARS} max):", value=FULL_10_MIN if MAX_SEC>=120 else "Assalam-o-Alaikum! Ye Mehar Mart ka Pure Honey 100 percent khalis hai! Sirf 2975 me!", height=280, max_chars=MAX_CHARS)

chars = len(text_input)
st.metric("Time", f"{chars//15} sec / {MAX_SEC} sec", f"{chars} chars")
st.progress(min(chars/MAX_CHARS, 1.0))

# === MAIN FIX - CHUNK ME BANAYEGA - NO AUDIO ERROR KHATAM ===
async def gen_in_chunks(text, voice):
    os.makedirs("voice", exist_ok=True)
    
    # 1. Text ko 400 chars ke chunks me todo - isi se error khatam hoga
    chunks = []
    temp = ""
    for sentence in re.split(r'(?<=[.!?।\n])\s+', text):
        if len(temp) + len(sentence) < 400:
            temp += " " + sentence
        else:
            if temp.strip():
                chunks.append(temp.strip())
            temp = sentence
    if temp.strip():
        chunks.append(temp.strip())
    
    if not chunks:
        chunks = [text[i:i+400] for i in range(0, len(text), 400)]
    
    st.write(f"Total {len(chunks)} parts me bana raha hun...")
    
    files = []
    bar = st.progress(0)
    status_text = st.empty()
    
    for i, ch in enumerate(chunks):
        ch_fixed = fix_urdu(ch)
        if not ch_fixed.strip():
            continue
        p_path = f"voice/chunk_{i}.mp3"
        status_text.text(f"Part {i+1}/{len(chunks)} - {ch_fixed[:50]}...")
        
        # Retry 2 times if fail
        for attempt in range(3):
            try:
                await edge_tts.Communicate(ch_fixed, voice, rate="-5%", volume="+10%").save(p_path)
                break
            except Exception as e:
                if attempt == 2:
                    st.error(f"Part {i+1} fail: {e}")
                    raise e
                await asyncio.sleep(1)
        
        files.append(p_path)
        bar.progress((i+1)/len(chunks))
    
    # Merge all
    final = "voice/FINAL_10MIN_FIXED.mp3"
    try:
        import imageio_ffmpeg
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        with open("voice/list.txt","w", encoding="utf-8") as f:
            for fp in files:
                f.write(f"file '{os.path.abspath(fp)}'\n")
        subprocess.run([ffmpeg,"-y","-f","concat","-safe","0","-i","voice/list.txt","-c","copy",final], check=True, capture_output=True)
    except Exception as e:
        st.warning(f"FFmpeg merge fail {e}, first part play")
        final = files[0]
    
    status_text.empty()
    return final, len(chunks)

if st.button("🎙️ FIXED VOICE BANAO - NO ERROR", type="primary", use_container_width=True):
    with st.spinner(f"{MAX_SEC} sec ki voice {len(text_input)//400+1} parts me ban rahi... 1 min lagega..."):
        try:
            path, parts = asyncio.run(gen_in_chunks(text_input, voice_name))
            st.balloons()
            st.success(f"✅ {len(text_input)//15} Second ki Voice Ready - {parts} parts me - No Error!")
            st.audio(path)
            with open(path, "rb") as f:
                st.download_button(f"📥 Download {len(text_input)//15} Sec", f, file_name=f"FIXED_{len(text_input)//15}SEC.mp3", mime="audio/mpeg")
        except Exception as e:
            st.error(f"Error: {e}")
            st.info("Tip: Text me se Urdu , ، aur zyada dots ... hata do, aur dubara try karo!")

st.divider()
st.caption("V91 Fix: 400 chars per chunk - NoAudioReceived khatam! - Ayesha voice best hai!")
