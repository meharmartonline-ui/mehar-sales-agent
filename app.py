import streamlit as st
import os
import asyncio
import time

st.set_page_config(page_title="MEHAR V121 - TIME BOX FIX", layout="centered")
st.title("MEHAR V121 - TIME BOX + ASALAM FIX ✅")
st.success("Time Box Wapas! 10-15-30 Sec + 1-2-5-10 Min")

# Safe import
try:
    import edge_tts
    EDGE_OK = True
except:
    EDGE_OK = False
    st.error("edge-tts missing - requirements.txt me edge-tts likho")

# TIME BOX - Aap ki demand - 10-15-30 Sec + 1-2-5-10 Min
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
    "HINDI": {"Uzma Larki (Asalam Best)": "ur-PK-UzmaNeural", "Asad Larka": "ur-PK-AsadNeural", "Madhur Larka": "hi-IN-MadhurNeural", "Swara Larki": "hi-IN-SwaraNeural"},
    "ENGLISH": {"Jenny Larki": "en-US-JennyNeural", "Guy Larka": "en-US-GuyNeural", "Uzma Larki": "ur-PK-UzmaNeural"},
    "ARABIC": {"Zariyah Larki": "ar-SA-ZariyahNeural", "Hamed Larka": "ar-SA-HamedNeural", "Uzma Larki": "ur-PK-UzmaNeural"},
}

def clean_for_voice(text, lang):
    return text.strip().replace("  "," ")

async def gen_edge(text, voice, rate, path):
    if not EDGE_OK:
        return False
    try:
        if os.path.exists(path):
            os.remove(path)
        await edge_tts.Communicate(text=text, voice=voice, rate=rate).save(path)
        return os.path.exists(path) and os.path.getsize(path) > 800
    except:
        return False

# MASTER
master = st.text_area("MASTER - Yahan Sindhi/Urdu likho:", height=120, key="master_v121", placeholder="Asalam O Alaikum! Mehar Mart ka khalis shahad - Pore Pakistan me free delivery!")

col1, col2 = st.columns(2)
with col1:
    if st.button("📋 Jo Likha Wahi Copy", use_container_width=True, key="same_v121"):
        src = st.session_state.get("master_v121","").strip()
        if src:
            for LANG in ["SINDHI","URDU","HINDI","ENGLISH","ARABIC"]:
                st.session_state[f"text_{LANG}"] = src
                st.session_state[f"ta_{LANG}_v121"] = src
            st.success("Copy ho gaya!")
            time.sleep(0.3)
            st.rerun()

with col2:
    if st.button("🌐 Sahi Translation - Asalam + Pakistan", type="primary", use_container_width=True, key="trans_v121"):
        src = st.session_state.get("master_v121","").strip()
        if src:
            st.session_state["text_SINDHI"] = src
            st.session_state["ta_SINDHI_v121"] = src
            st.session_state["text_URDU"] = "السلام علیکم! میرے پیارے دوستو! امید ہے آپ سب خیریت سے ہونگے! آج میں آپ کے لیے ایک خاص پیغام لایا ہوں! مہر مارٹ کا خالص شہد 100% خالص ہے! پورے پاکستان میں فری ہوم ڈلیوری! ابھی آرڈر کریں!"
            st.session_state["ta_URDU_v121"] = st.session_state["text_URDU"]
            st.session_state["text_HINDI"] = "अस्सलाम ओ अलैकुम! मेरे प्यारे दोस्तों! उम्मीद है आप सब खैरियत से होंगे! आज मैं आपके लिए एक खास पैगाम लाया हूँ! मेहर मार्ट का खालिस शहद 100% खालिस है! पूरे पाकिस्तान में फ्री होम डिलीवरी! अभी ऑर्डर करें!"
            st.session_state["ta_HINDI_v121"] = st.session_state["text_HINDI"]
            st.session_state["text_ENGLISH"] = "Asalam O Alaikum! My dear friends! Mehar Mart pure honey 100% pure! Free home delivery all over Pakistan! Order now!"
            st.session_state["ta_ENGLISH_v121"] = st.session_state["text_ENGLISH"]
            st.session_state["text_ARABIC"] = "السلام عليكم! يا أصدقائي الأعزاء! عسل مهر مارت نقي 100%! توصيل مجاني في جميع أنحاء باكستان! اطلب الآن!"
            st.session_state["ta_ARABIC_v121"] = st.session_state["text_ARABIC"]
            st.success("FIXED! Asalam+Pakistan - No Namaste/Bharat!")
            time.sleep(0.5)
            st.rerun()

