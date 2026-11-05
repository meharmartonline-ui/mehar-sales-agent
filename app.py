
# ============================================================
# MEHAR V104 - WORLD STUDIO HYBRID
# Universal Translator + Voice Character Library
# Groq Translation + Edge TTS Free + ElevenLabs Pro
# MP3 / WAV / SRT / Background Music / Dialogue
# ============================================================

import asyncio
import os
import re
import json
import time
import tempfile
import subprocess
from pathlib import Path

import streamlit as st
import edge_tts
import imageio_ffmpeg
import requests

try:
    from groq import Groq
except Exception:
    Groq = None

try:
    from gtts import gTTS
except Exception:
    gTTS = None


st.set_page_config(
    page_title="MEHAR V104 - WORLD STUDIO",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 MEHAR V104 - WORLD STUDIO")
st.caption(
    "UNIVERSAL TRANSLATOR • VOICE CHARACTERS • "
    "ELEVENLABS PRO • FREE TTS • MP3 + WAV + SRT"
)

# ------------------------------------------------------------
# SECRETS
# ------------------------------------------------------------

def secret(name, default=""):
    try:
        return st.secrets.get(name, default)
    except Exception:
        return os.getenv(name, default)


GROQ_API_KEY = secret("GROQ_API_KEY")
ELEVENLABS_API_KEY = secret("ELEVENLABS_API_KEY")

GROQ_MODEL = secret("GROQ_MODEL", "llama-3.3-70b-versatile")
ELEVENLABS_MODEL = secret(
    "ELEVENLABS_MODEL",
    "eleven_multilingual_v2"
)

# ------------------------------------------------------------
# LANGUAGE CATALOGUE
# Display name, flag, Edge voice and gTTS code
# ------------------------------------------------------------

LANGUAGES = {
    "Urdu": {
        "flag": "🇵🇰", "country": "Pakistan",
        "edge_m": "ur-PK-AsadNeural",
        "edge_f": "ur-PK-UzmaNeural",
        "gtts": "ur"
    },
    "Sindhi": {
        "flag": "🇵🇰", "country": "Pakistan",
        "edge_m": None, "edge_f": None, "gtts": None
    },
    "English": {
        "flag": "🇬🇧", "country": "United Kingdom",
        "edge_m": "en-GB-RyanNeural",
        "edge_f": "en-GB-SoniaNeural",
        "gtts": "en"
    },
    "English (US)": {
        "flag": "🇺🇸", "country": "United States",
        "edge_m": "en-US-GuyNeural",
        "edge_f": "en-US-AriaNeural",
        "gtts": "en"
    },
    "Hindi": {
        "flag": "🇮🇳", "country": "India",
        "edge_m": "hi-IN-MadhurNeural",
        "edge_f": "hi-IN-SwaraNeural",
        "gtts": "hi"
    },
    "Arabic": {
        "flag": "🇸🇦", "country": "Saudi Arabia",
        "edge_m": "ar-SA-HamedNeural",
        "edge_f": "ar-SA-ZariyahNeural",
        "gtts": "ar"
    },
    "Bengali": {
        "flag": "🇧🇩", "country": "Bangladesh",
        "edge_m": "bn-BD-PradeepNeural",
        "edge_f": "bn-BD-NabanitaNeural",
        "gtts": "bn"
    },
    "Chinese (Simplified)": {
        "flag": "🇨🇳", "country": "China",
        "edge_m": "zh-CN-YunxiNeural",
        "edge_f": "zh-CN-XiaoxiaoNeural",
        "gtts": "zh-CN"
    },
    "Chinese (Traditional)": {
        "flag": "🇹🇼", "country": "Taiwan",
        "edge_m": "zh-TW-YunJheNeural",
        "edge_f": "zh-TW-HsiaoChenNeural",
        "gtts": "zh-TW"
    },
    "Japanese": {
        "flag": "🇯🇵", "country": "Japan",
        "edge_m": "ja-JP-KeitaNeural",
        "edge_f": "ja-JP-NanamiNeural",
        "gtts": "ja"
    },
    "Korean": {
        "flag": "🇰🇷", "country": "South Korea",
        "edge_m": "ko-KR-InJoonNeural",
        "edge_f": "ko-KR-SunHiNeural",
        "gtts": "ko"
    },
    "French": {
        "flag": "🇫🇷", "country": "France",
        "edge_m": "fr-FR-HenriNeural",
        "edge_f": "fr-FR-DeniseNeural",
        "gtts": "fr"
    },
    "German": {
        "flag": "🇩🇪", "country": "Germany",
        "edge_m": "de-DE-ConradNeural",
        "edge_f": "de-DE-KatjaNeural",
        "gtts": "de"
    },
    "Spanish": {
        "flag": "🇪🇸", "country": "Spain",
        "edge_m": "es-ES-AlvaroNeural",
        "edge_f": "es-ES-ElviraNeural",
        "gtts": "es"
    },
    "Portuguese": {
        "flag": "🇵🇹", "country": "Portugal",
        "edge_m": "pt-PT-DuarteNeural",
        "edge_f": "pt-PT-RaquelNeural",
        "gtts": "pt"
    },
    "Russian": {
        "flag": "🇷🇺", "country": "Russia",
        "edge_m": "ru-RU-DmitryNeural",
        "edge_f": "ru-RU-SvetlanaNeural",
        "gtts": "ru"
    },
    "Turkish": {
        "flag": "🇹🇷", "country": "Turkey",
        "edge_m": "tr-TR-AhmetNeural",
        "edge_f": "tr-TR-EmelNeural",
        "gtts": "tr"
    },
    "Persian": {
        "flag": "🇮🇷", "country": "Iran",
        "edge_m": None, "edge_f": None, "gtts": "fa"
    },
    "Italian": {
        "flag": "🇮🇹", "country": "Italy",
        "edge_m": "it-IT-DiegoNeural",
        "edge_f": "it-IT-ElsaNeural",
        "gtts": "it"
    },
    "Dutch": {
        "flag": "🇳🇱", "country": "Netherlands",
        "edge_m": "nl-NL-MaartenNeural",
        "edge_f": "nl-NL-FennaNeural",
        "gtts": "nl"
    },
    "Indonesian": {
        "flag": "🇮🇩", "country": "Indonesia",
        "edge_m": "id-ID-ArdiNeural",
        "edge_f": "id-ID-GadisNeural",
        "gtts": "id"
    },
    "Malay": {
        "flag": "🇲🇾", "country": "Malaysia",
        "edge_m": "ms-MY-OsmanNeural",
        "edge_f": "ms-MY-YasminNeural",
        "gtts": "ms"
    },
    "Thai": {
        "flag": "🇹🇭", "country": "Thailand",
        "edge_m": "th-TH-NiwatNeural",
        "edge_f": "th-TH-PremwadeeNeural",
        "gtts": "th"
    },
    "Vietnamese": {
        "flag": "🇻🇳", "country": "Vietnam",
        "edge_m": "vi-VN-NamMinhNeural",
        "edge_f": "vi-VN-HoaiMyNeural",
        "gtts": "vi"
    },
    "Ukrainian": {
        "flag": "🇺🇦", "country": "Ukraine",
        "edge_m": "uk-UA-OstapNeural",
        "edge_f": "uk-UA-PolinaNeural",
        "gtts": "uk"
    },
    "Greek": {
        "flag": "🇬🇷", "country": "Greece",
        "edge_m": "el-GR-NestorasNeural",
        "edge_f": "el-GR-AthinaNeural",
        "gtts": "el"
    },
    "Polish": {
        "flag": "🇵🇱", "country": "Poland",
        "edge_m": "pl-PL-MarekNeural",
        "edge_f": "pl-PL-ZofiaNeural",
        "gtts": "pl"
    },
    "Swedish": {
        "flag": "🇸🇪", "country": "Sweden",
        "edge_m": "sv-SE-MattiasNeural",
        "edge_f": "sv-SE-SofieNeural",
        "gtts": "sv"
    },
    "Norwegian": {
        "flag": "🇳🇴", "country": "Norway",
        "edge_m": "nb-NO-FinnNeural",
        "edge_f": "nb-NO-PernilleNeural",
        "gtts": "no"
    },
    "Danish": {
        "flag": "🇩🇰", "country": "Denmark",
        "edge_m": "da-DK-JeppeNeural",
        "edge_f": "da-DK-ChristelNeural",
        "gtts": "da"
    },
    "Finnish": {
        "flag": "🇫🇮", "country": "Finland",
        "edge_m": "fi-FI-HarriNeural",
        "edge_f": "fi-FI-NooraNeural",
        "gtts": "fi"
    },
    "Romanian": {
        "flag": "🇷🇴", "country": "Romania",
        "edge_m": "ro-RO-EmilNeural",
        "edge_f": "ro-RO-AlinaNeural",
        "gtts": "ro"
    },
    "Czech": {
        "flag": "🇨🇿", "country": "Czech Republic",
        "edge_m": "cs-CZ-AntoninNeural",
        "edge_f": "cs-CZ-VlastaNeural",
        "gtts": "cs"
    },
    "Swahili": {
        "flag": "🇰🇪", "country": "Kenya",
        "edge_m": "sw-KE-RafikiNeural",
        "edge_f": "sw-KE-ZuriNeural",
        "gtts": "sw"
    },
    "Filipino": {
        "flag": "🇵🇭", "country": "Philippines",
        "edge_m": "fil-PH-AngeloNeural",
        "edge_f": "fil-PH-BlessicaNeural",
        "gtts": "tl"
    },
    "Hebrew": {
        "flag": "🇮🇱", "country": "Israel",
        "edge_m": "he-IL-AvriNeural",
        "edge_f": "he-IL-HilaNeural",
        "gtts": "iw"
    },
    "Tamil": {
        "flag": "🇮🇳", "country": "India",
        "edge_m": "ta-IN-ValluvarNeural",
        "edge_f": "ta-IN-PallaviNeural",
        "gtts": "ta"
    },
    "Telugu": {
        "flag": "🇮🇳", "country": "India",
        "edge_m": "te-IN-MohanNeural",
        "edge_f": "te-IN-ShrutiNeural",
        "gtts": "te"
    },
    "Gujarati": {
        "flag": "🇮🇳", "country": "India",
        "edge_m": "gu-IN-NiranjanNeural",
        "edge_f": "gu-IN-DhwaniNeural",
        "gtts": "gu"
    },
    "Marathi": {
        "flag": "🇮🇳", "country": "India",
        "edge_m": "mr-IN-ManoharNeural",
        "edge_f": "mr-IN-AarohiNeural",
        "gtts": "mr"
    },
    "Punjabi": {
        "flag": "🇮🇳", "country": "India",
        "edge_m": "pa-IN-GurpreetNeural",
        "edge_f": "pa-IN-OjasNeural",
        "gtts": "pa"
    },
    "Nepali": {
        "flag": "🇳🇵", "country": "Nepal",
        "edge_m": None, "edge_f": None, "gtts": "ne"
    },
    "Irish": {
        "flag": "🇮🇪", "country": "Ireland",
        "edge_m": None, "edge_f": None, "gtts": "ga"
    },
    "Albanian": {
        "flag": "🇦🇱", "country": "Albania",
        "edge_m": None, "edge_f": None, "gtts": "sq"
    },
    "Armenian": {
        "flag": "🇦🇲", "country": "Armenia",
        "edge_m": None, "edge_f": None, "gtts": "hy"
    },
    "Azerbaijani": {
        "flag": "🇦🇿", "country": "Azerbaijan",
        "edge_m": None, "edge_f": None, "gtts": "az"
    },
    "Basque": {
        "flag": "🇪🇸", "country": "Basque region",
        "edge_m": None, "edge_f": None, "gtts": "eu"
    },
    "Catalan": {
        "flag": "🇪🇸", "country": "Catalonia",
        "edge_m": None, "edge_f": None, "gtts": "ca"
    },
    "Croatian": {
        "flag": "🇭🇷", "country": "Croatia",
        "edge_m": None, "edge_f": None, "gtts": "hr"
    },
    "Estonian": {
        "flag": "🇪🇪", "country": "Estonia",
        "edge_m": None, "edge_f": None, "gtts": "et"
    },
    "Georgian": {
        "flag": "🇬🇪", "country": "Georgia",
        "edge_m": None, "edge_f": None, "gtts": "ka"
    },
    "Icelandic": {
        "flag": "🇮🇸", "country": "Iceland",
        "edge_m": None, "edge_f": None, "gtts": "is"
    },
    "Latvian": {
        "flag": "🇱🇻", "country": "Latvia",
        "edge_m": None, "edge_f": None, "gtts": "lv"
    },
    "Lithuanian": {
        "flag": "🇱🇹", "country": "Lithuania",
        "edge_m": None, "edge_f": None, "gtts": "lt"
    },
    "Macedonian": {
        "flag": "🇲🇰", "country": "North Macedonia",
        "edge_m": None, "edge_f": None, "gtts": "mk"
    },
    "Serbian": {
        "flag": "🇷🇸", "country": "Serbia",
        "edge_m": None, "edge_f": None, "gtts": "sr"
    },
    "Slovak": {
        "flag": "🇸🇰", "country": "Slovakia",
        "edge_m": None, "edge_f": None, "gtts": "sk"
    },
    "Slovenian": {
        "flag": "🇸🇮", "country": "Slovenia",
        "edge_m": None, "edge_f": None, "gtts": "sl"
    },
    "Welsh": {
        "flag": "🏴", "country": "Wales",
        "edge_m": None, "edge_f": None, "gtts": "cy"
    },
    "Yiddish": {
        "flag": "🌍", "country": "Worldwide",
        "edge_m": None, "edge_f": None, "gtts": "yi"
    },
}

# ------------------------------------------------------------
# VOICE CHARACTER LIBRARY
# ------------------------------------------------------------

CHARACTERS = {
    "Male": [
        "Young Male", "Adult Male", "Mature Male",
        "Deep Male", "Hero Voice", "Male Narrator"
    ],
    "Female": [
        "Young Female", "Adult Female", "Mature Female",
        "Soft Female", "Bold Female", "Female Narrator"
    ],
    "Baby": [
        "Baby Boy", "Baby Girl", "Cute Child Style"
    ],
    "Old Man": [
        "Elderly Man", "Wise Grandfather", "Deep Grandfather"
    ],
    "Old Woman": [
        "Elderly Woman", "Warm Grandmother", "Soft Grandmother"
    ],
    "Special": [
        "Cartoon Boy", "Cartoon Girl", "Villain",
        "Monster", "Robot", "Comedy", "Cinematic Narrator"
    ],
}

CHARACTER_GENDER = {
    "Male": "male",
    "Female": "female",
    "Baby": "female",
    "Old Man": "male",
    "Old Woman": "female",
    "Special": "male",
}

# ------------------------------------------------------------
# GROQ CLIENT
# ------------------------------------------------------------

def get_groq():
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY missing. Streamlit Secrets mein apni Groq key add karein."
        )
    if Groq is None:
        raise RuntimeError("groq package install nahi hai.")
    return Groq(api_key=GROQ_API_KEY)


