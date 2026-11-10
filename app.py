import streamlit as st
import edge_tts, asyncio, os, io, re, time, tempfile, requests, subprocess, shutil, urllib.parse
from datetime import datetime

try:
    from mutagen.mp3 import MP3
except Exception:
    MP3 = None

st.set_page_config(page_title="MEHAR V104 WORLD STUDIO", page_icon="🌍", layout="wide")
st.title("🌍 MEHAR V104 - WORLD STUDIO")
st.caption("FREE MULTI-LANGUAGE VOICE • SINDHI CLEAR • MP3 / WAV / SRT • TIME SELECT")

# ================= SINDHI ALPHABET FIXER =================
SINDHI_FIX = {
    "ک": "ڪ", "ہ": "ه", "ے": "ي", "ی": "ي",
    "کے": "ڪي", "کی": "ڪي", "کا": "ڪا", "کون": "ڪون", "کیا": "ڪيا",
    "کاپی": "ڪاپي", "کاپي": "ڪاپي", "کارڈ": "ڪارڊ", "کارډ": "ڪارڊ",
    "شناختی": "شناختي", "تصویر": "تصوير", "سمی": "سميت", "چہرے": "چھري",
    "گھر": "گھر", "بھی": "بھي", "معذوری": "معذوري", "سرٹیفکیٹ": "سرٽيفڪيٽ",
    "ھے": "آھي", "ہے": "آھي", "ھیں": "آھن", "تک": "تائين",
}
def clean_sindhi(text):
    if not text: return text
    for ur, sd in SINDHI_FIX.items():
        text = text.replace(ur, sd)
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace(":", "۔")
    return text

def split_sindhi_chunks(text, max_len=180):
    parts = re.split(r"(?<=[۔؟!.\n])\s+", text)
    chunks, cur = [], ""
    for p in parts:
        p = p.strip()
        if not p: continue
        if len(cur) + len(p) > max_len and cur:
            chunks.append(cur.strip()); cur = p
        else:
            cur = (cur + " " + p).strip()
    if cur: chunks.append(cur)
    return [c for c in chunks if c]

def expand_to_duration(text, target_label):
    secs_map = {"15 Second":15,"30 Second":30,"1 Minute":60,"2 Minute":120,"5 Minute":300,"10 Minute":600}
    if target_label not in secs_map: return text
    target = secs_map[target_label]
    need_chars = target * 13
    if len(text) >= need_chars:
        cut = text[:need_chars]
        last = cut.rfind("۔")
        if last > 100: cut = cut[:last+1]
        return cut
    else:
        times = int(need_chars / max(1,len(text))) + 1
        repeated = (" ۔ " + text).join([text]*times)
        return repeated[:need_chars+200]

def make_sindhi_clear(text):
    # Google TTS tukre jodne se MP3 toot jata tha 0:00 ho jata tha
    # Is liye ab Edge TTS se Sindhi bolenge - ek hi sahi MP3 banta hai
    text = clean_sindhi(text)
    # Sindhi ke liye Edge ka ur-PK voice sab se stable hai
    # Alphabet fixer ki wajah se ucharan Sindhi wala hi rahega
    return run_async(make_edge(text, "ur-PK-AsadNeural", 0, 0)), text
# ==========================================================

LANGS = {
 "Sindhi (سنڌي)":"sd","Urdu (اردو)":"ur","Hindi (हिन्दी)":"hi","English":"en",
 "Arabic (العربية)":"ar","Roman Urdu":"ur","French":"fr","Spanish":"es","German":"de",
 "Italian":"it","Portuguese":"pt","Turkish":"tr","Chinese":"zh","Japanese":"ja",
 "Korean":"ko","Bengali":"bn","Punjabi":"pa","Pashto":"ps","Persian":"fa",
 "Russian":"ru","Indonesian":"id","Malay":"ms","Thai":"th","Vietnamese":"vi",
 "Dutch":"nl","Polish":"pl","Swedish":"sv","Greek":"el","Hebrew":"he",
 "Tamil":"ta","Telugu":"te","Marathi":"mr","Gujarati":"gu","Nepali":"ne"
}
DEFAULTS = {
 "ur":("ur-PK-AsadNeural","ur-PK-UzmaNeural"),
 "hi":("hi-IN-MadhurNeural","hi-IN-SwaraNeural"),
 "en":("en-US-GuyNeural","en-US-JennyNeural"),
 "ar":("ar-SA-HamedNeural","ar-SA-ZariyahNeural"),
 "sd":("ur-PK-AsadNeural","ur-PK-UzmaNeural"),
}
STYLES = {
 "Normal":(0,0),"Young Adult":(5,3),"Baby / Child-like (simulation)":(12,12),
 "Old Man (simulation)":(-15,-8),"Old Woman (simulation)":(-10,7),
 "Deep Male (simulation)":(-8,-12),"Bright Female (simulation)":(5,8),
 "Calm Narrator":(-8,-2),"Energetic":(12,4)
}

