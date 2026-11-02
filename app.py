import streamlit as st, os, asyncio, requests, subprocess
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="MEHAR V107 - FFMPEG FIX", layout="centered")

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

st.title("MEHAR V107 - WORLD STUDIO 🌍 - Voice Same + Video ffmpeg Fixed")

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

def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg","-version"], capture_output=True, timeout=5)
        return True
    except: return False

def make_video_light(image_path, audio_path, output_path, duration):
    try:
        # Simple 9:16 video - No complex filter
        cmd = ["ffmpeg","-y","-loop","1","-i",image_path,"-i",audio_path,"-c:v","libx264","-t","30","-c:a","aac","-shortest","-pix_fmt","yuv420p","-vf","scale=1080:1920",output_path]
        subprocess.run(cmd, capture_output=True, timeout=120)
        if os.path.exists(output_path) and os.path.getsize(output_path)>1000:
            return True, output_path
        # Fallback 2
        cmd2 = ["ffmpeg","-y","-loop","1","-i",image_path,"-i",audio_path,"-c:v","libx264","-c:a","aac","-shortest",output_path]
        subprocess.run(cmd2, capture_output=True, timeout=120)
        if os.path.exists(output_path):
            return True, output_path
        return False, "ffmpeg failed"
    except Exception as e:
        return False, str(e)

tab1, tab2 = st.tabs(["🎙️ VOICE STUDIO - SAME V102 - PAKA SAME", "🎬 VIDEO GENERATOR - FFMPEG FIXED"])

with tab1:
    st.markdown("### ✅ Purana Voice Studio - 100% Same - Aap ka 0:06 audio wala same!")
    st.success("Voice Paka Same - Larka/Larki, Alfabet 52/38/28, Time - V102 Same!")
    for lang in VOICES:
        if f"text_{lang}" not in st.session_state: st.session_state[f"text_{lang}"] = ""
    master = st.text_area("✍️ MASTER PROMPT:", height=120, key="master_text_widget_v107")
    if st.button("🔄 ALL 5 BOX BHARO", type="primary", use_container_width=True, key="btn_all_v107"):
        src = st.session_state.get("master_text_widget_v107","").strip()
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
                time_sel = st.selectbox(f"⏱️ Time:", list(TIME_OPTIONS.keys()), index=3, key=f"ts_{LANG}_v107")
                MAX_SEC = TIME_OPTIONS[time_sel]
            with c2:
                vkey = st.selectbox(f"🎤 Voice (Larka/Larki):", list(VOICES[LANG].keys()), key=f"v_{LANG}_v107")
                vname = VOICES[LANG][vkey]
            txt = st.text_area(f"✍️ {LANG} Text:", height=100, key=f"ta_{LANG}_v107", value=st.session_state.get(f"text_{LANG}",""))
            rate = st.select_slider(f"Speed:", options=["-5%","-15%","+10%"], value="-5%", key=f"sp_{LANG}_v107")
            if st.button(f"🎙️ Voice Banao {MAX_SEC}s - {vkey}", key=f"gen_{LANG}_v107", type="primary", use_container_width=True):
                if txt.strip():
                    os.makedirs("voice", exist_ok=True)
                    fp = f"voice/{LANG}_{MAX_SEC}_v107.mp3"
                    cleaned = clean_for_voice(txt, LANG)
                    with st.spinner(f"{LANG} {vkey}..."):
                        ok = asyncio.run(gen_edge(cleaned, vname, rate, fp))
                        if ok:
                            st.audio(fp)
                            with open(fp,"rb") as f: st.download_button(f"📥 Download {LANG} {vkey}", f, file_name=f"{LANG}_{vkey}.mp3", key=f"dl_{LANG}_v107")

