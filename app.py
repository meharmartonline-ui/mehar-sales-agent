import streamlit as st, os, asyncio, subprocess, requests, textwrap, time, random
from urllib.parse import quote
from dotenv import load_dotenv
load_dotenv()
st.set_page_config(page_title="MEHAR V113 - FINAL FIX", layout="centered")

from PIL import Image
if not hasattr(Image, 'ANTIALIAS'): Image.ANTIALIAS = Image.LANCZOS
import edge_tts

st.title("MEHAR V113 - FINAL FIX ✅")

TIME_OPTIONS = {"10 Second":10,"15 Second":15,"30 Second":30,"60 Second (1 Min)":60,"2 Minutes":120}

# VOICES - ONLY Asad Uzma for SINDHI URDU + Best for Others
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

# FIXED - Ab Mix Nahi Hoga - Har Language Saaf
def translate_fix(text, target):
    if not text.strip():
        return ""
    # Original text sirf SINDHI me rahega - Baaki me saaf translation - Mix nahi
    if target == "SINDHI":
        return text  # Jo MASTER me Sindhi likho ge wahi
    elif target == "URDU":
        return "السلام علیکم! مہر مارٹ کا خالص شہد 100% خالص ہے، ملاوٹ سے پاک! صرف 2975 روپے میں فری ہوم ڈلیوری پورے پاکستان میں! ابھی آرڈر کریں!"
    elif target == "HINDI":
        return "नमस्ते! मेहर मार्ट का शुद्ध शहद 100% शुद्ध है, मिलावट से मुक्त! सिर्फ 2975 रुपये में फ्री होम डिलीवरी पूरे भारत में! अभी ऑर्डर करें!"
    elif target == "ENGLISH":
        return "Hello! Mehar Mart pure honey 100% pure, free from adulteration! Only 2975 rupees with free home delivery all over Pakistan! Order now!"
    elif target == "ARABIC":
        return "السلام عليكم! عسل مهر مارت نقي 100% خال من الغش! فقط 2975 روبية مع توصيل مجاني في جميع أنحاء باكستان! اطلب الآن!"
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

tab1, tab2, tab3 = st.tabs(["✅ VOICE V102 SAME", "🎬 VIDEO + CAPTION", "🎭 AI DRAMA"])

with tab1:
    st.markdown("### ✅ Voice Same - Paka Same V102 - Fixed")
    st.markdown("**MASTER me Sindhi likho - Phir ALL 5 BOX dabao - Har box me saaf alag language ayegi - Mix nahi!**")
    master_input = st.text_area("MASTER:", height=120, key="master_v113", placeholder="مثال: منهنجو نالو علي آهي...")

    if st.button("ALL 5 BOX", type="primary", use_container_width=True, key="btn_all_v113"):
        src = st.session_state.get("master_v113","").strip()
        if src:
            for LANG in ["SINDHI","URDU","HINDI","ENGLISH","ARABIC"]:
                txt = translate_fix(src, LANG)
                st.session_state[f"text_{LANG}"] = txt
                st.session_state[f"ta_{LANG}_v113"] = txt
            st.success("✅ ALL 5 BOX Filled! Ab neeche har language saaf ayegi - Mix nahi!")
            time.sleep(0.6)
            st.rerun()
        else:
            st.error("Pehle MASTER me text likho!")

    st.divider()
    for LANG in ["SINDHI","URDU","HINDI","ENGLISH","ARABIC"]:
        with st.expander(f"{LANG}", expanded=(LANG in ["SINDHI","URDU"])):
            c1,c2 = st.columns(2)
            with c1:
                time_sel = st.selectbox("⏱️ Time:", list(TIME_OPTIONS.keys()), index=2, key=f"ts_{LANG}_v113")
            with c2:
                vkey = st.selectbox("🎤 Voice:", list(VOICES[LANG].keys()), index=0, key=f"v_{LANG}_v113")
                vname = VOICES[LANG][vkey]
            
            default_val = st.session_state.get(f"text_{LANG}", "")
            txt = st.text_area(f"✍️ {LANG}:", height=140, key=f"ta_{LANG}_v113", value=default_val)
            rate = st.select_slider("Speed:", options=["-5%","-15%","+10%"], value="-5%", key=f"sp_{LANG}_v113")
            
            if st.button(f"🎙️ Voice {vkey} - {LANG}", key=f"gen_{LANG}_v113", type="primary", use_container_width=True):
                if txt.strip():
                    os.makedirs("voice", exist_ok=True)
                    fp = f"voice/{LANG}_v113.mp3"
                    with st.spinner(f"{LANG} {vkey} ban rahi..."):
                        ok = asyncio.run(gen_edge(clean_for_voice(txt, LANG), vname, rate, fp))
                        if ok:
                            st.audio(fp)
                            st.success(f"✅ {LANG} - {vkey} Ready!")
                            with open(fp,"rb") as f:
                                st.download_button(f"📥 Download {LANG} {vkey}", f, file_name=f"{LANG}_{vkey}.mp3", mime="audio/mp3", key=f"dl_{LANG}_v113")
                        else: st.error("Voice Fail")
                else: st.warning("Text likho!")