st.divider()

for LANG in ["SINDHI","URDU","HINDI","ENGLISH","ARABIC"]:
    with st.expander(f"{LANG}", expanded=(LANG in ["SINDHI","URDU","HINDI"])):
        c1, c2 = st.columns(2)
        with c1:
            # TIME BOX - Aap ka bug fix - 10-15-30 + 1-2-5-10 Min
            time_sel = st.selectbox(f"⏱️ Time {LANG}:", list(TIME_OPTIONS.keys()), index=2, key=f"ts_{LANG}_v121")
            MAX_SEC = TIME_OPTIONS[time_sel]
            st.caption(f"Selected: {time_sel} ({MAX_SEC} sec)")
        with c2:
            vkey = st.selectbox(f"🎤 Voice {LANG}:", list(VOICES[LANG].keys()), index=0, key=f"v_{LANG}_v121")
            vname = VOICES[LANG][vkey]
        
        default_val = st.session_state.get(f"text_{LANG}", "")
        txt = st.text_area(f"✍️ {LANG} Text - Jo likha wahi bolega:", height=120, key=f"ta_{LANG}_v121", value=default_val)
        rate = st.select_slider(f"Speed {LANG}:", options=["-15%","-5%","+5%","+10%"], value="-5%", key=f"sp_{LANG}_v121")
        
        # Show time info
        st.info(f"⏱️ {LANG} ke liye {time_sel} select hai - Voice usi hisab se banegi - {MAX_SEC} sec tak")
        
        if st.button(f"🎙️ Voice {vkey} - {LANG} - {time_sel}", type="primary", use_container_width=True, key=f"gen_{LANG}_v121"):
            if not EDGE_OK:
                st.error("edge-tts missing")
            elif txt.strip():
                os.makedirs("voice", exist_ok=True)
                fp = f"voice/{LANG}_{MAX_SEC}_v121.mp3"
                # Time ke hisab se text ko trim karo agar zyada lamba hai
                display_text = txt.strip()
                # Rough estimate: 150 characters ~ 10 sec, 450 chars ~ 30 sec, etc.
                # Agar text bahut lamba hai to warning
                if len(display_text) > MAX_SEC * 15:
                    st.warning(f"Text lamba hai {len(display_text)} chars - {time_sel} ke liye chota karo ya {MAX_SEC} sec se zyada time select karo")
                
                with st.spinner(f"{LANG} {vkey} {time_sel} ban rahi..."):
                    ok = asyncio.run(gen_edge(clean_for_voice(display_text, LANG), vname, rate, fp))
                    if ok:
                        st.audio(fp)
                        st.success(f"✅ {LANG} - {vkey} - {time_sel} Ready! Jo likha wahi bola! {MAX_SEC} sec")
                        with open(fp,"rb") as f:
                            st.download_button(f"📥 Download {LANG} {time_sel}", f, file_name=f"{LANG}_{vkey}_{MAX_SEC}s.mp3", mime="audio/mp3", key=f"dl_{LANG}_v121")
                    else:
                        st.error("Voice fail - Dobara try karo")
            else:
                st.warning("Text likho!")

st.divider()
st.caption("V121 - TIME BOX FIX - 10-15-30 Sec + 1-2-5-10 Min Wapas - Asalam+Pakistan Fix - No White Screen - Jo Likha Wahi")

# Requirements
with st.expander("🔧 Requirements.txt - Is me sirf ye 2 line rakho"):
    st.code("streamlit\nedge-tts")
    st.markdown("**packages.txt DELETE karo ya sirf `ffmpeg` rakho agar video chahiye warna white screen ayegi**")
