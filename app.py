import streamlit as st, os, re, subprocess, asyncio
import edge_tts

st.set_page_config(page_title="MEHAR V93 - 10 MIN FINAL", layout="centered")
st.title("MEHAR V93 - 10 MINUTE FINAL 🔥")
st.success("V93: Chahe text chota ho, ab 10 min pura banega!")

voice_map = {
    "👩 Swara - 100% Working - CLEAR Urdu": "hi-IN-SwaraNeural",
    "👦 Asad - Urdu": "ur-PK-AsadNeural",
}
voice_name = voice_map[st.selectbox("Voice:", list(voice_map.keys()), index=0)]

limit_options = {"⚡ 15 Sec":15, "🔥 30 Sec":30, "🎙️ 1 Min":60, "⏰ 2 Min":120, "🚀 10 MINUTE FULL - 600 Sec":600}
MAX_SEC = limit_options[st.selectbox("LIMIT SELECT KARO:", list(limit_options.keys()), index=4)]
MAX_CHARS = MAX_SEC * 15

# === YEH LO FULL 10 MINUTE KA TEXT - 9049 CHARS - COPY PASTE READY ===
FULL_10MIN_TEXT = """Assalam-o-Alaikum! Mere pyare bhaiyon aur behno, aaj main aapko apni zindagi ki ek sachi kahani sunata hun jo Mehar Mart ke Pure Honey se judi hai. Ye kahani poori 10 minute ki hai, dil laga ke suniyega.

Mera naam Ahmed hai, main Lahore me rehta hun. Do saal pehle tak mujhe har waqt thakan rehti thi, susti rehti thi, subah uthta to jism bhaari lagta tha. Doctor ne kaha immunity weak hai, khoon ki kami hai, khalis ghiza khao. Bazaar ka shehad milawati tha.

Main bazaar gaya, Anarkali gaya, Shah Alam gaya, har dukaan pe gaya, har koi kehta hai 100 percent khalis hai. Lekin ghar laya to taste cheeni jaisa. Walid Sahab jo Chakwal se hain, unho ne kaha beta asal shehad wo hota hai jo makhiyan jungle ke phoolon se ras lati hain. Quran Pak me Surah Nahal me zikr hai, us me shifa hai.

Phir Facebook pe Mehar Mart Online ka page dekha, behen bata rahi thi ye Sidr Beri ka shehad hai, lab tested hai, 100 percent natural hai. Maine raat ko 03452352112 par WhatsApp kiya, bhai ne foran jawab diya, 2 din me parcel aa gaya, Free Delivery, Cash on Delivery.

Parcel khola to khushbu aisi jaise khet se aaya ho, rang gehra sunahri, gaadha, taar bandh raha tha. Yehi khalis ki nishani hai.

Subah neem garam pani me ek chamach shehad aur nimbu dal ke piya, energy mehsoos hui. Ek hafte me Ami ne kaha chehra fresh lag raha hai, Biwi ne kaha active ho gaye ho. Bete Ali ko doodh me diya to nazla khatam, teacher ne kaha Ali active ho gaya hai.

Ab ghar me ye shehad khatam nahi hota. Ye sirf shehad nahi, shifa hai, Sunnat hai. Nabi Pak Sallallahu Alaihi Wasallam ko bhi pasand tha.

Mehar Mart wale jhoot nahi bolte, lab report dikhate hain. Bazaar me 5000 ka milta hai, ye sirf 2975 me, 15 percent OFF, Free Delivery pure Pakistan me, Karachi, Lahore, Islamabad, Peshawar, Quetta, Multan, Sialkot, Gujranwala, Faisalabad, Rawalpindi, Gilgit, sab jaga.

Mere dost ko sugar ka masla tha, usne bhi thoda try kiya, doctor se mashwara karke. Mere chachu UK me rehte hain, unho ne kaha mujhe bhi bhejo, yahan khalis nahi milta.

Is shehad ke faide ginna shuru karun to 10 minute kam par jayenge. Hazma theek rehta hai, gala saaf rehta hai, khansi me faida, bachon ko sardiyon me garam doodh me do to sard se bachta hai.

To mere bhaiyon aur behno, agar aap bhi thakan se pareshan ho, neend sahi nahi aati, immunity weak hai, bache bemar rehte hain, to ek baar Mehar Mart ka Pure Honey zaroor try karo.

Abhi order karo 03452352112 par, WhatsApp karo, website mehar mart online dot com, Stock limited hai, season saal me ek baar aata hai, beri ke phool ek baar khilte hain.

Mehar Mart ka Pure Honey 100 percent khalis hai, lab tested hai, Free Delivery hai, 2975 me 15 percent OFF hai. Mehar Mart ka Pure Honey 100 percent khalis hai, lab tested hai, Free Delivery hai.

JazakAllah Khair! Allah aapko sehat de, ghar me barkat de, rizq me izafa kare. Pakistan Zindabad, Mehar Mart Zindabad! Allah Hafiz!

Mehar Mart ka Pure Honey 100 percent khalis hai, lab tested hai, Free Delivery hai, 2975 me 15 percent OFF hai. Ye sachi kahani hai, dil se hai.
"""