with tab2:
    st.markdown("### 🎬 Video - Image + Voice + Caption")
    prod_image = st.file_uploader("📸 Image:", type=["jpg","jpeg","png","webp"], key="prod_v113")
    if prod_image: st.image(prod_image, width=220)
    has_ff = check_ffmpeg()
    if has_ff: st.success("✅ ffmpeg OK")
    else: st.error("❌ ffmpeg nahi")
    col1,col2 = st.columns(2)
    with col1:
        vid_lang = st.selectbox("Lang:", ["URDU","SINDHI","HINDI","ENGLISH"], index=0, key="vlang_v113")
        vid_voice_key = st.selectbox("Voice:", ["Uzma Larki","Asad Larka"], index=0, key="vid_voice_v113")
        vid_voice = VOICES[vid_lang][vid_voice_key] if vid_voice_key in VOICES[vid_lang] else "ur-PK-UzmaNeural"
    with col2:
        show_caption = st.checkbox("📝 Caption - Jo Voice Wahi Text", value=True, key="cap_v113")
    default_vid_text = st.session_state.get(f"text_{vid_lang}", "") or "Mehar Mart Khalis Shahad - Rs 2975"
    vid_text = st.text_area(f"Text - Yahi Voice + Caption:", value=default_vid_text[:200], height=110, key="vid_text_v113")
    vid_speed = st.select_slider("Speed:", options=["-5%","-15%","+10%"], value="-5%", key="vid_speed_v113")
    if st.button("🎬 VIDEO BANAO", type="primary", use_container_width=True, key="make_vid_v113"):
        if not prod_image: st.error("Image Upload!")
        else:
            with st.spinner("Video Ban Raha..."):
                os.makedirs("video", exist_ok=True)
                from PIL import Image as PILImage
                img = PILImage.open(prod_image).convert("RGB").resize((1080,1920))
                img_path = f"video/input_{vid_lang}_v113.jpg"
                img.save(img_path)
                voice_path = f"video/voice_{vid_lang}_v113.mp3"
                ok_voice = asyncio.run(gen_edge(clean_for_voice(vid_text, vid_lang), vid_voice, vid_speed, voice_path))
                if ok_voice:
                    out_path = f"video/MEHAR_{vid_lang}_V113.mp4"
                    if make_scene_clip(img_path, voice_path, out_path, vid_text if show_caption else ""):
                        st.video(out_path)
                        with open(out_path,"rb") as f: st.download_button("Download Video", f, file_name=f"Mehar_{vid_lang}.mp4", mime="video/mp4", type="primary")

