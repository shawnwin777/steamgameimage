import argparse, asyncio, io, json, re, subprocess
from pathlib import Path
from urllib.parse import urlparse
import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps

def appid(x):
    if re.fullmatch(r"\d{3,10}",x): return x
    u=urlparse(x); m=re.match(r"/app/(\d{3,10})",u.path)
    if u.hostname!="store.steampowered.com" or not m: raise ValueError("Steam app URL required")
    return m.group(1)
def get(url,params=None):
    r=requests.get(url,params=params,timeout=30,headers={"User-Agent":"Mozilla/5.0"});r.raise_for_status();return r
def textfont(size):
    for path in ["/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc","/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        if Path(path).exists():return ImageFont.truetype(path,size)
    return ImageFont.load_default()

def official_movie(d,out):
    """Download only an explicitly advertised Steam MP4, with source validation."""
    candidates=[]
    for movie in d.get("movies",[]):
        mp4=movie.get("mp4") or {}
        for key in ("max","480"):
            url=mp4.get(key)
            if isinstance(url,str) and url not in candidates:candidates.append(url)
    notes={"candidates":len(candidates),"status":"not_available","source_url":None,"error":None}
    for url in candidates:
        host=(urlparse(url).hostname or "").lower()
        if not (host=="steamstatic.com" or host.endswith(".steamstatic.com") or host=="steamcontent.com" or host.endswith(".steamcontent.com")):
            continue
        target=out/"official_trailer.mp4"
        try:
            with requests.get(url,stream=True,timeout=(15,45),headers={"User-Agent":"Mozilla/5.0"}) as r:
                r.raise_for_status()
                finalhost=(urlparse(r.url).hostname or "").lower()
                if not (finalhost=="steamstatic.com" or finalhost.endswith(".steamstatic.com") or finalhost=="steamcontent.com" or finalhost.endswith(".steamcontent.com")):
                    raise ValueError("Unexpected trailer redirect: "+finalhost)
                size=0
                with target.open("wb") as fh:
                    for chunk in r.iter_content(1024*1024):
                        if not chunk:continue
                        size+=len(chunk)
                        if size>100_000_000:raise ValueError("Trailer too large")
                        fh.write(chunk)
            probe=subprocess.run(["ffprobe","-v","error","-show_entries","stream=codec_type","-show_entries","format=duration","-of","json",str(target)],check=True,capture_output=True,text=True,timeout=30)
            meta=json.loads(probe.stdout)
            dur=float(meta.get("format",{}).get("duration",0))
            if dur<2 or not any(v.get("codec_type")=="video" for v in meta.get("streams",[])):raise ValueError("Invalid trailer video")
            notes.update({"status":"downloaded","source_url":url,"duration_seconds":dur,"bytes":size})
            return target,notes
        except Exception as exc:
            notes["error"]=str(exc)[:250]
            target.unlink(missing_ok=True)
            print("Official trailer download failed:",exc,flush=True)
    return None,notes

def main():
    p=argparse.ArgumentParser();p.add_argument("app");p.add_argument("--output-dir",default="output");a=p.parse_args()
    ident=appid(a.app)
    d=get("https://store.steampowered.com/api/appdetails",{"appids":ident,"cc":"tw","l":"tchinese"}).json()[ident]
    if not d["success"]:raise RuntimeError("Steam data missing")
    d=d["data"]
    out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
    trailer,trailer_info=official_movie(d,out)
    print("Trailer probe result:",json.dumps(trailer_info,ensure_ascii=False),flush=True)
    shots=[];sources=[]
    for shot in d.get("screenshots",[]):
        u=shot.get("path_full","")
        if not u.startswith("https://"):continue
        try:
            im=Image.open(io.BytesIO(get(u).content));im.load()
            if im.width<640 or im.height<360:continue
            shots.append(im.convert("RGB"));sources.append(u)
            if len(shots)==4:break
        except Exception as exc:print("Image failed:",exc)
    if len(shots)<4:raise RuntimeError("Four real screenshots required; none fabricated")
    try:
        q=get("https://store.steampowered.com/appreviews/"+ident,{"json":1,"filter":"all","language":"all","purchase_type":"all","num_per_page":0}).json()["query_summary"]
        review={"Mostly Positive":"大多好評","Very Positive":"極度好評","Mixed":"意見不一","Overwhelmingly Positive":"壓倒性好評"}.get(q.get("review_score_desc"),q.get("review_score_desc","未提供"))
    except Exception:review="未提供"
    price=d.get("price_overview") or {}
    free=d.get("is_free",False);original="免費遊玩" if free else price.get("initial_formatted","未提供")
    current="免費遊玩" if free else price.get("final_formatted","未提供")
    pct=price.get("discount_percent",0)
    discount="無" if free or not pct else "-"+str(pct)+"%"
    end="不適用" if free or not pct else "未提供"
    info={"media_mode":"official_trailer" if trailer else "official_screenshots","trailer":trailer_info,"name":d["name"],"app_id":ident,"original":original,"current":current,"discount":discount,"end":end,"review":review,"traditional_chinese":"待確認","sources":sources}
    # Do not infer Traditional Chinese support without a verified language table.
    try:
        from bs4 import BeautifulSoup
        soup=BeautifulSoup(get("https://store.steampowered.com/app/"+ident+"/",{"l":"tchinese","cc":"tw"}).text,"html.parser")
        for tr in soup.select("table.game_language_options tr"):
            if "繁體中文" in tr.get_text(" ",strip=True):
                info["traditional_chinese"]="支援" if "checkmark" in str(tr).lower() else "待確認";break
    except Exception:pass
    font=textfont(30);small=textfont(20);large=textfont(38)
    frames=[]
    for i,shot in enumerate(shots):
        canvas=Image.new("RGB",(720,1280),"#0B1018")
        canvas.paste(ImageOps.fit(shot,(720,690),method=Image.Resampling.LANCZOS),(0,0))
        dr=ImageDraw.Draw(canvas)
        dr.rectangle((0,690,720,1280),fill="#162235")
        dr.rectangle((0,690,720,699),fill="#946BFF")
        dr.text((25,715),"SGS // CYBERPUNK GAME INTEL",font=small,fill="#00E5BC")
        dr.text((25,755),info["name"][:21],font=large,fill="white")
        entries=[("原價",original),("現價",current),("折扣",discount),("優惠截止",end),("玩家總評",review),("繁體中文",info["traditional_chinese"])]
        for j,(label,val) in enumerate(entries):
            x=25+j%2*340;y=835+j//2*110
            dr.rounded_rectangle((x,y,x+320,y+100),radius=9,fill="#243448",outline="#946BFF",width=2)
            dr.text((x+12,y+8),label,font=small,fill="white")
            dr.text((x+12,y+45),str(val)[:15],font=font,fill="#00E5BC")
        f=out/("frame"+str(i)+".png");canvas.save(f);frames.append(f)
    # Voice can fail; never misrepresent a silent output as narrated.
    mp3=out/"voice.mp3";voice_ok=False
    narration="SGS 遊戲快訊，"+info["name"]+"，"+current+"，玩家總評"+review+"。"
    try:
        import edge_tts
        asyncio.run(edge_tts.Communicate(narration,"zh-TW-YunJheNeural",rate="+12%").save(str(mp3)))
        voice_ok=mp3.exists() and mp3.stat().st_size>1000
    except Exception as exc:print("Voice failed:",exc)
    info["voice_status"]="generated" if voice_ok else "not_available"
    (out/"source_manifest.json").write_text(json.dumps(info,ensure_ascii=False,indent=2))
    if trailer:
        # Overlay real moving trailer in the top area of the SGS data frame.
        cmd=["ffmpeg","-y","-loglevel","error","-stream_loop","-1","-i",str(trailer),
             "-loop","1","-i",str(frames[0])]
        if voice_ok:cmd+=["-i",str(mp3)]
        cmd+=["-filter_complex",
              "[0:v]scale=720:690:force_original_aspect_ratio=increase,crop=720:690,fps=30,setsar=1[top];"
              "[1:v]fps=30[base];[base][top]overlay=0:0:shortest=0,format=yuv420p[v]",
              "-map","[v]"]
        if voice_ok:cmd+=["-map","2:a:0","-af","apad","-c:a","aac"]
        else:cmd+=["-an"]
    else:
        concat=out/"frames.ffconcat"
        concat.write_text("ffconcat version 1.0\n"+"".join("file '"+str(f.resolve())+"'\nduration 2.5\n" for f in frames)+"file '"+str(frames[-1].resolve())+"'\n")
        cmd=["ffmpeg","-y","-loglevel","error","-safe","0","-f","concat","-i",str(concat)]
        if voice_ok:cmd+=["-i",str(mp3)]
        cmd+=["-vf","fps=30,format=yuv420p"]
        cmd+=(["-af","apad","-c:a","aac"] if voice_ok else ["-an"])
    cmd+=["-t","10","-c:v","libx264","-preset","veryfast","-crf","22","-movflags","+faststart",str(out/"SGS_10sec.mp4")]
    subprocess.run(cmd,check=True)
    print("Created:",out/"SGS_10sec.mp4")
if __name__=="__main__":main()
