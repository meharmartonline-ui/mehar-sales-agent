import streamlit as st
import asyncio, edge_tts, time, json

st.set_page_config(page_title="MEHAR V105 FINAL", layout="centered")
st.title("MEHAR V105 - FINAL FIXED")
st.success("✅ V105 - 1 Request Translation - No Rate Limit")

# --- GROQ SETUP ---
import os
from groq import Groq
groq_key = st.secrets.get("GROQ_API_KEY") if hasattr(st, 'secrets') else os.getenv("GROQ_API_KEY")
client = Groq(api_key=groq_key) if groq_key else None
if client:
    st.success("✅ Groq Connected - Translation Pakka")
else:
    st.error("Groq Key missing - Secrets me dalo")

for k in ['sindhi_box','urdu_box','hindi_box','english_box','arabic_box','master_box']:
    if k not in st.session_state:
        st.session_state[k] = ""

def translate_all_in_one(text):
    """1 request me 4 zaban - Rate limit khatam"""
    if not client or not text.strip():
        return None
    try:
        prompt = f"""
        You are translator. Translate this Urdu story into 4 languages.
        Story: {text}
        
        Return ONLY valid JSON like this, no extra text:
        {{
          "sindhi": "translation in Sindhi Arabic script (سنڌي)",
          "hindi": "translation in Hindi Devanagari (हिंदी)",
          "english": "translation in English",
          "arabic": "translation in Arabic (العربية)"
        }}
        Rules: Keep THE LAST PROMISE as is. Never add Mehar Mart or honey ads.
        """
        r = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role":"system","content":"You are a JSON translator. Only return JSON."},
                {"role":"user","content":prompt}
            ],
            temperature=0.2,
            max_tokens=2000
        )
        data = json.loads(r.choices[0].message.content.strip())
        return data
    except Exception as e:
        st.error(f"Groq Error: {e}")
        return None

master = st.text_area("📝 MASTER PROMPT (Urdu me likho):", height=180, key="master_box", placeholder="ہر گاؤں کی ایک کہانی...")

c1,c2 = st.columns(2)
with c1:
    if st.button("🔄 ALL 5 BOX BHARO - 1 CLICK", type="primary", use_container_width=True):
        if not master.strip():
            st.warning("Pehle likho!")
        elif not client:
            st.error("Groq Key nahi hai!")
        else:
            with st.spinner("1 request me 4 zaban translate ho rahi..."):
                result = translate_all_in_one(master)
                if result:
                    st.session_state['sindhi_box'] = result.get('sindhi', master)
                    st.session_state['urdu_box'] = master
                    st.session_state['hindi_box'] = result.get('hindi', master)
                    st.session_state['english_box'] = result.get('english', master)
                    st.session_state['arabic_box'] = result.get('arabic', master)
                    st.success("✅ Ho Gaya! Ab har box me alag zaban check karo!")
                    st.balloons()
                else:
                    # Fallback - Jo Likha Wahi
                    for k in ['sindhi_box','urdu_box','hindi_box','english_box','arabic_box']:
                        st.session_state[k] = master
                    st.warning("Groq fail - Same text copy kiya")
with c2:
    if st.button("🗑️ CLEAR", use_container_width=True):
        for k in ['sindhi_box','urdu_box','hindi_box','english_box','arabic_box','master_box']:
            st.session_state[k] = ""
        st.rerun()

# --- VOICES - LARKA LARKI FIX ---
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
    v_map = VOICES[key]
    count = len(st.session_state.get(key,""))
    with st.expander(f"✅ {title} - {count} chars", expanded=True):
        st.selectbox("Time:", ["60 Second"], key=f"t_{key}")
        sel = st.selectbox("Voice (Larka/Larki):", list(v_map.keys()), key=f"v_{key}")
        st.text_area("Text:", height=160, key=key, max_chars=840)
        spd = st.slider("Speed:", -20, 20, -5, key=f"s_{key}")
        if st.button(f"🎙️ Voice Banao - {sel}", key=f"b_{key}", use_container_width=True):
            txt = st.session_state.get(key,"")
            if txt.strip():
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