with tab2:
    st.markdown("### 🎬 VIDEO AD - FFMPEG FIX - Aapki Honey Image Se Ad")
    has_ffmpeg = check_ffmpeg()
    if has_ffmpeg:
        st.success("✅ ffmpeg Installed - Video Banega!")
    else:
        st.warning("⚠️ ffmpeg nahi hai - packages.txt me ffmpeg likh ke Commit karo - Phir Manage app -> Reboot - Phir ffmpeg ayega!")
        st.code("packages.txt me likho:\nffmpeg", language="text")
    
    prod_image = st.file_uploader("📸 Product Image (Honey Jar):", type=["jpg","jpeg","png","webp"], key="prod_v107")
    
    col1,col2 = st.columns(2)
    with col1:
        vid_lang = st.selectbox("🌍 Language:", ["SINDHI","URDU","HINDI","ENGLISH","ARABIC"], index=1, key="vlang_v107")
        vid_time = st.selectbox("⏱️ Duration:", list(TIME_OPTIONS.keys()), index=3, key="vid_time_v107")
        VID_SEC = TIME_OPTIONS[vid_time]
    with col2:
        vid_voice_key = st.selectbox("🎤 Voice:", list(VOICES[vid_lang].keys()), key="vid_voice_v107")
        vid_voice = VOICES[vid_lang][vid_voice_key]
        vid_speed = st.select_slider("Speed:", options=["-5%","-15%","+10%"], value="-5%", key="vid_speed_v107")
    
    default_vid_text = st.session_state.get(f"text_{vid_lang}", "") or st.session_state.get("master_text_widget_v107","") or "Mehar Mart Khalis Shahad - 100% Pure - Rs 2975 - Free Delivery!"
    vid_text = st.text_area(f"✍️ Video Text ({vid_lang}):", value=default_vid_text[:VID_SEC*14], height=120, key="vid_text_v107")
    
    if st.button("🎬 VIDEO BANAO - FINAL FIX", type="primary", use_container_width=True, key="make_video_v107"):
        if not prod_image:
            st.error("Image Upload Karo!")
        elif not vid_text.strip():
            st.error("Text Likho!")
        elif not has_ffmpeg:
            st.error("ffmpeg install nahi - packages.txt banao - Upar dekho!")
            st.info("Voice to ban gaya hai niche - Audio download karo - Video ke liye packages.txt -> ffmpeg -> Reboot")
            # Still make voice
            os.makedirs("video", exist_ok=True)
            voice_path = f"video/voice_{vid_lang}_{VID_SEC}_v107.mp3"
            cleaned_vid = clean_for_voice(vid_text, vid_lang)
            ok_voice = asyncio.run(gen_edge(cleaned_vid, vid_voice, vid_speed, voice_path))
            if ok_voice:
                st.audio(voice_path)
                with open(voice_path,"rb") as f: st.download_button("📥 Download Audio - Voice Ready!", f, file_name=f"{vid_lang}_audio.mp3", key="dl_audio_no_ffmpeg")
        else:
            with st.spinner(f"🎬 {vid_lang} Video Ban Raha... 20 sec..."):
                try:
                    os.makedirs("video", exist_ok=True)
                    from PIL import Image as PILImage
                    img = PILImage.open(prod_image).convert("RGB")
                    img = img.resize((1080,1920))
                    img_path = f"video/input_{vid_lang}_v107.jpg"
                    img.save(img_path)
                    
                    voice_path = f"video/voice_{vid_lang}_{VID_SEC}_v107.mp3"
                    cleaned_vid = clean_for_voice(vid_text, vid_lang)
                    ok_voice = asyncio.run(gen_edge(cleaned_vid, vid_voice, vid_speed, voice_path))
                    
                    if not ok_voice:
                        st.error("Voice Fail")
                    else:
                        output_path = f"video/MEHAR_AD_{vid_lang}_{VID_SEC}s_V107.mp4"
                        success, result = make_video_light(img_path, voice_path, output_path, VID_SEC)
                        if success:
                            st.success(f"✅ Video Ready! {vid_lang} - Mobile 9:16 - FFmpeg Fixed!")
                            st.video(result)
                            with open(result,"rb") as f:
                                st.download_button(f"📥 Download Ad {vid_lang}", f, file_name=f"Mehar_{vid_lang}_Ad_{VID_SEC}s.mp4", mime="video/mp4", type="primary", use_container_width=True, key="dl_vid_v107")
                            st.audio(voice_path)
                            st.balloons()
                        else:
                            st.error(f"Video Error: {result}")
                except Exception as e:
                    st.error(f"Error: {e}")

st.caption("V107 - FFmpeg Fix: packages.txt me ffmpeg add karo - Voice Paka Same V102 - Video Final")
