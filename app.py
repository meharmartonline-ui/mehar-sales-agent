import streamlit as st
import edge_tts, asyncio, os, re, time, tempfile, requests, subprocess, shutil, urllib.parse
from datetime import datetime

try:
    from mutagen.mp3 import MP3
except Exception:
    MP3 = None

st.set_page_config(page_title="MEHAR V106 - AUTO TRANSLATE BOX", page_icon="🌍", layout="centered")
st.title("🌍 MEHAR V106")
st.caption("Jo likhoge wo auto translate hoke usi language me bolega • 1 Box")

# ============ SINDHI ============
def clean_sindhi(text):
    if not text: return text
    fixes = {"ک":"ڪ","ی":"ي","ے":"ي","ہ":"ھ","کے":"ڪي","کی":"ڪي","کا":"ڪا","ھے":"آھي","ہے":"آھي","ھیں":"آھن","تک":"تائين","کیا":"ڪيا","کون":"ڪون"}
    for u,s in fixes.items(): text=text.replace(u,s)
    return re.sub(r"\s+"," ",text).strip()

def make_sindhi_clear(text):
    text=clean_sindhi(text)
    sentences=[s.strip() for s in text.replace("\n","۔").split("۔") if s.strip()]
    chunks=[]
    for s in sentences:
        s=s+"۔"
        if len(s)<=190: chunks.append(s)
        else:
            parts=s.split(","); cur=""
            for p in parts:
                if len(cur)+len(p)>180 and cur: chunks.append(cur.strip()); cur=p
                else: cur=cur+","+p if cur else p
            if cur: chunks.append(cur.strip())
    if not chunks: chunks=[text]
    tmpdir=tempfile.mkdtemp(); mp3_files=[]; headers={"User-Agent":"Mozilla/5.0"}
    for i,ch in enumerate(chunks):
        q=urllib.parse.quote(ch)
        url=f"https://translate.google.com/translate_tts?ie=UTF-8&q={q}&tl=sd&client=tw-ob"
        r=requests.get(url,headers=headers,timeout=20)
        if r.status_code!=200 or len(r.content)<500:
            time.sleep(1); r=requests.get(url,headers=headers,timeout=20)
        if len(r.content)<500: raise RuntimeError(f"Sindhi awaz fail jumla {i+1}")
        p=os.path.join(tmpdir,f"part{i}.mp3")
        with open(p,"wb") as f: f.write(r.content)
        mp3_files.append(p); time.sleep(0.4)
    if len(mp3_files)==1:
        with open(mp3_files[0],"rb") as f: return f.read(), text
    list_path=os.path.join(tmpdir,"list.txt")
    with open(list_path,"w",encoding="utf-8") as f:
        for p in mp3_files: f.write(f"file '{p}'\n")
    out_path=os.path.join(tmpdir,"final.mp3")
    res=subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",list_path,"-c","copy",out_path],capture_output=True,timeout=60)
    if res.returncode==0 and os.path.exists(out_path):
        with open(out_path,"rb") as f: return f.read(), text
    raise RuntimeError("ffmpeg nahi mila. packages.txt me ffmpeg likh ke Reboot karo.")