def groq_text(system_prompt, user_prompt, temperature=0.2):
    client = get_groq()
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()


def detect_source_language(text):
    prompt = (
        "Identify the language of the input. "
        "Return only its common English language name. "
        "Recognize Roman Urdu separately from English where possible. "
        "Do not translate the text."
    )
    return groq_text(prompt, text, 0.0)


def translate_text(text, target_language):
    system = (
        "You are a professional multilingual translator. "
        "Translate the user's complete text into the requested target language. "
        "Preserve the original meaning, names, numbers, tone and paragraph structure. "
        "Do not summarize, explain, or add information. "
        "For Roman Urdu, understand it as Urdu written in Latin letters. "
        "For Sindhi, use natural Sindhi language and script. "
        "Return only the translated text."
    )
    user = (
        f"Target language: {target_language}\n\n"
        f"Text to translate:\n{text}"
    )
    return groq_text(system, user, 0.1)


# ------------------------------------------------------------
# TEXT AND AUDIO UTILITIES
# ------------------------------------------------------------

def split_text(text, max_chars=240):
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []

    sentences = re.split(r"(?<=[.!?؟۔])\s+", text)
    chunks, current = [], ""

    for sentence in sentences:
        words = sentence.split()
        for word in words:
            candidate = (current + " " + word).strip()
            if len(candidate) <= max_chars:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                current = word

    if current:
        chunks.append(current)

    return chunks


