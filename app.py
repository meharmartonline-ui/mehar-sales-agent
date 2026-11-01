
import streamlit as st
import asyncio
import tempfile
import os
import re
import json
import subprocess
import time

import edge_tts
import imageio_ffmpeg
from google.cloud import texttospeech
from google.oauth2 import service_account


# ============================================================
# MEHAR V95 WORLD STUDIO — AUTO LANGUAGE EDITION
# Existing voices + automatic script detection + safer audio
# ============================================================

st.set_page_config(
    page_title="MEHAR V95 - WORLD STUDIO",
    page_icon="🌍",
    layout="centered"
)

st.title("MEHAR V95 - WORLD STUDIO 🌍")
st.success("V95 AUTO LANGUAGE EDITION | Asad + Uzma | Sindhi AI TTS")

# ------------------------------------------------------------
# VOICE CATALOG — ORIGINAL V95 VOICES PRESERVED
# ------------------------------------------------------------

URDU_AGE_LABELS = {
    "10 Sal Larki - Uzma": "ur-PK-UzmaNeural",
    "20 Sal Larki - Uzma": "ur-PK-UzmaNeural",
    "30 Sal Larki - Uzma": "ur-PK-UzmaNeural",
    "50 Sal Larki - Uzma": "ur-PK-UzmaNeural",
    "60 Sal Larki - Uzma": "ur-PK-UzmaNeural",
    "10 Sal Larka - Asad": "ur-PK-AsadNeural",
    "20 Sal Larka - Asad": "ur-PK-AsadNeural",
    "30 Sal Larka - Asad": "ur-PK-AsadNeural",
    "50 Sal Larka - Asad": "ur-PK-AsadNeural",
    "60 Sal Larka - Asad": "ur-PK-AsadNeural",
}

EDGE_VOICES = {
    "Hindi": {
        "Female - Swara": "hi-IN-SwaraNeural",
        "Male - Madhur": "hi-IN-MadhurNeural",
    },
    "English": {
        "Female - Aria": "en-US-AriaNeural",
        "Male - Guy": "en-US-GuyNeural",
    },
    "Arabic": {
        "Female - Zariyah": "ar-SA-ZariyahNeural",
        "Male - Hamed": "ar-SA-HamedNeural",
    },
}

LANGUAGE_LABELS = {
    "Urdu": "🇵🇰 URDU CLEAR - اردو",
    "Sindhi": "🇵🇰 SINDHI KHALIS - سنڌي",
    "Hindi": "🇮🇳 HINDI - हिंदी",
    "English": "🇺🇸 ENGLISH CLEAR",
    "Arabic": "🇸🇦 ARABIC - عربي",
}

DEFAULT_TEXTS = {
    "Urdu": "السلام علیکم! میرے پیارے بھائیوں اور بہنوں! مہر مارٹ میں خوش آمدید۔",
    "Sindhi": "السلام عليڪم! منهنجا پيارا ڀائرو ۽ ڀينرون! مهر مارٽ ۾ ڀليڪار.",
    "Hindi": "नमस्ते! मेहर मार्ट में आपका स्वागत है।",
    "English": "Hello friends! Welcome to Mehar Mart.",
    "Arabic": "السلام عليكم! أهلاً وسهلاً بكم في مهر مارت.",
}

DURATION_OPTIONS = {
    "⚡ 15 Sec": 15,
    "🔥 30 Sec": 30,
    "🎙️ 1 Min": 60,
    "⏰ 2 Min": 120,
    "🚀 10 Min FULL": 600,
}

