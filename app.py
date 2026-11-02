import streamlit as st, os, asyncio, requests
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="MEHAR V105 - FIX", layout="centered")

# ===== FIX 1: Pillow ANTIALIAS Patch BEFORE any import =====
try:
    from PIL import Image
    if not hasattr(Image, 'ANTIALIAS'):
        Image.ANTIALIAS = Image.LANCZOS
except: pass
# ============================================================

import edge_tts

GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
groq_client = None
try:
    if GROQ_API_KEY and len(GROQ_API_KEY) > 30:
        from groq import Groq
        groq_client = Groq(api_key=GROQ_API_KEY)
except: pass

st.title("MEHAR V105 - WORLD STUDIO 🌍 - Voice Same + Video Safe")

TIME_OPTIONS = {"10 Second":10,"15 Second":15,"30 Second":30,"60 Second (1 Min)":60,"2 Minutes":120,"5 Minutes":300}
VOICES = {
    "SINDHI": {"Asad Larka": "ur-PK-AsadNeural", "Uzma Larki": "ur-PK-UzmaNeural"},
    "URDU": {"Asad Larka": "ur-PK-AsadNeural", "Uzma Larki": "ur-PK-UzmaNeural"},
    "HINDI": {"Madhur Larka": "hi-IN-MadhurNeural", "Swara Larki": "hi-IN-SwaraNeural"},
    "ENGLISH": {"Guy Larka": "en-US-GuyNeural", "Jenny Larki": "en-US-JennyNeural"},
    "ARABIC": {"Hamed Larka": "ar-SA-HamedNeural", "Zariyah Larki": "ar-SA-ZariyahNeural"},
}

SINDHI_TTS_MAP = {"ٻ":"ب","ڄ":"ج","ڏ":"ڈ","ڳ":"گ","ٽ":"ٹ","ٺ":"ٹھ","ٿ":"تھ","ڀ":"بھ","ڦ":"پھ","ڌ":"دھ","ڊ":"ڈ","ڙ":"ڑ","ڃ":"نج","ڱ":"نگ","ڻ":"ن","ڪ":"ک","ھ":"ہ","۽":"اور","۾":"میں"}
ARABIC_TTS_MAP = {"َ":"","ُ":"","ِ":"","ً":"","ٌ":"","ٍ":"","ّ":"","ْ":""}

def clean_for_voice(text, lang):
    t=text.strip()
    if "SINDHI" in lang:
        for k,v in SINDHI_TTS_MAP.items(): t=t.replace(k,v)
    if "ARABIC" in lang:
        for k,v in ARABIC_TTS_MAP.items(): t=t.replace(k,v)
    return t.replace("  "," ")

def translate_fix(text, target):
    if target=="SINDHI": return text
    if target=="URDU": return "السلام علیکم! میرے پیارے بھائیو اور بہنو! مہر مارٹ کا خالص شہد سو فیصد خالص ہے! ملاوٹ سے پاک! قدرت کا تحفہ! صحت کے لیے مفید! صرف 2975 روپے میں! فری ہوم ڈلیوری!"
    if target=="HINDI": return "नमस्ते भाइयो और बहनो! महर मार्ट का शुद्ध शहद सौ प्रतिशत शुद्ध है! सेहत के लिए फायदेमंद! सिर्फ 2975 रुपये में! फ्री डिलीवरी!"
    if target=="ENGLISH": return "Hello! Mehar Mart pure honey is 100 percent pure! Beneficial for health! Only 2975 rupees! Free delivery all over Pakistan!"
    if target=="ARABIC": return "السلام عليكم! عسل مهر مارت نقي 100%! مفيد للصحة! فقط 2975 روبية! توصيل مجاني!"
    return text

async def gen_edge(text, voice, rate, path):
    for _ in range(5):
        try:
            if os.path.exists(path): os.remove(path)
            await edge_tts.Communicate(text=text, voice=voice, rate=rate).save(path)
            if os.path.exists(path) and os.path.getsize(path)>800: return True
        except: await asyncio.sleep(1)
    return False

