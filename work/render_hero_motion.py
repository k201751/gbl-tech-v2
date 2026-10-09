from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, random, subprocess, os
W,H,FPS,DUR=1280,720,30,14.4
FRAMES=int(FPS*DUR)
BG=(24,0,8); WINE=(82,0,25); CRIMSON=(153,0,47); RASP=(220,20,83); PINK=(242,126,148); BLUSH=(247,220,228)
font_regular=r'D:\Dev-Projects\gbl-tech-v2\assets\font-work-sans-500.ttf'
font_bold=r'D:\Dev-Projects\gbl-tech-v2\assets\font-work-sans-700.ttf'
font_serif=r'D:\Dev-Projects\gbl-tech-v2\assets\font-instrument-serif-italic.ttf'
ff=r'C:\Users\Ali\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
out=r'D:\Dev-Projects\gbl-tech-v2\assets\hero-lost-client-preview.mp4'
poster=r'D:\Dev-Projects\gbl-tech-v2\assets\hero-lost-client-preview-poster.jpg'

def clamp(x,a=0,b=1): return max(a,min(b,x))
def ease(x):
    x=clamp(x); return x*x*(3-2*x)
def outcubic(x):
    x=clamp(x); return 1-(1-x)**3
def pulse(t,a,b,fade=.22):
    if t<a or t>b:return 0
    return min(1,(t-a)/fade,(b-t)/fade)
def text_width(draw,text,font,spacing=0):
    return sum(draw.textlength(c,font=font) for c in text)+max(0,len(text)-1)*spacing
def tracked(draw,xy,text,font,fill,spacing=0,anchor='center'):
    x,y=xy; total=text_width(draw,text,font,spacing)
    if anchor=='center': x-=total/2
    for c in text:
        draw.text((x,y),c,font=font,fill=fill,anchor='lm')
        x+=draw.textlength(c,font=font)+spacing

def group_text(lines, color=BLUSH):
    layer=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(layer)
    for item in lines:
        text,y,size,spacing,kind=item
        f=ImageFont.truetype(font_serif if kind=='serif' else (font_bold if kind=='bold' else font_regular),size)
        tracked(d,(W/2,y),text,f,color+(255,),spacing,'center')
    return layer