ROMAN_URDU_WORDS = {
    "hai", "hain", "hy", "ho", "tha", "thi", "the",
    "aap", "ap", "mera", "meri", "mere", "hamara",
    "hum", "main", "mein", "kya", "kyun", "kaise",
    "kaisa", "acha", "achha", "bohat", "bahut",
    "nahi", "nahin", "kar", "karo", "karein",
    "karen", "kijiye", "chahiye", "liye", "liye",
    "bhai", "behen", "dost", "salam", "assalam",
    "khush", "aaj", "kal", "sab", "apna",
    "apni", "aur", "ke", "ki", "ka", "ko",
    "se", "par", "mein", "me", "yeh", "ye",
    "woh", "wo", "mera", "tum", "aapka",
    "aapki", "zabardast", "shukriya", "meharbani",
}

SINDHI_UNIQUE = set("ٻڄڏڊڙڱڳڪڻٽٿڀڌڇ")

# ------------------------------------------------------------
# LANGUAGE AUTO DETECTION
# ------------------------------------------------------------

def detect_language(text):
    text = (text or "").strip()

    if not text:
        return "Urdu"

    # Count script characters
    counts = {
        "Sindhi": 0,
        "Urdu": 0,
        "Hindi": 0,
        "Arabic": 0,
        "Latin": 0,
    }

    for ch in text:
        code = ord(ch)

        if 0x0900 <= code <= 0x097F:
            counts["Hindi"] += 1

        elif ch in SINDHI_UNIQUE:
            counts["Sindhi"] += 1

        elif 0x0600 <= code <= 0x06FF or 0x0750 <= code <= 0x077F:
            counts["Urdu"] += 1

        elif ch.isascii() and ch.isalpha():
            counts["Latin"] += 1

    # Script-based detection
    if counts["Hindi"] > 0:
        return "Hindi"

    if counts["Sindhi"] > 0:
        return "Sindhi"

    if counts["Urdu"] > 0:
        # Arabic-specific characters help distinguish Arabic.
        arabic_chars = set("ةىؤئ")
        if any(ch in arabic_chars for ch in text):
            return "Arabic"
        return "Urdu"

    # Roman Urdu detection
    words = set(re.findall(r"[a-zA-Z]+", text.lower()))
    matches = len(words.intersection(ROMAN_URDU_WORDS))

    if counts["Latin"] > 0 and matches >= 2:
        return "Urdu"

    return "English"


# ------------------------------------------------------------
# SESSION STATE
# ------------------------------------------------------------

if "mehar_v95_script" not in st.session_state:
    st.session_state.mehar_v95_script = DEFAULT_TEXTS["Urdu"]

if "mehar_v95_audio" not in st.session_state:
    st.session_state.mehar_v95_audio = None

def clear_script():
    st.session_state.mehar_v95_script = ""
    st.session_state.mehar_v95_audio = None


# ------------------------------------------------------------
# SCRIPT INPUT
# ------------------------------------------------------------

st.subheader("📝 YOUR SCRIPT")

text_input = st.text_area(
    "Text likhein ya paste karein:",
    key="mehar_v95_script",
    height=230,
    max_chars=18000,
    help="Urdu, Sindhi, Hindi, Arabic, English ya Roman Urdu."
)

detected_language = detect_language(text_input)

st.info(
    f"🔍 Auto-detected language: {detected_language}"
)

if text_input.strip():
    st.caption("Copy ke liye neeche text box ke copy icon ko use karein.")
    st.code(text_input, language=None)

col_copy, col_clear = st.columns(2)

with col_copy:
    st.button(
        "📋 COPY TEXT",
        use_container_width=True,
        disabled=not bool(text_input.strip()),
        help="Text box ke copy icon se text copy karein."
    )

with col_clear:
    st.button(
        "🧹 CLEAR TEXT",
        use_container_width=True,
        on_click=clear_script
    )


# ------------------------------------------------------------
# LANGUAGE OVERRIDE — AUTO IS DEFAULT
# ------------------------------------------------------------

language_options = [
    "🤖 AUTO DETECT",
    LANGUAGE_LABELS["Urdu"],
    LANGUAGE_LABELS["Sindhi"],
    LANGUAGE_LABELS["Hindi"],
    LANGUAGE_LABELS["English"],
    LANGUAGE_LABELS["Arabic"],
]