# ============ LANGUAGES + VOICES ============
LANGS = {
 "Sindhi (سنڌي)":"sd","Urdu (اردو)":"ur","Hindi (हिन्दी)":"hi","English":"en",
 "Arabic (العربية)":"ar","Roman Urdu":"ur","French":"fr","Spanish":"es","German":"de",
 "Italian":"it","Portuguese":"pt","Turkish":"tr","Chinese":"zh","Japanese":"ja",
 "Korean":"ko","Bengali":"bn","Punjabi":"pa","Pashto":"ps","Persian":"fa",
 "Russian":"ru","Indonesian":"id","Malay":"ms","Thai":"th","Vietnamese":"vi",
 "Dutch":"nl","Polish":"pl","Swedish":"sv","Greek":"el","Hebrew":"he",
 "Tamil":"ta","Telugu":"te","Marathi":"mr","Gujarati":"gu","Nepali":"ne"
}
# Har language ki Male / Female awaz
VOICES = {
 "sd":("ur-PK-AsadNeural","ur-PK-UzmaNeural"),
 "ur":("ur-PK-AsadNeural","ur-PK-UzmaNeural"),
 "hi":("hi-IN-MadhurNeural","hi-IN-SwaraNeural"),
 "en":("en-US-GuyNeural","en-US-JennyNeural"),
 "ar":("ar-SA-HamedNeural","ar-SA-ZariyahNeural"),
 "fr":("fr-FR-HenriNeural","fr-FR-DeniseNeural"),
 "es":("es-ES-AlvaroNeural","es-ES-ElviraNeural"),
 "de":("de-DE-ConradNeural","de-DE-KatjaNeural"),
 "it":("it-IT-DiegoNeural","it-IT-ElsaNeural"),
 "pt":("pt-BR-AntonioNeural","pt-BR-FranciscaNeural"),
 "tr":("tr-TR-AhmetNeural","tr-TR-EmelNeural"),
 "zh":("zh-CN-YunyangNeural","zh-CN-XiaoxiaoNeural"),
 "ja":("ja-JP-KeitaNeural","ja-JP-NanamiNeural"),
 "ko":("ko-KR-InJoonNeural","ko-KR-SunHiNeural"),
 "bn":("bn-IN-BashkarNeural","bn-IN-TanishaaNeural"),
 "pa":("pa-IN-GurpreetNeural","pa-IN-VanitaNeural"),
 "ps":("ps-AF-LatifullahNeural","ps-AF-GulnaraNeural"),
 "fa":("fa-IR-FaridNeural","fa-IR-DilaraNeural"),
 "ru":("ru-RU-DmitryNeural","ru-RU-SvetlanaNeural"),
 "id":("id-ID-ArdiNeural","id-ID-GadisNeural"),
 "ms":("ms-MY-OsmanNeural","ms-MY-YasminNeural"),
 "th":("th-TH-NiwatNeural","th-TH-PremwadeeNeural"),
 "vi":("vi-VN-NamMinhNeural","vi-VN-HoaiMyNeural"),
 "nl":("nl-NL-MaartenNeural","nl-NL-ColetteNeural"),
 "pl":("pl-PL-MarekNeural","pl-PL-ZofiaNeural"),
 "sv":("sv-SE-MattiasNeural","sv-SE-SofieNeural"),
 "el":("el-GR-NestorasNeural","el-GR-AthinaNeural"),
 "he":("he-IL-AvriNeural","he-IL-HilaNeural"),
 "ta":("ta-IN-ValluvarNeural","ta-IN-PallaviNeural"),
 "te":("te-IN-MohanNeural","te-IN-ShrutiNeural"),
 "mr":("mr-IN-ManoharNeural","mr-IN-AarohiNeural"),
 "gu":("gu-IN-NiranjanNeural","gu-IN-DhwaniNeural"),
 "ne":("ne-NP-SagarNeural","ne-NP-HemkalaNeural"),
}

def secret(name):
    v=os.getenv(name,"")
    try:
        if not v and hasattr(st,"secrets"): v=st.secrets.get(name,"")
    except Exception: pass
    return str(v).strip()

def run_async(coro):
    try: asyncio.get_running_loop()
    except RuntimeError: return asyncio.run(coro)
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex: return ex.submit(asyncio.run,coro).result()

async def make_edge(text, voice, rate, pitch):
    job=edge_tts.Communicate(text,voice,rate=f"{rate:+d}%",pitch=f"{pitch:+d}Hz")
    out=bytearray()
    async for chunk in job.stream():
        if chunk.get("type")=="audio": out.extend(chunk.get("data",b""))
    if not out: raise RuntimeError("TTS audio return nahi hua.")
    return bytes(out)
    def groq_translate(text,target_lang_name,key,model):
    if not key: raise ValueError("Auto Translate ke liye Groq API Key sidebar me dalo.")
    # Jo model band ho gaya ho to doosra try karo
    models_to_try = [model, "openai/gpt-oss-120b", "llama-3.1-8b-instant", "llama-3.3-70b-versatile"]
    # Duplicate hatao
    seen=set(); models=[]
    for m in models_to_try:
        if m not in seen: models.append(m); seen.add(m)
    last_err=""
    for m in models:
        r=requests.post("https://api.groq.com/openai/v1/chat/completions",headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},json={"model":m,"temperature":0.2,"messages":[{"role":"system","content":f"Translate the given text accurately into {target_lang_name}. If text is already in {target_lang_name}, just return it cleaned with correct alphabet. For Sindhi use correct alphabet: ڪ for k, ک for kh, ٻ ڄ ڏ ڳ for implosives, ڃ ڱ ڻ for nasals, ي for y, ھ for h. For Urdu use Urdu alphabet. For Hindi use Devanagari. Preserve meaning, names, numbers, paragraphs. Return ONLY translation, no explanation."},{"role":"user","content":text}]},timeout=90)
        if r.status_code==200:
            return r.json()["choices"][0]["message"]["content"].strip()
        last_err=f"Groq {r.status_code}: {r.text[:300]}"
        if "model_not_found" not in r.text and r.status_code!=404:
            break
    raise RuntimeError(last_err)

def expand_to_duration(text,target):
    m={"15 Second":15,"30 Second":30,"1 Minute":60,"2 Minute":120,"5 Minute":300,"10 Minute":600}
    if target not in m: return text
    need=m[target]*13
    if len(text)>=need:
        cut=text[:need]; last=cut.rfind("۔")
        if last>100: cut=cut[:last+1]
        return cut
    times=int(need/max(1,len(text)))+1
    return (" ۔ "+text).join([text]*times)[:need+200]

def duration(data):
    if MP3 is None: return 10.0
    with tempfile.NamedTemporaryFile(suffix=".mp3",delete=False) as f: f.write(data); name=f.name
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
        rows+=[str(i),f"{stamp(cur)} --> {stamp(end)}",part,""]; cur=end
    return "\n".join(rows)

