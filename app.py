import streamlit as st
import asyncio
import edge_tts

st.set_page_config(page_title="MEHAR V102 FIXED - FINAL", layout="centered")
st.title("Asalam - Jo Likha Wahi")
st.success("✅ FINAL FIX - No Mehar Mart - Jo Likha Wahi")

for k in ['ta_sindhi_text','ta_urdu_text','ta_hindi_text','ta_english_text','ta_arabic_text','master']:
    if k not in st.session_state:
        st.session_state[k] = ""

# --- MASTER ---
master = st.text_area("📝 MASTER PROMPT:", height=160, key="master", placeholder="Yahan naya likho...")

col1, col2 = st.columns(2)
with col1:
    if st.button("🔄 ALL 5 BOX BHARO - JO LIKHA WAHI", type="primary", use_container_width=True):
        if not master.strip():
            st.warning("Pehle likho Bhai!")
        else:
            st.session_state['ta_sindhi_text'] = master
            st.session_state['ta_urdu_text'] = master
            st.session_state['ta_hindi_text'] = master
            st.session_state['ta_english_text'] = master
            st.session_state['ta_arabic_text'] = master
            st.success("✅ Ho Gaya!")
with col2:
    if st.button("🗑️ SAB CLEAR KARO", use_container_width=True):
        for k in ['ta_sindhi_text','ta_urdu_text','ta_hindi_text','ta_english_text','ta_arabic_text','master']:
            st.session_state[k] = ""
        st.success("✅ Clear Ho Gaya - Ab naya likh sakte ho!")
        st.rerun()

# --- VOICE ---
VOICES = {
    "sindhi": {"Asad 10-60 Sal Larka": "ur-PK-AsadNeural"},
    "urdu": {"Asad Larka": "ur-PK-AsadNeural"},
    "hindi": {"Madhur Larka": "hi-IN-MadhurNeural"},
    "english": {"Guy Larka": "en-US-GuyNeural"},
    "arabic": {"Hamed Larka": "ar-SA-HamedNeural"}
}
async def make_voice(text, voice, speed, filename):
    await edge_tts.Communicate(text, voice, rate=f"{speed:+d}%").save(filename)

def render_box(box_key, flag, voice_dict):
    with st.expander(f"✅ {flag} - {len(st.session_state.get(box_key,''))} chars", expanded=False):
        st.selectbox("Time:", ["60 Second"], key=f"time_{box_key}")
        sel = st.selectbox("Voice:", list(voice_dict.keys()), key=f"v_{box_key}")
        st.text_area("Text (840 max):", height=120, key=box_key, max_chars=840)
        speed = st.slider("Speed:", -20, 20, -5, key=f"s_{box_key}")
        if st.button(f"🎙️ Voice Banao - {sel}", key=f"b_{box_key}", use_container_width=True):
            txt = st.session_state.get(box_key,"")
            if txt.strip():
                fn = f"/tmp/{box_key}.mp3"
                asyncio.run(make_voice(txt, voice_dict[sel], speed, fn))
                st.audio(fn)

render_box('ta_sindhi_text', '🇵🇰 SINDHI BOX', VOICES["sindhi"])
render_box('ta_urdu_text', '🇵🇰 URDU BOX', VOICES["urdu"])
render_box('ta_hindi_text', '🇮🇳 HINDI BOX', VOICES["hindi"])
render_box('ta_english_text', '🇬🇧 ENGLISH BOX', VOICES["english"])
render_box('ta_arabic_text', '🇸🇦 ARABIC BOX', VOICES["arabic"])