selected_language = st.selectbox(
    "🌍 LANGUAGE MODE:",
    language_options,
    index=0
)

if selected_language == "🤖 AUTO DETECT":
    language = detected_language
else:
    language = next(
        key for key, value in LANGUAGE_LABELS.items()
        if value == selected_language
    )

st.success(f"Selected language: {language}")


# ------------------------------------------------------------
# VOICE SELECTION
# ------------------------------------------------------------

if language == "Urdu":
    voice_label = st.selectbox(
        "🎙️ ASAD / UZMA ORIGINAL V95 PRESETS:",
        list(URDU_AGE_LABELS.keys()),
        index=6
    )
    voice_name = URDU_AGE_LABELS[voice_label]
    engine = "edge"

    st.info(
        "Urdu voice: Asad / Uzma. Age labels are presets only; "
        "they do not change the actual voice age."
    )

elif language == "Sindhi":
    sindhi_voices = {
        "Female AI Voice - Kore": "Kore",
        "Male AI Voice - Charon": "Charon",
    }

    voice_label = st.selectbox(
        "🎙️ SINDHI VOICE:",
        list(sindhi_voices.keys())
    )
    voice_name = sindhi_voices[voice_label]
    engine = "gemini_cloud"

    st.info(
        "Sindhi engine: Google Cloud Gemini-TTS | sd-IN Preview. "
        "Pakistani Sindhi accent is guided through the voice prompt."
    )

else:
    selected_voices = EDGE_VOICES[language]

    voice_label = st.selectbox(
        "🎙️ SELECT VOICE:",
        list(selected_voices.keys())
    )
    voice_name = selected_voices[voice_label]
    engine = "edge"


# ------------------------------------------------------------
# DURATION AND SPEECH SETTINGS
# ------------------------------------------------------------

limit_label = st.selectbox(
    "⏱️ AUDIO LIMIT:",
    list(DURATION_OPTIONS.keys()),
    index=0
)

MAX_SEC = DURATION_OPTIONS[limit_label]
MAX_CHARS = MAX_SEC * 30

word_count = len(text_input.split())
estimated_seconds = word_count / 2.5 if word_count else 0

c1, c2 = st.columns(2)
c1.metric("Words", word_count)
c2.metric("Estimated speech", f"{estimated_seconds:.0f} sec")

st.progress(
    min(estimated_seconds / MAX_SEC, 1.0)
    if MAX_SEC else 0
)

if estimated_seconds > MAX_SEC:
    st.warning(
        "Script selected duration limit se zyada ho sakta hai. "
        "Longer duration select karein."
    )

rate = st.select_slider(
    "⚡ EDGE SPEECH SPEED:",
    options=["-15%", "-10%", "-5%", "+0%", "+10%"],
    value="-5%",
    disabled=(engine != "edge")
)

style = st.selectbox(
    "🎭 SINDHI SPEECH STYLE:",
    [
        "Natural, clear, warm Pakistani Sindhi narration",
        "Energetic commercial advertisement",
        "Calm and friendly storytelling",
        "Professional radio announcer",
    ],
    disabled=(engine != "gemini_cloud")
)

st.caption(
    "Duration estimate hai. Actual audio duration language, pauses "
    "aur speaking speed par depend karti hai."
)


# ------------------------------------------------------------
# SAFE TEXT CHUNKING
# Keep words intact and avoid dropping small words.
# ------------------------------------------------------------

def split_text_chars(text, max_chars=280):
    text = (text or "").strip()

    if not text:
        return []

    words = re.findall(r"\S+", text)
    chunks = []
    current = ""

    for word in words:
        if len(word) > max_chars:
            raise ValueError(
                "A single word is longer than the allowed audio chunk."
            )

        candidate = f"{current} {word}".strip()

        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                chunks.append(current)
            current = word

    if current:
        chunks.append(current)

    return chunks


