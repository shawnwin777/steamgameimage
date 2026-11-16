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
def main():
    p=argparse.ArgumentParser();p.add_argument("app");p.add_argument("--output-dir",default="output");a=p.parse_args()
    ident=appid(a.app)
    d=get("https://store.steampowered.com/api/appdetails",{"appids":ident,"cc":"tw","l":"tchinese"}).json()[ident]
    if not d["success"]:raise RuntimeError("Steam data missing")
    d=d["data"]
    out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
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
    info={"name":d["name"],"app_id":ident,"original":original,"current":current,"discount":discount,"end":end,"review":review,"traditional_chinese":"待確認","sources":sources}
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
    concat=out/"frames.ffconcat"
    concat.write_text("ffconcat version 1.0\n"+"".join("file '"+str(f.resolve())+"'\nduration 2.5\n" for f in frames)+"file '"+str(frames[-1].resolve())+"'\n")
    cmd=["ffmpeg","-y","-loglevel","error","-safe","0","-f","concat","-i",str(concat)]
    if voice_ok:cmd+=["-i",str(mp3)]
    cmd+=["-vf","fps=30,format=yuv420p","-t","10","-c:v","libx264","-preset","veryfast","-crf","22","-movflags","+faststart"]
    cmd+=(["-af","apad","-c:a","aac"] if voice_ok else ["-an"])
    cmd.append(str(out/"SGS_10sec.mp4"))
    subprocess.run(cmd,check=True)
    print("Created:",out/"SGS_10sec.mp4")
if __name__=="__main__":main()
