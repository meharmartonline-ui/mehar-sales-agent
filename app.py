import streamlit as st, os, asyncio, subprocess, textwrap
from dotenv import load_dotenv
load_dotenv()
st.set_page_config(page_title="MEHAR V109 - CAPTION", layout="centered")

from PIL import Image, ImageDraw, ImageFont
if not hasattr(Image, 'ANTIALIAS'): Image.ANTIALIAS = Image.LANCZOS
import edge_tts

GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
st.title("MEHAR V109 - CAPTION + VOICE + IMAGE 🌍")

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

# V109 - Caption Image Creator - Jo Voice Wahi Text
def create_caption_image(text, lang, width=1080, height=300):
    # Create black semi-transparent bg with white/yellow text
    img = Image.new('RGBA', (width, height), (0,0,0,180))
    draw = ImageDraw.Draw(img)
    try:
        # Try to load urdu font if available else default
        font = ImageFont.truetype("DejaVuSans.ttf", 42)
    except:
        try: font = ImageFont.load_default()
        except: font = None
    # Wrap text
    wrapped = textwrap.wrap(text, width=22)[:3] # 3 lines max
    y = 20
    for line in wrapped:
        # Center
        bbox = draw.textbbox((0,0), line, font=font) if font else (0,0,0,0)
        w = bbox[2]-bbox[0] if font else len(line)*20
        x = (width - w)//2
        draw.text((x, y), line, font=font, fill=(255,255,255,255), stroke_width=2, stroke_fill=(0,0,0,255))
        y += 55
    return img