def split_text_utf8(text, max_bytes=2200):
    text = (text or "").strip()

    if not text:
        return []

    words = re.findall(r"\S+", text)
    chunks = []
    current = ""

    for word in words:
        word_size = len(word.encode("utf-8"))

        if word_size > max_bytes:
            raise ValueError(
                "A single word is too large for Sindhi TTS."
            )

        candidate = f"{current} {word}".strip()

        if len(candidate.encode("utf-8")) <= max_bytes:
            current = candidate
        else:
            if current:
                chunks.append(current)
            current = word

    if current:
        chunks.append(current)

    return chunks


# ------------------------------------------------------------
# AUDIO JOINING
# ------------------------------------------------------------

def join_mp3_files(paths, output_path):
    if not paths:
        raise RuntimeError("No audio chunks were generated.")

    if len(paths) == 1:
        with open(paths[0], "rb") as f:
            return f.read()

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    list_path = os.path.join(
        os.path.dirname(output_path),
        "concat_list.txt"
    )

    with open(list_path, "w", encoding="utf-8") as f:
        for path in paths:
            safe_path = os.path.abspath(path).replace("\\", "/")
            safe_path = safe_path.replace("'", "'\\''")
            f.write(f"file '{safe_path}'\n")

    result = subprocess.run(
        [
            ffmpeg,
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", list_path,
            "-vn",
            "-c:a", "libmp3lame",
            "-b:a", "128k",
            output_path,
        ],
        check=True,
        capture_output=True,
        timeout=600,
    )

    if not os.path.exists(output_path):
        raise RuntimeError("Final audio file was not created.")

    if os.path.getsize(output_path) < 800:
        raise RuntimeError("Final audio file is empty or incomplete.")

    with open(output_path, "rb") as f:
        return f.read()


# ------------------------------------------------------------
# EDGE TTS — NO WRONG-LANGUAGE FALLBACK
# ------------------------------------------------------------

async def edge_chunk(text, voice, speech_rate, path):
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=speech_rate
    )

    await communicate.save(path)

    if not os.path.exists(path) or os.path.getsize(path) < 800:
        raise RuntimeError("Edge TTS returned an empty audio chunk.")


def generate_edge_audio(text, voice, speech_rate):
    chunks = split_text_chars(text, 280)

    if not chunks:
        raise ValueError("Please enter your script.")

    progress = st.progress(0)
    status = st.empty()

    with tempfile.TemporaryDirectory(
        prefix="mehar_v95_edge_"
    ) as folder:

        audio_paths = []

        for i, chunk in enumerate(chunks):
            chunk_path = os.path.join(
                folder,
                f"edge_{i:04d}.mp3"
            )

            success = False
            last_error = None

            for attempt in range(3):
                try:
                    if os.path.exists(chunk_path):
                        os.remove(chunk_path)

                    asyncio.run(
                        edge_chunk(
                            chunk,
                            voice,
                            speech_rate,
                            chunk_path
                        )
                    )

                    success = True
                    break

                except Exception as exc:
                    last_error = exc
                    time.sleep(1.2 * (attempt + 1))

            if not success:
                raise RuntimeError(
                    f"Voice generation failed at chunk {i + 1} "
                    f"of {len(chunks)}. No chunk was skipped. "
                    f"Error: {last_error}"
                )

            audio_paths.append(chunk_path)

            progress.progress((i + 1) / len(chunks))
            status.write(
                f"Generating audio: {i + 1}/{len(chunks)}"
            )

        final_path = os.path.join(
            folder,
            "MEHAR_V95_FINAL.mp3"
        )

        return join_mp3_files(audio_paths, final_path)


# ------------------------------------------------------------
# GOOGLE CLOUD GEMINI TTS — SINDHI
# ------------------------------------------------------------

