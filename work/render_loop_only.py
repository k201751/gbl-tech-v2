from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, random, subprocess, os
W,H,FPS=1280,720,30
BLACK=(0,0,0); INK=(36,7,15); WINE=(82,0,25); CRIMSON=(153,0,47); RASP=(220,20,83); PINK=(242,126,148); BLUSH=(247,220,228)
reg=r'D:\Dev-Projects\gbl-tech-v2\assets\font-work-sans-500.ttf'; bold=r'D:\Dev-Projects\gbl-tech-v2\assets\font-work-sans-700.ttf'; serif=r'D:\Dev-Projects\gbl-tech-v2\assets\font-instrument-serif-italic.ttf'
ff=r'C:\Users\Ali\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
out_intro=r'D:\Dev-Projects\gbl-tech-v2\assets\hero-urgency-intro.mp4'; out_loop=r'D:\Dev-Projects\gbl-tech-v2\assets\hero-interface-loop.mp4'; poster=r'D:\Dev-Projects\gbl-tech-v2\assets\hero-urgency-final-poster.jpg'
def clamp(v,a=0,b=1):return max(a,min(b,v))
def ease(v):v=clamp(v);return 1-(1-v)**3
def smooth(v):v=clamp(v);return v*v*(3-2*v)
def tw(draw,text,font,spacing):return sum(draw.textlength(c,font=font) for c in text)+spacing*(len(text)-1)
def tracked(draw,text,y,font,fill,spacing=0,x=W/2):
    cur=x-tw(draw,text,font,spacing)/2
    for c in text:
        draw.text((cur,y),c,font=font,fill=fill,anchor='lm');cur+=draw.textlength(c,font=font)+spacing
def centered_layer(top,big,big_size=150,top_size=27,big_color=BLUSH):
    l=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(l)
    tracked(d,top,286,ImageFont.truetype(reg,top_size),BLUSH+(255,),7)
    tracked(d,big,382,ImageFont.truetype(bold,big_size),big_color+(255,),-5)
    return l