async def edge_save(text, voice, rate, pitch, path):
    await edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=rate,
        pitch=pitch
    ).save(path)


def ffmpeg_bin():
    return imageio_ffmpeg.get_ffmpeg_exe()


def valid_audio(path, minimum=500):
    return os.path.isfile(path) and os.path.getsize(path) > minimum


def edge_chunk(text, voice, rate, pitch, path, retries=3):
    last_error = None

    for attempt in range(retries):
        try:
            if os.path.exists(path):
                os.remove(path)

            asyncio.run(
                edge_save(text, voice, rate, pitch, path)
            )

            if valid_audio(path):
                return

            last_error = RuntimeError("Empty audio received")

        except Exception as exc:
            last_error = exc

        time.sleep(0.7 * (attempt + 1))

    raise RuntimeError(f"Edge TTS failed: {last_error}")


def elevenlabs_chunk(text, voice_id, path):
    if not ELEVENLABS_API_KEY:
        raise RuntimeError("ElevenLabs API key missing.")

    if not voice_id:
        raise RuntimeError(
            "Is character ka ElevenLabs voice ID Streamlit Secrets mein configure nahi hai."
        )

    url = (
        "https://api.elevenlabs.io/v1/text-to-speech/"
        + voice_id
    )

    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }

    payload = {
        "text": text,
        "model_id": ELEVENLABS_MODEL,
        "voice_settings": {
            "stability": 0.50,
            "similarity_boost": 0.75,
            "style": 0.35,
            "use_speaker_boost": True,
        }
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=180
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"ElevenLabs error {response.status_code}: "
            f"{response.text[:500]}"
        )

    Path(path).write_bytes(response.content)

    if not valid_audio(path):
        raise RuntimeError("ElevenLabs returned empty audio.")


