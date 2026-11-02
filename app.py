import streamlit as st, os, asyncio, requests
from dotenv import load_dotenv
load_dotenv()
import edge_tts
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# MoviePy for Video
try:
    from moviepy.editor import ImageClip, AudioFileClip, TextClip, CompositeVideoClip, ColorClip, concatenate_videoclips
    HAS_MOVIEPY = True
except:
    HAS_MOVIEPY = False

GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
groq_client = None
try:
    if GROQ_API_KEY and len(GROQ_API_KEY) > 30:
        from groq import Groq
        groq_client = Groq(api_key=GROQ_API_KEY)
except: pass

st.set_page_config(page_title="MEHAR V103 - VIDEO GENERATOR", layout="centered")
st.title("MEHAR V103 - WORLD STUDIO 🌍 - Voice + Video Ad Generator")

if not HAS_MOVIEPY:
    st.error("MoviePy install karo: pip install moviepy Pillow")
    
TIME_OPTIONS = {"10 Second":10,"15 Second":15,"30 Second":30,"60 Second (1 Min)":60,"2 Minutes":120,"5 Minutes":300}
VOICES = {
    "SINDHI": {"Asad Larka": "ur-PK-AsadNeural", "Uzma Larki": "ur-PK-UzmaNeural"},
    "URDU": {"Asad Larka": "ur-PK-AsadNeural", "Uzma Larki": "ur-PK-UzmaNeural"},
    "HINDI": {"Madhur Larka": "hi-IN-MadhurNeural", "Swara Larki": "hi-IN-SwaraNeural"},
    "ENGLISH": {"Guy Larka": "en-US-GuyNeural", "Jenny Larki": "en-US-JennyNeural"},
    "ARABIC": {"Hamed Larka": "ar-SA-HamedNeural", "Zariyah Larki": "ar-SA-ZariyahNeural"},
}

# Alfabet Maps - V102 Same
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

# ===== TABS - System Same + Video New =====
tab1, tab2 = st.tabs(["🎙️ VOICE STUDIO (V102 Same)", "🎬 VIDEO GENERATOR - NEW"])

with tab1:
    st.markdown("### Same Voice Studio - Larka Larki - Time - Alfabet Fix")
    for lang in VOICES:
        if f"text_{lang}" not in st.session_state: st.session_state[f"text_{lang}"] = ""
    master = st.text_area("✍️ MASTER PROMPT:", height=120, key="master_text_widget")
    if st.button("🔄 ALL 5 BOX BHARO", type="primary", use_container_width=True):
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
                time_sel = st.selectbox(f"⏱️ Time:", list(TIME_OPTIONS.keys()), index=3, key=f"ts_{LANG}")
                MAX_SEC = TIME_OPTIONS[time_sel]
            with c2:
                vkey = st.selectbox(f"🎤 Voice:", list(VOICES[LANG].keys()), key=f"v_{LANG}")
                vname = VOICES[LANG][vkey]
            txt = st.text_area(f"✍️ {LANG} Text:", height=100, key=f"ta_{LANG}")
            rate = st.select_slider(f"Speed:", options=["-5%","-15%","+10%"], value="-5%", key=f"sp_{LANG}")
            if st.button(f"🎙️ Voice Banao {MAX_SEC}s", key=f"gen_{LANG}", type="primary", use_container_width=True):
                if txt:
                    os.makedirs("voice", exist_ok=True)
                    fp = f"voice/{LANG}_{MAX_SEC}.mp3"
                    cleaned = clean_for_voice(txt, LANG)
                    ok = asyncio.run(gen_edge(cleaned, vname, rate, fp))
                    if ok:
                        st.audio(fp)
                        st.session_state[f"last_audio_{LANG}"] = fp

