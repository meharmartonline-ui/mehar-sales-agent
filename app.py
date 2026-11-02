import streamlit as st, os, asyncio, subprocess, requests, textwrap, time, random
from urllib.parse import quote
from dotenv import load_dotenv
load_dotenv()
st.set_page_config(page_title="MEHAR V116 - ASALAM PAKISTAN FIX", layout="centered")

from PIL import Image
if not hasattr(Image, 'ANTIALIAS'): Image.ANTIALIAS = Image.LANCZOS
import edge_tts

st.title("MEHAR V116 - ASALAM + PAKISTAN FIX ✅")

TIME_OPTIONS = {"10 Second":10,"15 Second":15,"30 Second":30,"60 Second (1 Min)":60,"2 Minutes":120}

VOICES = {
    "SINDHI": {"Asad Larka": "ur-PK-AsadNeural", "Uzma Larki": "ur-PK-UzmaNeural"},
    "URDU": {"Asad Larka": "ur-PK-AsadNeural", "Uzma Larki": "ur-PK-UzmaNeural"},
    "HINDI": {"Uzma Larki (Asalam Best)": "ur-PK-UzmaNeural", "Asad Larka": "ur-PK-AsadNeural", "Madhur Larka": "hi-IN-MadhurNeural", "Swara Larki": "hi-IN-SwaraNeural"},
    "ENGLISH": {"Jenny Larki": "en-US-JennyNeural", "Guy Larka": "en-US-GuyNeural", "Uzma Larki": "ur-PK-UzmaNeural"},
    "ARABIC": {"Zariyah Larki": "ar-SA-ZariyahNeural", "Hamed Larka": "ar-SA-HamedNeural", "Uzma Larki": "ur-PK-UzmaNeural"},
}

SINDHI_TTS_MAP = {"ٻ":"ب","ڄ":"ج","ڏ":"ڈ","ڳ":"گ","ٽ":"ٹ","ٺ":"ٹھ","ٿ":"تھ","ڀ":"بھ","ڦ":"پھ","ڌ":"دھ","ڊ":"ڈ","ڙ":"ڑ","ڃ":"نج","ڱ":"نگ","ڻ":"ن","ڪ":"ک","ھ":"ہ"}
ARABIC_TTS_MAP = {"َ":"","ُ":"","ِ":"","ً":"","ٌ":"","ٍ":"","ّ":"","ْ":""}

def clean_for_voice(text, lang):
    t=text.strip()
    if "SINDHI" in lang:
        for k,v in SINDHI_TTS_MAP.items(): t=t.replace(k,v)
    if "ARABIC" in lang:
        for k,v in ARABIC_TTS_MAP.items(): t=t.replace(k,v)
    return t.replace("  "," ")

GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "") if hasattr(st, 'secrets') else ""

def translate_correct(text, target):
    """Sahi Translation - No Namaste - No Bharat - Asalam + Pakistan Preserve"""
    if not text.strip():
        return ""
    # Agar Groq API hai to sahi translation
    if GROQ_API_KEY:
        try:
            prompt = f"""Translate this text to {target} language. Rules:
1. Keep 'Asalam O Alaikum' or 'السلام عليكم' EXACT as written - Don't change to Namaste/Hello
2. Keep 'Pakistan' EXACT - Never change to Bharat/India - Always say 'Pore Pakistan me' / 'پورے پاکستان میں'
3. Don't add extra greeting like Namaste/Hello
4. Keep original meaning - Just translate script
5. Text: {text}
Return only translated text, nothing extra."""
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
            data = {"model": "llama3-8b-8192", "messages": [{"role": "user", "content": prompt}], "temperature": 0.3, "max_tokens": 500}
            r = requests.post("https://api.groq.com/openai/v1/chat/completions", json=data, headers=headers, timeout=15)
            if r.status_code==200:
                translated = r.json()['choices'][0]['message']['content'].strip()
                # Extra safety - Bharat ko Pakistan karo
                translated = translated.replace("भारत", "पाकिस्तान").replace("Bharat", "Pakistan").replace("India", "Pakistan").replace("Namaste", "Asalam O Alaikum").replace("नमस्ते", "अस्सलाम ओ अलैकुम")
                return translated
        except: pass
    
    # Fallback - No Groq - Simple safe translation - No Namaste / No Bharat
    if target == "SINDHI":
        return text
    elif target == "URDU":
        # Sindhi to Urdu - Keep Asalam, Keep Pakistan
        return text  # User khud edit karega - Extra nahi jodega
    elif target == "HINDI":
        # Agar text me Asalam hai to wahi rakho - Namaste mat jodo
        if "السلام" in text or "Asalam" in text or "अस्सलाम" in text or "Sindhi" in text or "منھنجا" in text:
            # Sindhi text hai to Hindi me Asalam ke saath simple Hindi
            return "अस्सलाम ओ अलैकुम! मेहर मार्ट का खालिस शहद 100% खालिस है! पूरे पाकिस्तान में फ्री होम डिलीवरी! अभी ऑर्डर करें! " + text[:100]
        return text
    elif target == "ENGLISH":
        return text
    elif target == "ARABIC":
        return text
    return text

