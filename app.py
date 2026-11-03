# MEHAR V103 - WORLD STUDIO HYBRID
# Stable language routing, dedicated voices, chunk retries, MP3/WAV, optional music.
# Groq is deliberately NOT used as a TTS engine. Keep API keys in Streamlit Secrets.

import asyncio
import os
import re
import subprocess
import tempfile
import time
from pathlib import Path

import streamlit as st
import edge_tts
import imageio_ffmpeg

try:
    from gtts import gTTS
except Exception:
    gTTS = None

try:
    from google.cloud import texttospeech
    from google.oauth2 import service_account
except Exception:
    texttospeech = None
    service_account = None


st.set_page_config(
    page_title="MEHAR V103 - WORLD STUDIO",
    page_icon="🌍",
    layout="centered",
)

st.title("MEHAR V103 - WORLD STUDIO 🌍")
st.caption("AUTO LANGUAGE • DEDICATED VOICES • CHUNK RETRY • MP3 + WAV")

# ---------------------------------------------------------------------
# Voice catalogue. Voice names are fixed to their language; no cross-
# language fallback is ever attempted.
# ---------------------------------------------------------------------
LANGUAGES = {
    "Urdu": {
        "male": ("Asad", "ur-PK-AsadNeural"),
        "female": ("Uzma", "ur-PK-UzmaNeural"),
        "gtts": "ur",
    },
    "Hindi": {
        "male": ("Madhur", "hi-IN-MadhurNeural"),
        "female": ("Swara", "hi-IN-SwaraNeural"),
        "gtts": "hi",
    },
    "English": {
        "male": ("Guy", "en-US-GuyNeural"),
        "female": ("Aria", "en-US-AriaNeural"),
        "gtts": "en",
    },
    "Arabic": {
        "male": ("Hamed", "ar-SA-HamedNeural"),
        "female": ("Zariyah", "ar-SA-ZariyahNeural"),
        "gtts": "ar",
    },
    "Sindhi": {
        "male": ("Charon (Google Cloud)", "Charon"),
        "female": ("Kore (Google Cloud)", "Kore"),
        "gtts": None,
    },
}

# Detection is script-first. Urdu and Arabic share the Arabic script, so
# vocabulary markers are used; ambiguous text requires user confirmation.
URDU_MARKERS = set("""
ہے ہیں تھا تھی تھے ہوں ہو کیا یہ وہ میں ہم آپ تم سے کو کا کی کے پر
اور لیکن نہیں ایک کہ بھی ساتھ لیے والا والی بہت میرے ہماری آپکا
""".split())
ARABIC_MARKERS = set("""
هذا هذه ذلك تلك الذي التي الذين نحن أنا أنت أنتم هو هي هم في من إلى
على عن مع كان كانت يكون ليس لا نعم مرحبا السلام عليكم أهلا كيف لماذا
""".split())
SINDHI_MARKERS = set("آهي آهيون آھيون ڇا ڪهڙو ڪهڙي منهنجو منهنجي اوهان توهان سنڌي".split())
SINDHI_CHARS = set("ٻ ڄ ڳ ڱ ڦ ڄ ڏ ڊ ٽ ٺ ٿ ڌ ڇ ڙ ڻ ڪ")
DEVANAGARI = re.compile(r"[\u0900-\u097F]")
ARABIC_SCRIPT = re.compile(r"[\u0600-\u06FF\u0750-\u077F]")
LATIN = re.compile(r"[A-Za-z]")


