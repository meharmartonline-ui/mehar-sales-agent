import streamlit as st
import os
import asyncio
import edge_tts
from groq import Groq

st.set_page_config(page_title="MEHAR V103 FINAL FIXED", layout="centered")
st.title("Asalam - Jo Likha Wahi - V103")
st.success("✅ V103 - Translation ON - Mehar Mart OFF - Larka Larki Fix")

# --- GROQ ---
groq_key = st.secrets.get("GROQ_API_KEY") if hasattr(st, 'secrets') else os.getenv("GROQ_API_KEY")
client = Groq(api_key=groq_key) if groq_key else None
if client:
    st.success("✅ Groq Connected")
else:
    st.warning("Groq Key missing - Secrets me dalo")

for k in ['ta_sindhi_text','ta_urdu_text','ta_hindi_text','ta_english_text','ta_arabic_text','master']:
    if k not in st.session_state:
        st.session_state[k] = ""

# --- FIXED TRANSLATION - NO MEHAR MART ---
def translate_fix(text, lang):
    if not client or not text.strip():
        return text
    
    prompts = {
        "SINDHI": f"Translate this EXACT story into Sindhi (سنڌي Arabic script) only. Do NOT add any honey, Mehar Mart, or ads. Keep THE LAST PROMISE in English. Story: {text}",
        "URDU": f"Translate this EXACT story into Urdu (اردو) only. Do NOT add honey or ads. Story: {text}",
        "HINDI": f"Translate this EXACT story into Hindi (हिंदी Devanagari) only. No ads. Story: {text}",
        "ENGLISH": f"Translate this EXACT story into English only. No ads. Story: {text}",
        "ARABIC": f"Translate this EXACT story into Arabic (العربية) only. No ads. Story: {text}"
    }
    
    try:
        r = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a precise translator. Never add extra advertisement."},
                {"role": "user", "content": prompts[lang]}
            ],
            temperature=0.1,
            max_tokens=1200
        )
        return r.choices[0].message.content.strip()
    except Exception as e:
        return text  # Fail hua to original hi de do

# --- MASTER ---
master = st.text_area("📝 MASTER PROMPT:", height=160, key="master", placeholder="Har gaaon ki ek kahani...")

col1, col2 = st.columns(2)
with col1:
    if st.button("🔄 ALL 5 BOX BHARO - TRANSLATE KARO", type="primary", use_container_width=True):
        if not master.strip():
            st.warning("Pehle likho!")
        elif not client:
            st.error("Groq Key nahi!")
        else:
            with st.spinner("5 zabano me translate ho raha hai..."):
                # FIX: ta_ keys me direct dalo - Empty bug khatam
                st.session_state['ta_sindhi_text'] = translate_fix(master, "SINDHI")
                st.session_state['ta_urdu_text'] = translate_fix(master, "URDU")
                st.session_state['ta_hindi_text'] = translate_fix(master, "HINDI")
                st.session_state['ta_english_text'] = translate_fix(master, "ENGLISH")
                st.session_state['ta_arabic_text'] = translate_fix(master, "ARABIC")
                st.success("✅ Ho Gaya! Ab har box me apni zaban me aayega!")
                st.balloons()
with col2:
    if st.button("🗑️ CLEAR", use_container_width=True):
        for k in ['ta_sindhi_text','ta_urdu_text','ta_hindi_text','ta_english_text','ta_arabic_text','master']:
            st.session_state[k] = ""
        st.rerun()

# --- VOICES - LARKA LARKI FIX ---
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
    with st.expander(f"✅ {flag} - {len(st.session_state.get(box_key,''))} chars", expanded=False):
        st.selectbox("Time:", ["60 Second"], key=f"time_{box_key}")
        sel = st.selectbox("Voice (Larka/Larki):", list(voice_dict.keys()), key=f"voice_{box_key}")
        st.text_area("Text:", height=120, key=box_key, max_chars=840)
        speed = st.slider("Speed:", -20, 20, -5, key=f"spd_{box_key}")
        if st.button(f"🎙️ Voice Banao - {sel}", key=f"btn_{box_key}", use_container_width=True):
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
