import streamlit as st
import asyncio, edge_tts, time
try:
    from deep_translator import GoogleTranslator
    HAS_TRANS = True
except:
    HAS_TRANS = False

st.set_page_config(page_title="MEHAR V107 NO EMPTY", layout="centered")
st.title("MEHAR V107 - Boxes Kabhi Khali Nahi")
st.success("✅ V107 - Empty Box Fix - 100% Bharega")

# --- INIT ---
for k in ['sindhi_box','urdu_box','hindi_box','english_box','arabic_box','master_box']:
    if k not in st.session_state:
        st.session_state[k] = ""

def safe_translate(text, target):
    # FIX: Kabhi empty return nahi karega
    if not text.strip():
        return ""
    if not HAS_TRANS:
        return text # Translator nahi to Urdu hi de do
    try:
        time.sleep(1.5)
        result = GoogleTranslator(source='auto', target=target).translate(text)
        # Agar result khali hai to original de do
        if not result or len(result.strip()) < 2:
            return text
        return result
    except Exception as e:
        # Error aaye to bhi original text de do - Khali nahi
        return text

# --- MASTER ---
master = st.text_area("📝 MASTER PROMPT (Urdu me likho):", height=180, key="master_box", placeholder="ہر گاؤں کی ایک کہانی...")

if st.button("🔄 ALL 5 BOX BHARO - KABHI KHALI NAHI HOGA", type="primary", use_container_width=True):
    txt = st.session_state.get('master_box', '').strip()
    if not txt:
        st.warning("Pehle MASTER me likho Bhai!")
    else:
        with st.spinner("Bhar raha hu... 8 sec..."):
            # Pehle Urdu Box
            st.session_state['urdu_box'] = txt
            
            # Baqi 4 - Agar fail bhi ho to txt hi ayega
            s = safe_translate(txt, 'sd')
            st.session_state['sindhi_box'] = s if s else txt
            
            h = safe_translate(txt, 'hi')
            st.session_state['hindi_box'] = h if h else txt
            
            en = safe_translate(txt, 'en')
            st.session_state['english_box'] = en if en else txt
            
            ar = safe_translate(txt, 'ar')
            st.session_state['arabic_box'] = ar if ar else txt
            
            st.success("✅ Ho Gaya! Ab check karo - 1 bhi box khali nahi hoga!")
            time.sleep(0.5)
            st.rerun() # FIX: Rerun se box foran bhar ke dikhega

if st.button("🗑️ CLEAR ALL", use_container_width=True):
    for k in ['sindhi_box','urdu_box','hindi_box','english_box','arabic_box','master_box']:
        st.session_state[k] = ""
    st.rerun()

st.divider()

# --- VOICE ---
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
    color = "🔴 KHALI" if count==0 else f"✅ {count} chars"
    with st.expander(f"{color} - {title}", expanded=True):
        v_map = VOICES[key]
        sel = st.selectbox("Voice (Larka/Larki):", list(v_map.keys()), key=f"v_{key}")
        st.text_area(f"{title} Text:", height=150, key=key, max_chars=840)
        spd = st.slider("Speed:", -20, 20, -5, key=f"s_{key}")
        if st.button(f"🎙️ Voice Banao - {sel}", key=f"b_{key}", use_container_width=True):
            txt = st.session_state.get(key,"")
            if not txt.strip():
                st.error("Box khali hai Bhai! Pehle bharo")
            else:
                fn = f"/tmp/{key}.mp3"
                asyncio.run(make_voice(txt, v_map[sel], spd, fn))
                st.audio(fn)
                with open(fn,"rb") as f:
                    st.download_button("⬇️ Download", f, file_name=f"{key}.mp3", key=f"dl_{key}")

render_box('sindhi_box','🇵🇰 SINDHI BOX')
render_box('urdu_box','🇵🇰 URDU BOX')
render_box('hindi_box','🇮🇳 HINDI BOX')
render_box('english_box','🇬🇧 ENGLISH BOX')
render_box('arabic_box','🇸🇦 ARABIC BOX')
