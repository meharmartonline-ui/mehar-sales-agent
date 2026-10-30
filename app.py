import streamlit as st, os, asyncio, subprocess
import edge_tts

st.set_page_config(page_title="MEHAR V88 - LIMIT DROPDOWN", layout="centered")
st.title("MEHAR V88 - Voice Limit Dropdown 🔥")
st.success("Ab 15 sec se 10 min tak ka limit select karo!")

# === 1. LIMIT DROPDOWN - AAPKI DEMAND ===
limit_options = {
    "⚡ 15 Second - Daraz Viral (BEST FOR SALE)": 15,
    "🔥 20 Second - TikTok Ad": 20,
    "💯 30 Second - Facebook Ad": 30,
    "🎙️ 1 Minute - Short Review": 60,
    "⏰ 2 Minute - Long Review": 120,
    "🎬 5 Minute - YouTube": 300,
    "🚀 10 Minute - Full Story (MAX)": 600,
}

selected_label = st.selectbox("⏱️ VOICE LIMIT SELECT KARO:", list(limit_options.keys()), index=0)
MAX_SEC = limit_options[selected_label]
# Approx 15 characters = 1 second
MAX_CHARS = MAX_SEC * 15 

st.info(f"✅ Selected: **{selected_label}** = Max **{MAX_CHARS} Characters** (~{MAX_SEC} sec)")

# === 2. VOICE SELECT ===
voice_map = {
    "👩 Larki - Uzma - 80% Real (Viral)": "ur-PK-UzmaNeural",
    "👩 Larki - Ayesha - Mature": "ur-PK-AyeshaNeural",
    "👦 Larka - Asad": "ur-PK-AsadNeural",
}
v_choice = st.selectbox("Kon bolay?", list(voice_map.keys()))
voice_name = voice_map[v_choice]

# === 3. TEXT BOX WITH LIVE LIMIT ===
default_texts = {
    15: "Assalam-o-Alaikum! Ye Mehar Mart ka Pure Honey 100% khalis hai! Sirf 2975 me 15% OFF - Abhi Order Karo!",
    20: "Guys ye Mehar Mart ka Pure Honey hai, 100% natural, immunity ke liye best! Sirf 2975 me Free Delivery ke sath!",
    30: "Assalam-o-Alaikum! Aaj main laya hun Pure Honey jo 100% khalis hai, bachon aur baron ke liye best. Abhi 2975 me mil raha hai Free Delivery ke sath, jaldi order karo!",
    60: "Assalam-o-Alaikum guys! Ye Mehar Mart ka Pure Honey 100% Natural hai. Taste bohat zabardast, immunity strong karta hai. Subah garam pani me len to faida hi faida. Sirf 2975 me 15% OFF aur Free Delivery pure Pakistan me. Order karo!",
    120: "Assalam-o-Alaikum guys! Aaj review hai Mehar Mart ke Pure Honey ka. Ye 100% khalis hai, koi cheeni nahi. Maine khud use kiya hai, bohat natural meetha hai. Bachon ki sehat ke liye best hai, immunity strong karta hai. Abhi Mehar Mart pe sirf 2975 me 15% OFF aur Free Delivery mil rahi hai pure Pakistan me. Stock limited hai, jaldi order karo 0345... par!",
}

# Auto text as per limit
auto_text = default_texts.get(MAX_SEC, default_texts[60])

text = st.text_area(f"Text Likho (Max {MAX_CHARS} chars):", value=auto_text, height=180, max_chars=MAX_CHARS)

# Live counter
char_count = len(text)
sec_count = char_count // 15
progress = char_count / MAX_CHARS if MAX_CHARS>0 else 0

col1, col2 = st.columns(2)
col1.metric("Characters", f"{char_count} / {MAX_CHARS}")
col2.metric("Time", f"~{sec_count} sec / {MAX_SEC} sec")

st.progress(min(progress, 1.0))

if progress > 1.0:
    st.error(f"⚠️ Limit Cross! {MAX_CHARS - char_count} chars kam karo!")
elif progress > 0.9:
    st.warning("⚠️ Limit ke kareeb ho - thoda kam karo!")
else:
    st.success(f"✅ Perfect - Limit ke andar hai!")

# === 4. GENERATE ===
async def gen_voice(text, voice):
    os.makedirs("voice", exist_ok=True)
    path = "voice/final_limit_voice.mp3"
    await edge_tts.Communicate(text, voice, rate="-5%", pitch="+1Hz", volume="+10%").save(path)
    return path

if st.button(f"🎙️ {MAX_SEC} SEC KI VOICE BANAO - HUMAN JESA", type="primary", use_container_width=True, disabled=progress>1.0):
    with st.spinner(f"{MAX_SEC} sec ki voice ban rahi... 10 sec..."):
        try:
            path = asyncio.run(gen_voice(text, voice_name))
            st.balloons()
            st.success(f"🔥 {sec_count} Second ki Voice Ready! Limit: {MAX_SEC} sec")
            st.audio(path)
            with open(path, "rb") as f:
                st.download_button(f"📥 Download {sec_count} Sec Voice", f, file_name=f"VOICE_{MAX_SEC}SEC.mp3", mime="audio/mpeg")
        except Exception as e:
            st.error(f"Error: {e}")

st.divider()
st.caption("Mehar Mart V88 - 15 sec se 10 min tak - Full Unlimited FREE!")