def secret(name):
    val=os.getenv(name,"")
    try:
        if not val and hasattr(st,"secrets"): val=st.secrets.get(name,"")
    except Exception: pass
    return str(val).strip()

def run_async(coro):
    try: asyncio.get_running_loop()
    except RuntimeError: return asyncio.run(coro)
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
        return ex.submit(asyncio.run,coro).result()

@st.cache_data(ttl=3600)
def catalogue():
    return run_async(edge_tts.list_voices())

def get_voices(lang, gender):
    try:
        result=[]
        for v in catalogue():
            if v.get("Locale","").split("-")[0].lower()==lang:
                if v.get("Gender","").lower()==gender.lower():
                    result.append(v["ShortName"])
        return sorted(set(result))
    except Exception: return []

def choose_voice(label, gender, selected=""):
    lang=LANGS[label]
    if selected: return selected
    found=get_voices(lang,gender)
    if found: return found[0]
    if lang in DEFAULTS: return DEFAULTS[lang][0 if gender=="Male" else 1]
    raise RuntimeError(f"{label}: {gender} free voice catalogue mein available nahi.")

async def make_edge(text, voice, rate, pitch):
    job=edge_tts.Communicate(text,voice,rate=f"{rate:+d}%",pitch=f"{pitch:+d}Hz")
    out=bytearray()
    async for chunk in job.stream():
        if chunk.get("type")=="audio": out.extend(chunk.get("data",b""))
    if not out: raise RuntimeError("TTS audio return nahi hua.")
    return bytes(out)

def make_eleven(text,key,voice_id,model):
    if not key or not voice_id: raise ValueError("ElevenLabs API key aur Voice ID dono required hain.")
    r=requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
      headers={"xi-api-key":key,"Content-Type":"application/json","Accept":"audio/mpeg"},
      json={"text":text,"model_id":model or "eleven_multilingual_v2",
            "voice_settings":{"stability":0.5,"similarity_boost":0.75}},timeout=120)
    if r.status_code>=400: raise RuntimeError(f"ElevenLabs {r.status_code}: {r.text[:400]}")
    return r.content

def duration(data):
    if MP3 is None: return 10.0
    with tempfile.NamedTemporaryFile(suffix=".mp3",delete=False) as f:
        f.write(data); name=f.name
    try: return MP3(name).info.length
    except Exception: return 10.0
    finally:
        try: os.remove(name)
        except OSError: pass