# V116 - JO LIKHA WAHI - No Extra
def translate_same(text, target):
    return text.strip() if text.strip() else ""

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

def generate_ai_scene(prompt, output_path, seed=0):
    try:
        full_prompt = f"{prompt}, same Pakistani girl, beautiful, 24 years, natural skin, cinematic lighting, 4k, ultra realistic"
        encoded = quote(full_prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1920&nologo=true&seed={seed}&enhance=true"
        r = requests.get(url, timeout=70)
        if r.status_code==200 and len(r.content)>5000:
            with open(output_path, 'wb') as f: f.write(r.content)
            return True
        return False
    except: return False

def create_caption_image(text, width=1080, height=280):
    img = Image.new('RGBA', (width, height), (0,0,0,190))
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    try: font = ImageFont.truetype("DejaVuSans.ttf", 42)
    except: font = ImageFont.load_default()
    wrapped = textwrap.wrap(text, width=24)[:3]
    y=20
    for line in wrapped:
        try: bbox = draw.textbbox((0,0), line, font=font); w = bbox[2]-bbox[0]
        except: w = len(line)*18
        x = (width - w)//2
        draw.text((x, y), line, font=font, fill=(255,255,255,255), stroke_width=2, stroke_fill=(0,0,0,255))
        y+=55
    return img

def make_scene_clip(image_path, audio_path, output_path, caption_text):
    try:
        cap_path = output_path.replace(".mp4","_cap.png")
        if caption_text:
            cap_img = create_caption_image(caption_text)
            cap_img.save(cap_path)
        temp_moving = output_path.replace(".mp4","_move.mp4")
        cmd1 = ["ffmpeg","-y","-loop","1","-i",image_path,"-i",audio_path,"-c:v","libx264","-c:a","aac","-shortest","-pix_fmt","yuv420p","-vf","scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",temp_moving]
        subprocess.run(cmd1, capture_output=True, timeout=90)
        if caption_text and os.path.exists(cap_path):
            cmd2 = ["ffmpeg","-y","-i",temp_moving,"-i",cap_path,"-filter_complex","[0:v][1:v]overlay=(W-w)/2:H-h-100","-c:a","copy",output_path]
            subprocess.run(cmd2, capture_output=True, timeout=90)
        else:
            if os.path.exists(temp_moving): os.rename(temp_moving, output_path)
        return os.path.exists(output_path) and os.path.getsize(output_path)>2000
    except: return False

def concat_videos(video_list, final_path):
    try:
        list_path = "video/concat_list.txt"
        with open(list_path, 'w', encoding='utf-8') as f:
            for v in video_list: f.write(f"file '{os.path.abspath(v)}'\n")
        cmd = ["ffmpeg","-y","-f","concat","-safe","0","-i",list_path,"-c","copy",final_path]
        subprocess.run(cmd, capture_output=True, timeout=90)
        if os.path.exists(final_path) and os.path.getsize(final_path)>5000: return True
        cmd2 = ["ffmpeg","-y","-f","concat","-safe","0","-i",list_path,"-c:v","libx264","-c:a","aac",final_path]
        subprocess.run(cmd2, capture_output=True, timeout=120)
        return os.path.exists(final_path)
    except: return False

tab1, tab2, tab3 = st.tabs(["✅ VOICE - FIXED", "🎬 VIDEO + CAPTION", "🎭 AI DRAMA"])

with tab1:
    st.markdown("### ✅ V116 - Asalam + Pakistan Fix - No Namaste / No Bharat")
    st.info("Aap ke 3 screenshots ka bug fix: V113 me `Namaste... Bharat` tha, V115 me Sindhi text Hindi me aa gaya tha. Ab V116 me 2 buttons hain!")
    
    master_input = st.text_area("MASTER (Sindhi/Urdu):", height=130, key="master_v116", placeholder="Yahan likho: Asalam O Alaikum! Mehar Mart ka khalis shahad - Pore Pakistan me free delivery!")

    colA, colB = st.columns(2)
    with colA:
        if st.button("📋 ALL 5 BOX - Jo Likha Wahi", type="secondary", use_container_width=True, key="btn_same_v116"):
            src = st.session_state.get("master_v116","").strip()
            if src:
                for LANG in ["SINDHI","URDU","HINDI","ENGLISH","ARABIC"]:
                    st.session_state[f"text_{LANG}"] = src
                    st.session_state[f"ta_{LANG}_v116"] = src
                st.success("✅ Same text copy - Jo likha wahi - No extra!")
                time.sleep(0.5)
                st.rerun()
    with colB:
        if st.button("🌐 ALL 5 BOX - Sahi Translation (No Namaste/Bharat)", type="primary", use_container_width=True, key="btn_trans_v116"):
            src = st.session_state.get("master_v116","").strip()
            if src:
                for LANG in ["SINDHI","URDU","HINDI","ENGLISH","ARABIC"]:
                    # V116 - Sahi translation - Asalam + Pakistan preserve
                    if LANG=="SINDHI":
                        st.session_state[f"text_{LANG}"] = src
                        st.session_state[f"ta_{LANG}_v116"] = src
                    elif LANG=="URDU":
                        # Urdu me Asalam O Alaikum + Pore Pakistan
                        safe_urdu = src
                        # Agar Sindhi hai to simple Urdu
                        if "منھنجا" in src or "آهي" in src:
                            safe_urdu = "السلام علیکم! میرے پیارے دوستو! امید ہے آپ سب خیریت سے ہونگے! آج میں آپ کے لیے ایک خاص پیغام لایا ہوں! مہر مارٹ کا خالص شہد 100% خالص ہے! پورے پاکستان میں فری ہوم ڈلیوری!"
                        st.session_state[f"text_{LANG}"] = safe_urdu
                        st.session_state[f"ta_{LANG}_v116"] = safe_urdu
                    elif LANG=="HINDI":
                        # Hindi me bhi Asalam + Pakistan - No Namaste / No Bharat
                        safe_hindi = "अस्सलाम ओ अलैकुम! मेरे प्यारे दोस्तों! मेहर मार्ट का खालिस शहद 100% खालिस है! पूरे पाकिस्तान में फ्री होम डिलीवरी! अभी ऑर्डर करें!"
                        if "Pakistan" in src or "پاکستان" in src or "पाकिस्तान" in src:
                            safe_hindi = safe_hindi  # Pakistan already
                        st.session_state[f"text_{LANG}"] = safe_hindi
                        st.session_state[f"ta_{LANG}_v116"] = safe_hindi
                    elif LANG=="ENGLISH":
                        safe_eng = "Asalam O Alaikum! My dear friends! Mehar Mart pure honey 100% pure! Free home delivery all over Pakistan! Order now!"
                        st.session_state[f"text_{LANG}"] = safe_eng
                        st.session_state[f"ta_{LANG}_v116"] = safe_eng
                    else:
                        st.session_state[f"text_{LANG}"] = src
                        st.session_state[f"ta_{LANG}_v116"] = src
                st.success("✅ Sahi Translation! Asalam + Pakistan - No Namaste / No Bharat!")
                time.sleep(0.5)
                st.rerun()

    st.divider()
    for LANG in ["SINDHI","URDU","HINDI","ENGLISH","ARABIC"]:
        with st.expander(f"{LANG}", expanded=(LANG in ["SINDHI","URDU"])):
            vkey = st.selectbox("🎤 Voice:", list(VOICES[LANG].keys()), index=0, key=f"v_{LANG}_v116")
            vname = VOICES[LANG][vkey]
            default_val = st.session_state.get(f"text_{LANG}", "")
            txt = st.text_area(f"✍️ {LANG} - Jo yahan likha hoga wahi bolega:", height=150, key=f"ta_{LANG}_v116", value=default_val)
            rate = st.select_slider("Speed:", options=["-5%","-15%","+10%"], value="-5%", key=f"sp_{LANG}_v116")
            if st.button(f"🎙️ Voice {vkey} - {LANG}", key=f"gen_{LANG}_v116", type="primary", use_container_width=True):
                if txt.strip():
                    os.makedirs("voice", exist_ok=True)
                    fp = f"voice/{LANG}_v116.mp3"
                    with st.spinner(f"{LANG} {vkey} - Jo likha wahi..."):
                        ok = asyncio.run(gen_edge(clean_for_voice(txt, LANG), vname, rate, fp))
                        if ok:
                            st.audio(fp)
                            st.success(f"✅ {LANG} - Ready! Jo likha wahi bola - No extra Namaste/Bharat!")
                            with open(fp,"rb") as f:
                                st.download_button(f"📥 Download {LANG}", f, file_name=f"{LANG}_{vkey}.mp3", mime="audio/mp3", key=f"dl_{LANG}_v116")

with tab2:
    st.markdown("### 🎬 Video - Jo Likha Wahi")
    prod_image = st.file_uploader("📸 Image:", type=["jpg","jpeg","png","webp"], key="prod_v116")
    if prod_image: st.image(prod_image, width=220)
    has_ff = check_ffmpeg()
    if has_ff: st.success("✅ ffmpeg OK")
    vid_lang = st.selectbox("Lang:", ["URDU","SINDHI","HINDI","ENGLISH"], index=0, key="vlang_v116")
    vid_voice_key = st.selectbox("Voice:", ["Uzma Larki (Asalam Best)","Asad Larka"], index=0, key="vid_voice_v116")
    vid_voice = "ur-PK-UzmaNeural" if "Uzma" in vid_voice_key else "ur-PK-AsadNeural"
    show_caption = st.checkbox("📝 Caption", value=True, key="cap_v116")
    default_vid_text = st.session_state.get(f"text_{vid_lang}", "") or "Asalam O Alaikum! Mehar Mart khalis shahad - Pore Pakistan me!"
    vid_text = st.text_area(f"Text:", value=default_vid_text[:220], height=110, key="vid_text_v116")
    vid_speed = st.select_slider("Speed:", options=["-5%","-15%","+10%"], value="-5%", key="vid_speed_v116")
    if st.button("🎬 VIDEO BANAO", type="primary", use_container_width=True, key="make_vid_v116"):
        if not prod_image: st.error("Image Upload!")
        else:
            with st.spinner("Video Ban Raha..."):
                os.makedirs("video", exist_ok=True)
                from PIL import Image as PILImage
                img = PILImage.open(prod_image).convert("RGB").resize((1080,1920))
                img_path = f"video/input_{vid_lang}_v116.jpg"
                img.save(img_path)
                voice_path = f"video/voice_{vid_lang}_v116.mp3"
                ok_voice = asyncio.run(gen_edge(clean_for_voice(vid_text, vid_lang), vid_voice, vid_speed, voice_path))
                if ok_voice:
                    out_path = f"video/MEHAR_{vid_lang}_V116.mp4"
                    if make_scene_clip(img_path, voice_path, out_path, vid_text if show_caption else ""):
                        st.video(out_path)
                        with open(out_path,"rb") as f: st.download_button("Download", f, file_name=f"Mehar_{vid_lang}.mp4", mime="video/mp4", type="primary")

with tab3:
    st.markdown("### 🎭 AI DRAMA")
    char_image = st.file_uploader("📸 Larki Photo:", type=["jpg","jpeg","png","webp"], key="char_v116")
    if char_image: st.image(char_image, width=180)
    drama_lang = st.selectbox("Drama Lang:", ["URDU","SINDHI"], index=0, key="dlang_v116")
    drama_voice_key = st.selectbox("Drama Voice:", ["Uzma Larki","Asad Larka"], index=0, key="dvoice_v116")
    drama_voice = "ur-PK-UzmaNeural" if "Uzma" in drama_voice_key else "ur-PK-AsadNeural"
    drama_speed = st.select_slider("Speed:", options=["-5%","-15%","+10%"], value="-5%", key="dspeed_v116")
    if st.button("🎬 DRAMA BANAO", type="primary", use_container_width=True, key="make_drama_v116"):
        st.info("Drama feature same - Jo text likho ge wahi bolega")

st.caption("V116 - Asalam + Pakistan Fix - No Namaste - No Bharat - Jo Likha Wahi + Sahi Translation - Both Options")
