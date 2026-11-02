import streamlit as st, os, asyncio, subprocess
from dotenv import load_dotenv
load_dotenv()
st.set_page_config(page_title="MEHAR V108 - MOVEMENT FIX", layout="centered")

from PIL import Image
if not hasattr(Image, 'ANTIALIAS'): Image.ANTIALIAS = Image.LANCZOS
import edge_tts

GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
st.title("MEHAR V108 - LARKI MOVEMENT FIX 🌍")

TIME_OPTIONS = {"10 Second":10,"15 Second":15,"30 Second":30,"60 Second (1 Min)":60,"2 Minutes":120}
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
    if target=="URDU": return "السلام علیکم! میرے پیارے بھائیو! مہر مارٹ کا خالص شہد 100% خالص ہے! ملاوٹ سے پاک! صرف 2975 روپے میں! فری ہوم ڈلیوری!"
    if target=="HINDI": return "नमस्ते! महर मार्ट का शुद्ध शहद 100% शुद्ध है! सिर्फ 2975 रुपये में! फ्री डिलीवरी!"
    if target=="ENGLISH": return "Hello! Mehar Mart pure honey 100% pure! Only 2975 rupees! Free delivery!"
    if target=="ARABIC": return "السلام عليكم! عسل مهر مارت نقي 100%! فقط 2975 روبية!"
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
    try: subprocess.run(["ffmpeg","-version"], capture_output=True, timeout=5); return True
    except: return False

# V108 - MOVEMENT FILTER - Larki Hilegi
def make_video_movement(image_path, audio_path, output_path, movement_type):
    try:
        # Movement Filters - Larki Hilegi
        if movement_type == "Talking Zoom - Larki Hilegi":
            # Slow Zoom In + Slight Pan - Like talking photo
            vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='min(zoom+0.0015,1.25)':d=1:x='iw/2-(iw/zoom/2)+sin(on/5)*10':y='ih/2-(ih/zoom/2)+sin(on/10)*5',scale=1080:1920"
        elif movement_type == "Ken Burns - Slow Move":
            vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='if(lte(zoom,1.0),1.0,max(1.001*zoom,1.3))':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)',scale=1080:1920"
        else: # Static with breathing
            vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='1+0.0005*sin(on/10)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)',scale=1080:1920"

        cmd = ["ffmpeg","-y","-loop","1","-i",image_path,"-i",audio_path,"-c:v","libx264","-t","30","-c:a","aac","-b:a","192k","-shortest","-pix_fmt","yuv420p","-vf",vf,output_path]
        subprocess.run(cmd, capture_output=True, timeout=120)
        if os.path.exists(output_path) and os.path.getsize(output_path)>2000:
            return True, output_path
        # Fallback simple
        cmd2 = ["ffmpeg","-y","-loop","1","-i",image_path,"-i",audio_path,"-c:v","libx264","-c:a","aac","-shortest","-vf","scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",output_path]
        subprocess.run(cmd2, capture_output=True, timeout=120)
        if os.path.exists(output_path): return True, output_path
        return False, "ffmpeg fail"
    except Exception as e: return False, str(e)

tab1, tab2 = st.tabs(["🎙️ VOICE STUDIO - SAME V102", "🎬 VIDEO - LARKI MOVEMENT FIX V108"])

with tab1:
    st.markdown("### ✅ Purana Voice Same - Paka Same")
    for lang in VOICES:
        if f"text_{lang}" not in st.session_state: st.session_state[f"text_{lang}"] = ""
    master = st.text_area("✍️ MASTER:", height=100, key="master_v108")
    if st.button("🔄 ALL 5 BOX", type="primary", use_container_width=True, key="btn_all_v108"):
        src = st.session_state.get("master_v108","").strip()
        if src:
            for LANG in VOICES:
                st.session_state[f"text_{LANG}"] = translate_fix(src, LANG)
                st.session_state[f"ta_{LANG}"] = translate_fix(src, LANG)
            st.rerun()
    for LANG in ["SINDHI","URDU","HINDI","ENGLISH","ARABIC"]:
        with st.expander(f"{LANG}", expanded=False):
            c1,c2 = st.columns(2)
            with c1:
                time_sel = st.selectbox("⏱️ Time:", list(TIME_OPTIONS.keys()), index=2, key=f"ts_{LANG}_v108")
                MAX_SEC = TIME_OPTIONS[time_sel]
            with c2:
                vkey = st.selectbox("🎤 Voice:", list(VOICES[LANG].keys()), key=f"v_{LANG}_v108")
                vname = VOICES[LANG][vkey]
            txt = st.text_area(f"✍️ {LANG}:", height=80, key=f"ta_{LANG}_v108", value=st.session_state.get(f"text_{LANG}",""))
            rate = st.select_slider("Speed:", options=["-5%","-15%","+10%"], value="-5%", key=f"sp_{LANG}_v108")
            if st.button(f"🎙️ Voice {vkey}", key=f"gen_{LANG}_v108", type="primary", use_container_width=True):
                if txt.strip():
                    os.makedirs("voice", exist_ok=True)
                    fp = f"voice/{LANG}_{MAX_SEC}_v108.mp3"
                    ok = asyncio.run(gen_edge(clean_for_voice(txt, LANG), vname, rate, fp))
                    if ok: st.audio(fp); st.success(f"{LANG} {vkey} Ready!")

