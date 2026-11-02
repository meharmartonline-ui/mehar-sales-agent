import streamlit as st, os, asyncio, subprocess, requests, textwrap, time, random
from urllib.parse import quote
from dotenv import load_dotenv
load_dotenv()
st.set_page_config(page_title="MEHAR V115 - ASALAM FIX", layout="centered")

from PIL import Image
if not hasattr(Image, 'ANTIALIAS'): Image.ANTIALIAS = Image.LANCZOS
import edge_tts

st.title("MEHAR V115 - JO LIKHA WAHI BOLEGA ✅")

TIME_OPTIONS = {"10 Second":10,"15 Second":15,"30 Second":30,"60 Second (1 Min)":60,"2 Minutes":120}

# V115 - Har Language me Asad Uzma option - Taake Asalam saaf bole
VOICES = {
    "SINDHI": {"Asad Larka": "ur-PK-AsadNeural", "Uzma Larki": "ur-PK-UzmaNeural"},
    "URDU": {"Asad Larka": "ur-PK-AsadNeural", "Uzma Larki": "ur-PK-UzmaNeural"},
    "HINDI": {"Uzma Larki (Asalam ke liye Best)": "ur-PK-UzmaNeural", "Asad Larka (Asalam Best)": "ur-PK-AsadNeural", "Madhur Larka (Hindi)": "hi-IN-MadhurNeural", "Swara Larki (Hindi)": "hi-IN-SwaraNeural"},
    "ENGLISH": {"Jenny Larki": "en-US-JennyNeural", "Guy Larka": "en-US-GuyNeural", "Uzma Larki": "ur-PK-UzmaNeural", "Asad Larka": "ur-PK-AsadNeural"},
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

# V115 - JO LIKHA WAHI - KOI NAMASTE / HELLO / EXTRA NAHI
def translate_fix(text, target):
    if not text.strip():
        return ""
    # Jo MASTER me likha hai wahi - Koi extra Namaste / Hello / Bharat / Pakistan nahi jodega
    return text.strip()

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

tab1, tab2, tab3 = st.tabs(["✅ VOICE - JO LIKHA WAHI", "🎬 VIDEO + CAPTION", "🎭 AI DRAMA"])

with tab1:
    st.markdown("### ✅ V115 - Jo Likha Wahi Bolega - Namaste Bug Fixed")
    st.success("Ab koi extra `Namaste / Hello / Bharat / Pakistan` nahi - Jo MASTER me likho ge wahi har box me jayega - Jo box me likha hoga wahi voice banegi!")
    st.markdown("**Tariqa: MASTER me `Asalam O Alaikum` likho - ALL 5 BOX dabao - Phir HINDI box me Voice `Uzma Larki (Asalam ke liye Best)` select karo - Wo Asalam saaf bolegi - Madhur Hindi voice Asalam saaf nahi bolta!**")
    
    master_input = st.text_area("MASTER:", height=130, key="master_v115", placeholder="Yahan likho: Asalam O Alaikum! Mehar Mart ka khalis shahad - Pore Pakistan me free delivery!")

    if st.button("ALL 5 BOX - Jo Likha Wahi Copy - No Extra", type="primary", use_container_width=True, key="btn_all_v115"):
        src = st.session_state.get("master_v115","").strip()
        if src:
            for LANG in ["SINDHI","URDU","HINDI","ENGLISH","ARABIC"]:
                st.session_state[f"text_{LANG}"] = src
                st.session_state[f"ta_{LANG}_v115"] = src
            st.success(f"✅ Copy ho gaya! Ab Hindi me bhi `Asalam O Alaikum` hi hai - `Namaste` khatam! Jo likha wahi bolega!")
            time.sleep(0.6)
            st.rerun()
        else:
            st.error("Pehle MASTER me likho!")

    st.divider()
    for LANG in ["SINDHI","URDU","HINDI","ENGLISH","ARABIC"]:
        with st.expander(f"{LANG}", expanded=(LANG in ["SINDHI","URDU","HINDI"])):
            c1,c2 = st.columns(2)
            with c1:
                time_sel = st.selectbox("⏱️ Time:", list(TIME_OPTIONS.keys()), index=2, key=f"ts_{LANG}_v115")
            with c2:
                vkey = st.selectbox("🎤 Voice:", list(VOICES[LANG].keys()), index=0, key=f"v_{LANG}_v115")
                vname = VOICES[LANG][vkey]
            
            default_val = st.session_state.get(f"text_{LANG}", "")
            txt = st.text_area(f"✍️ {LANG} - Jo yahan likha hoga wahi bolega (Extra nahi):", height=150, key=f"ta_{LANG}_v115", value=default_val)
            rate = st.select_slider("Speed:", options=["-5%","-15%","+10%"], value="-5%", key=f"sp_{LANG}_v115")
            
            if st.button(f"🎙️ Voice {vkey} - {LANG}", key=f"gen_{LANG}_v115", type="primary", use_container_width=True):
                if txt.strip():
                    os.makedirs("voice", exist_ok=True)
                    fp = f"voice/{LANG}_v115.mp3"
                    with st.spinner(f"{LANG} {vkey} - Jo likha wahi bol raha..."):
                        ok = asyncio.run(gen_edge(clean_for_voice(txt, LANG), vname, rate, fp))
                        if ok:
                            st.audio(fp)
                            st.success(f"✅ {LANG} - {vkey} Ready! - Jo likha tha wahi bola!")
                            with open(fp,"rb") as f:
                                st.download_button(f"📥 Download {LANG} {vkey}", f, file_name=f"{LANG}_{vkey}.mp3", mime="audio/mp3", key=f"dl_{LANG}_v115")
                        else: st.error("Voice Fail")
                else: st.warning("Text likho!")

with tab2:
    st.markdown("### 🎬 Video - Jo Likha Wahi Voice + Wahi Caption")
    prod_image = st.file_uploader("📸 Image:", type=["jpg","jpeg","png","webp"], key="prod_v115")
    if prod_image: st.image(prod_image, width=220)
    has_ff = check_ffmpeg()
    if has_ff: st.success("✅ ffmpeg OK")
    col1,col2 = st.columns(2)
    with col1:
        vid_lang = st.selectbox("Lang:", ["URDU","SINDHI","HINDI","ENGLISH"], index=0, key="vlang_v115")
        vid_voice_key = st.selectbox("Voice:", ["Uzma Larki (Asalam Best)","Asad Larka"], index=0, key="vid_voice_v115")
        vid_voice = "ur-PK-UzmaNeural" if "Uzma" in vid_voice_key else "ur-PK-AsadNeural"
    with col2:
        show_caption = st.checkbox("📝 Caption - Jo Likha Wahi", value=True, key="cap_v115")
    default_vid_text = st.session_state.get(f"text_{vid_lang}", "") or "Asalam O Alaikum! Mehar Mart khalis shahad!"
    vid_text = st.text_area(f"Text - Yahi bolega - Namaste nahi bolega:", value=default_vid_text[:220], height=110, key="vid_text_v115")
    vid_speed = st.select_slider("Speed:", options=["-5%","-15%","+10%"], value="-5%", key="vid_speed_v115")
    if st.button("🎬 VIDEO BANAO - JO LIKHA WAHI", type="primary", use_container_width=True, key="make_vid_v115"):
        if not prod_image: st.error("Image Upload!")
        else:
            with st.spinner("Video Ban Raha - Jo likha wahi..."):
                os.makedirs("video", exist_ok=True)
                from PIL import Image as PILImage
                img = PILImage.open(prod_image).convert("RGB").resize((1080,1920))
                img_path = f"video/input_{vid_lang}_v115.jpg"
                img.save(img_path)
                voice_path = f"video/voice_{vid_lang}_v115.mp3"
                ok_voice = asyncio.run(gen_edge(clean_for_voice(vid_text, vid_lang), vid_voice, vid_speed, voice_path))
                if ok_voice:
                    out_path = f"video/MEHAR_{vid_lang}_V115.mp4"
                    if make_scene_clip(img_path, voice_path, out_path, vid_text if show_caption else ""):
                        st.video(out_path)
                        with open(out_path,"rb") as f: st.download_button("Download Video", f, file_name=f"Mehar_{vid_lang}.mp4", mime="video/mp4", type="primary")

with tab3:
    st.markdown("### 🎭 AI DRAMA")
    char_image = st.file_uploader("📸 Larki Photo:", type=["jpg","jpeg","png","webp"], key="char_v115")
    if char_image: st.image(char_image, width=180)
    drama_lang = st.selectbox("Drama Lang:", ["URDU","SINDHI"], index=0, key="dlang_v115")
    drama_voice_key = st.selectbox("Drama Voice:", ["Uzma Larki","Asad Larka"], index=0, key="dvoice_v115")
    drama_voice = "ur-PK-UzmaNeural" if "Uzma" in drama_voice_key else "ur-PK-AsadNeural"
    drama_speed = st.select_slider("Speed:", options=["-5%","-15%","+10%"], value="-5%", key="dspeed_v115")
    drama_caption = st.checkbox("Caption", value=True, key="dcap_v115")
    scenes_text = []
    for i in range(3):
        st.markdown(f"**Scene {i+1}:**")
        p = st.text_input(f"Scene {i+1} Prompt:", value=f"Same girl holding honey jar happy {i+1}", key=f"sprompt_{i}_v115")
        t = st.text_input(f"Scene {i+1} Voice - Jo likha wahi bolegi:", value="Asalam O Alaikum! Mehar Mart khalis shahad - Pore Pakistan me free delivery" if i==0 else f"Order karen {i+1}", key=f"stext_{i}_v115")
        scenes_text.append({"prompt": p, "text_urdu": t})
    if st.button("🎬 DRAMA BANAO", type="primary", use_container_width=True, key="make_drama_v115"):
        os.makedirs("video/drama", exist_ok=True)
        clip_paths=[]
        seed_base=random.randint(1,99999)
        prog=st.progress(0)
        for idx, scene in enumerate(scenes_text):
            prog.progress(int((idx/len(scenes_text))*100))
            img_path = f"video/drama/scene_{idx+1}_v115.jpg"
            ok_img = generate_ai_scene(scene['prompt'], img_path, seed_base+idx)
            if not ok_img and char_image:
                from PIL import Image as PILImage
                im = PILImage.open(char_image).convert("RGB").resize((1080,1920))
                im.save(img_path)
            voice_path = f"video/drama/scene_{idx+1}_v115.mp3"
            ok_voice = asyncio.run(gen_edge(clean_for_voice(scene['text_urdu'], drama_lang), drama_voice, drama_speed, voice_path))
            if ok_voice:
                clip_path = f"video/drama/clip_{idx+1}_v115.mp4"
                if make_scene_clip(img_path, voice_path, clip_path, scene['text_urdu'] if drama_caption else ""):
                    clip_paths.append(clip_path)
        prog.progress(100)
        if clip_paths:
            final = "video/drama/FINAL_DRAMA_V115.mp4"
            if concat_videos(clip_paths, final):
                st.video(final)
                with open(final,"rb") as f: st.download_button("DOWNLOAD DRAMA", f, file_name="Mehar_Drama_V115.mp4", mime="video/mp4", type="primary")

st.caption("V115 - Asalam O Alaikum Fix - Namaste Bug Fixed - Jo Likha Wahi Bolega - Extra Kuch Nahi")
