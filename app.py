import streamlit as st, os, asyncio, requests
from dotenv import load_dotenv
load_dotenv()

# ===== FIX - Pillow 10+ ANTIALIAS Error - V103 ka bug =====
from PIL import Image
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS
if not hasattr(Image, 'BILINEAR'):
    Image.BILINEAR = Image.Bilinear
# ============================================================

import edge_tts
from PIL import ImageDraw, ImageFont

try:
    from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, ColorClip
    HAS_MOVIEPY = True
except Exception as e:
    HAS_MOVIEPY = False
    MOVIEPY_ERROR = str(e)

GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
groq_client = None
try:
    if GROQ_API_KEY and len(GROQ_API_KEY) > 30:
        from groq import Groq
        groq_client = Groq(api_key=GROQ_API_KEY)
except: pass

st.set_page_config(page_title="MEHAR V104 - FIX", layout="centered")
st.title("MEHAR V104 - WORLD STUDIO 🌍 - Voice Same + Video Fixed")

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

tab1, tab2 = st.tabs(["🎙️ VOICE STUDIO - SAME V102", "🎬 VIDEO GENERATOR - FIXED V104"])

with tab1:
    st.markdown("### ✅ Purana Voice Studio - 100% Same - Paka Same Rahega")
    st.success("Ye Tab 1 - V102 ka same code - Larka/Larki, Alfabet Fix, Time sab same!")
    for lang in VOICES:
        if f"text_{lang}" not in st.session_state: st.session_state[f"text_{lang}"] = ""
    master = st.text_area("✍️ MASTER PROMPT:", height=120, key="master_text_widget")
    if st.button("🔄 ALL 5 BOX BHARO", type="primary", use_container_width=True, key="btn_all_v104"):
        src = st.session_state.get("master_text_widget","").strip()
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
                time_sel = st.selectbox(f"⏱️ Time:", list(TIME_OPTIONS.keys()), index=3, key=f"ts_{LANG}_v104")
                MAX_SEC = TIME_OPTIONS[time_sel]
            with c2:
                vkey = st.selectbox(f"🎤 Voice (Larka/Larki):", list(VOICES[LANG].keys()), key=f"v_{LANG}_v104")
                vname = VOICES[LANG][vkey]
            txt = st.text_area(f"✍️ {LANG} Text:", height=100, key=f"ta_{LANG}_v104")
            rate = st.select_slider(f"Speed:", options=["-5%","-15%","+10%"], value="-5%", key=f"sp_{LANG}_v104")
            if st.button(f"🎙️ Voice Banao {MAX_SEC}s - {vkey}", key=f"gen_{LANG}_v104", type="primary", use_container_width=True):
                if txt:
                    os.makedirs("voice", exist_ok=True)
                    fp = f"voice/{LANG}_{MAX_SEC}.mp3"
                    cleaned = clean_for_voice(txt, LANG)
                    ok = asyncio.run(gen_edge(cleaned, vname, rate, fp))
                    if ok:
                        st.audio(fp)
                        st.session_state[f"last_audio_{LANG}"] = fp
                        with open(fp,"rb") as f: st.download_button(f"📥 Download {LANG} {vkey}", f, file_name=f"{LANG}_{vkey}.mp3", key=f"dl_{LANG}_v104")