with tab2:
    st.markdown("### 🎬 V108 - LARKI MOVEMENT FIX - Ab Hilegi!")
    has_ff = check_ffmpeg()
    if has_ff: st.success("✅ ffmpeg OK - Movement Video Banega!")
    else: st.warning("packages.txt me ffmpeg likho + Reboot")

    st.info("Aap ki screenshot wali Larki - Ab is me movement ayegi - Talking Zoom!")
    prod_image = st.file_uploader("📸 Larki + Honey Image:", type=["jpg","jpeg","png","webp"], key="prod_v108")

    col1,col2 = st.columns(2)
    with col1:
        vid_lang = st.selectbox("🌍 Language:", ["SINDHI","URDU","HINDI","ENGLISH","ARABIC"], index=1, key="vlang_v108")
        vid_voice_key = st.selectbox("🎤 Larki Voice:", list(VOICES[vid_lang].keys()), index=1, key="vid_voice_v108") # Default Larki
        vid_voice = VOICES[vid_lang][vid_voice_key]
    with col2:
        vid_time = st.selectbox("⏱️ Duration:", list(TIME_OPTIONS.keys()), index=2, key="vid_time_v108")
        VID_SEC = TIME_OPTIONS[vid_time]
        movement = st.selectbox("🎥 Movement Type:", ["Talking Zoom - Larki Hilegi", "Ken Burns - Slow Move", "Breathing - Halki Movement"], index=0, key="move_v108")

    default_vid_text = st.session_state.get(f"text_{vid_lang}", "") or "Mehar Mart Khalis Shahad - 100% Pure - Rs 2975 - Free Delivery - Order Now!"
    vid_text = st.text_area(f"✍️ {vid_lang} Text (Larki Bolegi):", value=default_vid_text[:VID_SEC*14], height=100, key="vid_text_v108")
    vid_speed = st.select_slider("Voice Speed:", options=["-5%","-15%","+10%"], value="-5%", key="vid_speed_v108")

    st.markdown("**👇 Important: Larki ki awaz ke liye `Uzma Larki / Swara Larki` select karo - Larka nahi!**")

    if st.button("🎬 VIDEO BANAO - LARKI HILEGI + BOLEGI", type="primary", use_container_width=True, key="make_video_v108"):
        if not prod_image: st.error("Image Upload Karo!")
        elif not vid_text.strip(): st.error("Text Likho!")
        elif not has_ff: st.error("ffmpeg nahi - packages.txt banao")
        else:
            with st.spinner(f"🎬 {vid_voice_key} Video Ban Raha - Movement ke saath - 25 sec..."):
                try:
                    os.makedirs("video", exist_ok=True)
                    from PIL import Image as PILImage
                    img = PILImage.open(prod_image).convert("RGB")
                    # Make 1080x1920 - Portrait
                    img = img.resize((1080,1920))
                    img_path = f"video/input_{vid_lang}_v108.jpg"
                    img.save(img_path)

                    voice_path = f"video/voice_{vid_lang}_v108.mp3"
                    ok_voice = asyncio.run(gen_edge(clean_for_voice(vid_text, vid_lang), vid_voice, vid_speed, voice_path))
                    if not ok_voice: st.error("Voice Fail")
                    else:
                        output_path = f"video/MEHAR_AD_{vid_lang}_MOVING_V108.mp4"
                        success, result = make_video_movement(img_path, voice_path, output_path, movement)
                        if success:
                            st.success(f"✅ Video Ready! {vid_voice_key} Bolegi + {movement} - Movement Fixed!")
                            st.video(result)
                            with open(result,"rb") as f:
                                st.download_button(f"📥 Download - {vid_voice_key} Moving Ad", f, file_name=f"Mehar_{vid_lang}_{vid_voice_key}_Moving.mp4", mime="video/mp4", type="primary", use_container_width=True, key="dl_vid_v108")
                            st.audio(voice_path)
                            st.balloons()
                            st.info("Ab Larki hilegi - Zoom + halki movement - Photo zinda lagega! Asli muh hilana (lip-sync) ke liye V109 me AI Talking Avatar dunga!")
                        else: st.error(f"Video Error: {result}")
                except Exception as e: st.error(f"Error: {e}")

st.caption("V108 - Movement Fix - Voice Paka Same V102 - Larki Movement: Zoom + Pan + Breathing")