def detect_language(text: str):
    """Return (language, confidence, reason); None means safely ambiguous."""
    s = text.strip()
    if not s:
        return None, 0.0, "No text"
    if DEVANAGARI.search(s):
        return "Hindi", 0.99, "Devanagari script"
    if any(ch in SINDHI_CHARS for ch in s):
        return "Sindhi", 0.96, "Sindhi-specific characters"
    words = set(re.findall(r"\w+", s.lower(), flags=re.UNICODE))
    urdu_hits = len(words & URDU_MARKERS)
    arabic_hits = len(words & ARABIC_MARKERS)
    sindhi_hits = len(words & SINDHI_MARKERS)
    if sindhi_hits:
        return "Sindhi", min(0.96, 0.72 + sindhi_hits * 0.08), "Sindhi vocabulary"
    if ARABIC_SCRIPT.search(s):
        if urdu_hits > arabic_hits:
            return "Urdu", min(0.96, 0.72 + (urdu_hits-arabic_hits) * 0.06), "Urdu vocabulary"
        if arabic_hits > urdu_hits:
            return "Arabic", min(0.96, 0.72 + (arabic_hits-urdu_hits) * 0.06), "Arabic vocabulary"
        return None, 0.45, "Urdu and Arabic both use Arabic script; text is ambiguous"
    if LATIN.search(s):
        # Roman Urdu common words; otherwise use English.
        roman_urdu = set("hai hain hy tha thi thay kya kahan mera meri ap aur nahi nahin bhai acha achi".split())
        hits = len(words & roman_urdu)
        if hits >= 2:
            return "Urdu", min(0.92, 0.65 + hits * 0.07), "Roman Urdu vocabulary"
        return "English", 0.90, "Latin alphabet"
    return None, 0.0, "Could not identify the script"


def split_text(text, max_chars=240):
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    # Keep sentence boundaries where possible.
    sentences = re.split(r"(?<=[.!?؟۔])\s+", text)
    chunks, current = [], ""
    for sentence in sentences:
        if len(sentence) > max_chars:
            words = sentence.split()
            for word in words:
                candidate = (current + " " + word).strip()
                if len(candidate) <= max_chars:
                    current = candidate
                else:
                    if current:
                        chunks.append(current)
                    current = word
        else:
            candidate = (current + " " + sentence).strip()
            if len(candidate) <= max_chars:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                current = sentence
    if current:
        chunks.append(current)
    return chunks


async def _edge_save(text, voice, rate, path):
    await edge_tts.Communicate(text=text, voice=voice, rate=rate).save(path)


def ffmpeg_bin():
    return imageio_ffmpeg.get_ffmpeg_exe()


def validate_audio(path, min_bytes=500):
    return os.path.isfile(path) and os.path.getsize(path) > min_bytes


def synthesize_edge_chunk(text, voice, rate, path, retries=3):
    last_error = None
    for attempt in range(retries):
        try:
            if os.path.exists(path):
                os.remove(path)
            asyncio.run(_edge_save(text, voice, rate, path))
            if validate_audio(path):
                return
            last_error = RuntimeError("Provider returned an empty/very small audio file")
        except Exception as exc:
            last_error = exc
        time.sleep(0.7 * (attempt + 1))
    raise RuntimeError(f"Edge TTS failed after {retries} attempts: {last_error}")


def synthesize_gtts_chunk(text, lang, path):
    if gTTS is None:
        raise RuntimeError("gTTS backup package is not installed")
    gTTS(text=text, lang=lang, slow=False).save(path)
    if not validate_audio(path):
        raise RuntimeError("gTTS returned an empty audio file")


def concat_mp3(paths, output_path):
    if not paths:
        raise RuntimeError("No audio chunks were produced")
    if len(paths) == 1:
        Path(output_path).write_bytes(Path(paths[0]).read_bytes())
    else:
        list_file = os.path.join(os.path.dirname(output_path), "concat.txt")
        with open(list_file, "w", encoding="utf-8") as f:
            for item in paths:
                safe = os.path.abspath(item).replace("\\", "/").replace("'", "'\\''")
                f.write(f"file '{safe}'\n")
        subprocess.run(
            [ffmpeg_bin(), "-y", "-f", "concat", "-safe", "0",
             "-i", list_file, "-vn", "-c:a", "libmp3lame", "-q:a", "3",
             output_path],
            check=True, capture_output=True, timeout=300,
        )
    if not validate_audio(output_path, 800):
        raise RuntimeError("Final MP3 validation failed")


def synthesize_edge_text(text, voice, rate, language, workdir, prefix, progress_cb=None):
    chunks = split_text(text)
    if not chunks:
        raise ValueError("Please enter text")
    paths = []
    for idx, chunk in enumerate(chunks):
        p = os.path.join(workdir, f"{prefix}_{idx:04d}.mp3")
        try:
            synthesize_edge_chunk(chunk, voice, rate, p)
        except Exception:
            # Same-language backup only. Never use a different language voice.
            fallback = LANGUAGES[language].get("gtts")
            if not fallback:
                raise
            p = os.path.join(workdir, f"{prefix}_backup_{idx:04d}.mp3")
            synthesize_gtts_chunk(chunk, fallback, p)
        paths.append(p)
        if progress_cb:
            progress_cb(idx + 1, len(chunks))
    out = os.path.join(workdir, f"{prefix}_joined.mp3")
    concat_mp3(paths, out)
    return out, chunks