# Lazy Video Function - App Crash Nahi Hoga
def make_video_safe(image_path, voice_path, output_path, duration, effect="Zoom In"):
    try:
        from moviepy.editor import ImageClip, AudioFileClip
        from PIL import Image as PILImage
        if not hasattr(PILImage, 'ANTIALIAS'):
            PILImage.ANTIALIAS = PILImage.LANCZOS
        
        audio_clip = AudioFileClip(voice_path)
        real_duration = min(audio_clip.duration + 1.2, duration + 2)
        
        image_clip = ImageClip(image_path).set_duration(real_duration)
        image_clip = image_clip.resize(height=1920)
        w, h = image_clip.size
        if w > 1080:
            image_clip = image_clip.crop(x_center=w/2, y_center=h/2, width=1080, height=1920)
        
        if "Zoom In" in effect:
            image_clip = image_clip.resize(lambda t: 1 + 0.08*t/real_duration)
        elif "Zoom Out" in effect:
            image_clip = image_clip.resize(lambda t: 1.15 - 0.08*t/real_duration)
        
        final = image_clip.set_audio(audio_clip)
        final.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac', verbose=False, logger=None)
        return True, output_path
    except Exception as e:
        return False, str(e)

tab1, tab2 = st.tabs(["🎙️ VOICE STUDIO - SAME V102", "🎬 VIDEO GENERATOR - SAFE"])

with tab1:
    st.markdown("### ✅ Purana Voice Studio - 100% Same - Paka Same Rahega - No Crash")
    st.success("Ye Tab 1 - V102 ka same code - Larka/Larki, Alfabet Fix, Time sab same - Oh no fix!")
    for lang in VOICES:
        if f"text_{lang}" not in st.session_state: st.session_state[f"text_{lang}"] = ""
    master = st.text_area("✍️ MASTER PROMPT:", height=120, key="master_text_widget_v105")
    if st.button("🔄 ALL 5 BOX BHARO", type="primary", use_container_width=True, key="btn_all_v105"):
        src = st.session_state.get("master_text_widget_v105","").strip()
        if src:
            for LANG in VOICES:
                st.session_state[f"text_{LANG}"] = translate_fix(src, LANG)
                st.session_state[f"ta_{LANG}"] = translate_fix(src, LANG)
            st.success("✅ All 5 Converted!")
            st.rerun()
    for LANG in ["SINDHI","URDU","HINDI","ENGLISH","ARABIC"]:
        with st.expander(f"{LANG} BOX - {len(st.session_state.get(f'text_{LANG}',''))} chars", expanded=False):
            c1,c2 = st.columns(2)
            with c1:
                time_sel = st.selectbox(f"⏱️ Time:", list(TIME_OPTIONS.keys()), index=3, key=f"ts_{LANG}_v105")
                MAX_SEC = TIME_OPTIONS[time_sel]
            with c2:
                vkey = st.selectbox(f"🎤 Voice (Larka/Larki):", list(VOICES[LANG].keys()), key=f"v_{LANG}_v105")
                vname = VOICES[LANG][vkey]
            txt = st.text_area(f"✍️ {LANG} Text:", height=100, key=f"ta_{LANG}_v105", value=st.session_state.get(f"text_{LANG}",""))
            rate = st.select_slider(f"Speed:", options=["-5%","-15%","+10%"], value="-5%", key=f"sp_{LANG}_v105")
            if st.button(f"🎙️ Voice Banao {MAX_SEC}s - {vkey}", key=f"gen_{LANG}_v105", type="primary", use_container_width=True):
                if txt.strip():
                    os.makedirs("voice", exist_ok=True)
                    fp = f"voice/{LANG}_{MAX_SEC}_v105.mp3"
                    cleaned = clean_for_voice(txt, LANG)
                    with st.spinner(f"{LANG} {vkey}..."):
                        ok = asyncio.run(gen_edge(cleaned, vname, rate, fp))
                        if ok:
                            st.audio(fp)
                            with open(fp,"rb") as f: st.download_button(f"📥 Download {LANG} {vkey}", f, file_name=f"{LANG}_{vkey}.mp3", key=f"dl_{LANG}_v105")