def mask_reveal(layer,p,from_center=True):
    p=ease(p); alpha=layer.getchannel('A'); m=Image.new('L',(W,H),0); d=ImageDraw.Draw(m)
    if from_center:
        hh=int(H*p/2); d.rectangle((0,H//2-hh,W,H//2+hh),fill=255)
    else:d.rectangle((0,0,int(W*p),H),fill=255)
    import PIL.ImageChops as Ch
    layer=layer.copy(); layer.putalpha(Ch.multiply(alpha,m)); return layer

def sliced_exit(layer,p):
    p=ease(p); out=Image.new('RGBA',(W,H),(0,0,0,0)); strips=10
    for i in range(strips):
        y0=i*H//strips; y1=(i+1)*H//strips
        sl=layer.crop((0,y0,W,y1)); dx=int((W*.48+80*i/strips)*p)*(1 if i%2==0 else -1)
        a=int(255*(1-p)); sl.putalpha(sl.getchannel('A').point(lambda v:v*a//255))
        out.alpha_composite(sl,(dx,y0))
    return out

def scene_layer(layer,t,a,hold,exit_end):
    if t<a or t>exit_end:return None
    if t<a+.55:return mask_reveal(layer,(t-a)/.55)
    if t<=hold:return layer
    return sliced_exit(layer,(t-hold)/(exit_end-hold))

f1=group_text([('YOU LOST A',284,28,8,'regular'),('CLIENT',380,150,-5,'bold')])
f2=group_text([('IN JUST',252,26,8,'regular'),('3 SECONDS',370,132,-5,'bold')],PINK)
f3=group_text([('REASON?',355,144,-3,'serif')])
f4small=group_text([("YOUR WEBSITE WASN'T THAT",270,25,6,'regular')])
f4big=group_text([('IMPACTFUL',382,132,-5,'bold')],PINK)

cmd=[ff,'-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',out]
p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.DEVNULL)
last=None
for n in range(FRAMES):
    t=n/FPS
    im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im,'RGBA')
    # tonal field
    d.rectangle((0,0,W,H),fill=(30,0,10,255))
    d.ellipse((-280,-460,650,470),fill=(82,0,25,80))
    d.ellipse((780,330,1500,1050),fill=(153,0,47,46))
    # quiet editorial grid
    for x in range(80,W,160): d.line((x,92,x,H-70),fill=(247,220,228,11),width=1)
    for y in (150,360,570): d.line((50,y,W-50,y),fill=(247,220,228,15),width=1)
    # persistent website journey, builds once and changes after loss
    build=outcubic(t/.75)
    y=360
    end=int(80+(1120*build))
    d.line((80,y,end,y),fill=(242,126,148,60),width=2)
    for x in (260,500,740,980):
        if x<end:
            d.ellipse((x-5,y-5,x+5,y+5),fill=(30,0,10,255),outline=(242,126,148,105),width=2)
    # visitor marker path and loss
    if t<3.6:
        q=outcubic(clamp((t-.15)/2.85)); x=70+1120*q
        if t>2.45: x += 220*ease((t-2.45)/.75)
        glow=Image.new('RGBA',(W,H),(0,0,0,0)); gd=ImageDraw.Draw(glow)
        for r,a in ((32,20),(18,45),(8,255)):gd.ellipse((x-r,y-r,x+r,y+r),fill=PINK+(a,))
        glow=glow.filter(ImageFilter.GaussianBlur(10)) if t>2.2 else glow
        im=Image.alpha_composite(im.convert('RGBA'),glow).convert('RGB'); d=ImageDraw.Draw(im,'RGBA')
        for k in range(1,6):
            tx=x-k*20; d.ellipse((tx-3,y-3,tx+3,y+3),fill=(242,126,148,max(0,90-k*13)))
    elif t<6.6:
        # broken path and countdown orbit
        d.rectangle((758,354,842,366),fill=(30,0,10,255))
        q=clamp((t-3.75)/2.4); ang=-math.pi/2+math.tau*q
        box=(W/2-185,H/2-185,W/2+185,H/2+185)
        d.arc(box,start=-90,end=-90+360*(1-q),fill=(242,126,148,125),width=3)
        px=W/2+185*math.cos(ang); py=H/2+185*math.sin(ang)
        d.ellipse((px-6,py-6,px+6,py+6),fill=PINK+(220,))
    elif t<8.8:
        # total stillness for the question
        d.line((W/2-180,y,W/2+180,y),fill=(242,126,148,30),width=1)
    else:
        # path tries to rebuild, then locks into a stronger ordered system
        q=ease((t-8.8)/1.8)
        for i,yy in enumerate((250,305,415,470)):
            length=int((160+160*i)*q)
            direction=-1 if i%2 else 1
            x0=W//2-length//2 + direction*int((1-q)*260)
            d.rounded_rectangle((x0,yy,x0+length,yy+3),radius=2,fill=(242,126,148,45+i*12))
        if t>11.0:
            lock=ease((t-11)/1.2)
            d.rectangle((80,566,80+int(1120*lock),568),fill=(220,20,83,150))
    # text compositions
    l=scene_layer(f1,t,.55,2.9,3.55)
    if l: im=Image.alpha_composite(im.convert('RGBA'),l).convert('RGB')
    l=scene_layer(f2,t,3.6,6.0,6.6)
    if l: im=Image.alpha_composite(im.convert('RGBA'),l).convert('RGB')
    l=scene_layer(f3,t,6.65,8.35,8.8)
    if l: im=Image.alpha_composite(im.convert('RGBA'),l).convert('RGB')
    if t>=8.85:
        small=mask_reveal(f4small,(t-8.85)/.55)
        im=Image.alpha_composite(im.convert('RGBA'),small).convert('RGB')
        # letter-rise feel via seven vertical masks arriving from below
        p4=clamp((t-9.35)/1.05)
        if p4>0:
            base=Image.new('RGBA',(W,H),(0,0,0,0))
            for i in range(8):
                x0=i*W//8; x1=(i+1)*W//8
                local=ease(clamp((p4-i*.055)/.62))
                sl=f4big.crop((x0,0,x1,H)); dy=int((1-local)*95)
                a=int(255*local); sl.putalpha(sl.getchannel('A').point(lambda v:v*a//255))
                base.alpha_composite(sl,(x0,dy))
            im=Image.alpha_composite(im.convert('RGBA'),base).convert('RGB')
    # frame labels and grain
    d=ImageDraw.Draw(im,'RGBA')
    smallf=ImageFont.truetype(font_regular,13)
    tracked(d,(70,667),'GBL TECHNOLOGIES',smallf,BLUSH+(110,),2,'left')
    tracked(d,(W-70,667),'ATTENTION / DECISION',smallf,BLUSH+(90,),2,'center')
    random.seed(n)
    grain=Image.new('RGBA',(160,90),(0,0,0,0)); gd=ImageDraw.Draw(grain)
    for _ in range(1100):
        x=random.randrange(160);y0=random.randrange(90);v=random.choice((255,0));gd.point((x,y0),fill=(v,v,v,random.randrange(2,10)))
    grain=grain.resize((W,H),Image.Resampling.BILINEAR)
    im=Image.alpha_composite(im.convert('RGBA'),grain).convert('RGB')
    if n==FRAMES-1:last=im.copy()
    p.stdin.write(im.tobytes())
p.stdin.close(); code=p.wait()
if code: raise SystemExit(code)
last.save(poster,quality=92)
print(out)