def scale_center(layer,s):
    nw,nh=int(W*s),int(H*s);r=layer.resize((nw,nh),Image.Resampling.LANCZOS);o=Image.new('RGBA',(W,H));o.alpha_composite(r,((W-nw)//2,(H-nh)//2));return o
def slices(layer,amount):
    o=Image.new('RGBA',(W,H));n=12
    for i in range(n):
        y0=i*H//n;y1=(i+1)*H//n;sl=layer.crop((0,y0,W,y1));dx=int(amount*(1 if i%2 else -1));o.alpha_composite(sl,(dx,y0))
    return o

def ui_card(seed,w=330,h=210):
    rnd=random.Random(seed); palettes=[(WINE,PINK),(INK,RASP),(CRIMSON,BLUSH),(WINE,BLUSH)]
    base,accent=palettes[seed%len(palettes)]; c=Image.new('RGBA',(w,h),base+(255,));d=ImageDraw.Draw(c,'RGBA')
    # browser bar
    d.rectangle((0,0,w,25),fill=(12,0,5,255));d.ellipse((11,9,17,15),fill=PINK+(180,));d.ellipse((23,9,29,15),fill=RASP+(130,));d.rounded_rectangle((45,8,w-16,16),4,fill=BLUSH+(24,))
    variant=seed%4
    if variant==0:
        d.rectangle((18,42,w-18,132),fill=accent+(38,));d.rectangle((32,55,155,65),fill=BLUSH+(205,));d.rectangle((32,75,205,82),fill=BLUSH+(70,));d.rounded_rectangle((32,99,94,119),10,fill=accent+(220,));d.rectangle((188,50,w-35,125),fill=accent+(85,))
    elif variant==1:
        d.rectangle((18,42,150,h-22),fill=accent+(75,));d.rectangle((168,45,w-20,54),fill=BLUSH+(180,));
        for y in (70,92,114,136):d.rounded_rectangle((168,y,w-20,y+13),6,fill=BLUSH+(32+seed%30,))
    elif variant==2:
        d.rectangle((18,42,w-18,72),fill=accent+(110,));
        for i in range(3):
            x=18+i*101;d.rounded_rectangle((x,88,x+88,176),7,fill=BLUSH+(24+i*10,));d.rectangle((x+12,102,x+72,112),fill=accent+(150,));d.rectangle((x+12,124,x+62,130),fill=BLUSH+(60,))
    else:
        d.rectangle((18,42,w-18,113),fill=accent+(55,));d.ellipse((w//2-38,49,w//2+38,125),fill=accent+(150,));d.rectangle((52,139,w-52,149),fill=BLUSH+(180,));d.rectangle((92,164,w-92,172),fill=BLUSH+(55,))
    return c
CARDS=[ui_card(i) for i in range(20)]
def wall_frame(t,entry=1.0):
    im=Image.new('RGBA',(W,H),BLACK+(255,));
    # large plane so rotation/cropping stays full
    plane=Image.new('RGBA',(1840,1160),(8,0,3,255));
    period_x=370;period_y=250; phase=(t%4.0)/4.0
    ox=int(-period_x*phase);oy=int(period_y*phase*.55)
    idx=0
    for row in range(-2,6):
        for col in range(-2,7):
            x=col*period_x+ox+(row%2)*85;y=row*period_y+oy
            card=CARDS[idx%len(CARDS)];idx+=1
            plane.alpha_composite(card,(x,y))
    plane=plane.rotate(-7,resample=Image.Resampling.BICUBIC,expand=True,fillcolor=(0,0,0,255))
    # subtle perspective impression through crop + scale
    crop=plane.crop(((plane.width-W)//2,(plane.height-H)//2,(plane.width+W)//2,(plane.height+H)//2))
    if entry<1:
        s=1.55-.55*ease(entry);crop=scale_center(crop,s);crop.putalpha(int(255*ease(entry)))
    im.alpha_composite(crop)
    # burgundy veil keeps typography dominant
    veil=Image.new('RGBA',(W,H),(20,0,7,95));im=Image.alpha_composite(im,veil)
    d=ImageDraw.Draw(im,'RGBA');tracked(d,'YOUR WEBSITE WASN\'T THAT',282,ImageFont.truetype(reg,25),BLUSH+(255,),7);tracked(d,'IMPACTFUL',382,ImageFont.truetype(bold,140),PINK+(255,),-5)
    return im.convert('RGB')

def intro_frame(t):
    im=Image.new('RGBA',(W,H),BLACK+(255,))
    # 1. abrupt lost-client hit
    if .38<=t<2.65:
        l=centered_layer('YOU LOST A','CLIENT',158)
        q=clamp((t-.38)/.16);s=1.34-.34*ease(q);l=scale_center(l,s)
        if t<.56:l=slices(l,(1-q)*48)
        im=Image.alpha_composite(im,l)
        if .38<=t<.47:
            d=ImageDraw.Draw(im,'RGBA');d.rectangle((0,350,W,354),fill=PINK+(210,))
    # hard blackout / countdown
    elif 2.82<=t<5.95:
        d=ImageDraw.Draw(im,'RGBA');f3=ImageFont.truetype(bold,165);fsmall=ImageFont.truetype(reg,27)
        enter=ease((t-2.82)/.22);tracked(d,'IN JUST',258,fsmall,BLUSH+(int(255*enter),),8)
        tracked(d,'3 SECONDS',378,f3,PINK+(int(255*enter),),-6)
        q=clamp((t-3.0)/2.7);box=(W//2-245,H//2-245,W//2+245,H//2+245)
        d.arc(box,-90,-90+360*(1-q),fill=PINK+(180,),width=4)
        for i in range(12):
            a=-math.pi/2+i*math.tau/12;x=W/2+244*math.cos(a);y=H/2+244*math.sin(a);d.ellipse((x-3,y-3,x+3,y+3),fill=BLUSH+(45,))
    # reason: pure black, still, longer hold
    elif 6.2<=t<8.62:
        d=ImageDraw.Draw(im);f=ImageFont.truetype(serif,150);tracked(d,'REASON?',360,f,BLUSH+(255,),-3)
    # setup line, pure black
    elif 8.78<=t<10.25:
        d=ImageDraw.Draw(im);f=ImageFont.truetype(reg,33);tracked(d,"YOUR WEBSITE WASN'T THAT",360,f,BLUSH+(255,),7)
    # final UI wall begins; abrupt IMPACTFUL hit
    elif t>=10.25:
        return wall_frame(t-10.25,clamp((t-10.25)/.34))
    return im.convert('RGB')

def encode(path,dur,fn):
    cmd=[ff,'-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',path]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.DEVNULL)
    last=None
    for n in range(int(dur*FPS)):
        last=fn(n/FPS);p.stdin.write(last.tobytes())
    p.stdin.close();c=p.wait()
    if c:raise SystemExit(c)
    return last
encode(out_loop,4.0,lambda t:wall_frame(t,1.0))
print(out_loop)