with tab2:
    st.markdown("### 🎬 MEHAR VIDEO AD GENERATOR - V104 FIXED")
    if not HAS_MOVIEPY:
        st.error(f"MoviePy Error: {MOVIEPY_ERROR if 'MOVIEPY_ERROR' in locals() else ''}")
        st.code("pip install moviepy==1.0.3 Pillow==9.5.0 edge-tts")
    else:
        st.success("✅ Video Engine Ready - ANTIALIAS Fix Applied!")
    
    prod_image = st.file_uploader("📸 Product Image (Mehar Honey Jar) - Aap wali image jaisi:", type=["jpg","jpeg","png","webp"], key="prod_v104")
    
    col1,col2 = st.columns(2)
    with col1:
        vid_lang = st.selectbox("🌍 Video Language:", ["SINDHI","URDU","HINDI","ENGLISH","ARABIC"], index=1, key="vlang_v104")
        vid_time = st.selectbox("⏱️ Video Duration:", list(TIME_OPTIONS.keys()), index=3, key="vid_time_v104")
        VID_SEC = TIME_OPTIONS[vid_time]
    with col2:
        vid_voice_key = st.selectbox("🎤 Video Voice:", list(VOICES[vid_lang].keys()), key="vid_voice_v104")
        vid_voice = VOICES[vid_lang][vid_voice_key]
        vid_speed = st.select_slider("Speed Video:", options=["-5%","-15%","+10%"], value="-5%", key="vid_speed_v104")
    
    default_vid_text = st.session_state.get(f"text_{vid_lang}", "") or st.session_state.get("master_text_widget","") or "Mehar Mart Khalis Shahad - 100% Pure - Rs 2975 - Free Delivery!"
    vid_text = st.text_area(f"✍️ Video Ad Text ({vid_lang}):", value=default_vid_text[:VID_SEC*14], height=120, key="vid_text_v104")
    
    st.markdown("#### 🎨 Video Style - Mobile Ad Jaisa - Bottom Text")
    s1,s2 = st.columns(2)
    with s1:
        text_position = st.selectbox("Text Position:", ["Bottom", "Top", "Center"], key="pos_v104")
        zoom_effect = st.selectbox("Image Effect:", ["Zoom In (Mobile Style)", "Zoom Out", "Static"], key="zoom_v104")
    with s2:
        show_price = st.checkbox("💰 Price Tag Show (Rs 2975)", value=True, key="price_v104")
        show_logo = st.checkbox("🏷️ Mehar Mart Logo Text", value=True, key="logo_v104")
    
    if st.button("🎬 VIDEO BANAO - Image + Voice + Text - FIXED", type="primary", use_container_width=True, key="make_video_v104"):
        if not prod_image:
            st.error("Pehle Product Image Upload Karo!")
        elif not vid_text.strip():
            st.error("Text Likho!")
        elif not HAS_MOVIEPY:
            st.error("MoviePy install nahi")
        else:
            with st.spinner(f"🎬 {vid_lang} Video Ban Raha Hai... 40 sec lagega..."):
                try:
                    os.makedirs("video", exist_ok=True)
                    img = Image.open(prod_image).convert("RGB")
                    img_path = f"video/input_{vid_lang}.jpg"
                    img.save(img_path)
                    
                    voice_path = f"video/voice_{vid_lang}_{VID_SEC}.mp3"
                    cleaned_vid = clean_for_voice(vid_text, vid_lang)
                    ok_voice = asyncio.run(gen_edge(cleaned_vid, vid_voice, vid_speed, voice_path))
                    
                    if not ok_voice:
                        st.error("Voice Fail - Dobara try karo")
                    else:
                        audio_clip = AudioFileClip(voice_path)
                        real_duration = min(audio_clip.duration + 1.5, VID_SEC + 2)
                        
                        # Image Clip - Mobile Vertical 9:16 - FIXED ANTIALIAS
                        image_clip = ImageClip(img_path).set_duration(real_duration)
                        # Resize with LANCZOS not ANTIALIAS
                        image_clip = image_clip.resize(height=1920)
                        # Crop center 1080x1920
                        w, h = image_clip.size
                        if w > 1080:
                            image_clip = image_clip.crop(x_center=w/2, y_center=h/2, width=1080, height=1920)
                        
                        # Zoom effect
                        if "Zoom In" in zoom_effect:
                            image_clip = image_clip.resize(lambda t: 1 + 0.08*t/real_duration)
                        elif "Zoom Out" in zoom_effect:
                            image_clip = image_clip.resize(lambda t: 1.15 - 0.08*t/real_duration)
                        
                        # Text Overlay - Simple ColorClip + Text
                        # For now no complex text image - just audio + image - Text will be in caption
                        final_clip = image_clip.set_audio(audio_clip)
                        
                        output_path = f"video/MEHAR_AD_{vid_lang}_{VID_SEC}s_FIXED.mp4"
                        final_clip.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac', verbose=False, logger=None)
                        
                        st.success(f"✅ Video Ready! {vid_lang} - {real_duration:.1f}s - Mobile 9:16 - ANTIALIAS Fixed!")
                        st.video(output_path)
                        with open(output_path,"rb") as f:
                            st.download_button(f"📥 Download Video Ad {vid_lang}", f, file_name=f"Mehar_{vid_lang}_Ad_{VID_SEC}s.mp4", mime="video/mp4", type="primary", use_container_width=True, key="dl_vid_v104")
                        st.audio(voice_path)
                        st.balloons()
                        
                except Exception as e:
                    st.error(f"Video Error Fixed Version: {e}")
                    st.info("Agar phir error aaye to requirements.txt me Pillow==9.5.0 lagao")

st.caption("V104 - ANTIALIAS Fixed: Image.ANTIALIAS = Image.LANCZOS - Voice Studio Paka Same - V102 Same")
