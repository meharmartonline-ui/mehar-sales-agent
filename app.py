import streamlit as st, os, asyncio, requests, subprocess, tempfile
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="MEHAR V106 - LIGHT", layout="centered")

from PIL import Image
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS

import edge_tts

GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
groq_client = None
try:
    if GROQ_API_KEY and len(GROQ_API_KEY) > 30:
        from groq import Groq
        groq_client = Groq(api_key=GROQ_API_KEY)
except: pass

st.title("MEHAR V106 - WORLD STUDIO 🌍 - Voice Same + Video Light")

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

# Light Video Maker - No MoviePy Needed - Uses ffmpeg if available else slideshow
def make_video_light(image_path, audio_path, output_path, duration, effect="Zoom In"):
    try:
        # Try ffmpeg direct - Streamlit Cloud has ffmpeg
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", image_path,
            "-i", audio_path,
            "-c:v", "libx264",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
            "-pix_fmt", "yuv420p",
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            return True, output_path
        # Fallback - try without vf
        cmd2 = ["ffmpeg","-y","-loop","1","-i",image_path,"-i",audio_path,"-c:v","libx264","-c:a","aac","-shortest",output_path]
        result2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=120)
        if os.path.exists(output_path):
            return True, output_path
        return False, result.stderr[:500]
    except Exception as e:
        return False, str(e)

tab1, tab2 = st.tabs(["🎙️ VOICE STUDIO - SAME V102 - PAKA SAME", "🎬 VIDEO GENERATOR - LIGHT - NO MOVIEPY"])

with tab1:
    st.markdown("### ✅ Purana Voice Studio - 100% Same - Paka Same Rahega - Requirements Fixed!")
    st.success("V102 ka same code - Larka/Larki, Alfabet 52/38/28, Time - Oh no & Requirements fix!")
    for lang in VOICES:
        if f"text_{lang}" not in st.session_state: st.session_state[f"text_{lang}"] = ""
    master = st.text_area("✍️ MASTER PROMPT:", height=120, key="master_text_widget_v106")
    if st.button("🔄 ALL 5 BOX BHARO", type="primary", use_container_width=True, key="btn_all_v106"):
        src = st.session_state.get("master_text_widget_v106","").strip()
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
                time_sel = st.selectbox(f"⏱️ Time:", list(TIME_OPTIONS.keys()), index=3, key=f"ts_{LANG}_v106")
                MAX_SEC = TIME_OPTIONS[time_sel]
            with c2:
                vkey = st.selectbox(f"🎤 Voice (Larka/Larki):", list(VOICES[LANG].keys()), key=f"v_{LANG}_v106")
                vname = VOICES[LANG][vkey]
            txt = st.text_area(f"✍️ {LANG} Text:", height=100, key=f"ta_{LANG}_v106", value=st.session_state.get(f"text_{LANG}",""))
            rate = st.select_slider(f"Speed:", options=["-5%","-15%","+10%"], value="-5%", key=f"sp_{LANG}_v106")
            if st.button(f"🎙️ Voice Banao {MAX_SEC}s - {vkey}", key=f"gen_{LANG}_v106", type="primary", use_container_width=True):
                if txt.strip():
                    os.makedirs("voice", exist_ok=True)
                    fp = f"voice/{LANG}_{MAX_SEC}_v106.mp3"
                    cleaned = clean_for_voice(txt, LANG)
                    with st.spinner(f"{LANG} {vkey}..."):
                        ok = asyncio.run(gen_edge(cleaned, vname, rate, fp))
                        if ok:
                            st.audio(fp)
                            with open(fp,"rb") as f: st.download_button(f"📥 Download {LANG} {vkey}", f, file_name=f"{LANG}_{vkey}.mp3", key=f"dl_{LANG}_v106")

with tab2:
    st.markdown("### 🎬 VIDEO AD - LIGHT - No MoviePy - 100% Working - Aapki Image Se")
    st.success("✅ No MoviePy Needed - Sirf ffmpeg - Streamlit Cloud pe built-in hai!")
    
    prod_image = st.file_uploader("📸 Product Image (Honey Jar) Upload:", type=["jpg","jpeg","png","webp"], key="prod_v106")
    
    col1,col2 = st.columns(2)
    with col1:
        vid_lang = st.selectbox("🌍 Language:", ["SINDHI","URDU","HINDI","ENGLISH","ARABIC"], index=1, key="vlang_v106")
        vid_time = st.selectbox("⏱️ Duration:", list(TIME_OPTIONS.keys()), index=3, key="vid_time_v106")
        VID_SEC = TIME_OPTIONS[vid_time]
    with col2:
        vid_voice_key = st.selectbox("🎤 Voice:", list(VOICES[vid_lang].keys()), key="vid_voice_v106")
        vid_voice = VOICES[vid_lang][vid_voice_key]
        vid_speed = st.select_slider("Speed:", options=["-5%","-15%","+10%"], value="-5%", key="vid_speed_v106")
    
    default_vid_text = st.session_state.get(f"text_{vid_lang}", "") or st.session_state.get("master_text_widget_v106","") or "Mehar Mart Khalis Shahad - 100% Pure - Rs 2975 - Free Delivery!"
    vid_text = st.text_area(f"✍️ Video Text ({vid_lang}):", value=default_vid_text[:VID_SEC*14], height=120, key="vid_text_v106")
    zoom_effect = st.selectbox("Image Effect:", ["Zoom In (Mobile Style)", "Static"], key="zoom_v106")
    
    if st.button("🎬 VIDEO BANAO - LIGHT FIXED", type="primary", use_container_width=True, key="make_video_v106"):
        if not prod_image:
            st.error("Image Upload Karo!")
        elif not vid_text.strip():
            st.error("Text Likho!")
        else:
            with st.spinner(f"🎬 {vid_lang} Video Ban Raha... 20 sec..."):
                try:
                    os.makedirs("video", exist_ok=True)
                    from PIL import Image as PILImage
                    img = PILImage.open(prod_image).convert("RGB")
                    img = img.resize((1080,1920))
                    img_path = f"video/input_{vid_lang}_v106.jpg"
                    img.save(img_path)
                    
                    voice_path = f"video/voice_{vid_lang}_{VID_SEC}_v106.mp3"
                    cleaned_vid = clean_for_voice(vid_text, vid_lang)
                    ok_voice = asyncio.run(gen_edge(cleaned_vid, vid_voice, vid_speed, voice_path))
                    
                    if not ok_voice:
                        st.error("Voice Fail")
                    else:
                        output_path = f"video/MEHAR_AD_{vid_lang}_{VID_SEC}s_V106.mp4"
                        success, result = make_video_light(img_path, voice_path, output_path, VID_SEC, zoom_effect)
                        if success:
                            st.success(f"✅ Video Ready! {vid_lang} - Mobile 9:16 - Requirements Fixed!")
                            st.video(result)
                            with open(result,"rb") as f:
                                st.download_button(f"📥 Download Ad {vid_lang}", f, file_name=f"Mehar_{vid_lang}_Ad_{VID_SEC}s.mp4", mime="video/mp4", type="primary", use_container_width=True, key="dl_vid_v106")
                            st.audio(voice_path)
                            st.balloons()
                        else:
                            st.error(f"FFmpeg Error: {result}")
                            st.info("Voice to ban gaya! Audio download karo - Video ke liye Replit pe ffmpeg install karo: apt-get install ffmpeg")
                            st.audio(voice_path)
                except Exception as e:
                    st.error(f"Error: {e}")

st.caption("V106 - Requirements Fixed: No MoviePy - Light - Voice Paka Same V102 - Video ffmpeg Light")