def get_cloud_tts_client():
    project_id = st.secrets.get(
        "GOOGLE_CLOUD_PROJECT",
        ""
    )

    service_info = st.secrets.get(
        "GOOGLE_CLOUD_SERVICE_ACCOUNT",
        None
    )

    if not project_id or not service_info:
        raise RuntimeError(
            "Sindhi setup missing. Streamlit Cloud > "
            "App settings > Secrets mein "
            "GOOGLE_CLOUD_PROJECT aur "
            "GOOGLE_CLOUD_SERVICE_ACCOUNT add karein."
        )

    if isinstance(service_info, str):
        service_info = json.loads(service_info)

    credentials = (
        service_account.Credentials.from_service_account_info(
            dict(service_info),
            scopes=[
                "https://www.googleapis.com/auth/cloud-platform"
            ]
        )
    )

    return texttospeech.TextToSpeechClient(
        credentials=credentials
    )


def generate_sindhi_audio(text, voice):
    chunks = split_text_utf8(text, 2200)

    if not chunks:
        raise ValueError("Sindhi script enter karein.")

    client = get_cloud_tts_client()

    progress = st.progress(0)
    status = st.empty()

    prompt = (
        "Speak the supplied text in clear, natural Sindhi. "
        "Use a fluent Pakistani Sindhi conversational accent "
        "as naturally as possible. Keep Sindhi pronunciation clear. "
        "Read the text exactly as supplied. Do not translate it. "
        "Do not summarize, paraphrase, repeat, add or omit words. "
        "Preserve proper names, including Pakistan. "
        "Pronounce every written word and short word clearly. "
        f"Speaking style: {style}."
    )

    with tempfile.TemporaryDirectory(
        prefix="mehar_v95_sindhi_"
    ) as folder:

        audio_paths = []

        for i, chunk in enumerate(chunks):
            chunk_path = os.path.join(
                folder,
                f"sindhi_{i:04d}.mp3"
            )

            last_error = None
            success = False

            for attempt in range(3):
                try:
                    synthesis_input = (
                        texttospeech.SynthesisInput(
                            text=chunk,
                            prompt=prompt
                        )
                    )

                    voice_params = (
                        texttospeech.VoiceSelectionParams(
                            language_code="sd-IN",
                            name=voice,
                            model_name="gemini-3.1-flash-tts-preview"
                        )
                    )

                    audio_config = (
                        texttospeech.AudioConfig(
                            audio_encoding=(
                                texttospeech.AudioEncoding.MP3
                            )
                        )
                    )

                    response = client.synthesize_speech(
                        input=synthesis_input,
                        voice=voice_params,
                        audio_config=audio_config
                    )

                    if not response.audio_content:
                        raise RuntimeError(
                            "Google returned empty audio."
                        )

                    with open(chunk_path, "wb") as f:
                        f.write(response.audio_content)

                    if os.path.getsize(chunk_path) < 800:
                        raise RuntimeError(
                            "Sindhi audio chunk is too small."
                        )

                    success = True
                    break

                except Exception as exc:
                    last_error = exc
                    time.sleep(1.5 * (attempt + 1))

            if not success:
                raise RuntimeError(
                    f"Sindhi audio failed at chunk {i + 1} "
                    f"of {len(chunks)}. No chunk was skipped. "
                    f"Error: {last_error}"
                )

            audio_paths.append(chunk_path)

            progress.progress((i + 1) / len(chunks))
            status.write(
                f"Sindhi audio: {i + 1}/{len(chunks)}"
            )

        final_path = os.path.join(
            folder,
            "MEHAR_KHALIS_SINDHI_FINAL.mp3"
        )

        return join_mp3_files(audio_paths, final_path)


# ------------------------------------------------------------
# TEST VOICE
# ------------------------------------------------------------

PREVIEW_TEXTS = {
    "Urdu": "السلام علیکم! یہ مہر مارٹ وائس ٹیسٹ ہے۔",
    "Sindhi": "السلام عليڪم! هي مهر مارٽ جو سنڌي آواز ٽيسٽ آهي.",
    "Hindi": "नमस्ते! यह मेहर मार्ट का वॉइस टेस्ट है।",
    "English": "Hello! This is the Mehar Mart voice test.",
    "Arabic": "السلام عليكم! هذا اختبار صوت مهر مارت.",
}