def get_elevenlabs_voice_id(character, language):
    # Configure these in Streamlit Secrets.
    # Example key: ELEVEN_VOICE_BABY_BOY
    key_map = {
        "Young Male": "ELEVEN_VOICE_YOUNG_MALE",
        "Adult Male": "ELEVEN_VOICE_ADULT_MALE",
        "Mature Male": "ELEVEN_VOICE_MATURE_MALE",
        "Deep Male": "ELEVEN_VOICE_DEEP_MALE",
        "Hero Voice": "ELEVEN_VOICE_HERO",
        "Male Narrator": "ELEVEN_VOICE_MALE_NARRATOR",
        "Young Female": "ELEVEN_VOICE_YOUNG_FEMALE",
        "Adult Female": "ELEVEN_VOICE_ADULT_FEMALE",
        "Mature Female": "ELEVEN_VOICE_MATURE_FEMALE",
        "Soft Female": "ELEVEN_VOICE_SOFT_FEMALE",
        "Bold Female": "ELEVEN_VOICE_BOLD_FEMALE",
        "Female Narrator": "ELEVEN_VOICE_FEMALE_NARRATOR",
        "Baby Boy": "ELEVEN_VOICE_BABY_BOY",
        "Baby Girl": "ELEVEN_VOICE_BABY_GIRL",
        "Cute Child Style": "ELEVEN_VOICE_CUTE_CHILD",
        "Elderly Man": "ELEVEN_VOICE_OLD_MAN",
        "Wise Grandfather": "ELEVEN_VOICE_GRANDFATHER",
        "Deep Grandfather": "ELEVEN_VOICE_DEEP_GRANDFATHER",
        "Elderly Woman": "ELEVEN_VOICE_OLD_WOMAN",
        "Warm Grandmother": "ELEVEN_VOICE_GRANDMOTHER",
        "Soft Grandmother": "ELEVEN_VOICE_SOFT_GRANDMOTHER",
        "Cartoon Boy": "ELEVEN_VOICE_CARTOON_BOY",
        "Cartoon Girl": "ELEVEN_VOICE_CARTOON_GIRL",
        "Villain": "ELEVEN_VOICE_VILLAIN",
        "Monster": "ELEVEN_VOICE_MONSTER",
        "Robot": "ELEVEN_VOICE_ROBOT",
        "Comedy": "ELEVEN_VOICE_COMEDY",
        "Cinematic Narrator": "ELEVEN_VOICE_CINEMATIC",
    }

    key = key_map.get(character)
    if not key:
        return None

    return secret(key, "")