with tab2:
    st.markdown("### 🎬 MEHAR VIDEO AD GENERATOR - Mobile Jaisa")
    st.info("1 Image Upload Karo -> Language Select Karo -> Voice + Video Auto Banega - Product Advertise!")
    
    prod_image = st.file_uploader("📸 Product Image Upload (Mehar Honey Jar):", type=["jpg","jpeg","png","webp"])
    
    col1,col2 = st.columns(2)
    with col1:
        vid_lang = st.selectbox("🌍 Video Language:", ["SINDHI","URDU","HINDI","ENGLISH","ARABIC"], index=1)
        vid_time = st.selectbox("⏱️ Video Duration:", list(TIME_OPTIONS.keys()), index=3, key="vid_time")
        VID_SEC = TIME_OPTIONS[vid_time]
    with col2:
        vid_voice_key = st.selectbox("🎤 Video Voice:", list(VOICES[vid_lang].keys()), key="vid_voice")
        vid_voice = VOICES[vid_lang][vid_voice_key]
        vid_speed = st.select_slider("Speed Video:", options=["-5%","-15%","+10%"], value="-5%", key="vid_speed")
    
    # Auto text from voice box or master
    default_vid_text = st.session_state.get(f"text_{vid_lang}", "") or st.session_state.get("master_text_widget","") or "Mehar Mart Khalis Shahad - 100% Pure - Free Delivery!"
    vid_text = st.text_area(f"✍️ Video Ad Text ({vid_lang}):", value=default_vid_text[:VID_SEC*14], height=120, key="vid_text")
    
    st.markdown("#### 🎨 Video Style - Mobile Ad Jaisa")
    s1,s2,s3 = st.columns(3)
    with s1:
        bg_color = st.color_picker("Background Color:", "#FFF8E1")
        text_color = st.color_picker("Text Color:", "#000000")
    with s2:
        zoom_effect = st.selectbox("Image Effect:", ["Zoom In (Mobile Style)", "Zoom Out", "Static", "Ken Burns"])
        text_position = st.selectbox("Text Position:", ["Bottom", "Top", "Center"])
    with s3:
        show_price = st.checkbox("💰 Price Tag Show (Rs 2975)", value=True)
        show_logo = st.checkbox("🏷️ Mehar Mart Logo Text", value=True)
    
    if st.button("🎬 VIDEO BANAO - Image + Voice + Text", type="primary", use_container_width=True):
        if not prod_image:
            st.error("Pehle Product Image Upload Karo!")
        elif not vid_text.strip():
            st.error("Text Likho!")
        elif not HAS_MOVIEPY:
            st.error("MoviePy missing")
        else:
            with st.spinner(f"🎬 {vid_lang} Video Ban Raha Hai... Image + Voice + Text... 30 sec..."):
                try:
                    os.makedirs("video", exist_ok=True)
                    # Save uploaded image
                    img = Image.open(prod_image).convert("RGB")
                    img_path = f"video/input_{vid_lang}.jpg"
                    img.save(img_path)
                    
                    # 1. Voice Generate
                    voice_path = f"video/voice_{vid_lang}_{VID_SEC}.mp3"
                    cleaned_vid = clean_for_voice(vid_text, vid_lang)
                    ok_voice = asyncio.run(gen_edge(cleaned_vid, vid_voice, vid_speed, voice_path))
                    
                    if not ok_voice:
                        st.error("Voice Fail")
                    else:
                        # 2. Create Video - Mobile Style
                        audio_clip = AudioFileClip(voice_path)
                        real_duration = min(audio_clip.duration + 1, VID_SEC + 2)  # Voice + 1 sec
                        
                        # Image Clip with Zoom Effect
                        image_clip = ImageClip(img_path).set_duration(real_duration)
                        # Resize to 1080x1920 - Mobile Vertical (9:16)
                        image_clip = image_clip.resize(height=1920)
                        # Center crop to 1080x1920
                        image_clip = image_clip.crop(x_center=image_clip.w/2, y_center=image_clip.h/2, width=1080, height=1920)
                        
                        # Zoom effect
                        if "Zoom In" in zoom_effect:
                            image_clip = image_clip.resize(lambda t: 1 + 0.1*t/real_duration)
                        elif "Zoom Out" in zoom_effect:
                            image_clip = image_clip.resize(lambda t: 1.2 - 0.1*t/real_duration)
                        
                        # Color background
                        bg_clip = ColorClip(size=(1080,1920), color=[255,248,225], duration=real_duration)
                        
                        # Composite - Image on BG
                        # For simplicity, use image_clip as base
                        final_clip = image_clip
                        
                        # Add Text Overlays using PIL (for Urdu/Sindhi support)
                        # Create text image
                        txt_img = Image.new('RGBA', (1000, 400), (0,0,0,0))
                        draw = ImageDraw.Draw(txt_img)
                        # Try to load Urdu font - fallback default
                        try:
                            # Use default - PIL will handle
                            font = ImageFont.load_default()
                            # Wrap text
                            wrapped = "\n".join([vid_text[i:i+35] for i in range(0, len(vid_text), 35)][:4])
                            draw.text((20,20), wrapped, fill=text_color, font=font)
                        except:
                            pass
                        txt_path = f"video/text_{vid_lang}.png"
                        txt_img.save(txt_path)
                        
                        text_clip = ImageClip(txt_path).set_duration(real_duration).set_position(('center', 0.75), relative=True)
                        
                        # Final Composite
                        final = CompositeVideoClip([final_clip, text_clip]).set_audio(audio_clip)
                        
                        output_path = f"video/MEHAR_AD_{vid_lang}_{vid_voice_key}_{VID_SEC}s.mp4"
                        final.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac', verbose=False, logger=None)
                        
                        st.success(f"✅ Video Ready! {vid_lang} - {real_duration:.1f}s - Mobile Vertical 9:16")
                        st.video(output_path)
                        with open(output_path,"rb") as f:
                            st.download_button(f"📥 Download Video Ad {vid_lang}", f, file_name=f"Mehar_{vid_lang}_Ad_{VID_SEC}s.mp4", mime="video/mp4", type="primary", use_container_width=True)
                        st.audio(voice_path)
                        
                except Exception as e:
                    st.error(f"Video Error: {e}")
                    st.info("Tip: Replit me MoviePy install karo: pip install moviepy Pillow edge_tts python-dotenv")

st.caption("V103 - Voice + Video Generator - Ek Image Se Ad Video - Mobile Style 9:16 - Voice Alfabet Clear")
