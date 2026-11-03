import streamlit as st, asyncio, edge_tts, time
from deep_translator import GoogleTranslator

st.set_page_config(page_title="MEHAR V106 NO GROQ", layout="centered")
st.title("MEHAR V106 - Lifetime Free - No Groq")
st.success("✅ No API Key - No Expire - Slow but Pakka")

for k in ['sindhi_box','urdu_box','hindi_box','english_box','arabic_box','master_box']:
    if k not in st.session_state:
        st.session_state[k] = ""

def translate_slow(text, to_code):
    try:
        time.sleep(2.5) # FIX - 2.5 sec rukna zaroori hai
        return GoogleTranslator(source='auto', target=to_code).translate(text)
    except:
        return text

master = st.text_area("📝 MASTER PROMPT:", height=180, key="master_box", placeholder="ہر گاؤں کی ایک کہانی...")

if st.button("🔄 ALL 5 BOX BHARO - 10 SEC LAGEGA", type="primary", use_container_width=True):
    if not master.strip():
        st.warning("Pehle likho Bhai!")
    else:
        with st.spinner("10 second ruk ke translate ho raha hai... Block nahi hoga"):
            st.session_state['urdu_box'] = master
            st.session_state['sindhi_box'] = translate_slow(master, 'sd')
            st.session_state['hindi_box'] = translate_slow(master, 'hi')
            st.session_state['english_box'] = translate_slow(master, 'en')
            st.session_state['arabic_box'] = translate_slow(master, 'ar')
            st.success("✅ Ho Gaya! Ab har box me alag zaban ayegi!")
            st.balloons()

# Voices - Larka Larki Fix
VOICES = {
    "sindhi_box": {"Asad Larka": "ur-PK-AsadNeural", "Uzma Larki": "ur-PK-UzmaNeural"},
    "urdu_box": {"Asad Larka": "ur-PK-AsadNeural", "Uzma Larki": "ur-PK-UzmaNeural"},
    "hindi_box": {"Madhur Larka": "hi-IN-MadhurNeural", "Swara Larki": "hi-IN-SwaraNeural"},
    "english_box": {"Guy Larka": "en-US-GuyNeural", "Jenny Larki": "en-US-JennyNeural"},
    "arabic_box": {"Hamed Larka": "ar-SA-HamedNeural", "Zariyah Larki": "ar-SA-ZariyahNeural"},
}
async def make_voice(text, voice, speed, fname):
    await edge_tts.Communicate(text, voice, rate=f"{speed:+d}%").save(fname)

def render_box(key, title):
    count = len(st.session_state.get(key,""))
    with st.expander(f"✅ {title} - {count} chars", expanded=True):
        sel = st.selectbox("Voice (Larka/Larki):", list(VOICES[key].keys()), key=f"v_{key}")
        st.text_area("Text:", height=150, key=key, max_chars=840)
        spd = st.slider("Speed:", -20, 20, -5, key=f"s_{key}")
        if st.button(f"🎙️ Voice Banao - {sel}", key=f"b_{key}", use_container_width=True):
            txt = st.session_state.get(key,"")
            if txt.strip():
                fn = f"/tmp/{key}.mp3"
                asyncio.run(make_voice(txt, VOICES[key][sel], spd, fn))
                st.audio(fn)

render_box('sindhi_box','🇵🇰 SINDHI BOX')
render_box('urdu_box','🇵🇰 URDU BOX')
render_box('hindi_box','🇮🇳 HINDI BOX')
render_box('english_box','🇬🇧 ENGLISH BOX')
render_box('arabic_box','🇸🇦 ARABIC BOX')