def get_sindhi_client():
    if texttospeech is None or service_account is None:
        raise RuntimeError("Google Cloud TTS libraries missing; install requirements.txt")
    project = st.secrets.get("GOOGLE_CLOUD_PROJECT", "")
    account = st.secrets.get("GOOGLE_CLOUD_SERVICE_ACCOUNT", None)
    if not project or not account:
        raise RuntimeError(
            "Sindhi voice setup missing. Streamlit Secrets mein "
            "GOOGLE_CLOUD_PROJECT aur GOOGLE_CLOUD_SERVICE_ACCOUNT add karein. "
            "Groq key yahan use nahi hoti."
        )
    if isinstance(account, str):
        import json
        account = json.loads(account)
    creds = service_account.Credentials.from_service_account_info(
        dict(account),
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    return texttospeech.TextToSpeechClient(credentials=creds)


def synthesize_sindhi(text, voice, workdir, prefix):
    client = get_sindhi_client()
    chunks = split_text(text, 700)
    paths = []
    for idx, chunk in enumerate(chunks):
        request_input = texttospeech.SynthesisInput(
            text=chunk,
            prompt=("Speak the exact text in clear, natural Sindhi. "
                    "Do not translate, add, or omit words.")
        )
        params = texttospeech.VoiceSelectionParams(
            language_code="sd-IN",
            name=voice,
            model_name="gemini-3.1-flash-tts-preview",
        )
        config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        response = client.synthesize_speech(
            input=request_input, voice=params, audio_config=config
        )
        if not response.audio_content:
            raise RuntimeError(f"Sindhi TTS returned empty audio at chunk {idx+1}")
        path = os.path.join(workdir, f"{prefix}_{idx:04d}.mp3")
        Path(path).write_bytes(response.audio_content)
        if not validate_audio(path):
            raise RuntimeError(f"Sindhi audio chunk {idx+1} failed validation")
        paths.append(path)
    out = os.path.join(workdir, f"{prefix}_joined.mp3")
    concat_mp3(paths, out)
    return out, chunks


def mix_background_music(input_mp3, music_bytes, volume, output_mp3, workdir):
    music_path = os.path.join(workdir, "background_music")
    Path(music_path).write_bytes(music_bytes)
    subprocess.run(
        [ffmpeg_bin(), "-y", "-i", input_mp3, "-stream_loop", "-1",
         "-i", music_path, "-filter_complex",
         f"[1:a]volume={volume}[bg];[0:a][bg]amix=inputs=2:duration=first:dropout_transition=2",
         "-c:a", "libmp3lame", "-q:a", "3", output_mp3],
        check=True, capture_output=True, timeout=300,
    )
    if not validate_audio(output_mp3, 800):
        raise RuntimeError("Background music mix failed validation")
    return output_mp3


def to_wav(input_mp3, output_wav):
    subprocess.run(
        [ffmpeg_bin(), "-y", "-i", input_mp3, "-ac", "2", "-ar", "44100",
         output_wav],
        check=True, capture_output=True, timeout=300,
    )
    if not validate_audio(output_wav, 1000):
        raise RuntimeError("WAV conversion failed validation")
    return output_wav


def fmt_srt_time(seconds):
    ms = int(max(0, seconds) * 1000)
    h, rem = divmod(ms, 3600000)
    m, rem = divmod(rem, 60000)
    s, ms = divmod(rem, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def make_approx_srt(chunks, language, rate):
    # Estimated cue timing; not forced-alignment word timestamps.
    cues, cursor = [], 0.0
    speed_factor = 1.0
    if rate.startswith("+"):
        speed_factor = 1.08
    elif rate.startswith("-"):
        try:
            speed_factor = 1 + int(rate[:-1]) / 100
        except Exception:
            pass
    for idx, chunk in enumerate(chunks, 1):
        words = max(1, len(chunk.split()))
        duration = max(1.2, words / (2.6 * max(0.5, speed_factor)))
        start, end = cursor, cursor + duration
        cues.append(f"{idx}\n{fmt_srt_time(start)} --> {fmt_srt_time(end)}\n{chunk}\n")
        cursor = end + 0.15
    return "\n".join(cues)


def parse_dialogue(text):
    """Recognize [MALE] / [FEMALE] line prefixes; untagged lines use default voice."""
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        match = re.match(r"^\[(MALE|FEMALE)\]\s*(.*)$", line, re.I)
        if match:
            rows.append((match.group(1).lower(), match.group(2).strip()))
        else:
            rows.append(("default", line))
    return [(speaker, body) for speaker, body in rows if body]


# ---------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------
st.subheader("📝 Script to Voice")
mode = st.radio("Language mode", ["Auto Detect", "Choose language manually"], horizontal=True)
script = st.text_area(
    "Apna script yahan paste karein",
    height=230,
    placeholder="Urdu, Sindhi, Hindi, English ya Arabic text paste karein...",
)

detected, confidence, reason = detect_language(script)
if mode == "Auto Detect":
    if detected and confidence >= 0.70:
        st.success(f"Detected: {detected} • confidence {confidence:.0%} • {reason}")
        language = detected
    else:
        st.warning(f"Language clear nahi hui: {reason}. Urdu/Arabic same script use karte hain.")
        language = st.selectbox("Please confirm language", list(LANGUAGES.keys()))
else:
    language = st.selectbox("Select script language", list(LANGUAGES.keys()))

if script.strip() and detected and detected != language and mode == "Choose language manually":
    st.info(f"Script detection says {detected}; manual selection {language} rakhi gayi hai.")

voice_gender = st.radio("Voice", ["Female", "Male"], horizontal=True)
voice_name = LANGUAGES[language]["female" if voice_gender == "Female" else "male"][1]
voice_label = LANGUAGES[language]["female" if voice_gender == "Female" else "male"][0]
if language == "Sindhi":
    st.info("Sindhi voice Google Cloud Gemini-TTS se chalegi. Iske liye Google Cloud credentials chahiye; Groq key kaam nahi karegi.")
else:
    st.info(f"Selected dedicated voice: {voice_label} • {voice_name}")

rate = st.select_slider(
    "Speech speed",
    options=["-15%", "-10%", "-5%", "+0%", "+5%", "+10%"],
    value="-5%",
)

dialogue_mode = st.checkbox("Dialogue mode ([MALE] / [FEMALE] lines)", value=False)
music_file = st.file_uploader("Optional background music (MP3/WAV/M4A)", type=["mp3", "wav", "m4a"])
music_volume = st.slider("Background music volume", 0.0, 0.35, 0.08, 0.01)
duration_limit = st.selectbox("Maximum script duration", ["15 sec", "30 sec", "1 min", "2 min", "5 min", "10 min"], index=3)
max_seconds = {"15 sec":15, "30 sec":30, "1 min":60, "2 min":120, "5 min":300, "10 min":600}[duration_limit]
word_count = len(script.split())
estimated_seconds = word_count / 2.5 if word_count else 0
c1, c2 = st.columns(2)
c1.metric("Words", word_count)
c2.metric("Estimated duration", f"{estimated_seconds:.0f} sec")
if estimated_seconds > max_seconds:
    st.warning("Script selected duration se lamba lag raha hai. Duration barha dein ya text short karein.")

st.caption("SRT timing is estimated from text length; exact word-level synchronization/forced alignment is not included.")

if st.button("🔊 TEST VOICE", use_container_width=True):
    if not script.strip():
        st.warning("Pehle script paste karein.")
    elif mode == "Auto Detect" and (not detected or confidence < 0.70):
        st.warning("Pehle detected language confirm karein.")
    else:
        try:
            sample = script.strip()[:180]
            with tempfile.TemporaryDirectory(prefix="mehar_v103_test_") as td:
                if language == "Sindhi":
                    path, _ = synthesize_sindhi(sample, voice_name, td, "preview")
                else:
                    path, _ = synthesize_edge_text(sample, voice_name, rate, language, td, "preview")
                st.audio(Path(path).read_bytes(), format="audio/mpeg")
                st.success("Voice preview ready.")
        except Exception as exc:
            st.error(f"Voice preview failed: {exc}")

if st.button("🎙️ GENERATE FINAL AUDIO", type="primary", use_container_width=True):
    if not script.strip():
        st.error("Please enter your script.")
    elif mode == "Auto Detect" and (not detected or confidence < 0.70):
        st.error("Auto detection uncertain hai. Language manually confirm karein.")
    elif estimated_seconds > max_seconds:
        st.error("Script selected duration limit se zyada hai.")
    else:
        progress = st.progress(0)
        status = st.empty()
        try:
            with tempfile.TemporaryDirectory(prefix="mehar_v103_") as td:
                if dialogue_mode:
                    lines = parse_dialogue(script)
                    if not lines:
                        raise ValueError("Dialogue script mein [MALE] ya [FEMALE] text nahi mila.")
                    segment_paths, all_chunks = [], []
                    for idx, (speaker, body) in enumerate(lines):
                        gender = speaker if speaker in ("male", "female") else voice_gender.lower()
                        this_voice = LANGUAGES[language][gender][1]
                        if language == "Sindhi":
                            seg_path, seg_chunks = synthesize_sindhi(body, this_voice, td, f"dialogue_{idx}")
                        else:
                            seg_path, seg_chunks = synthesize_edge_text(body, this_voice, rate, language, td, f"dialogue_{idx}")
                        segment_paths.append(seg_path)
                        all_chunks.extend(seg_chunks)
                        progress.progress((idx + 1) / len(lines))
                        status.write(f"Dialogue line {idx+1}/{len(lines)} generated")
                    # Re-encode segments to a single MP3 using concat demuxer.
                    combined = os.path.join(td, "dialogue_final.mp3")
                    concat_mp3(segment_paths, combined)
                    final_mp3 = combined
                    srt_chunks = all_chunks
                else:
                    def update_progress(done, total):
                        progress.progress(done / total)
                        status.write(f"Audio chunks: {done}/{total}")
                    if language == "Sindhi":
                        final_mp3, srt_chunks = synthesize_sindhi(script, voice_name, td, "main")
                    else:
                        final_mp3, srt_chunks = synthesize_edge_text(script, voice_name, rate, language, td, "main", update_progress)

                if music_file is not None:
                    mixed = os.path.join(td, "final_with_music.mp3")
                    final_mp3 = mix_background_music(final_mp3, music_file.getvalue(), music_volume, mixed, td)

                mp3_bytes = Path(final_mp3).read_bytes()
                wav_path = os.path.join(td, "final.wav")
                to_wav(final_mp3, wav_path)
                wav_bytes = Path(wav_path).read_bytes()
                srt_text = make_approx_srt(srt_chunks, language, rate)

                st.session_state["v103_mp3"] = mp3_bytes
                st.session_state["v103_wav"] = wav_bytes
                st.session_state["v103_srt"] = srt_text
                st.session_state["v103_script"] = script
                st.session_state["v103_language"] = language
                st.session_state["v103_voice"] = voice_label
                st.success(f"✅ Audio ready • {language} • {voice_label}")
                st.balloons()
        except Exception as exc:
            st.error(f"Generation failed: {exc}")
            st.info("Agar error Sindhi ka hai to Google Cloud TTS credentials/API/billing check karein. Groq key ko Google private_key mein paste na karein.")

if st.session_state.get("v103_mp3"):
    st.divider()
    st.subheader("🎧 Final Output")
    st.write(f"{st.session_state.get('v103_language')} • {st.session_state.get('v103_voice')}")
    st.audio(st.session_state["v103_mp3"], format="audio/mpeg")
    safe_name = re.sub(r"[^A-Za-z0-9_-]+", "_", st.session_state.get("v103_language", "audio"))
    st.download_button("📥 Download MP3", st.session_state["v103_mp3"], f"MEHAR_V103_{safe_name}.mp3", "audio/mpeg", use_container_width=True)
    st.download_button("📥 Download WAV", st.session_state["v103_wav"], f"MEHAR_V103_{safe_name}.wav", "audio/wav", use_container_width=True)
    st.download_button("📝 Download SRT subtitles (estimated timing)", st.session_state["v103_srt"], f"MEHAR_V103_{safe_name}.srt", "application/x-subrip", use_container_width=True)
    st.download_button("📄 Download script TXT", st.session_state["v103_script"].encode("utf-8"), "MEHAR_V103_SCRIPT.txt", "text/plain", use_container_width=True)

st.divider()
st.caption("MEHAR V103 WORLD STUDIO • Auto language routing • Urdu / Sindhi / Hindi / English / Arabic")
