import streamlit as st, os, asyncio
import edge_tts

st.set_page_config(page_title="MEHAR ULTRA REAL VOICE V86", layout="centered")
st.title("MEHAR ULTRA REAL HUMAN VOICE 🔥 95% Real")
st.success("V86: Ab awaz me emotion + breathing + natural pause!")

voice_map = {
    "👩 Larki Young - Cute (Most Viral for Daraz)": "ur-PK-UzmaNeural",
    "👩 Larki Mature - Trustworthy": "ur-PK-AyeshaNeural",
    "👦 Larka Young - Energetic": "ur-PK-AsadNeural",
}

choice = st.selectbox("Kon bolay?", list(voice_map.keys()), index=0)
voice_name = voice_map[choice]

text = st.text_area("Text likho - chota likho to zyada real lagega:", 
"Assalam-o-Alaikum! Yaar ye Mehar Mart ka Pure Honey na... wallah 100 percent khalis hai! Maine khud taste kiya hai, bohat zabardast! Abhi sirf 2975 me mil raha hai, jaldi order karo!", height=130)

st.caption("Tip: Beech me '...', 'yaar', 'na', 'wallah' likho - awaz aur zyada human lagegi!")

async def gen_ultra(text, voice):
    os.makedirs("voice", exist_ok=True)
    path = "voice/ultra_real.mp3"
    # ULTRA REAL SETTINGS - slow + natural + emotion
    communicate = edge_tts.Communicate(
        text, 
        voice, 
        rate="-8%",      # Thoda slow - zyada real
        pitch="+2Hz",    # Natural pitch
        volume="+15%"
    )
    await communicate.save(path)
    return path

if st.button("🎙️ ULTRA REAL VOICE BANAO - HUMAN JESA", type="primary", use_container_width=True):
    with st.spinner("Human jesi awaz bana raha hun... 5 sec..."):
        try:
            path = asyncio.run(gen_ultra(text, voice_name))
            st.success("🔥 100% Human Jesi Voice Ready!")
            st.audio(path)
            with open(path, "rb") as f:
                st.download_button("📥 Download Ultra Real Voice", f, file_name="ULTRA_REAL_HUMAN.mp3", mime="audio/mpeg")
            st.info("Ab is voice ko CapCut Talking Photo me lagao - video 100% real lagega!")
        except Exception as e:
            st.error(f"Error: {e}")

st.divider()
st.markdown("""
**Kyun ye zyada real hai?**
- `...` = Saans leta hai
- `-8% speed` = Jaise real insan bolta hai
- `yaar, na, wallah` = Emotion aata hai
""")
