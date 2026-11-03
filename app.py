import streamlit as st
import asyncio
import edge_tts

# --- FREE TRANSLATOR - NO API KEY NEEDED ---
try:
    from deep_translator import GoogleTranslator
    HAS_TRANSLATOR = True
except:
    HAS_TRANSLATOR = False
    st.error("deep_translator install karo: pip install deep-translator")

st.set_page_config(page_title="MEHAR V104 FINAL FIXED", layout="centered")
st.title("Asalam - V104 FINAL - Translation Fixed")
st.success("✅ V104 - Free Translation - No Groq Needed")

for k in ['ta_sindhi_text','ta_urdu_text','ta_hindi_text','ta_english_text','ta_arabic_text','master']:
    if k not in st.session_state:
        st.session_state[k] = ""

def translate_free(text, target_code):
    """Free Google Translator - Mehar Mart kabhi nahi ayega"""
    if not text.strip() or not HAS_TRANSLATOR:
        return text
    try:
        # target_code: sd=Sindhi, ur=Urdu, hi=Hindi, en=English, ar=Arabic
        translated = GoogleTranslator(source='auto', target=target_code).translate(text)
        return translated
    except Exception as e:
        st.error(f"Translate error {target_code}: {e}")
        return text

# --- MASTER ---
master = st.text_area("📝 MASTER PROMPT (Urdu me likho):", height=160, key="master", placeholder="ہر گاؤں کی ایک کہانی ہوتی ہے...")

col1, col2 = st.columns(2)
with col1:
    if st.button("🔄 ALL 5 BOX BHARO - TRANSLATE", type="primary", use_container_width=True):
        if not master.strip():
            st.warning("Pehle likho Bhai!")
        else:
            with st.spinner("Translate ho raha hai..."):
                # FIX: Har box ko uski zaban me translate karo
                st.session_state['ta_sindhi_text'] = translate_free(master, 'sd')  # Sindhi
                st.session_state['ta_urdu_text'] = master  # Urdu - same
                st.session_state['ta_hindi_text'] = translate_free(master, 'hi')  # Hindi
                st.session_state['ta_english_text'] = translate_free(master, 'en')  # English
                st.session_state['ta_arabic_text'] = translate_free(master, 'ar')  # Arabic
                st.success("✅ Ho Gaya! Ab har box me alag zaban!")
                st.balloons()
with col2:
    if st.button("🗑️ CLEAR", use_container_width=True):
        for k in st.session_state.keys():
            st.session_state[k] = ""
        st.rerun()

# --- REQUIREMENTS.TXT ME YE ADD KARNA ---
# streamlit
# edge-tts
# deep-translator

VOICES = {
    "sindhi": {"Asad Larka (10-60)": "ur-PK-AsadNeural", "Uzma Larki (10-60)": "ur-PK-UzmaNeural"},
    "urdu": {"Asad Larka": "ur-PK-AsadNeural", "Uzma Larki": "ur-PK-UzmaNeural"},
    "hindi": {"Madhur Larka": "hi-IN-MadhurNeural", "Swara Larki": "hi-IN-SwaraNeural"},
    "english": {"Guy Larka": "en-US-GuyNeural", "Jenny Larki": "en-US-JennyNeural"},
    "arabic": {"Hamed Larka": "ar-SA-HamedNeural", "Zariyah Larki": "ar-SA-ZariyahNeural"}
}

async def make_voice(text, voice, speed, filename):
    await edge_tts.Communicate(text, voice, rate=f"{speed:+d}%").save(filename)

def render_box(box_key, flag, voice_dict):
    with st.expander(f"✅ {flag} - {len(st.session_state.get(box_key,''))} chars", expanded=True):
        st.selectbox("Time:", ["60 Second"], key=f"time_{box_key}")
        sel = st.selectbox("Voice (Larka/Larki):", list(voice_dict.keys()), key=f"v_{box_key}")
        st.text_area("Text:", height=140, key=box_key, max_chars=840)
        speed = st.slider("Speed:", -20, 20, -5, key=f"spd_{box_key}")
        if st.button(f"🎙️ Voice Banao - {sel}", key=f"b_{box_key}", use_container_width=True):
            txt = st.session_state.get(box_key,"")
            if txt.strip():
                fn = f"/tmp/{box_key}.mp3"
                asyncio.run(make_voice(txt, voice_dict[sel], speed, fn))
                st.audio(fn)
                with open(fn,"rb") as f:
                    st.download_button("⬇️ Download", f, file_name=f"{box_key}.mp3", key=f"dl_{box_key}")

render_box('ta_sindhi_text', '🇵🇰 SINDHI BOX', VOICES["sindhi"])
render_box('ta_urdu_text', '🇵🇰 URDU BOX', VOICES["urdu"])
render_box('ta_hindi_text', '🇮🇳 HINDI BOX', VOICES["hindi"])
render_box('ta_english_text', '🇬🇧 ENGLISH BOX', VOICES["english"])
render_box('ta_arabic_text', '🇸🇦 ARABIC BOX', VOICES["arabic"])