def concat_mp3(paths, output_path):
    if not paths:
        raise RuntimeError("No audio chunks generated.")

    if len(paths) == 1:
        Path(output_path).write_bytes(Path(paths[0]).read_bytes())
    else:
        list_file = os.path.join(
            os.path.dirname(output_path),
            "concat_list.txt"
        )

        with open(list_file, "w", encoding="utf-8") as file:
            for item in paths:
                safe = os.path.abspath(item).replace("\\", "/")
                safe = safe.replace("'", "'\\''")
                file.write(f"file '{safe}'\n")

        subprocess.run(
            [
                ffmpeg_bin(), "-y",
                "-f", "concat", "-safe", "0",
                "-i", list_file,
                "-vn", "-c:a", "libmp3lame",
                "-q:a", "3", output_path
            ],
            check=True,
            capture_output=True,
            timeout=300
        )

    if not valid_audio(output_path, 800):
        raise RuntimeError("Final MP3 validation failed.")


def synthesize_text(
    text, language, provider, character, voice_gender,
    rate, pitch, workdir, prefix, progress=None
):
    chunks = split_text(text)
    if not chunks:
        raise ValueError("Text is empty.")

    paths = []

    edge_voice = LANGUAGES[language].get(
        "edge_f" if voice_gender == "female" else "edge_m"
    )

    eleven_voice = get_elevenlabs_voice_id(character, language)

    for index, chunk in enumerate(chunks):
        path = os.path.join(
            workdir, f"{prefix}_{index:04d}.mp3"
        )

        if provider == "ElevenLabs Pro":
            elevenlabs_chunk(chunk, eleven_voice, path)

        elif provider == "MEHAR Free":
            if edge_voice:
                edge_chunk(chunk, edge_voice, rate, pitch, path)
            else:
                fallback = LANGUAGES[language].get("gtts")

                if not fallback or gTTS is None:
                    raise RuntimeError(
                        f"{language} ke liye free TTS voice available nahi. "
                        "ElevenLabs voice ID configure karein."
                    )

                gTTS(
                    text=chunk,
                    lang=fallback,
                    slow=False
                ).save(path)

                if not valid_audio(path):
                    raise RuntimeError("Free TTS returned empty audio.")
        else:
            raise ValueError("Unknown voice provider.")

        paths.append(path)

        if progress:
            progress(index + 1, len(chunks))

    output = os.path.join(workdir, f"{prefix}_final.mp3")
    concat_mp3(paths, output)

    return output, chunks


def mix_music(input_mp3, music_bytes, volume, output_mp3, workdir):
    music_path = os.path.join(workdir, "background_music")
    Path(music_path).write_bytes(music_bytes)

    subprocess.run(
        [
            ffmpeg_bin(), "-y",
            "-i", input_mp3,
            "-stream_loop", "-1",
            "-i", music_path,
            "-filter_complex",
            f"[1:a]volume={volume}[bg];"
            "[0:a][bg]amix=inputs=2:duration=first:"
            "dropout_transition=2",
            "-c:a", "libmp3lame",
            "-q:a", "3",
            output_mp3
        ],
        check=True,
        capture_output=True,
        timeout=300
    )

    if not valid_audio(output_mp3):
        raise RuntimeError("Music mix failed.")

    return output_mp3


def to_wav(input_mp3, output_wav):
    subprocess.run(
        [
            ffmpeg_bin(), "-y",
            "-i", input_mp3,
            "-ac", "2",
            "-ar", "44100",
            output_wav
        ],
        check=True,
        capture_output=True,
        timeout=300
    )

    if not valid_audio(output_wav, 1000):
        raise RuntimeError("WAV conversion failed.")

    return output_wav


