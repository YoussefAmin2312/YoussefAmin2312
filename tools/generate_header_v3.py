"""NOCTURNE — procedural profile artwork. Requires Pillow.
Run python3 tools/generate_header_v3.py. Set PROFILE_SERIF_FONT and
PROFILE_SANS_FONT to custom font paths when running outside macOS.
"""
from pathlib import Path
from functools import lru_cache
import math,os
from PIL import Image,ImageDraw,ImageFont
OUT=Path(__file__).resolve().parents[1]/'assets'
W,H=1440,850
N,MS=96,80
C={'bg':'#08090b','ivory':'#e7e1d6','muted':'#aba69e','line':'#34312e','gold':'#a88d65'}
@lru_cache(None)
def font(size,serif=False):
    key='PROFILE_SERIF_FONT' if serif else 'PROFILE_SANS_FONT'
    fallback='/System/Library/Fonts/Supplemental/Georgia Italic.ttf' if serif else '/System/Library/Fonts/SFNS.ttf'
    return ImageFont.truetype(os.environ.get(key,fallback),size)
def centered(d,text,y,size,color,serif=False):
    f=font(size,serif);width=d.textlength(text,font=f)
    d.text(((W-width)/2,y),text,font=f,fill=color)
def tracked(d,text,y,size,spacing,color):
    f=font(size);width=sum(d.textlength(c,font=f) for c in text)+spacing*(len(text)-1)
    x=(W-width)/2
    for c in text:
        d.text((x,y),c,font=f,fill=color);x+=d.textlength(c,font=f)+spacing

def fixed():
    im=Image.new('RGB',(W,H),C['bg']);d=ImageDraw.Draw(im)
    # The page behaves like a book cover: typography first, generous negative space.
    d.line((80,74,612,74),fill=C['line'])
    d.line((828,74,1360,74),fill=C['line'])
    centered(d,'Y / A',58,22,C['gold'],True)
    tracked(d,'SOFTWARE ENGINEER',169,19,7,C['muted'])
    centered(d,'Youssef',209,164,C['ivory'],True)
    tracked(d,'& AI PRODUCT DEVELOPER',422,20,5,C['muted'])
    # Small location signature belongs to the typography rather than a status bar.
    tracked(d,'UNITED ARAB EMIRATES',753,16,5,C['gold'])
    return im

def silk(d,phase):
    # Continuous contour lines form a sweeping asymmetric silk fold.
    # Opacity is represented by palette colors; nothing overlaps the title.
    for j in range(56):
        t=j/55
        pts=[]
        for x in range(0,W+1,6):
            u=x/W
            envelope=math.sin(math.pi*u)**1.3
            fold=math.sin(2*math.pi*u+0.55*math.sin(phase))*46
            twist=math.sin(3*math.pi*u+phase)*12*envelope
            y=630+fold+twist+(t-.5)*(32+92*envelope)+18*math.sin(t*math.pi+u*5+phase)*envelope
            pts.append((x,y))
        strength=(math.sin(t*math.pi)**3)*.7+.08
        # Champagne highlights move slowly through the fabric.
        glint=.65+.35*math.sin(phase+5*t)
        rgb=tuple(round(a+(b-a)*strength*glint) for a,b in zip((10,11,14),(154,139,117)))
        d.line(pts,fill=rgb,width=1)

def main():
    OUT.mkdir(exist_ok=True);base=fixed();frames=[]
    pal=Image.new('RGB',(256,1));pal.putdata([tuple(round(a+(b-a)*i/255) for a,b in zip((8,9,11),(231,225,214))) for i in range(256)])
    pal=pal.quantize(colors=256)
    for i in range(N):
        im=base.copy();silk(ImageDraw.Draw(im),math.tau*i/N)
        if i==0:im.save(OUT/'nocturne-static.png',optimize=True)
        frames.append(im.quantize(palette=pal,dither=Image.Dither.NONE))
    frames[0].save(OUT/'nocturne.gif',save_all=True,append_images=frames[1:],duration=MS,loop=0,optimize=True,disposal=1)
    # Matching section divider, kept crisp at every display size.
    (OUT/'toolkit.svg').write_text('''<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="140" viewBox="0 0 1440 140"><rect width="1440" height="140" fill="#08090b"/><path d="M80 72H520M920 72H1360" stroke="#34312e"/><text x="720" y="86" text-anchor="middle" fill="#e7e1d6" font-family="Georgia,serif" font-size="44" font-style="italic">The toolkit.</text></svg>''')
    print('Nocturne:',(OUT/'nocturne.gif').stat().st_size,'bytes')
if __name__=='__main__':main()
