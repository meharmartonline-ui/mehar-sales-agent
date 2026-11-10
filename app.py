import streamlit as st
import edge_tts, asyncio, os, io, re, time, tempfile, requests
from datetime import datetime
from pydub import AudioSegment
from mutagen.mp3 import MP3

st.set_page_config(page_title="MEHAR V104 WORLD STUDIO", page_icon="🌍", layout="wide")
st.title("🌍 MEHAR V104 - WORLD STUDIO")
st.caption("FREE MULTI-LANGUAGE VOICE • OPTIONAL ELEVENLABS PRO • MP3 / WAV / SRT")

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
 # SINDHI: pehle asli Sindhi try karo, na mile to Urdu fallback
 "sd":("sd-PK-DilawerNeural","sd-PK-GulBadanNeural"),
}
FALLBACK_SD = ("ur-PK-AsadNeural","ur-PK-UzmaNeural")

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
    # SINDHI VOICE WALA FIX
    if lang == "sd":
        try:
            real = [v["ShortName"] for v in catalogue() if v.get("Locale","").lower().startswith("sd") and v.get("Gender","").lower()==gender.lower()]
            if real: return sorted(set(real))
        except Exception: pass
        # Agar asli Sindhi na mili to Urdu fallback
        return [FALLBACK_SD[0]] if gender=="Male" else [FALLBACK_SD[1]]
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
    if selected: return selected, lang=="sd" and "ur-PK" in selected
    found=get_voices(lang,gender)
    if found:
        is_fallback = lang=="sd" and "ur-PK" in found[0]
        return found[0], is_fallback
    if lang in DEFAULTS: return DEFAULTS[lang][0 if gender=="Male" else 1], lang=="sd"
    raise RuntimeError(f"{label}: {gender} free voice catalogue mein available nahi.")

async def make_edge(text, voice, rate, pitch):
    job=edge_tts.Communicate(text,voice,rate=f"{rate:+d}%",pitch=f"{pitch:+d}Hz")
    out=bytearray()
    async for chunk in job.stream():
        if chunk.get("type")=="audio": out.extend(chunk.get("data",b""))
    if not out: raise RuntimeError("TTS audio return nahi hua. Internet/voice availability check karein.")
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
    with tempfile.NamedTemporaryFile(suffix=".mp3",delete=False) as f:
        f.write(data); name=f.name
    try: return MP3(name).info.length
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
            wav=AudioSegment.from_file(io.BytesIO(data),format="mp3")
            buf=io.BytesIO(); wav.export(buf,format="wav")
            st.download_button("⬇️ WAV",buf.getvalue(),name+".wav","audio/wav",key="wav"+name)
        except Exception as e: st.warning(f"WAV conversion unavailable: {e}")
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
       {"role":"system","content":f"Translate accurately into {target}. Preserve meaning, names, numbers and paragraphs. For Sindhi use standard Sindhi script. Return only translation."},
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

st.warning("Sindhi note: free Edge catalogue mein dedicated Sindhi neural voice guaranteed nahi. Sindhi option Urdu Asad/Uzma fallback use karta hai; pure Sindhi pronunciation guaranteed nahi.")
voice_tab,trans_tab,help_tab=st.tabs(["🎙️ VOICE STUDIO","🌐 TRANSLATOR","ℹ️ GUIDE"])

