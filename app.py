import streamlit as st
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os, math
import numpy as np

st.set_page_config(page_title="MEHAR AD V71 VOICE", layout="centered")
st.title("MEHAR MART - AI Ad Maker V71 🎙️🎬")
st.caption("Image + 15s/20s/30s Video Ad + Voiceover for FB / TikTok / Insta")

def get_font(size):
    try:
        return ImageFont.truetype("arialbd.ttf", size)
    except:
        return ImageFont.load_default()

def generate_image(prompt):
    url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=1080&height=1080&model=flux&nologo=true&enhance=true"
    r = requests.get(url, timeout=90)
    if r.status_code == 200:
        return Image.open(BytesIO(r.content)).convert("RGB")
    return None

def generate_voice(text, lang='ur'):
    try:
        from gtts import gTTS
        os.makedirs("voice", exist_ok=True)
        path = "voice/voiceover.mp3"
        # gTTS - Urdu/Hindi voice
        tts = gTTS(text=text, lang='en', slow=False)  # en best for mixed Urdu
        # Try Urdu if available, else English
        try:
            tts = gTTS(text=text, lang='ur', slow=False)
        except:
            tts = gTTS(text=text, lang='en', slow=False)
        tts.save(path)
        return path
    except Exception as e:
        st.error(f"Voice error: {e}")
        return None

def create_video_ad_with_voice(product_img, product_name, price, offer, duration, format_type, voice_path=None):
    if format_type in ["TikTok 9:16", "Instagram Story 9:16"]:
        W, H = 1080, 1920
    else:
        W, H = 1080, 1080

    fps = 24
    total_frames = duration * fps
    frames = []
    p_size = 700 if W==1080 and H==1080 else 800
    product_img = product_img.resize((p_size, p_size))

    for i in range(total_frames):
        t = i / fps
        frame = Image.new("RGB", (W, H), "white")
        draw = ImageDraw.Draw(frame)
        progress = i / total_frames
        zoom = 1.0 + 0.15 * math.sin(progress * math.pi)
        pw, ph = int(p_size * zoom), int(p_size * zoom)
        p_img_z = product_img.resize((pw, ph))
        x = (W - pw)//2
        y = 150 if W==1080 and H==1080 else 300
        if t > 3:
            y = 100 if W==1080 and H==1080 else 250
        frame.paste(p_img_z, (x, y))

        if t < 3:
            draw.rectangle([0, 0, W, 120], fill="#FF6A00")
            draw.text((W//2, 60), "MEHAR MART", fill="white", font=get_font(60), anchor="mm")
            draw.text((W//2, H-200), product_name[:30], fill="#111", font=get_font(40), anchor="mm")
        elif t < duration-5:
            draw.rectangle([0, 0, W, 120], fill="#FF6A00")
            draw.text((W//2, 60), "MEHAR MART", fill="white", font=get_font(32), anchor="mm")
            if W == 1080 and H == 1920:
                draw.text((W//2, 1250), product_name[:35], fill="#111", font=get_font(42), anchor="mm")
                draw.text((W//2, 1350), f"Rs. {price}", fill="#FF6A00", font=get_font(80), anchor="mm")
                draw.text((W//2, 1450), offer, fill="#0D47A1", font=get_font(36), anchor="mm")
            else:
                draw.text((W//2, 850), product_name[:35], fill="#111", font=get_font(36), anchor="mm")
                draw.text((W//2, 920), f"Rs. {price} | {offer}", fill="#FF6A00", font=get_font(50), anchor="mm")
        else:
            draw.rectangle([0, 0, W, H], fill="#0D47A1")
            draw.text((W//2, H//2 - 200), "ORDER NOW", fill="white", font=get_font(90), anchor="mm")
            draw.text((W//2, H//2 + 20), f"Rs. {price} - {offer}", fill="white", font=get_font(50), anchor="mm")
            draw.text((W//2, H//2 + 150), "03452352112", fill="white", font=get_font(60), anchor="mm")

        frames.append(np.array(frame))

    os.makedirs("ads", exist_ok=True)
    temp_video = f"ads/temp_{duration}s.mp4"
    final_video = f"ads/Mehar_Ad_{duration}s_VOICE_{format_type.replace(' ','_')}.mp4"
    
    import imageio
    imageio.mimsave(temp_video, frames, fps=fps, macro_block_size=1)

    # Add voice if available
    if voice_path and os.path.exists(voice_path):
        try:
            from moviepy.editor import VideoFileClip, AudioFileClip
            video = VideoFileClip(temp_video)
            audio = AudioFileClip(voice_path)
            # Loop or trim audio to video duration
            if audio.duration < video.duration:
                audio = audio.loop(duration=video.duration)
            else:
                audio = audio.subclip(0, video.duration)
            video = video.set_audio(audio)
            video.write_videofile(final_video, codec='libx264', audio_codec='aac', verbose=False, logger=None)
            video.close()
            audio.close()
            return final_video
        except Exception as e:
            st.warning(f"Voice add me error, silent video de raha hun: {e}")
            return temp_video
    else:
        return temp_video

# UI
product_name = st.text_input("Product Name *", value="Pure Beri Flowers Honey 500gm")
price = st.text_input("Price *", value="2975")
offer = st.text_input("Offer *", value="15% OFF - Free Delivery")
prompt_input = st.text_area("AI Image Prompt *", value="Pure Beri Flowers Honey jar 500gm, clear glass jar golden honey, white background, studio lighting, MEHAR MART label")

st.divider()
st.subheader("🎙️ Voiceover Settings")
voice_on = st.checkbox("Voice add karna hai? (Bolega video me)", value=True)
default_voice_text = f"Mehar Mart laya hai {product_name}, 100 percent pure, original beri flowers honey, sirf {price} rupay me, {offer}, abhi order karein, Call ya WhatsApp zero three four five, two three five, two one one two, Free Delivery All Pakistan!"
voice_text = st.text_area("Voice me kya bolega? (Jo likho ge wahi bolega)", value=default_voice_text, height=100)

col1, col2 = st.columns(2)
with col1:
    duration = st.selectbox("Duration *", [15, 20, 30])
with col2:
    format_type = st.selectbox("Format *", ["FB Feed 1:1", "TikTok 9:16", "Instagram Story 9:16"])

if st.button("🚀 IMAGE + VOICE VIDEO AD BANAO"):
    if not prompt_input.strip():
        st.error("Prompt likho Bhai!")
    else:
        with st.spinner("1/3 Image bana raha hai..."):
            img = generate_image(prompt_input)
            if not img:
                st.error("Image fail")
                st.stop()
            st.image(img, use_container_width=True)

        voice_path = None
        if voice_on:
            with st.spinner("2/3 Voice bana raha hai... 🎙️"):
                voice_path = generate_voice(voice_text)
                if voice_path:
                    st.audio(voice_path)
                    st.success("Voice ban gayi!")

        with st.spinner(f"3/3 {duration}s Video + Voice bana raha hai..."):
            video_path = create_video_ad_with_voice(img, product_name, price, offer, duration, format_type, voice_path)
            st.success(f"Ho gaya Bhai! {duration}s Ad with Voice ready!")
            st.video(video_path)
            with open(video_path, "rb") as f:
                st.download_button(f"📥 Download {duration}s Voice Ad", f, file_name=f"Mehar_Voice_Ad_{duration}s.mp4", mime="video/mp4")