def make_video_with_caption(image_path, audio_path, output_path, caption_text, show_caption, movement_type):
    try:
        # Create caption overlay image
        caption_path = "video/caption_overlay.png"
        if show_caption:
            cap_img = create_caption_image(caption_text, "URDU")
            cap_img.save(caption_path)
        
        # Video filter with movement + caption overlay
        if movement_type == "Talking Zoom - Larki Hilegi":
            base_vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='min(zoom+0.0015,1.25)':d=1:x='iw/2-(iw/zoom/2)+sin(on/5)*8':y='ih/2-(ih/zoom/2)':s=1080x1920"
        else:
            base_vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='if(lte(zoom,1.0),1.0,max(1.001*zoom,1.2))':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920"

        if show_caption and os.path.exists(caption_path):
            # Input 1: image, Input 2: audio, Input 3: caption png
            # Complex filter: zoom image then overlay caption at bottom
            filter_complex = f"[0:v]{base_vf}[base];[base][2:v]overlay=(W-w)/2:H-h-150:shortest=1:format=auto"
            cmd = ["ffmpeg","-y","-loop","1","-i",image_path,"-i",audio_path,"-i",caption_path,"-filter_complex",filter_complex,"-c:a","aac","-b:a","192k","-shortest","-pix_fmt","yuv420p","output_path_temp"]
            # Use simple overlay for stability
            vf_simple = f"{base_vf},scale=1080:1920"
            # First make moving video
            temp_moving = "video/temp_moving.mp4"
            cmd1 = ["ffmpeg","-y","-loop","1","-i",image_path,"-i",audio_path,"-c:v","libx264","-c:a","aac","-shortest","-pix_fmt","yuv420p","-vf",f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",temp_moving]
            subprocess.run(cmd1, capture_output=True, timeout=90)
            # Now overlay caption
            cmd2 = ["ffmpeg","-y","-i",temp_moving,"-i",caption_path,"-filter_complex","[0:v][1:v]overlay=(W-w)/2:H-h-120","-c:a","copy",output_path]
            subprocess.run(cmd2, capture_output=True, timeout=90)
        else:
            cmd = ["ffmpeg","-y","-loop","1","-i",image_path,"-i",audio_path,"-c:v","libx264","-c:a","aac","-shortest","-pix_fmt","yuv420p","-vf","scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",output_path]
            subprocess.run(cmd, capture_output=True, timeout=90)

        if os.path.exists(output_path) and os.path.getsize(output_path)>2000:
            return True, output_path
        return False, "ffmpeg fail"
    except Exception as e: return False, str(e)

tab1, tab2 = st.tabs(["🎙️ VOICE - SAME V102", "🎬 VIDEO - CAPTION + LARKI + IMAGE V109"])

with tab1:
    st.markdown("### ✅ Voice Same - Paka Same")
    for lang in VOICES:
        if f"text_{lang}" not in st.session_state: st.session_state[f"text_{lang}"] = ""
    master = st.text_area("✍️ MASTER:", height=80, key="master_v109")
    if st.button("🔄 ALL 5 BOX", type="primary", use_container_width=True, key="btn_all_v109"):
        src = st.session_state.get("master_v109","").strip()
        if src:
            for LANG in VOICES:
                st.session_state[f"text_{LANG}"] = translate_fix(src, LANG)
            st.rerun()
    for LANG in ["SINDHI","URDU","HINDI","ENGLISH","ARABIC"]:
        with st.expander(f"{LANG}", expanded=False):
            vkey = st.selectbox("🎤 Voice:", list(VOICES[LANG].keys()), key=f"v_{LANG}_v109")
            vname = VOICES[LANG][vkey]
            txt = st.text_area(f"{LANG}:", height=60, key=f"ta_{LANG}_v109", value=st.session_state.get(f"text_{LANG}",""))
            rate = st.select_slider("Speed:", options=["-5%","-15%","+10%"], value="-5%", key=f"sp_{LANG}_v109")
            if st.button(f"🎙️ {vkey}", key=f"gen_{LANG}_v109", type="primary", use_container_width=True):
                if txt.strip():
                    os.makedirs("voice", exist_ok=True)
                    fp = f"voice/{LANG}_v109.mp3"
                    ok = asyncio.run(gen_edge(clean_for_voice(txt, LANG), vname, rate, fp))
                    if ok: st.audio(fp)

with tab2:
    st.markdown("### 🎬 V109 - CAPTION WALA VIDEO - Jo Voice Wahi Text!")
    has_ff = check_ffmpeg()
    if has_ff: st.success("✅ ffmpeg OK")
    else: st.warning("packages.txt me ffmpeg likho + Reboot")

    prod_image = st.file_uploader("📸 Image (Larki + Honey):", type=["jpg","jpeg","png","webp"], key="prod_v109")
    col1,col2 = st.columns(2)
    with col1:
        vid_lang = st.selectbox("🌍 Lang:", ["SINDHI","URDU","HINDI","ENGLISH","ARABIC"], index=1, key="vlang_v109")
        vid_voice_key = st.selectbox("🎤 Larki:", list(VOICES[vid_lang].keys()), index=1, key="vid_voice_v109")
        vid_voice = VOICES[vid_lang][vid_voice_key]
    with col2:
        vid_time = st.selectbox("⏱️ Time:", list(TIME_OPTIONS.keys()), index=2, key="vid_time_v109")
        movement = st.selectbox("🎥 Move:", ["Talking Zoom - Larki Hilegi", "Ken Burns"], index=0, key="move_v109")
        show_caption = st.checkbox("📝 CAPTION SHOW? - Jo Voice Wahi Text", value=True, key="cap_check_v109")
        caption_style = st.selectbox("Caption Style:", ["White Text + Black Bg", "Yellow Text"], key="cap_style_v109")

    default_vid_text = st.session_state.get(f"text_{vid_lang}", "") or "Mehar Mart Khalis Shahad - 100% Pure - Rs 2975 - Free Delivery!"
    vid_text = st.text_area(f"✍️ Text - Yahi Voice Bolegi + Yahi Caption Ayega ({vid_lang}):", value=default_vid_text[:200], height=110, key="vid_text_v109")
    vid_speed = st.select_slider("Speed:", options=["-5%","-15%","+10%"], value="-5%", key="vid_speed_v109")

    st.markdown(f"**Preview Caption:** `{vid_text[:60]}...` - Yehi video me neeche ayega!")

    if st.button("🎬 VIDEO BANAO - IMAGE + LARKI VOICE + CAPTION", type="primary", use_container_width=True, key="make_video_v109"):
        if not prod_image: st.error("Image Upload!")
        elif not vid_text.strip(): st.error("Text Likho!")
        elif not has_ff: st.error("ffmpeg nahi")
        else:
            with st.spinner(f"🎬 {vid_voice_key} - Image + Voice + Caption - 30 sec..."):
                try:
                    os.makedirs("video", exist_ok=True)
                    from PIL import Image as PILImage
                    img = PILImage.open(prod_image).convert("RGB").resize((1080,1920))
                    img_path = f"video/input_{vid_lang}_v109.jpg"
                    img.save(img_path)

                    voice_path = f"video/voice_{vid_lang}_v109.mp3"
                    ok_voice = asyncio.run(gen_edge(clean_for_voice(vid_text, vid_lang), vid_voice, vid_speed, voice_path))
                    if not ok_voice: st.error("Voice Fail")
                    else:
                        output_path = f"video/MEHAR_AD_{vid_lang}_CAPTION_V109.mp4"
                        success, result = make_video_with_caption(img_path, voice_path, output_path, vid_text, show_caption, movement)
                        if success:
                            st.success(f"✅ Ready! Image + {vid_voice_key} Voice + Caption - Jo Voice Wahi Text!")
                            st.video(result)
                            with open(result,"rb") as f:
                                st.download_button(f"📥 Download Ad - Caption Wala", f, file_name=f"Mehar_{vid_lang}_Caption_Ad.mp4", mime="video/mp4", type="primary", use_container_width=True, key="dl_vid_v109")
                            st.audio(voice_path)
                            st.balloons()
                        else: st.error(f"Error: {result}")
                except Exception as e: st.error(f"Error: {e}")

st.caption("V109 - Caption Added - Jo Voice Wahi Text Video me - Image + Larki Voice + Caption - Voice Same V102")
