import streamlit as st
import os
import asyncio
import edge_tts
from groq import Groq

st.set_page_config(page_title="MEHAR V102 FIXED - ASALAM FIX - JO LIKHA WAHI", layout="centered", page_icon="🎙️")
st.markdown("<style>.stButton>button{border-radius:12px; font-weight:bold;}</style>", unsafe_allow_html=True)

st.title("Asalam - Jo Likha Wahi")
st.caption("MEHAR V102 FIXED - ASALAM FIX - Bug Fixed Version")

# --- GROQ CLIENT ---
groq_key = st.secrets.get("GROQ_API_KEY") if hasattr(st, 'secrets') else None
if not groq_key:
    groq_key = os.getenv("GROQ_API_KEY")

client = None
if groq_key:
    try:
        client = Groq(api_key=groq_key)
        st.success("✅ Groq Connected - Asalam Fix Active")
    except Exception as e:
        st.error(f"Groq Error: {e}")
else:
    st.warning("⚠️ GROQ_API_KEY add karo Streamlit Secrets me")

# --- SESSION STATE INIT ---
for k in ['sindhi_text','urdu_text','hindi_text','english_text','arabic_text']:
    if k not in st.session_state:
        st.session_state[k] = ""

# --- FIXED TRANSLATION FUNCTION ---
def translate_exact(text, target):
    if not client or not text.strip():
        return text
    
    lang_prompts = {
        "SINDHI": f"Task: Translate EXACTLY into Sindhi Arabic script. Rules: DO NOT add Mehar Mart honey ad. Keep 'THE LAST PROMISE' in English. Story:\n{text}",
        "URDU": f"Task: Translate EXACTLY into Urdu. Rules: DO NOT add Mehar Mart honey ad. Keep 'THE LAST PROMISE' in English. Story:\n{text}",
        "HINDI": f"Task: Translate EXACTLY into Hindi Devanagari. Rules: DO NOT add honey ad. Story:\n{text}",
        "ENGLISH": f"Task: Translate EXACTLY into English. Keep 'THE LAST PROMISE' as is. Story:\n{text}",
        "ARABIC": f"Task: Translate EXACTLY into Arabic. Rules: DO NOT add honey ad. Story:\n{text}"
    }
    
    try:
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a precise translator. You translate EXACTLY what user gives. You never add extra content."},
                {"role": "user", "content": lang_prompts[target]}
            ],
            temperature=0.1,
            max_tokens=1200
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

VOICE_MAP_SIMPLE = {
    "sindhi_text": {"Asad 10-60 Sal Larka": "ur-PK-AsadNeural"},
    "urdu_text": {"Asad Larka": "ur-PK-AsadNeural", "Uzma Larki": "ur-PK-UzmaNeural"},
    "hindi_text": {"Madhur Larka": "hi-IN-MadhurNeural", "Swara Larki": "hi-IN-SwaraNeural"},
    "english_text": {"Guy Larka": "en-US-GuyNeural", "Jenny Larki": "en-US-JennyNeural"},
    "arabic_text": {"Hamed Larka": "ar-SA-HamedNeural", "Zariyah Larki": "ar-SA-ZariyahNeural"}
}

async def make_voice(text, voice, speed, filename):
    rate = f"{speed:+d}%"
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(filename)

# --- MASTER PROMPT ---
st.markdown("### 📝 MASTER PROMPT:")
master_prompt = st.text_area("MASTER PROMPT:", height=160, placeholder="Har gaaon ki ek kahani hoti hai... yahan likho", label_visibility="collapsed")

if st.button("🔄 ALL 5 BOX BHARO - ASALAM FIX - JO LIKHA WAHI", type="primary", use_container_width=True):
    if not master_prompt.strip():
        st.warning("Bhai pehle MASTER PROMPT me kahani likho!")
    elif not client:
        st.error("Groq Key nahi hai!")
    else:
        with st.spinner("Bhai 5 zubanon me convert ho raha hai... 10 sec"):
            st.session_state['sindhi_text'] = translate_exact(master_prompt, "SINDHI")
            st.session_state['urdu_text'] = translate_exact(master_prompt, "URDU")
            st.session_state['hindi_text'] = translate_exact(master_prompt, "HINDI")
            st.session_state['english_text'] = translate_exact(master_prompt, "ENGLISH")
            st.session_state['arabic_text'] = translate_exact(master_prompt, "ARABIC")
            st.success("✅ Bug Fix Ho Gaya! Ab 5 boxes me THE LAST PROMISE wala naya text aa gaya!")

st.divider()

def render_box(lang_key, flag_title):
    with st.expander(f"✅ {flag_title} - {len(st.session_state.get(lang_key, ''))} chars", expanded=False):
        time_opt = st.selectbox(f"{lang_key} Time:", ["60 Second (1 Min)", "30 Second", "90 Second"], key=f"time_{lang_key}")
        voice_map = VOICE_MAP_SIMPLE[lang_key]
        voice_options = list(voice_map.keys())
        selected_voice_label = st.selectbox(f"Voice (Larka/Larki):", voice_options, key=f"voice_{lang_key}")
        text_val = st.text_area(f"Text (840 max) - Jo Likha Wahi Bolega:", value=st.session_state.get(lang_key, ""), height=140, key=f"ta_{lang_key}", max_chars=840)
        st.session_state[lang_key] = text_val
        speed = st.slider(f"Speed:", -20, 20, -5, key=f"speed_{lang_key}", format="%d%%")
        if st.button(f"🎙️ Voice Banao 60s - {selected_voice_label}", key=f"btn_{lang_key}", use_container_width=True):
            if not text_val.strip():
                st.warning("Text khali hai Bhai!")
            else:
                try:
                    filename = f"/tmp/{lang_key}.mp3"
                    asyncio.run(make_voice(text_val, voice_map[selected_voice_label], speed, filename))
                    st.audio(filename)
                    with open(filename, "rb") as f:
                        st.download_button("⬇️ Download MP3", f, file_name=f"{lang_key}.mp3", key=f"dl_{lang_key}")
                except Exception as e:
                    st.error(f"Voice Error: {e}")

render_box('sindhi_text', '🇵🇰 SINDHI BOX')
render_box('urdu_text', '🇵🇰 URDU BOX')
render_box('hindi_text', '🇮🇳 HINDI BOX')
render_box('english_text', '🇬🇧 ENGLISH BOX')
render_box('arabic_text', '🇸🇦 ARABIC BOX')
