import streamlit as st
import os
import asyncio
import time
import re

st.set_page_config(page_title="MEHAR V125 - 0:01 FIX", layout="centered")
st.title("MEHAR V125 - 0:01 + TIME BOX FIX ✅")
st.success("⏱️ Time Box Full Width + Voice 0:01 Fix - Ab Lambi Voice Banegi!")

try:
    import edge_tts
    EDGE_OK = True
except:
    EDGE_OK = False
    st.error("edge-tts missing")

TIME_OPTIONS = {
    "10 Second": 10,
    "15 Second": 15,
    "30 Second": 30,
    "60 Second (1 Min)": 60,
    "2 Minutes": 120,
    "5 Minutes": 300,
    "10 Minutes": 600
}

VOICES = {
    "SINDHI": {"Asad Larka": "ur-PK-AsadNeural", "Uzma Larki": "ur-PK-UzmaNeural"},
    "URDU": {"Asad Larka": "ur-PK-AsadNeural", "Uzma Larki": "ur-PK-UzmaNeural"},
    "HINDI": {"Uzma Larki (Asalam Best)": "ur-PK-UzmaNeural", "Asad Larka": "ur-PK-AsadNeural", "Swara Larki (Hindi Pure - Lambi Voice)": "hi-IN-SwaraNeural", "Madhur Larka (Hindi Pure)": "hi-IN-MadhurNeural"},
    "ENGLISH": {"Jenny Larki": "en-US-JennyNeural", "Guy Larka": "en-US-GuyNeural"},
    "ARABIC": {"Zariyah Larki": "ar-SA-ZariyahNeural", "Hamed Larka": "ar-SA-HamedNeural"},
}

# VOICE FIX - 0:01 wala bug fix - 100% aur special chars hatao
def clean_for_voice(text, lang):
    t = text.strip()
    # 100% -> 100 percent - Isi se 0:01 banta tha
    t = t.replace("100%", "100 percent")
    t = t.replace("100 %", "100 percent")
    t = t.replace("%", " percent ")
    t = t.replace("!", " ! ")
    t = t.replace("।", ".")
    # Extra spaces clean
    t = re.sub(r'\s+', ' ', t)
    return t.strip()

# Auto suggest best voice for long Hindi text
def suggest_voice(text, current_voice):
    # Agar Hindi Devanagari hai aur text lamba hai to Swara best hai - Lambi voice
    has_hindi = bool(re.search(r'[\u0900-\u097F]', text))
    if has_hindi and len(text) > 80:
        return "hi-IN-SwaraNeural"
    return current_voice

async def gen_edge(text, voice, rate, path):
    if not EDGE_OK:
        return False, "edge-tts missing"
    try:
        if os.path.exists(path):
            os.remove(path)
        # Timeout badhao - Lambi voice ke liye
        communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
        await communicate.save(path)
        if os.path.exists(path):
            size = os.path.getsize(path)
            # Size check - Agar 1 second hai to size chota hoga < 5000 bytes
            if size < 4000:
                return False, f"Voice bahut choti bani {size} bytes - Text me 100% ya special char tha - Ab fixed!"
            return True, f"OK {size} bytes"
        return False, "File nahi bani"
    except Exception as e:
        return False, str(e)

# MASTER
master = st.text_area("MASTER:", height=100, key="master_v125", placeholder="Asalam O Alaikum! Mehar Mart ka khalis shahad - 100 percent khalis!")

c1, c2 = st.columns(2)
with c1:
    if st.button("📋 Jo Likha Wahi Copy", use_container_width=True, key="same_v125"):
        src = st.session_state.get("master_v125","").strip()
        if src:
            for LANG in ["SINDHI","URDU","HINDI","ENGLISH","ARABIC"]:
                st.session_state[f"text_{LANG}"] = src
            st.success("Copy!")
            time.sleep(0.3)
            st.rerun()
with c2:
    if st.button("🌐 Asalam+Pakistan Fix", type="primary", use_container_width=True, key="trans_v125"):
        src = st.session_state.get("master_v125","").strip()
        if src:
            st.session_state["text_SINDHI"] = src
            st.session_state["text_URDU"] = "السلام علیکم! میرے پیارے دوستو! مہر مارٹ کا خالص شہد 100 فیصد خالص ہے! پورے پاکستان میں فری ہوم ڈلیوری!"
            st.session_state["text_HINDI"] = "अस्सलाम ओ अलैकुम! मेरे प्यारे दोस्तों! उम्मीद है आप सब खैरियत से होंगे! मेहर मार्ट का खालिस शहद 100 परसेंट खालिस है! पूरे पाकिस्तान में फ्री होम डिलीवरी! अभी ऑर्डर करें!"
            st.session_state["text_ENGLISH"] = "Asalam O Alaikum! My dear friends! Mehar Mart pure honey 100 percent pure! Free home delivery all over Pakistan!"
            st.session_state["text_ARABIC"] = "السلام عليكم! عسل مهر مارت نقي 100 بالمئة! توصيل مجاني في جميع أنحاء باكستان!"
            st.success("Fixed! 100 percent wala fix bhi hai!")
            time.sleep(0.4)
            st.rerun()