def stamp(sec):
    ms=int(max(0,sec)*1000); h,ms=divmod(ms,3600000); m,ms=divmod(ms,60000); s,ms=divmod(ms,1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def srt_text(text,seconds):
    parts=[x.strip() for x in re.split(r"(?<=[.!?؟۔])\s+|\n+",text) if x.strip()] or [text]
    weights=[max(1,len(x)) for x in parts]; total=sum(weights); cur=0; rows=[]
    for i,(part,w) in enumerate(zip(parts,weights),1):
        end=cur+seconds*w/total
        rows += [str(i),f"{stamp(cur)} --> {stamp(end)}",part,""]
        cur=end
    return "\n".join(rows)

def downloads(data,text,name):
    st.audio(data,format="audio/mp3")
    a,b,c=st.columns(3)
    with a: st.download_button("⬇️ MP3",data,name+".mp3","audio/mpeg",key="mp3"+name)
    with b:
        try:
            if shutil.which("ffmpeg") is None:
                st.download_button("⬇️ WAV (MP3)",data,name+".mp3","audio/mpeg",key="wav"+name)
            else:
                with tempfile.NamedTemporaryFile(suffix=".mp3",delete=False) as f:
                    f.write(data); mp3_path=f.name
                wav_path = mp3_path + ".wav"
                res = subprocess.run(["ffmpeg","-y","-i",mp3_path,wav_path], capture_output=True, timeout=30)
                if res.returncode == 0 and os.path.exists(wav_path) and os.path.getsize(wav_path) > 100:
                    with open(wav_path,"rb") as wf: wav_bytes = wf.read()
                    st.download_button("⬇️ WAV",wav_bytes,name+".wav","audio/wav",key="wav"+name)
                else:
                    st.download_button("⬇️ WAV (MP3)",data,name+".mp3","audio/mpeg",key="wav"+name)
                try: os.remove(mp3_path)
                except OSError: pass
                try:
                    if os.path.exists(wav_path): os.remove(wav_path)
                except OSError: pass
        except Exception:
            st.download_button("⬇️ WAV (MP3)",data,name+".mp3","audio/mpeg",key="wav"+name)
    with c:
        try:
            subs=srt_text(text,duration(data))
            st.download_button("📝 SRT",subs.encode(),name+".srt","text/plain",key="srt"+name)
        except Exception as e: st.warning(f"SRT error: {e}")

def groq_translate(text,target,key,model):
    if not key: raise ValueError("Auto Translate ke liye Groq API key sidebar mein add karein.")
    r=requests.post("https://api.groq.com/openai/v1/chat/completions",
      headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},
      json={"model":model,"temperature":0.2,"messages":[
       {"role":"system","content":f"Translate accurately into {target}. Use correct Sindhi alphabet: ڪ for k, ک for kh, ٻ ڄ ڏ ڳ for implosives, ڃ ڱ ڻ for nasals. Preserve meaning, names, numbers and paragraphs. Return only translation."},
       {"role":"user","content":text}]},timeout=90)
    if r.status_code>=400: raise RuntimeError(f"Groq {r.status_code}: {r.text[:400]}")
    return r.json()["choices"][0]["message"]["content"].strip()

with st.sidebar:
    st.header("⚙️ Settings")
    st.caption("Free Edge TTS ke liye API key nahi chahiye.")
    groq_key=st.text_input("Groq API Key (optional)",secret("GROQ_API_KEY"),type="password")
    groq_model=st.text_input("Groq model","llama-3.3-70b-versatile")
    eleven_key=st.text_input("ElevenLabs API Key (optional)",secret("ELEVENLABS_API_KEY"),type="password")
    eleven_id=st.text_input("ElevenLabs Voice ID",secret("ELEVENLABS_VOICE_ID"))
    eleven_model=st.text_input("ElevenLabs model","eleven_multilingual_v2")
    if st.button("🔄 Refresh voice catalogue"): catalogue.clear(); st.rerun()

voice_tab,trans_tab,help_tab=st.tabs(["🎙️ VOICE STUDIO","🌐 TRANSLATOR","ℹ️ GUIDE"])

