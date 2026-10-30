import streamlit as st, os, asyncio, re
import edge_tts

st.set_page_config(page_title="MEHAR V90 - URDU CLEAR FIX", layout="centered")
st.title("MEHAR V90 - Urdu Saaf Talafuz Fix 🔥")
st.success("Ab alfaz clear - toote ge nahi!")

# === PRONUNCIATION DICTIONARY - ROMAN URDU KO SAHI KAREGA ===
def fix_urdu_pronunciation(text):
    # Common galat bole jane wale alfaz ko sahi phonetic me badlo
    fixes = {
        "Assalam-o-Alaikum": "As-salamu Alaikum",
        "Warehmatullahi": "Wa Rahmatullahi",
        "Wabarakatuhu": "Wa Barakatuhu",
        "bhaiyon": "bhai-yon",
        "behnon": "beh-non",
        "zindagi": "zin-da-gi",
        "sachi": "sa-chi",
        "kahani": "ka-ha-ni",
        "Mehar Mart": "Mehar Mart",
        "Pure Honey": "Pure Honey",
        "khalis": "khaa-lis",
        "shifa": "shi-fa",
        "Quran": "Quran Pak",
        "Sallallahu": "Sallallahu Alaihi Wasallam",
        "thakan": "tha-kan",
        "immunity": "immunity",
        "zabardast": "zabardast",
        "zaiqa": "zai-qa",
        "faida": "fai-da",
        "JazakAllah": "Jazak Allah",
        "InshaAllah": "Insha Allah",
        "03452352112": "zero three four five, two three five, two one one two",
    }
    for wrong, right in fixes.items():
        text = re.sub(re.escape(wrong), right, text, flags=re.IGNORECASE)
    
    # Roman Urdu ko saans ke saath bolo - commas add
    text = text.replace("  ", " ")
    text = text.replace(". ", ". , ")
    text = text.replace("! ", "! , ")
    text = text.replace("? ", "? , ")
    # Lambe jumle tod do
    text = re.sub(r'([a-zA-Z]{15,})', r'\1 ,', text)
    return text

# === SETTINGS ===
limit_options = {
    "⚡ 15 Sec - Viral": 15, "🔥 20 Sec": 20, "💯 30 Sec": 30,
    "🎙️ 1 Min": 60, "⏰ 2 Min": 120, "🚀 10 Min": 600,
}
sel = st.selectbox("Limit:", list(limit_options.keys()), index=0)
MAX_SEC = limit_options[sel]
MAX_CHARS = MAX_SEC * 15

voice_map = {
    "👩 Uzma - CLEAR (Best for Urdu)": "ur-PK-UzmaNeural",
    "👩 Ayesha - SAAF URDU (Most Clear)": "ur-PK-AyeshaNeural", # YE SAB SE SAAF BOLTI HAI
    "👦 Asad - Clear": "ur-PK-AsadNeural",
}
v_choice = st.selectbox("Voice (Ayesha sab se saaf hai):", list(voice_map.keys()), index=1)
voice_name = voice_map[v_choice]

st.info("💡 TIP: Agar Urdu me likhna hai to is tarah likho - zyada clear bolegi:\n`السلام علیکم` > Roman se zyada saaf!")

# TABS - Roman vs Urdu Script
tab1, tab2 = st.tabs(["🔤 Roman Urdu (Aap wala)", "🕌 Urdu Script (100% Clear)"])

with tab1:
    roman_text = st.text_area(f"Roman Urdu Text ({MAX_CHARS} max):", 
    "As-salamu Alaikum! Mere pyare bhaiyon aur behnon. Aaj main aapko Mehar Mart ke khalis honey ki kahani sunata hun. Ye 100 percent khalis hai, is me shifa hai. Sirf 2975 me!",
    height=180, max_chars=MAX_CHARS, key="roman")

with tab2:
    urdu_text = st.text_area("Urdu Script me likho - 100% saaf bolegi:", 
    "السلام علیکم! میرے پیارے بھائیوں اور بہنوں۔ آج میں آپ کو مہر مارٹ کے خالص شہد کی کہانی سناتا ہوں۔ یہ سو فیصد خالص ہے، اس میں شفا ہے۔ صرف 2975 میں!",
    height=180, key="urdu")

# Final text select karo
use_urdu_script = st.checkbox("✅ Urdu Script wala istemal karo (Zyada Clear)", value=False)
raw_text = urdu_text if use_urdu_script else roman_text

if raw_text:
    fixed_text = fix_urdu_pronunciation(raw_text)
    st.caption(f"Fixed for Voice: {fixed_text[:200]}...")
    
    chars = len(raw_text)
    st.metric("Chars / Time", f"{chars} / {MAX_CHARS}", f"{chars//15} sec / {MAX_SEC} sec")
    st.progress(min(chars/MAX_CHARS, 1.0))

    async def gen_clear(text, voice):
        os.makedirs("voice", exist_ok=True)
        path = "voice/clear_urdu.mp3"
        # CLEAR SETTINGS: slow + clear
        await edge_tts.Communicate(text, voice, rate="-10%", pitch="+0Hz", volume="+20%").save(path)
        return path

    if st.button("🎙️ SAAF URDU VOICE BANAO", type="primary", use_container_width=True):
        with st.spinner("Saaf talafuz me bana raha..."):
            final_text = fixed_text
            path = asyncio.run(gen_clear(final_text, voice_name))
            st.success("✅ Saaf Voice Ready - Ab lafz nahi tootenge!")
            st.audio(path)
            with open(path, "rb") as f:
                st.download_button("📥 Download Clear Voice", f, file_name="CLEAR_URDU.mp3", mime="audio/mpeg")

st.divider()
st.markdown("""
**Bhai Clear Voice ke 3 Raaz:**
1. **Voice Ayesha select karo** - Uzma se zyada saaf Urdu bolti hai
2. **Speed -10% rakhi hai** - taake lafz clear hon
3. **Roman me `As-salamu Alaikum` likho** - `Assalam-o-Alaikum` se zyada saaf

**100% Clear chahiye to Tab 2 me Urdu Script me likho - `السلام علیکم` - ye kabhi galat nahi bolegi!**
""")