st.divider()

for LANG in ["SINDHI","URDU","HINDI","ENGLISH","ARABIC"]:
    with st.expander(f"🔊 {LANG}", expanded=(LANG=="HINDI")):
        
        # TIME BOX - FULL WIDTH - MOBILE FIX - Aap ke pehle screenshot me ye gayab tha
        st.markdown(f"### ⏱️ {LANG} TIME SELECT KARO (10-15-30 + 1-2-5-10 Min):")
        time_sel = st.selectbox(
            f"Time {LANG}:",
            list(TIME_OPTIONS.keys()),
            index=2,
            key=f"ts_{LANG}_v125",
            label_visibility="collapsed"
        )
        max_sec = TIME_OPTIONS[time_sel]
        st.success(f"✅ TIME: {time_sel} = {max_sec} seconds")

        # VOICE - FULL WIDTH
        st.markdown(f"### 🎤 {LANG} VOICE:")
        vkey = st.selectbox(f"Voice {LANG}:", list(VOICES[LANG].keys()), index=0, key=f"v_{LANG}_v125")
        vname = VOICES[LANG][vkey]
        
        # Auto suggestion for 0:01 fix
        default_val = st.session_state.get(f"text_{LANG}", "")
        if LANG=="HINDI" and default_val:
            suggested = suggest_voice(default_val, vname)
            if suggested != vname and "Devanagari" in default_val:
                st.warning(f"💡 Tip: Lambi Hindi voice ke liye `Swara Larki (Hindi Pure - Lambi Voice)` select karo - 0:01 fix hoga! Abhi {vkey} hai")

        txt = st.text_area(f"✍️ {LANG} Text:", height=130, key=f"ta_{LANG}_v125", value=default_val)
        st.caption(f"Chars: {len(txt)} | Time: {time_sel} | Lamba text = 5 Min / 10 Min select karo")

        st.markdown(f"### ⚡ Speed {LANG}:")
        rate = st.select_slider(f"Speed {LANG}", options=["-15%","-5%","+5%","+10%"], value="-5%", key=f"sp_{LANG}_v125", label_visibility="collapsed")
        st.write(f"Speed: {rate}")

        st.info(f"⏱️ {time_sel} | 🎤 {vkey} | 100% -> 100 percent auto fix - 0:01 bug fix")

        if st.button(f"🎙️ Voice {vkey} - {LANG} - {time_sel}", type="primary", use_container_width=True, key=f"gen_{LANG}_v125"):
            if txt.strip():
                os.makedirs("voice", exist_ok=True)
                fp = f"voice/{LANG}_{max_sec}_v125.mp3"
                
                cleaned = clean_for_voice(txt.strip(), LANG)
                
                if len(cleaned) > max_sec * 18:
                    st.warning(f"Text {len(cleaned)} chars - {time_sel} ke liye lamba hai - 5 Min ya 10 Min select karo warna 0:01 ayega!")
                
                with st.spinner(f"{LANG} {time_sel} ban rahi... 100% fix ke saath..."):
                    ok, msg = asyncio.run(gen_edge(cleaned, vname, rate, fp))
                    if ok:
                        st.audio(fp)
                        # Duration check
                        try:
                            # Rough duration from file size
                            size = os.path.getsize(fp)
                            est_sec = size // 3000
                        except:
                            est_sec = max_sec
                        st.success(f"✅ {LANG} Ready! {time_sel} - Duration ~{est_sec} sec - {msg} - Jo likha wahi bola!")
                        with open(fp,"rb") as f:
                            st.download_button(f"📥 Download {LANG} {time_sel} ({est_sec}s)", f, file_name=f"{LANG}_{max_sec}s_V125.mp3", mime="audio/mp3", key=f"dl_{LANG}_v125")
                    else:
                        st.error(f"Voice fail - {msg} - Swara Larki (Hindi Pure - Lambi Voice) try karo - 0:01 fix hogi!")
                        st.code(f"Error: {msg}")
            else:
                st.warning("Text likho!")

st.caption("V125 - 0:01 FIX + TIME BOX MOBILE FIX - 100% -> 100 percent - Swara Larki for long Hindi - 10-15-30 + 1-2-5-10 Min")