def fmt_srt(seconds):
    ms = int(max(0, seconds) * 1000)
    hours, rem = divmod(ms, 3600000)
    minutes, rem = divmod(rem, 60000)
    seconds, ms = divmod(rem, 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{ms:03}"


def make_srt(chunks, rate):
    cues = []
    cursor = 0.0

    speed = 1.0
    try:
        if rate.startswith("+"):
            speed = 1 + int(rate[:-1]) / 100
        elif rate.startswith("-"):
            speed = 1 + int(rate[:-1]) / 100
    except Exception:
        pass

    for index, chunk in enumerate(chunks, 1):
        words = max(1, len(chunk.split()))
        duration = max(1.2, words / (2.6 * max(0.5, speed)))

        start = cursor
        end = cursor + duration

        cues.append(
            f"{index}\n"
            f"{fmt_srt(start)} --> {fmt_srt(end)}\n"
            f"{chunk}\n"
        )

        cursor = end + 0.15

    return "\n".join(cues)


def parse_dialogue(text):
    rows = []

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        match = re.match(
            r"^\[(MALE|FEMALE|BABY|OLD MAN|OLD WOMAN|SPECIAL)\]\s*(.*)$",
            line,
            re.I
        )

        if match:
            rows.append((
                match.group(1).upper(),
                match.group(2).strip()
            ))
        else:
            rows.append(("DEFAULT", line))

    return [(a, b) for a, b in rows if b]


# ============================================================
# APP TABS
# ============================================================

tab_translate, tab_voice, tab_settings = st.tabs(
    ["🌐 UNIVERSAL TRANSLATOR", "🎙️ VOICE STUDIO", "⚙️ SETTINGS"]
)

# ============================================================
# UNIVERSAL TRANSLATOR
# ============================================================

with tab_translate:
    st.header("🌐 MEHAR Universal Translator")
    st.caption(
        "Auto detect • Roman Urdu • Urdu • Sindhi • Hindi • "
        "Arabic • World languages"
    )

    source_text = st.text_area(
        "Paste or type your text",
        height=220,
        key="translator_source",
        placeholder="Yahan kisi bhi language ka text likhein..."
    )

    detected_language = None

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔍 DETECT LANGUAGE", use_container_width=True):
            if not source_text.strip():
                st.warning("Pehle text likhein.")
            else:
                try:
                    detected_language = detect_source_language(source_text)
                    st.session_state["v104_detected"] = detected_language
                    st.success(
                        f"Detected language: {detected_language}"
                    )
                except Exception as exc:
                    st.error(f"Detection failed: {exc}")

    with col2:
        if st.button("🧹 CLEAR TEXT", use_container_width=True):
            st.session_state["translator_source"] = ""
            st.session_state.pop("v104_translation", None)
            st.rerun()

    if st.session_state.get("v104_detected"):
        st.info(
            "Detected: " + st.session_state["v104_detected"]
        )

    target_options = [
        f"{info['flag']} {name} — {info['country']}"
        for name, info in LANGUAGES.items()
    ]

    target_labels = st.selectbox(
        "Translate into target language",
        target_options,
        index=0
    )

    target_language = target_labels.split(" — ")[0].split(" ", 1)[1]

    if st.button(
        "🌍 TRANSLATE NOW",
        type="primary",
        use_container_width=True
    ):
        if not source_text.strip():
            st.warning("Pehle text enter karein.")
        else:
            try:
                with st.spinner("MEHAR translation kar raha hai..."):
                    translated = translate_text(
                        source_text,
                        target_language
                    )

                st.session_state["v104_translation"] = translated
                st.session_state["v104_target"] = target_language
                st.success("Translation complete.")

            except Exception as exc:
                st.error(f"Translation failed: {exc}")

    if st.session_state.get("v104_translation"):
        st.subheader("✅ Translation Result")

        st.text_area(
            "Translated text",
            value=st.session_state["v104_translation"],
            height=220,
            key="v104_translation_display"
        )

        st.download_button(
            "📥 Download Translation TXT",
            st.session_state["v104_translation"].encode("utf-8"),
            "MEHAR_V104_TRANSLATION.txt",
            "text/plain",
            use_container_width=True
        )

        if st.button(
            "🎙️ SEND TRANSLATION TO VOICE STUDIO",
            use_container_width=True
        ):
            st.session_state["voice_script"] = (
                st.session_state["v104_translation"]
            )
            st.success(
                "Text Voice Studio ke liye ready hai. "
                "Voice Studio tab kholein."
            )


# ============================================================
# VOICE STUDIO
# ============================================================

with tab_voice:
    st.header("🎙️ MEHAR Voice Character Studio")

    script = st.text_area(
        "Your script",
        height=220,
        key="voice_script",
        placeholder="Translation ya apna script yahan paste karein..."
    )

    st.subheader("1. Language")

    language = st.selectbox(
        "Select script language",
        list(LANGUAGES.keys()),
        index=0
    )

    language_info = LANGUAGES[language]

    st.info(
        f"{language_info['flag']} {language} • "
        f"{language_info['country']}"
    )

    st.subheader("2. Voice Provider")

    provider = st.radio(
        "Choose voice engine",
        ["MEHAR Free", "ElevenLabs Pro"],
        horizontal=True
    )

    st.subheader("3. Character Category")

    category = st.selectbox(
        "Select character group",
        list(CHARACTERS.keys())
    )

    character = st.selectbox(
        "Select character style",
        CHARACTERS[category]
    )

    default_gender = CHARACTER_GENDER[category]

    gender_options = ["male", "female"]

    if category == "Special":
        gender_options = ["male", "female"]

    voice_gender = st.radio(
        "Voice base",
        gender_options,
        index=gender_options.index(default_gender),
        horizontal=True
    )

    st.caption(
        "Baby, elderly, cartoon aur cinematic labels style presets hain. "
        "Actual result selected provider aur voice ID par depend karta hai."
    )

    st.subheader("4. Voice Controls")

    rate = st.select_slider(
        "Speech speed",
        options=[
            "-20%", "-15%", "-10%", "-5%",
            "+0%", "+5%", "+10%", "+15%", "+20%"
        ],
        value="-5%"
    )

    pitch = st.select_slider(
        "Pitch",
        options=[
            "-20Hz", "-15Hz", "-10Hz", "-5Hz",
            "+0Hz", "+5Hz", "+10Hz", "+15Hz", "+20Hz"
        ],
        value="+0Hz"
    )

    emotion = st.selectbox(
        "Expression / emotion",
        [
            "Natural",
            "Happy",
            "Sad",
            "Excited",
            "Angry",
            "Whisper",
            "Serious",
            "Cinematic"
        ]
    )

    st.caption(
        "Emotion selection is a preset label. Actual emotional delivery "
        "depends on the selected TTS provider and voice."
    )

    dialogue_mode = st.checkbox(
        "Dialogue mode ([MALE], [FEMALE], [BABY], "
        "[OLD MAN], [OLD WOMAN], [SPECIAL])"
    )

    music_file = st.file_uploader(
        "Optional background music",
        type=["mp3", "wav", "m4a"]
    )

    music_volume = st.slider(
        "Music volume",
        0.0, 0.35, 0.08, 0.01
    )

    duration_limit = st.selectbox(
        "Maximum script duration",
        ["15 sec", "30 sec", "1 min", "2 min", "5 min", "10 min"],
        index=3
    )

    max_seconds = {
        "15 sec": 15,
        "30 sec": 30,
        "1 min": 60,
        "2 min": 120,
        "5 min": 300,
        "10 min": 600
    }[duration_limit]

    word_count = len(script.split())
    estimated_seconds = word_count / 2.5 if word_count else 0

    c1, c2 = st.columns(2)
    c1.metric("Words", word_count)
    c2.metric("Estimated duration", f"{estimated_seconds:.0f} sec")

    if estimated_seconds > max_seconds:
        st.warning(
            "Script duration limit se lamba hai. "
            "Duration option barha dein."
        )

    # Voice test
    if st.button("🔊 TEST VOICE", use_container_width=True):
        if not script.strip():
            st.warning("Pehle script likhein.")
        else:
            try:
                with tempfile.TemporaryDirectory(
                    prefix="mehar_v104_test_"
                ) as td:
                    sample = script.strip()[:180]

                    path, _ = synthesize_text(
                        sample,
                        language,
                        provider,
                        character,
                        voice_gender,
                        rate,
                        pitch,
                        td,
                        "preview"
                    )

                    st.audio(
                        Path(path).read_bytes(),
                        format="audio/mpeg"
                    )
                    st.success("Voice preview ready.")

            except Exception as exc:
                st.error(f"Voice test failed: {exc}")

    # Final generation
    if st.button(
        "🎙️ GENERATE FINAL AUDIO",
        type="primary",
        use_container_width=True
    ):
        if not script.strip():
            st.error("Please enter your script.")

        elif estimated_seconds > max_seconds:
            st.error("Script selected duration se zyada hai.")

        else:
            progress = st.progress(0)
            status = st.empty()

            try:
                with tempfile.TemporaryDirectory(
                    prefix="mehar_v104_"
                ) as td:

                    if dialogue_mode:
                        lines = parse_dialogue(script)

                        if not lines:
                            raise ValueError(
                                "Dialogue script empty hai."
                            )

                        segment_paths = []
                        all_chunks = []

                        for index, (speaker, body) in enumerate(lines):
                            if speaker == "DEFAULT":
                                this_category = category
                                this_gender = voice_gender

                            else:
                                category_map = {
                                    "MALE": "Male",
                                    "FEMALE": "Female",
                                    "BABY": "Baby",
                                    "OLD MAN": "Old Man",
                                    "OLD WOMAN": "Old Woman",
                                    "SPECIAL": "Special"
                                }

                                this_category = category_map[speaker]
                                this_gender = CHARACTER_GENDER[
                                    this_category
                                ]

                            this_character = CHARACTERS[
                                this_category
                            ][0]

                            segment, chunks = synthesize_text(
                                body,
                                language,
                                provider,
                                this_character,
                                this_gender,
                                rate,
                                pitch,
                                td,
                                f"dialogue_{index}"
                            )

                            segment_paths.append(segment)
                            all_chunks.extend(chunks)

                            progress.progress(
                                (index + 1) / len(lines)
                            )
                            status.write(
                                f"Dialogue: {index+1}/{len(lines)}"
                            )

                        final_mp3 = os.path.join(
                            td, "dialogue_final.mp3"
                        )
                        concat_mp3(segment_paths, final_mp3)
                        srt_chunks = all_chunks

                    else:
                        def update_progress(done, total):
                            progress.progress(done / total)
                            status.write(
                                f"Audio chunks: {done}/{total}"
                            )

                        final_mp3, srt_chunks = synthesize_text(
                            script,
                            language,
                            provider,
                            character,
                            voice_gender,
                            rate,
                            pitch,
                            td,
                            "main",
                            update_progress
                        )

                    if music_file is not None:
                        mixed = os.path.join(
                            td, "final_with_music.mp3"
                        )

                        final_mp3 = mix_music(
                            final_mp3,
                            music_file.getvalue(),
                            music_volume,
                            mixed,
                            td
                        )

                    mp3_bytes = Path(final_mp3).read_bytes()

                    wav_path = os.path.join(td, "final.wav")
                    to_wav(final_mp3, wav_path)
                    wav_bytes = Path(wav_path).read_bytes()

                    srt_text = make_srt(srt_chunks, rate)

                    st.session_state["v104_mp3"] = mp3_bytes
                    st.session_state["v104_wav"] = wav_bytes
                    st.session_state["v104_srt"] = srt_text
                    st.session_state["v104_script"] = script
                    st.session_state["v104_language"] = language
                    st.session_state["v104_character"] = character
                    st.session_state["v104_provider"] = provider

                    st.success("✅ MEHAR V104 audio ready!")
                    st.balloons()

            except Exception as exc:
                st.error(f"Audio generation failed: {exc}")

    # Final downloads
    if st.session_state.get("v104_mp3"):
        st.divider()
        st.subheader("🎧 Final Audio")

        st.write(
            f"{st.session_state['v104_language']} • "
            f"{st.session_state['v104_character']} • "
            f"{st.session_state['v104_provider']}"
        )

        st.audio(
            st.session_state["v104_mp3"],
            format="audio/mpeg"
        )

        st.download_button(
            "📥 Download MP3",
            st.session_state["v104_mp3"],
            "MEHAR_V104_FINAL.mp3",
            "audio/mpeg",
            use_container_width=True
        )

        st.download_button(
            "📥 Download WAV",
            st.session_state["v104_wav"],
            "MEHAR_V104_FINAL.wav",
            "audio/wav",
            use_container_width=True
        )

        st.download_button(
            "📝 Download SRT",
            st.session_state["v104_srt"],
            "MEHAR_V104_SUBTITLES.srt",
            "application/x-subrip",
            use_container_width=True
        )

        st.download_button(
            "📄 Download Script TXT",
            st.session_state["v104_script"].encode("utf-8"),
            "MEHAR_V104_SCRIPT.txt",
            "text/plain",
            use_container_width=True
        )


# ============================================================
# SETTINGS
# ============================================================

with tab_settings:
    st.header("⚙️ MEHAR V104 Settings")

    st.markdown("""
    **Groq API:** Used for language detection and translation.

    **MEHAR Free:** Uses available Edge TTS voices, with gTTS
    fallback for supported languages.

    **ElevenLabs Pro:** Requires your own ElevenLabs API key,
    account access, available quota, and configured voice IDs.

    **Important:** Translation and voice generation are separate
    services. A language can be translated even if a free TTS voice
    is not available for that language.
    """)

    st.subheader("API connection status")

    if GROQ_API_KEY:
        st.success("Groq key found.")
    else:
        st.warning("Groq key missing.")

    if ELEVENLABS_API_KEY:
        st.success("ElevenLabs key found.")
    else:
        st.info("ElevenLabs key not configured. Free mode can still work.")

    st.subheader("ElevenLabs voice IDs")

    st.write(
        "Har character ke liye apna voice ID Streamlit Secrets mein "
        "configure kar sakte hain. Neeche example Secrets format diya hai."
    )

    st.code("""
GROQ_API_KEY = "your_groq_key"
GROQ_MODEL = "llama-3.3-70b-versatile"

ELEVENLABS_API_KEY = "your_elevenlabs_key"
ELEVENLABS_MODEL = "eleven_multilingual_v2"

ELEVEN_VOICE_YOUNG_MALE = "your_voice_id"
ELEVEN_VOICE_ADULT_MALE = "your_voice_id"
ELEVEN_VOICE_MATURE_MALE = "your_voice_id"
ELEVEN_VOICE_DEEP_MALE = "your_voice_id"
ELEVEN_VOICE_HERO = "your_voice_id"
ELEVEN_VOICE_MALE_NARRATOR = "your_voice_id"

ELEVEN_VOICE_YOUNG_FEMALE = "your_voice_id"
ELEVEN_VOICE_ADULT_FEMALE = "your_voice_id"
ELEVEN_VOICE_MATURE_FEMALE = "your_voice_id"
ELEVEN_VOICE_SOFT_FEMALE = "your_voice_id"
ELEVEN_VOICE_BOLD_FEMALE = "your_voice_id"
ELEVEN_VOICE_FEMALE_NARRATOR = "your_voice_id"

ELEVEN_VOICE_BABY_BOY = "your_voice_id"
ELEVEN_VOICE_BABY_GIRL = "your_voice_id"
ELEVEN_VOICE_CUTE_CHILD = "your_voice_id"

ELEVEN_VOICE_OLD_MAN = "your_voice_id"
ELEVEN_VOICE_GRANDFATHER = "your_voice_id"
ELEVEN_VOICE_DEEP_GRANDFATHER = "your_voice_id"

ELEVEN_VOICE_OLD_WOMAN = "your_voice_id"
ELEVEN_VOICE_GRANDMOTHER = "your_voice_id"
ELEVEN_VOICE_SOFT_GRANDMOTHER = "your_voice_id"

ELEVEN_VOICE_CARTOON_BOY = "your_voice_id"
ELEVEN_VOICE_CARTOON_GIRL = "your_voice_id"
ELEVEN_VOICE_VILLAIN = "your_voice_id"
ELEVEN_VOICE_MONSTER = "your_voice_id"
ELEVEN_VOICE_ROBOT = "your_voice_id"
ELEVEN_VOICE_COMEDY = "your_voice_id"
ELEVEN_VOICE_CINEMATIC = "your_voice_id"
""")

    st.warning(
        "Voice IDs example hain, real IDs nahi. Apne account ke actual "
        "voice IDs yahan set karein. API keys kisi ke saath share na karein."
    )

st.divider()
st.caption(
    "MEHAR V104 WORLD STUDIO • Universal Translation • "
    "Voice Character Library • Hybrid TTS"
)