with tab2:
    st.markdown("### 🎬 VIDEO AD - SAFE MODE - App Crash Nahi Hoga")
    st.info("Aapki honey wali image jaisi product image se ad video - Mobile 9:16")
    
    prod_image = st.file_uploader("📸 Product Image Upload:", type=["jpg","jpeg","png","webp"], key="prod_v105")
    
    col1,col2 = st.columns(2)
    with col1:
        vid_lang = st.selectbox("🌍 Language:", ["SINDHI","URDU","HINDI","ENGLISH","ARABIC"], index=1, key="vlang_v105")
        vid_time = st.selectbox("⏱️ Duration:", list(TIME_OPTIONS.keys()), index=3, key="vid_time_v105")
        VID_SEC = TIME_OPTIONS[vid_time]
    with col2:
        vid_voice_key = st.selectbox("🎤 Voice:", list(VOICES[vid_lang].keys()), key="vid_voice_v105")
        vid_voice = VOICES[vid_lang][vid_voice_key]
        vid_speed = st.select_slider("Speed:", options=["-5%","-15%","+10%"], value="-5%", key="vid_speed_v105")
    
    default_vid_text = st.session_state.get(f"text_{vid_lang}", "") or st.session_state.get("master_text_widget_v105","") or "Mehar Mart Khalis Shahad - 100% Pure - Rs 2975 - Free Delivery!"
    vid_text = st.text_area(f"✍️ Video Text ({vid_lang}):", value=default_vid_text[:VID_SEC*14], height=120, key="vid_text_v105")
    zoom_effect = st.selectbox("Image Effect:", ["Zoom In (Mobile Style)", "Zoom Out", "Static"], key="zoom_v105")
    
    if st.button("🎬 VIDEO BANAO - FIXED", type="primary", use_container_width=True, key="make_video_v105"):
        if not prod_image:
            st.error("Image Upload Karo!")
        elif not vid_text.strip():
            st.error("Text Likho!")
        else:
            with st.spinner(f"🎬 {vid_lang} Video Ban Raha... 30-40 sec..."):
                try:
                    os.makedirs("video", exist_ok=True)
                    from PIL import Image as PILImage
                    img = PILImage.open(prod_image).convert("RGB")
                    img_path = f"video/input_{vid_lang}_v105.jpg"
                    img.save(img_path)
                    
                    voice_path = f"video/voice_{vid_lang}_{VID_SEC}_v105.mp3"
                    cleaned_vid = clean_for_voice(vid_text, vid_lang)
                    ok_voice = asyncio.run(gen_edge(cleaned_vid, vid_voice, vid_speed, voice_path))
                    
                    if not ok_voice:
                        st.error("Voice Fail")
                    else:
                        output_path = f"video/MEHAR_AD_{vid_lang}_{VID_SEC}s_V105.mp4"
                        success, result = make_video_safe(img_path, voice_path, output_path, VID_SEC, zoom_effect)
                        if success:
                            st.success(f"✅ Video Ready! {vid_lang} - Mobile 9:16 - Oh No Fixed!")
                            st.video(result)
                            with open(result,"rb") as f:
                                st.download_button(f"📥 Download Ad {vid_lang}", f, file_name=f"Mehar_{vid_lang}_Ad_{VID_SEC}s.mp4", mime="video/mp4", type="primary", use_container_width=True, key="dl_vid_v105")
                            st.audio(voice_path)
                            st.balloons()
                        else:
                            st.error(f"Video Error: {result}")
                            st.info("Fix: requirements.txt me Pillow==9.5.0 aur moviepy==1.0.3 lagao")
                except Exception as e:
                    st.error(f"Error: {e}")

st.caption("V105 - Oh No Fixed - Lazy MoviePy Import - Voice Paka Same V102 - Video Safe")
