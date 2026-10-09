from PIL import Image,ImageDraw,ImageFont
import random,math,subprocess
W,H,FPS,DUR=1280,720,30,4.0
BLACK=(0,0,0);INK=(36,7,15);WINE=(82,0,25);CRIMSON=(153,0,47);RASP=(220,20,83);PINK=(242,126,148);BLUSH=(247,220,228)
reg=r'D:\Dev-Projects\gbl-tech-v2\assets\font-work-sans-500.ttf';bold=r'D:\Dev-Projects\gbl-tech-v2\assets\font-work-sans-700.ttf';ff=r'C:\Users\Ali\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe';out=r'D:\Dev-Projects\gbl-tech-v2\assets\hero-interface-loop.mp4'
def textw(d,s,f,sp):return sum(d.textlength(c,font=f) for c in s)+sp*(len(s)-1)
def tracked(d,s,y,f,fill,sp):
 x=W/2-textw(d,s,f,sp)/2
 for c in s:d.text((x,y),c,font=f,fill=fill,anchor='lm');x+=d.textlength(c,font=f)+sp
def card(seed):
 rnd=random.Random(seed);w,h=330,210;base=[WINE,INK,CRIMSON,WINE][seed%4];accent=[PINK,RASP,BLUSH,BLUSH][seed%4];c=Image.new('RGBA',(w,h),base+(255,));d=ImageDraw.Draw(c,'RGBA');d.rectangle((0,0,w,25),fill=(12,0,5,255));d.ellipse((11,9,17,15),fill=PINK+(180,));d.ellipse((23,9,29,15),fill=RASP+(130,));d.rounded_rectangle((45,8,w-16,16),4,fill=BLUSH+(24,));v=seed%4
 if v==0:d.rectangle((18,42,w-18,132),fill=accent+(38,));d.rectangle((32,55,155,65),fill=BLUSH+(205,));d.rectangle((32,75,205,82),fill=BLUSH+(70,));d.rounded_rectangle((32,99,94,119),10,fill=accent+(220,));d.rectangle((188,50,w-35,125),fill=accent+(85,))
 elif v==1:
  d.rectangle((18,42,150,h-22),fill=accent+(75,));d.rectangle((168,45,w-20,54),fill=BLUSH+(180,))
  for y in (70,92,114,136):d.rounded_rectangle((168,y,w-20,y+13),6,fill=BLUSH+(38,))
 elif v==2:
  d.rectangle((18,42,w-18,72),fill=accent+(110,))
  for i in range(3):
   x=18+i*101;d.rounded_rectangle((x,88,x+88,176),7,fill=BLUSH+(24+i*10,));d.rectangle((x+12,102,x+72,112),fill=accent+(150,));d.rectangle((x+12,124,x+62,130),fill=BLUSH+(60,))
 else:d.rectangle((18,42,w-18,113),fill=accent+(55,));d.ellipse((w//2-38,49,w//2+38,125),fill=accent+(150,));d.rectangle((52,139,w-52,149),fill=BLUSH+(180,));d.rectangle((92,164,w-92,172),fill=BLUSH+(55,))
 return c
plane=Image.new('RGBA',(2400,1500),(8,0,3,255));cards=[card(i) for i in range(30)];idx=0
for row in range(-1,7):
 for col in range(-1,8):
  plane.alpha_composite(cards[idx%len(cards)],(col*370+(row%2)*85,row*250));idx+=1
plane=plane.rotate(-7,resample=Image.Resampling.BICUBIC,expand=True,fillcolor=(0,0,0,255))
cmd=[ff,'-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',out];p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.DEVNULL)
fs=ImageFont.truetype(reg,25);fb=ImageFont.truetype(bold,140)
for n in range(int(FPS*DUR)):
 phase=2*math.pi*n/(FPS*DUR);cx=plane.width//2+int(115*math.sin(phase));cy=plane.height//2+int(55*math.sin(phase));im=plane.crop((cx-W//2,cy-H//2,cx+W//2,cy+H//2));veil=Image.new('RGBA',(W,H),(20,0,7,98));im=Image.alpha_composite(im,veil);d=ImageDraw.Draw(im,'RGBA');tracked(d,"YOUR WEBSITE WASN'T THAT",282,fs,BLUSH+(255,),7);tracked(d,'IMPACTFUL',382,fb,PINK+(255,),-5);p.stdin.write(im.convert('RGB').tobytes())
p.stdin.close();raise SystemExit(p.wait())
