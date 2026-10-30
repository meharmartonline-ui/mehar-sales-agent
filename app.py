import streamlit as st
import requests
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="MEHAR IMAGE AGENT", layout="centered")
st.title("MEHAR - AI Image Agent")

prompt = st.text_input("Jo banana hai likho:")

if st.button("Generate"):
    if prompt.strip() == "":
        st.error("Likho to sahi Bhai")
    else:
        with st.spinner("Bana raha hai..."):
            url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=1024&height=1024&nologo=true&enhance=false"
            r = requests.get(url, timeout=60)
            if r.status_code == 200:
                img = Image.open(BytesIO(r.content))
                st.image(img, use_container_width=True)
                st.download_button("Download", r.content, file_name="image.png", mime="image/png")
            else:
                st.error("Fail ho gaya, dobara try karo")