def downloads(data,text,name):
    st.audio(data,format="audio/mp3")
    a,b,c=st.columns(3)
    with a: st.download_button("⬇️ MP3",data,name+".mp3","audio/mpeg",key="mp3"+name)
    with b:
        try:
            if shutil.which("ffmpeg") is None: st.download_button("⬇️ WAV (MP3)",data,name+".mp3","audio/mpeg",key="wav"+name)
            else:
                with tempfile.NamedTemporaryFile(suffix=".mp3",delete=False) as f: f.write(data); mp3_path=f.name
                wav_path=mp3_path+".wav"
                res=subprocess.run(["ffmpeg","-y","-i",mp3_path,wav_path],capture_output=True,timeout=30)
                if res.returncode==0 and os.path.exists(wav_path) and os.path.getsize(wav_path)>100:
                    with open(wav_path,"rb") as wf: wav_bytes=wf.read()
                    st.download_button("⬇️ WAV",wav_bytes,name+".wav","audio/wav",key="wav"+name)
                else: st.download_button("⬇️ WAV (MP3)",data,name+".mp3","audio/mpeg",key="wav"+name)
                try: os.remove(mp3_path)
                except OSError: pass
                try:
                    if os.path.exists(wav_path): os.remove(wav_path)
                except OSError: pass
        except Exception: st.download_button("⬇️ WAV (MP3)",data,name+".mp3","audio/mpeg",key="wav"+name)
    with c:
        try:
            subs=srt_text(text,duration(data))
            st.download_button("📝 SRT",subs.encode(),name+".srt","text/plain",key="srt"+name)
        except Exception as e: st.warning(f"SRT error: {e}")

# ============ SIDEBAR ============
with st.sidebar:
    st.header("⚙️ Settings")
    groq_key=st.text_input("Groq API Key (Auto Translate)",secret("GROQ_API_KEY"),type="password")
    groq_model=st.text_input("Groq model","llama-3.3-70b-versatile")
    st.info("Groq Key hogi to jo bhi likhoge wo us language me translate hoga jo tum select karoge.")

# ============ SINGLE BOX ============
st.subheader("🎙️ 1 BOX - Likho / Paste Karo")

language=st.selectbox("👉 Kis Language me chahiye? (Isi me translate hoga + isi ki awaz banegi)",list(LANGS),index=0)
script=st.text_area("✍️ Yahan likho ya paste karo - Sindhi / Urdu / English / Roman koi bhi",height=200,placeholder="Yahan paste karo... jo bhi likhoge wo upar wali language me auto translate ho jayega")

c1,c2,c3=st.columns(3)
with c1:
    auto_trans=st.checkbox("🔄 Auto Translate ON",value=True)
    target_time=st.selectbox("⏱️ Target Time",["Auto (Text jitna hai)","15 Second","30 Second","1 Minute","2 Minute","5 Minute","10 Minute"])
with c2:
    gender=st.selectbox("Voice",["Male","Female"])
    style=st.selectbox("Style",["Normal","Young Adult","Baby / Child-like (simulation)","Old Man (simulation)","Old Woman (simulation)","Deep Male (simulation)","Bright Female (simulation)","Calm Narrator","Energetic"])
with c3:
    rate=st.slider("Speed",-25,25,0)
    pitch=st.slider("Pitch",-15,15,0)

if st.button("▶️ GENERATE - Translate + Voice",type="primary",use_container_width=True):
    if not script.strip(): st.error("Pehle text likho ya paste karo.")
    else:
        try:
            final_text=script.strip()
            # STEP 1: AUTO TRANSLATE - Jo likha hai usko selected language me badlo
            if auto_trans:
                if not groq_key:
                    st.warning("Groq Key nahi hai, is liye bina translate kiye hi bol raha hun. Key dalo to Auto Translate chalega.")
                else:
                    with st.spinner(f"Auto Translate ho raha hai -> {language}..."):
                        final_text=groq_translate(final_text,language,groq_key,groq_model)
                    st.success(f"✅ Translated to {language}:")
                    st.text_area("Translated Text - Ye ab bolega",final_text,height=120)
            # STEP 2: TIME
            final_text=expand_to_duration(final_text,target_time)
            # STEP 3: VOICE - Usi language ki awaz
            with st.spinner(f"Voice ban rahi hai - {language}..."):
                lang_code=LANGS[language]
                if lang_code=="sd":
                    audio, final_text = make_sindhi_clear(final_text)
                else:
                    voice = VOICES.get(lang_code,("en-US-GuyNeural","en-US-JennyNeural"))[0 if gender=="Male" else 1]
                    audio = run_async(make_edge(final_text,voice,rate,pitch))
            st.success(f"✅ Voice Ready - {language}")
            downloads(audio,final_text,f"MEHAR_V106_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        except Exception as e: st.error(f"Failed: {e}")

st.divider()
st.caption("MEHAR V106 • Likho kuch bhi -> Translate usi language me -> Voice usi language ki")