with voice_tab:
    st.subheader("Five independent voice boxes")
    st.info("Sindhi ke liye: Language Sindhi, Engine Sindhi Clear (Google sd), Auto Translate OFF agar text pehle se Sindhi hai.")
    for n in range(1,6):
      with st.expander(f"BOX {n}",expanded=(n==1)):
        l,r=st.columns([1.5,1])
        with l:
          language=st.selectbox("Language",list(LANGS),index=list(LANGS).index("Sindhi (سنڌي)") if n==1 else list(LANGS).index("Urdu (اردو)"),key=f"lang{n}")
          default_text = """نالو:
فون نمبر:
معذوري جو قسم:

شناختي ڪارڊ جي ڪاپي جي تصوير ٻئي پاسا

معذوري جو سرٽيفڪيٽ جيڪڏھن آھي ته ان جي تصوير

منھن کان پيرين تائين شناختي ڪارڊ سميت تصوير.

ٻئي تصوير صرف چھري جي عام ۽ نارمل.

جيڪڏھن گھر ۾ ھڪ کان وڌيڪ معذور آھن ته سڀني جي الڳ ڊيٽا ھجي""" if n==1 else ""
          script=st.text_area("Text / Script",value=default_text,height=180,key=f"text{n}")
          auto_trans = st.checkbox("🔄 Auto Translate karke bolo", value=False, key=f"auto{n}")
          engine=st.radio("Engine",["Sindhi Clear (Google sd)","Free Edge TTS","ElevenLabs Pro"],horizontal=True,key=f"engine{n}")
        with r:
          gender=st.selectbox("Voice category",["Male","Female"],key=f"gender{n}")
          style=st.selectbox("Character style",list(STYLES),key=f"style{n}")
          target_time=st.selectbox("⏱️ Target Time",["Auto (Text jitna hai)","15 Second","30 Second","1 Minute","2 Minute","5 Minute","10 Minute"],key=f"dur{n}")
          rate=st.slider("Extra speed",-25,25,0,key=f"rate{n}")
          pitch=st.slider("Extra pitch",-15,15,0,key=f"pitch{n}")
          options=get_voices(LANGS[language],gender) if engine=="Free Edge TTS" else []
          selected=st.selectbox("Voice",options,key=f"voice{n}") if options and engine=="Free Edge TTS" else ""
          if engine=="Free Edge TTS" and not options: st.caption("Default voice fallback will be tried if available.")
        if st.button(f"▶️ GENERATE BOX {n}",type="primary",key=f"go{n}"):
          if not script.strip(): st.error("Pehle text likhein.")
          else:
            try:
              sr,sp=STYLES[style]
              final_text = expand_to_duration(script, target_time)
              if auto_trans:
                  if not groq_key:
                      st.warning("Auto Translate ke liye Groq Key nahi hai, is liye original text hi bola ja raha hai.")
                  else:
                      with st.spinner(f"Auto Translate ho raha hai -> {language}..."):
                          final_text = groq_translate(final_text, language, groq_key, groq_model)
                      st.info(f"Translated: {final_text[:200]}")
              use_engine = engine
              if engine=="ElevenLabs Pro" and (not eleven_key or not eleven_id):
                  st.warning("ElevenLabs key / Voice ID khali hai, is liye Sindhi Clear use ho raha hai.")
                  use_engine = "Sindhi Clear (Google sd)"
              with st.spinner("Voice generate ho rahi hai..."):
                if use_engine=="Sindhi Clear (Google sd)":
                  audio, final_text = make_sindhi_clear(final_text)
                elif use_engine=="Free Edge TTS":
                  voice=choose_voice(language,gender,selected)
                  audio=run_async(make_edge(final_text,voice,max(-50,min(50,sr+rate)),max(-50,min(50,sp+pitch))))
                else:
                  audio=make_eleven(final_text,eleven_key,eleven_id,eleven_model)
              st.success(f"BOX {n}: Audio ready!")
              downloads(audio,final_text,f"MEHAR_V104_BOX{n}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            except Exception as e: st.error(f"Voice generation failed: {e}")

with trans_tab:
    st.subheader("Universal Translator")
    st.caption("Translator ke liye Groq key chahiye.")
    source=st.text_area("Source text",height=150,key="src")
    target=st.selectbox("Translate into",list(LANGS),key="target")
    if st.button("🌐 TRANSLATE",type="primary"):
      try:
        with st.spinner("Translation in progress..."): st.session_state["translated_v104"]=groq_translate(source,target,groq_key,groq_model)
        st.success("Translation complete.")
      except Exception as e: st.error(f"Translation failed: {e}")
    if st.session_state.get("translated_v104"):
      translated=st.text_area("Translated text",st.session_state["translated_v104"],height=150,key="translated_edit")
      st.download_button("⬇️ Download TXT",translated.encode("utf-8"),"MEHAR_TRANSLATION.txt","text/plain")
      if st.button("🎧 SINDHI CLEAR MEIN SUNO"):
        try:
          audio, _ = make_sindhi_clear(translated)
          downloads(audio,translated,f"MEHAR_TRANSLATION_{int(time.time())}")
        except Exception as e: st.error(f"Translation voice failed: {e}")

with help_tab:
    st.markdown("""
### SINDHI CLEAR
- Sindhi ke 52 harf: **ٻ ڄ ڏ ڳ ڪ ڃ ڱ ڻ ٽ ٺ ٿ ڊ ڍ ڌ ڀ ڦ ڇ**
- **ڪ** = k, **ک** = kh
- Jumle ke end pe **۔** lagao
- Awaz katne se bachane ke liye 180 harf wale tukre bante hain
- Auto Translate OFF rakho agar text pehle se Sindhi hai
### TIME
- Target Time se 15 sec, 30 sec, 1, 2, 5, 10 min select karo
- Chhota text hoga to repeat hoga, bara hoga to kaat diya jayega
### WAV
- WAV ke liye packages.txt mein `ffmpeg` hona chahiye, phir Reboot karo
- Agar ffmpeg na ho to WAV (MP3) milega, error nahi aayega
### FREE / PRO
- Edge TTS: no API key needed
- Sindhi Clear: Google sd, free
- ElevenLabs optional hai
""")
st.divider()
st.caption("MEHAR V104 WORLD STUDIO — Sindhi Clear + Time Edition")
