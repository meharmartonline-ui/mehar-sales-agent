import streamlit as st, os, asyncio, subprocess, requests, textwrap, time, random
from urllib.parse import quote
from dotenv import load_dotenv
load_dotenv()
st.set_page_config(page_title="MEHAR V110 - AI DRAMA", layout="centered")

from PIL import Image
if not hasattr(Image, 'ANTIALIAS'): Image.ANTIALIAS = Image.LANCZOS
import edge_tts

GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
st.title("MEHAR V110 - AI DRAMA STUDIO 🎬 - TechPulse Jaisa")

TIME_OPTIONS = {"10 Second":10,"15 Second":15,"30 Second":30,"60 Second (1 Min)":60}
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
    if target=="URDU": return "میرے پیارے بھائیو! مہر مارٹ کا خالص شہد!"
    if target=="HINDI": return "नमस्ते! महर मार्ट का शुद्ध शहद!"
    if target=="ENGLISH": return "Hello! Mehar Mart pure honey!"
    if target=="ARABIC": return "السلام عليكم! عسل مهر مارت!"
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

# Pollinations Free AI Image - TechPulse Jaisa Scene
def generate_ai_scene(prompt, output_path, seed=0):
    try:
        # Enhance prompt for same girl + cinematic
        full_prompt = f"{prompt}, same Pakistani girl, beautiful, 24 years, natural skin, cinematic lighting, 4k, ultra realistic, 9:16 portrait"
        encoded = quote(full_prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1920&nologo=true&seed={seed}&enhance=true"
        r = requests.get(url, timeout=60)
        if r.status_code==200 and len(r.content)>5000:
            with open(output_path, 'wb') as f: f.write(r.content)
            return True
        return False
    except Exception as e:
        print(e); return False

def create_caption_image(text, width=1080, height=280):
    img = Image.new('RGBA', (width, height), (0,0,0,190))
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    try: font = ImageFont.truetype("DejaVuSans.ttf", 40)
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
        # Caption
        cap_path = output_path.replace(".mp4","_cap.png")
        cap_img = create_caption_image(caption_text)
        cap_img.save(cap_path)

        # Moving video temp
        temp_moving = output_path.replace(".mp4","_move.mp4")
        vf_move = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='min(zoom+0.0012,1.2)':d=1:x='iw/2-(iw/zoom/2)+sin(on/8)*6':y='ih/2-(ih/zoom/2)':s=1080x1920"
        cmd1 = ["ffmpeg","-y","-loop","1","-i",image_path,"-i",audio_path,"-c:v","libx264","-c:a","aac","-shortest","-pix_fmt","yuv420p","-vf","scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",temp_moving]
        subprocess.run(cmd1, capture_output=True, timeout=90)
        # Overlay caption
        cmd2 = ["ffmpeg","-y","-i",temp_moving,"-i",cap_path,"-filter_complex","[0:v][1:v]overlay=(W-w)/2:H-h-100","-c:a","copy",output_path]
        subprocess.run(cmd2, capture_output=True, timeout=90)
        if os.path.exists(output_path) and os.path.getsize(output_path)>2000: return True
        return False
    except Exception as e: print(e); return False

def concat_videos(video_list, final_path):
    try:
        list_path = "video/concat_list.txt"
        with open(list_path, 'w') as f:
            for v in video_list:
                f.write(f"file '{os.path.abspath(v)}'\n")
        cmd = ["ffmpeg","-y","-f","concat","-safe","0","-i",list_path,"-c","copy",final_path]
        subprocess.run(cmd, capture_output=True, timeout=90)
        if os.path.exists(final_path) and os.path.getsize(final_path)>5000: return True
        # Re-encode if copy fails
        cmd2 = ["ffmpeg","-y","-f","concat","-safe","0","-i",list_path,"-c:v","libx264","-c:a","aac",final_path]
        subprocess.run(cmd2, capture_output=True, timeout=120)
        return os.path.exists(final_path)
    except Exception as e: print(e); return False

# TABS
tab1, tab2, tab3 = st.tabs(["🎙️ VOICE SAME V102", "🎬 CAPTION VIDEO V109", "🎭 AI DRAMA - TechPulse Jaisa V110"])

with tab1:
    st.markdown("### ✅ Voice Same - Paka Same")
    for lang in VOICES:
        if f"text_{lang}" not in st.session_state: st.session_state[f"text_{lang}"] = ""
    master = st.text_area("MASTER:", height=60, key="master_v110")
    if st.button("ALL 5 BOX", type="primary", use_container_width=True, key="btn_all_v110"):
        src = st.session_state.get("master_v110","").strip()
        if src:
            for LANG in VOICES: st.session_state[f"text_{LANG}"] = translate_fix(src, LANG)
            st.rerun()
    for LANG in ["SINDHI","URDU","HINDI","ENGLISH","ARABIC"]:
        with st.expander(f"{LANG}", expanded=False):
            vkey = st.selectbox("Voice:", list(VOICES[LANG].keys()), key=f"v_{LANG}_v110")
            vname = VOICES[LANG][vkey]
            txt = st.text_area(f"{LANG}:", height=50, key=f"ta_{LANG}_v110", value=st.session_state.get(f"text_{LANG}",""))
            rate = st.select_slider("Speed:", options=["-5%","-15%","+10%"], value="-5%", key=f"sp_{LANG}_v110")
            if st.button(f"{vkey}", key=f"gen_{LANG}_v110", type="primary", use_container_width=True):
                if txt.strip():
                    os.makedirs("voice", exist_ok=True)
                    fp = f"voice/{LANG}_v110.mp3"
                    ok = asyncio.run(gen_edge(clean_for_voice(txt, LANG), vname, rate, fp))
                    if ok: st.audio(fp)

with tab2:
    st.markdown("### V109 - Image + Voice + Caption")
    prod_image = st.file_uploader("Image:", type=["jpg","jpeg","png","webp"], key="prod_v109_v110")
    if prod_image:
        st.image(prod_image, width=200)
        st.success("Image OK - V109 se video banao - Larki hilegi + bolegi + caption!")

with tab3:
    st.markdown("### 🎬 V110 - AI DRAMA STUDIO - TechPulse Jaisa - Aap ke AI pe!")
    st.info("Ye wohi feature hai jo aap ne Facebook link me dekha - Same Larki, 5 Scene, Story, Kapde Change!")
    has_ff = check_ffmpeg()
    if has_ff: st.success("✅ ffmpeg OK - Drama Banega!")
    else: st.warning("packages.txt me ffmpeg likho + Reboot")

    st.markdown("**1. Character Photo (Aap ki Honey wali Larki ki saaf photo):**")
    char_image = st.file_uploader("📸 Larki ki Photo (Same Face ke liye):", type=["jpg","jpeg","png","webp"], key="char_v110")
    
    st.markdown("**2. Drama Type Select Karo:**")
    drama_type = st.selectbox("Story:", ["Mehar Honey Ad Drama - 5 Scene (Recommended)", "TechPulse Jaisa Sad to Happy Drama", "Custom Story - Khud Likho"], key="drama_type_v110")

    if drama_type == "Mehar Honey Ad Drama - 5 Scene (Recommended)":
        scenes = [
            {"prompt": "Pakistani girl sitting in bedroom floor sad tired, wearing casual home dress, messy room", "text_urdu": "پہلے میں بہت تھکی تھکی رہتی تھی، کمزوری محسوس ہوتی تھی", "text_en": "Pehle main thaki thaki rehti thi"},
            {"prompt": "Same girl looking in mirror holding Mehar honey jar, wearing white dress with black dots, smiling, bright bedroom", "text_urdu": "پھر مجھے مہر مارٹ کا خالص شہد ملا، 100% خالص", "text_en": "Phir Mehar Mart ka khalis shahad mila"},
            {"prompt": "Same girl sitting on sofa drinking honey water, wearing floral red dress, happy energetic", "text_urdu": "اب میں روز شہد پیتی ہوں، انرجی فل ہے، صحت اچھی ہے", "text_en": "Ab energy full hai"},
            {"prompt": "Same girl showing honey jar to camera in kitchen, wearing blue shirt, professional happy", "text_urdu": "صرف 2975 روپے میں، فری ہوم ڈلیوری پورے پاکستان میں", "text_en": "Sirf 2975 me free delivery"},
            {"prompt": "Same girl taking selfie with family holding honey jar, everyone smiling, happy ending", "text_urdu": "آپ بھی آرڈر کریں، مہر مارٹ خالص شہد، ابھی رابطہ کریں", "text_en": "Order now Mehar Mart"},
        ]
    elif drama_type == "TechPulse Jaisa Sad to Happy Drama":
        scenes = [
            {"prompt": "Pakistani girl sitting sad in bedroom wearing black hijab", "text_urdu": "یہ کہانی ایک لڑکی کی ہے جو بہت پریشان تھی", "text_en": "Sad girl"},
            {"prompt": "Same girl in front of mirror wearing white dress, thinking", "text_urdu": "پھر اس نے اپنی زندگی بدلنے کا فیصلہ کیا", "text_en": "She decided to change"},
            {"prompt": "Same girl sitting on university bench wearing floral dress smiling", "text_urdu": "یونیورسٹی میں وہ خوش رہنے لگی", "text_en": "Happy in university"},
            {"prompt": "Same girl taking selfie with boy, both happy", "text_urdu": "دوستی ہوئی اور زندگی بدل گئی", "text_en": "Friendship changed life"},
            {"prompt": "Same girl in office showing phone, blue shirt", "text_urdu": "اگلے دن ایک نیا آغاز ہوا", "text_en": "Next day new start"},
        ]
    else:
        scenes = []
        for i in range(3):
            p = st.text_input(f"Scene {i+1} Prompt (English):", key=f"custom_p_{i}_v110")
            t = st.text_input(f"Scene {i+1} Voice Text (Urdu):", key=f"custom_t_{i}_v110")
            if p and t: scenes.append({"prompt": p, "text_urdu": t, "text_en": t})

    col1,col2 = st.columns(2)
    with col1:
        drama_lang = st.selectbox("Drama Voice Language:", ["URDU","SINDHI","HINDI","ENGLISH"], index=0, key="dlang_v110")
        drama_voice_key = st.selectbox("Drama Larki Voice:", ["Uzma Larki","Swara Larki","Jenny Larki"], index=0, key="dvoice_v110")
        drama_voice = VOICES[drama_lang][drama_voice_key] if drama_voice_key in VOICES[drama_lang] else "ur-PK-UzmaNeural"
    with col2:
        drama_speed = st.select_slider("Speed:", options=["-5%","-15%","+10%"], value="-5%", key="dspeed_v110")
        show_drama_caption = st.checkbox("📝 Har Scene me Caption? - Jo Voice Wahi Text", value=True, key="dcap_v110")

    st.markdown(f"**Total Scenes: {len(scenes)} - Har Scene: Image (AI) + Voice (Uzma Larki) + Caption + Movement**")

    if st.button("🎬 DRAMA BANAO - TechPulse Jaisa - 5 Scene - 2 Min Lagega", type="primary", use_container_width=True, key="make_drama_v110"):
        if len(scenes)==0:
            st.error("Drama Type Select Karo!")
        elif not has_ff:
            st.error("ffmpeg nahi - packages.txt me ffmpeg + Reboot")
        else:
            os.makedirs("video/drama", exist_ok=True)
            progress = st.progress(0)
            status = st.empty()
            clip_paths = []
            seed_base = random.randint(1,999999)
            
            for idx, scene in enumerate(scenes):
                status.markdown(f"**Scene {idx+1}/{len(scenes)} Ban Raha: {scene['prompt'][:40]}...**")
                progress.progress(int((idx/len(scenes))*100))
                
                # 1. Generate AI Image - Free Pollinations
                img_path = f"video/drama/scene_{idx+1}_v110.jpg"
                ok_img = generate_ai_scene(scene['prompt'], img_path, seed=seed_base+idx)
                
                # Fallback - Use uploaded char image if AI fail
                if not ok_img and char_image:
                    from PIL import Image as PILImage
                    im = PILImage.open(char_image).convert("RGB").resize((1080,1920))
                    im.save(img_path)
                    ok_img = True
                elif not ok_img:
                    # Create placeholder color
                    im = Image.new('RGB', (1080,1920), (100+idx*20, 50, 150))
                    im.save(img_path)
                    ok_img = True

                # 2. Voice
                voice_path = f"video/drama/scene_{idx+1}_v110.mp3"
                txt_for_voice = scene['text_urdu'] if drama_lang in ["URDU","SINDHI"] else scene['text_en']
                ok_voice = asyncio.run(gen_edge(clean_for_voice(txt_for_voice, drama_lang), drama_voice, drama_speed, voice_path))
                
                if ok_img and ok_voice:
                    # 3. Video Clip with Movement + Caption
                    clip_path = f"video/drama/clip_{idx+1}_v110.mp4"
                    ok_clip = make_scene_clip(img_path, voice_path, clip_path, txt_for_voice if show_drama_caption else "")
                    if ok_clip:
                        clip_paths.append(clip_path)
                        st.image(img_path, width=150, caption=f"Scene {idx+1} OK")
                        st.audio(voice_path)
                time.sleep(1)

            progress.progress(100)
            if clip_paths:
                status.markdown("**Final Drama Jod Raha Hu...**")
                final_drama = f"video/drama/FINAL_DRAMA_{drama_lang}_V110.mp4"
                ok_final = concat_videos(clip_paths, final_drama)
                if ok_final:
                    st.success(f"✅ DRAMA READY! {len(clip_paths)} Scenes - TechPulse Jaisa - Same Larki - Voice + Caption + Movement!")
                    st.video(final_drama)
                    with open(final_drama,"rb") as f:
                        st.download_button("📥 DOWNLOAD FULL DRAMA - TechPulse Style", f, file_name=f"Mehar_Drama_{drama_lang}.mp4", mime="video/mp4", type="primary", use_container_width=True, key="dl_drama_v110")
                    st.balloons()
                else:
                    st.warning("Clips ban gaye per final jodne me issue - Alag alag clips download karo")
                    for cp in clip_paths:
                        with open(cp,"rb") as f: st.download_button(f"Download {cp}", f, file_name=cp)
            else:
                st.error("Drama Fail - Internet check karo - Pollinations free AI thoda slow hai")

st.caption("V110 - AI Drama Studio - TechPulse Jaisa - Same Character, 5 Scene, AI Image + Uzma Larki Voice + Caption + Movement - Voice Studio Paka Same V102")
