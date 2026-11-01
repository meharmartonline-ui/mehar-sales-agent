import streamlit as st, os, re, subprocess, asyncio, shutil
import edge_tts
from gtts import gTTS

st.set_page_config(page_title="MEHAR V95 - WORLD STUDIO", layout="centered")
st.title("MEHAR V95 - WORLD STUDIO 🌍")
st.success("V97 BUG FIX: Ab Larka/Larki Change Hogi!")

VOICE_CATEGORIES = {
    "🇵🇰 URDU CLEAR": {
        "👩 20 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "👦 20 Sal Larka - Asad": "ur-PK-AsadNeural",
        "👩 30 Sal Larki - Ayesha": "ur-PK-AyeshaNeural",
        "👩 20 Sal Larki - Swara": "hi-IN-SwaraNeural",
    },
    "🇵🇰 SINDHI KHALIS - سنڌي": {
        "👩 20 Sal Larki - Uzma": "ur-PK-UzmaNeural",
        "👦 20 Sal Larka - Asad": "ur-PK-AsadNeural",
        "👩 30 Sal Larki - Ayesha": "ur-PK-AyeshaNeural",
        "👩 20 Sal Larki - Swara": "hi-IN-SwaraNeural",
    },
    "🇺🇸 ENGLISH CLEAR": {
        "👩 20 Sal Larki - Jenny": "en-US-JennyNeural",
        "👦 20 Sal Larka - Guy": "en-US-GuyNeural",
        "👩 20 Sal Larki - Aria": "en-US-AriaNeural",
        "👦 30 Sal Larka - Davis": "en-US-DavisNeural",
    },
    "🇸🇦 ARABIC - عربي": {
        "👩 20 Sal Larki - Salma": "ar-EG-SalmaNeural",
        "👦 20 Sal Larka - Shakir": "ar-EG-ShakirNeural",
        "👩 30