if st.button(
    "🔊 TEST VOICE",
    use_container_width=True
):
    try:
        with st.spinner("Voice preview generating..."):
            if engine == "gemini_cloud":
                preview_bytes = generate_sindhi_audio(
                    PREVIEW_TEXTS["Sindhi"],
                    voice_name
                )
            else:
                preview_bytes = generate_edge_audio(
                    PREVIEW_TEXTS[language],
                    voice_name,
                    rate
                )

        st.audio(preview_bytes, format="audio/mpeg")
        st.success("Voice preview ready.")

    except Exception as exc:
        st.error(f"Preview error: {exc}")


# ------------------------------------------------------------
# GENERATE AUDIO
# ------------------------------------------------------------

if st.button(
    f"🎙️ GENERATE {language.upper()} VOICE",
    type="primary",
    use_container_width=True
):

    if not text_input.strip():
        st.error("Please enter your script.")

    elif len(text_input) > MAX_CHARS:
        st.error(
            f"Selected duration limit allows approximately "
            f"{MAX_CHARS} characters. Please choose a longer duration."
        )

    elif estimated_seconds > MAX_SEC:
        st.error(
            "Script selected duration limit se zyada hai. "
            "Longer duration choose karein."
        )

    else:
        try:
            with st.spinner(
                f"{language} | {voice_label} | Audio generating..."
            ):

                if engine == "gemini_cloud":
                    audio_bytes = generate_sindhi_audio(
                        text_input,
                        voice_name
                    )
                else:
                    audio_bytes = generate_edge_audio(
                        text_input,
                        voice_name,
                        rate
                    )

            st.session_state["mehar_v95_audio"] = audio_bytes
            st.session_state["mehar_v95_voice"] = voice_label
            st.session_state["mehar_v95_language"] = language

            st.balloons()
            st.success(
                "✅ AUDIO READY! No failed chunk was silently skipped."
            )

        except Exception as exc:
            st.session_state["mehar_v95_audio"] = None
            st.error(f"Generation error: {exc}")


# ------------------------------------------------------------
# FINAL AUDIO OUTPUT
# ------------------------------------------------------------

if st.session_state.get("mehar_v95_audio"):
    st.divider()
    st.subheader("🎧 FINAL AUDIO")

    audio_bytes = st.session_state["mehar_v95_audio"]

    safe_voice = re.sub(
        r"[^A-Za-z0-9_-]+",
        "_",
        st.session_state.get(
            "mehar_v95_voice",
            "MEHAR_VOICE"
        )
    )

    safe_language = st.session_state.get(
        "mehar_v95_language",
        "Audio"
    )

    st.audio(
        audio_bytes,
        format="audio/mpeg"
    )

    st.download_button(
        "📥 DOWNLOAD MP3",
        data=audio_bytes,
        file_name=f"MEHAR_V95_{safe_language}_{safe_voice}.mp3",
        mime="audio/mpeg",
        use_container_width=True
    )

    st.download_button(
        "📝 DOWNLOAD SCRIPT TXT",
        data=st.session_state[
            "mehar_v95_script"
        ].encode("utf-8"),
        file_name="MEHAR_V95_SCRIPT.txt",
        mime="text/plain",
        use_container_width=True
    )


# ------------------------------------------------------------
# FOOTER
# ------------------------------------------------------------

st.divider()

st.caption(
    "MEHAR V95 WORLD STUDIO | Auto Language Detection | "
    "Urdu Asad + Uzma | Sindhi Gemini-TTS | "
    "Hindi | English | Arabic"
)

st.caption(
    "Note: Auto-detection is best-effort. Roman Urdu pronunciation "
    "depends on the selected Urdu voice. Sindhi sd-IN is Preview; "
    "pronunciation should be tested with native Sindhi speakers."
)
