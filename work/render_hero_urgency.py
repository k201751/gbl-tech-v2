import argparse, math, subprocess
from pathlib import Path
import imageio_ffmpeg, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT=Path(r"D:\Dev-Projects\gbl-tech-v2"); ASSETS=ROOT/"assets"; WORK=ROOT/"work"
SOURCES=[WORK/f"hero-urgency-{n}.png" for n in ("person","lens","impact")]
MEDIUM=ASSETS/"font-work-sans-500.ttf"; BOLD=ASSETS/"font-work-sans-700.ttf"
FPS=24; DURATION=13.2
PLUM=(13,8,18); WHITE=(247,240,244); CORAL=(242,95,69); LAVENDER=(174,137,255)

def clamp(v): return max(0.0,min(1.0,v))
def smooth(v): v=clamp(v); return v*v*(3-2*v)
def ease(v): v=clamp(v); return 1-(1-v)**3
def prog(t,a,b): return clamp((t-a)/(b-a))

def cover(img,size,p,fx=.5,fy=.5,zoom=.06,drift=0):
    w,h=size; scale=max(w/img.width,h/img.height)*(1+zoom*p)
    rw,rh=max(w,round(img.width*scale)),max(h,round(img.height*scale))
    img=img.resize((rw,rh),Image.Resampling.LANCZOS)
    fx=clamp(fx+drift*(p-.5)); x=max(0,min(rw-w,round((rw-w)*fx))); y=max(0,min(rh-h,round((rh-h)*fy)))
    return img.crop((x,y,x+w,y+h))

def vignette(size):
    w,h=size; yy,xx=np.ogrid[:h,:w]; nx=(xx-w/2)/(w/2); ny=(yy-h/2)/(h/2)
    alpha=np.uint8(np.clip((np.sqrt(nx*nx+ny*ny)-.28)/.82,0,1)*150)
    layer=Image.new("RGBA",size,(0,0,0,255)); layer.putalpha(Image.fromarray(alpha,"L")); return layer

def background(t,size,portrait,src):
    a=cover(src[0],size,ease(prog(t,0,3.5)),.68 if portrait else .52,.5,.075,.10)
    b=cover(src[1],size,smooth(prog(t,2.8,7.7)),.72 if portrait else .57,.51,.14,-.06)
    c=cover(src[2],size,ease(prog(t,7.1,DURATION)),.54 if portrait else .46,.5,.09,.05)
    frame=Image.blend(a,b,smooth(prog(t,2.72,3.55))); frame=Image.blend(frame,c,smooth(prog(t,6.95,7.92)))
    dim=smooth(prog(t,5.65,6.35))*(1-smooth(prog(t,7.2,8.05)))
    if dim: frame=Image.blend(frame,Image.new("RGB",size,PLUM),dim*.73)
    frame=frame.convert("RGBA")
    if 1.1<=t<=5.9:
        p=smooth(prog(t,1.1,5.9)); y=size[1]*(.48 if portrait else .46); width=max(2,round(size[1]*(.012-.007*p)))
        line=Image.new("RGBA",size,(0,0,0,0))
        ImageDraw.Draw(line).line((size[0]*(.15+.28*p),y,size[0]*(.96-.25*p),y),fill=(*CORAL,round(150*(1-p*.35))),width=width)
        frame=Image.alpha_composite(frame,line.filter(ImageFilter.GaussianBlur(max(5,width*2))))
    if 3.4<=t<=8:
        p=prog(t,3.4,8); cx=size[0]*(.73 if portrait else .70); cy=size[1]*.51
        rings=Image.new("RGBA",size,(0,0,0,0)); draw=ImageDraw.Draw(rings); base=min(size)*(.12+p*.09)
        for i,color in enumerate((CORAL,LAVENDER,WHITE)):
            r=base+i*min(size)*.045; alpha=round((70-i*18)*math.sin(math.pi*p))
            draw.ellipse((cx-r,cy-r,cx+r,cy+r),outline=(*color,max(0,alpha)),width=max(1,round(min(size)*.0025)))
        frame=Image.alpha_composite(frame,rings.filter(ImageFilter.GaussianBlur(1.2)))
    return Image.alpha_composite(frame,vignette(size)).convert("RGB")

def font_for(text,maximum,max_width):
    for size in range(maximum,19,-2):
        font=ImageFont.truetype(str(BOLD),size)
        if font.getbbox(text)[2]<=max_width: return font
    return ImageFont.truetype(str(BOLD),20)

def text_layer(size,text,font,xy,color,alpha,blur,spacing=0):
    layer=Image.new("RGBA",size,(0,0,0,0)); draw=ImageDraw.Draw(layer); x,y=xy
    if spacing:
        for ch in text:
            draw.text((x,y),ch,font=font,fill=(*color,alpha),anchor="la"); x+=draw.textlength(ch,font=font)+spacing
    else: draw.text((x,y),text,font=font,fill=(*color,alpha),anchor="la")
    return layer.filter(ImageFilter.GaussianBlur(blur)) if blur>.1 else layer