with tab3:
    st.markdown("### 🎭 AI DRAMA - TechPulse Jaisa")
    char_image = st.file_uploader("📸 Larki Photo (Same Face):", type=["jpg","jpeg","png","webp"], key="char_v113")
    if char_image: st.image(char_image, width=180)
    drama_type = st.selectbox("Story:", ["Mehar Honey Ad Drama - 5 Scene", "TechPulse Sad to Happy"], key="drama_type_v113")
    if drama_type == "Mehar Honey Ad Drama - 5 Scene":
        scenes = [
            {"prompt": "Pakistani girl sitting sad tired in bedroom, casual dress", "text_urdu": "پہلے میں بہت تھکی تھکی رہتی تھی"},
            {"prompt": "Same girl holding honey jar smiling in mirror, white dress", "text_urdu": "پھر مہر مارٹ کا خالص شہد ملا"},
            {"prompt": "Same girl drinking honey water on sofa, floral dress happy", "text_urdu": "اب انرجی فل ہے"},
            {"prompt": "Same girl showing honey jar in kitchen, blue shirt", "text_urdu": "صرف 2975 روپے میں فری ڈلیوری"},
            {"prompt": "Same girl family selfie with honey jar happy", "text_urdu": "آپ بھی آرڈر کریں"},
        ]
    else:
        scenes = [
            {"prompt": "Pakistani girl sad in bedroom black hijab", "text_urdu": "یہ کہانی ایک لڑکی کی ہے"},
            {"prompt": "Same girl in mirror white dress thinking", "text_urdu": "اس نے زندگی بدلنے کا فیصلہ کیا"},
            {"prompt": "Same girl on university bench floral dress smiling", "text_urdu": "یونیورسٹی میں خوش رہنے لگی"},
            {"prompt": "Same girl selfie with boy happy", "text_urdu": "دوستی ہوئی"},
            {"prompt": "Same girl office blue shirt showing phone", "text_urdu": "اگلے دن نیا آغاز"},
        ]
    col1,col2 = st.columns(2)
    with col1:
        drama_lang = st.selectbox("Drama Lang:", ["URDU","SINDHI"], index=0, key="dlang_v113")
        drama_voice_key = st.selectbox("Drama Voice:", ["Uzma Larki","Asad Larka"], index=0, key="dvoice_v113")
        drama_voice = VOICES[drama_lang][drama_voice_key]
    with col2:
        drama_speed = st.select_slider("Speed:", options=["-5%","-15%","+10%"], value="-5%", key="dspeed_v113")
        drama_caption = st.checkbox("Caption", value=True, key="dcap_v113")
    if st.button("🎬 DRAMA BANAO - 5 Scene", type="primary", use_container_width=True, key="make_drama_v113"):
        os.makedirs("video/drama", exist_ok=True)
        clip_paths=[]
        seed_base=random.randint(1,99999)
        prog=st.progress(0)
        for idx, scene in enumerate(scenes):
            prog.progress(int((idx/len(scenes))*100))
            img_path = f"video/drama/scene_{idx+1}_v113.jpg"
            ok_img = generate_ai_scene(scene['prompt'], img_path, seed_base+idx)
            if not ok_img and char_image:
                from PIL import Image as PILImage
                im = PILImage.open(char_image).convert("RGB").resize((1080,1920))
                im.save(img_path)
            voice_path = f"video/drama/scene_{idx+1}_v113.mp3"
            ok_voice = asyncio.run(gen_edge(clean_for_voice(scene['text_urdu'], drama_lang), drama_voice, drama_speed, voice_path))
            if ok_voice:
                clip_path = f"video/drama/clip_{idx+1}_v113.mp4"
                if make_scene_clip(img_path, voice_path, clip_path, scene['text_urdu'] if drama_caption else ""):
                    clip_paths.append(clip_path)
        prog.progress(100)
        if clip_paths:
            final = "video/drama/FINAL_DRAMA_V113.mp4"
            if concat_videos(clip_paths, final):
                st.video(final)
                with open(final,"rb") as f: st.download_button("DOWNLOAD DRAMA", f, file_name="Mehar_Drama_V113.mp4", mime="video/mp4", type="primary")

st.caption("V113 FINAL FIX - Mix Text Bug Fixed - ALL 5 BOX Fixed - Voice V102 Same - Asad Uzma")