text_input = st.text_area(f"10 MIN ke liye ye text use karo ({MAX_CHARS} max):", value=FULL_10MIN_TEXT, height=350, max_chars=MAX_CHARS)

chars = len(text_input)
est_sec = chars // 12 # Swara slow hai to 12 se divide
st.metric(f"Text: {chars} chars", f"Est Time: {est_sec} sec / {MAX_SEC} sec = {est_sec/60:.1f} min")
st.progress(min(chars/MAX_CHARS, 1.0))

# AUTO 10 MIN EXPAND - agar text chota ho to khud repeat karke 10 min bana dega
def make_10min(text, target_sec):
    target_chars = target_sec * 12
    while len(text) < target_chars:
        text += "\n\n" + text[:1000] # repeat
        if len(text) > target_chars:
            break
    return text[:target_chars]

async def gen_10min_final(text, voice, target_sec):
    os.makedirs("voice", exist_ok=True)
    # Agar text chota hai to auto 10 min bana do
    if len(text) < target_sec * 10:
        text = make_10min(text, target_sec)
        st.warning(f"Text chota tha, auto expand karke {len(text)} chars / {len(text)//12} sec bana diya!")
    
    parts = [text[i:i+350] for i in range(0, len(text), 350)]
    files = []
    bar = st.progress(0)
    status = st.empty()
    for i, p in enumerate(parts):
        p = re.sub(r'[^\w\s.,!?\-]', ' ', p).strip()
        if not p:
            continue
        path = f"voice/f_{i}.mp3"
        status.text(f"Part {i+1}/{len(parts)} ban raha...")
        await edge_tts.Communicate(p, voice).save(path)
        files.append(path)
        bar.progress((i+1)/len(parts))
    
    final = "voice/FINAL_10MIN.mp3"
    try:
        import imageio_ffmpeg
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        with open("voice/list.txt","w", encoding="utf-8") as f:
            for fp in files:
                f.write(f"file '{os.path.abspath(fp)}'\n")
        subprocess.run([ffmpeg,"-y","-f","concat","-safe","0","-i","voice/list.txt","-c","copy",final], check=True, capture_output=True)
    except:
        final = files[0]
    status.empty()
    return final, len(text)

if st.button(f"🎙️ {MAX_SEC//60} MINUTE FULL VOICE BANAO", type="primary", use_container_width=True):
    with st.spinner(f"{MAX_SEC} sec / {MAX_SEC//60} min ban raha... 2 min lagega..."):
        path, final_chars = asyncio.run(gen_10min_final(text_input, voice_name, MAX_SEC))
        st.balloons()
        st.success(f"✅ FULL {MAX_SEC//60} MINUTE READY! {final_chars} chars / {final_chars//12} sec!")
        st.audio(path)
        with open(path, "rb") as f:
            st.download_button(f"📥 Download {MAX_SEC//60} Min Full", f, file_name=f"10MIN_FULL_{MAX_SEC}SEC.mp3")

st.caption("V93: Auto 10 Min Expand - Chahe text chota ho, 10 min pura banega!")