def typography(frame,t,portrait):
    w,h=frame.size; canvas=frame.convert("RGBA"); left=round(w*.075); max_width=round(w*(.86 if portrait else .72)); center=round(h*(.62 if portrait else .60))
    scenes=((.35,3.05,"YOU JUST LOST A","CLIENT",WHITE),(3.25,5.75,"IN JUST","3 SECONDS",CORAL),(5.95,7.70,"","REASON?",WHITE),(7.90,14.00,"YOUR WEBSITE WASN'T THAT","IMPACTFUL",LAVENDER))
    for start,end,small,large,color in scenes:
        if not start-.15<=t<=end+.05: continue
        enter=ease((t-start)/.62); leave=smooth((t-(end-.45))/.45); alpha=round(255*enter*(1-leave))
        if alpha<=0: continue
        blur=13*(1-enter)+8*leave; shift=round(22*(1-enter)-12*leave)
        if portrait: big_max,small_size=(118 if len(large)<=7 else 88),25; top=center-(80 if small else 25)
        else: big_max,small_size=(188 if len(large)<=7 else 142),30; top=center-(102 if small else 45)
        big=font_for(large,big_max,max_width); small_font=ImageFont.truetype(str(MEDIUM),small_size)
        if small:
            canvas=Image.alpha_composite(canvas,text_layer(frame.size,small,small_font,(left,top+shift),WHITE,round(alpha*.92),blur*.72,round(small_size*.16)))
            big_y=top+(61 if portrait else 76)
        else: big_y=top
        if blur>1:
            echo=CORAL if color!=CORAL else LAVENDER
            canvas=Image.alpha_composite(canvas,text_layer(frame.size,large,big,(left+round(blur*.55),big_y+shift),echo,round(alpha*.18),blur*1.15))
        canvas=Image.alpha_composite(canvas,text_layer(frame.size,large,big,(left,big_y+shift),color,alpha,blur))
        resolved=smooth((t-start-.38)/.42)*(1-smooth((t-end+.35)/.35))
        if resolved:
            length=round((52 if portrait else 74)*resolved); y=big_y+big.size*1.02
            ImageDraw.Draw(canvas).line((left,y,left+length,y),fill=(*CORAL,round(210*resolved)),width=3 if portrait else 4)
    return canvas.convert("RGB")

def frame_at(t,size,portrait,src,index):
    frame=typography(background(t,size,portrait,src),t,portrait); px=np.asarray(frame,dtype=np.int16)
    noise=np.random.default_rng(1804+index).normal(0,2.25,px.shape[:2])[:,:,None]
    return Image.fromarray(np.clip(px+noise,0,255).astype(np.uint8),"RGB")

def render(orientation,preview=False):
    portrait=orientation=="portrait"; size=(720,1280) if portrait else (1440,810); src=tuple(Image.open(p).convert("RGB") for p in SOURCES)
    suffix="-mobile" if portrait else ""; output=ASSETS/f"hero-urgency{suffix}.mp4"; poster=ASSETS/f"hero-urgency-poster{suffix}.jpg"
    if preview:
        times=(1.4,4.1,6.65,9.2,11.0,12.6); thumbs=[]
        for i,t in enumerate(times):
            image=frame_at(t,size,portrait,src,round(t*FPS)); tw=190 if portrait else 360
            thumbs.append(image.resize((tw,round(tw*size[1]/size[0])),Image.Resampling.LANCZOS))
        sheet=Image.new("RGB",(thumbs[0].width*3,thumbs[0].height*2),PLUM)
        for i,thumb in enumerate(thumbs): sheet.paste(thumb,((i%3)*thumb.width,(i//3)*thumb.height))
        path=WORK/f"hero-urgency-preview{suffix}.jpg"; sheet.save(path,quality=92); print(path); return
    ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    cmd=[ffmpeg,"-y","-f","rawvideo","-vcodec","rawvideo","-pix_fmt","rgb24","-s",f"{size[0]}x{size[1]}","-r",str(FPS),"-i","-","-an","-c:v","libx264","-preset","medium","-crf","21","-profile:v","high","-pix_fmt","yuv420p","-movflags","+faststart",str(output)]
    process=subprocess.Popen(cmd,stdin=subprocess.PIPE); total=round(DURATION*FPS)
    for i in range(total):
        process.stdin.write(np.asarray(frame_at(i/FPS,size,portrait,src,i),dtype=np.uint8).tobytes())
        if i%FPS==0: print(f"{orientation}: {i//FPS:02d}/{math.ceil(DURATION)}s",flush=True)
    process.stdin.close()
    if process.wait(): raise SystemExit("ffmpeg failed")
    frame_at(1.45,size,portrait,src,round(1.45*FPS)).save(poster,quality=92,subsampling=0)
    print(output); print(poster)

if __name__=="__main__":
    parser=argparse.ArgumentParser(); parser.add_argument("orientation",choices=("landscape","portrait")); parser.add_argument("--preview",action="store_true")
    args=parser.parse_args(); render(args.orientation,args.preview)