with voice_tab:
    st.subheader("Five independent voice boxes")
    for n in range(1,6):
      with st.expander(f"BOX {n}",expanded=(n==1)):
        l,r=st.columns([1.5,1])
        with l:
          language=st.selectbox("Language",list(LANGS),index=list(LANGS).index("Urdu (اردو)"),key=f"lang{n}")
          script=st.text_area("Text / Script",value="السلام علیکم! MEHAR WORLD STUDIO میں خوش آمدید۔" if n==1 else "",height=125,key=f"text{n}")
          # --- AUTO TRANSLATE WALA NAYA OPTION ---
          auto_trans = st.checkbox("🔄 Auto Translate karke bolo", value=False, key=f"auto{n}", help="Agar text doosri language mein hai to pehle isi language mein translate hoga, phir bolega. Is ke liye Groq Key chahiye.")
          engine=st.radio("Engine",["Free Edge TTS","ElevenLabs Pro"],horizontal=True,key=f"engine{n}")
        with r:
          gender=st.selectbox("Voice category",["Male","Female"],key=f"gender{n}")
          style=st.selectbox("Character style",list(STYLES),key=f"style{n}")
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
              final_text = script
              # --- AUTO TRANSLATE LOGIC ---
              if auto_trans:
                  if not groq_key:
                      st.warning("Auto Translate ke liye Groq Key nahi hai, is liye original text hi bola ja raha hai.")
                  else:
                      with st.spinner(f"Auto Translate ho raha hai -> {language}..."):
                          final_text = groq_translate(script, language, groq_key, groq_model)
                      st.info(f"Translated: {final_text[:200]}")
              use_engine = engine
              if engine=="ElevenLabs Pro" and (not eleven_key or not eleven_id):
                  st.warning("ElevenLabs key / Voice ID khali hai, is liye Free Edge TTS use ho raha hai.")
                  use_engine = "Free Edge TTS"
              with st.spinner("Voice generate ho rahi hai..."):
                if use_engine=="Free Edge TTS":
                  voice,is_sd_fallback=choose_voice(language,gender,selected)
                  audio=run_async(make_edge(final_text,voice,max(-50,min(50,sr+rate)),max(-50,min(50,sp+pitch))))
                else:
                  is_sd_fallback=False
                  audio=make_eleven(final_text,eleven_key,eleven_id,eleven_model)
              if is_sd_fallback:
                st.warning("Sindhi text Urdu voice se read hua. Yeh fallback hai, genuine Sindhi TTS nahi.")
              st.success(f"BOX {n}: Audio ready!")
              downloads(audio,final_text,f"MEHAR_V104_BOX{n}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            except Exception as e: st.error(f"Voice generation failed: {e}")

with trans_tab:
    st.subheader("Universal Translator")
    st.caption("Translator ke liye Groq key chahiye; translated text ki voice Free Edge TTS se ban sakti hai.")
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
      tl,tr=st.columns(2)
      with tl:
        voice_lang=st.selectbox("Voice language",list(LANGS),key="transvoice")
        voice_gender=st.selectbox("Voice gender",["Male","Female"],key="transgender")
      with tr:
        voice_style=st.selectbox("Voice style",list(STYLES),key="transstyle")
      if st.button("🎧 SPEAK TRANSLATION"):
        try:
          voice,fallback=choose_voice(voice_lang,voice_gender)
          rr,pp=STYLES[voice_style]
          audio=run_async(make_edge(translated,voice,rr,pp))
          if fallback: st.warning("Sindhi output Urdu voice fallback hai; pronunciation guaranteed nahi.")
          downloads(audio,translated,f"MEHAR_TRANSLATION_{int(time.time())}")
        except Exception as e: st.error(f"Translation voice failed: {e}")

with help_tab:
    st.markdown("""
### FREE
- Supported Edge TTS languages: no API key needed; internet required.
- Male/Female voice selection where catalogue offers them.
- MP3, WAV conversion and estimated sentence-level SRT.
- 5 separate text-to-voice boxes.
### AUTO TRANSLATE
- Voice Box mein 'Auto Translate karke bolo' tick karo to text pehle Groq se translate hoga, phir bolega.
- Is ke liye Groq API Key sidebar mein zaroori hai.
### SINDHI
- Pehle asli sd-PK voice dhoondi jati hai, na mile to Urdu Asad/Uzma fallback use hota hai.
- For authentic Sindhi, use a provider that explicitly supports Sindhi and configure its voice ID.
### CHARACTER STYLES
Baby, Old Man, Old Woman, Deep Male and Bright Female are rate/pitch simulations, not actual age-specific voices.
### PRO
ElevenLabs is optional and may incur charges according to your plan. Configure API key and Voice ID.
Groq is only used for translation; it is not needed for free TTS.
""")
st.divider()
st.caption("MEHAR V104 WORLD STUDIO — fresh build; V102/V103 originals remain untouched.")
