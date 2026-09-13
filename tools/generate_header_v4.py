"""Pixel/terminal profile artwork. Requires Pillow.
Run python3 tools/generate_header_v4.py. Optional PROFILE_MONO_FONT path.
"""
from pathlib import Path
import math,os
from PIL import Image,ImageDraw,ImageFont
OUT=Path(__file__).resolve().parents[1]/'assets'
W,H=1440,530
BG='#080a0d';INK='#e2e8ee';MUTED='#a4b0bd';ACCENT='#91afc5';LINE='#25313d'
FONT=os.environ.get('PROFILE_MONO_FONT','/System/Library/Fonts/Monaco.ttf')
GLYPHS={
'Y':['10001','10001','01010','00100','00100','00100','00100'],
'O':['01110','10001','10001','10001','10001','10001','01110'],
'U':['10001','10001','10001','10001','10001','10001','01110'],
'S':['01111','10000','10000','01110','00001','00001','11110'],
'E':['11111','10000','10000','11110','10000','10000','11111'],
'F':['11111','10000','10000','11110','10000','10000','10000']}
def text(d,xy,value,size,color=MUTED):
    d.text(xy,value,font=ImageFont.truetype(FONT,size),fill=color)
def pixel_text(d,value,x,y,scale=13):
    for letter in value:
        for row,bits in enumerate(GLYPHS[letter]):
            for col,bit in enumerate(bits):
                if bit=='1':d.rectangle((x+col*scale,y+row*scale,x+(col+1)*scale-2,y+(row+1)*scale-2),fill=INK)
        x+=6*scale

def fixed():
    im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
    text(d,(78,43),'>_',27,ACCENT)
    d.line((140,64,1360,64),fill=LINE)
    pixel_text(d,'YOUSSEF',80,141)
    text(d,(80,280),'Software Engineer',34,INK)
    text(d,(80,330),'& AI Product Developer',30,ACCENT)
    # Restrained register grid: decorative signal, no implied metrics or live status.
    for col in range(11):
        for row in range(10):
            x,y=1000+col*30,115+row*25
            d.rectangle((x,y,x+15,y+13),fill='#101923')
    d.line((80,449,1360,449),fill=LINE)
    text(d,(80,472),'[ SOFTWARE / AI ]',17,MUTED)
    text(d,(1297,469),'</>',22,ACCENT)
    return im

def main():
    OUT.mkdir(exist_ok=True);base=fixed();frames=[]
    for n in range(80):
        phase=math.tau*n/80;im=base.copy();d=ImageDraw.Draw(im)
        for col in range(11):
            height=2+round((math.sin(col*.55-phase)+1)*2.8)
            for row in range(height):
                x,y=1000+col*30,340-row*25
                color=ACCENT if row==height-1 else '#34495b'
                d.rectangle((x,y,x+15,y+13),fill=color)
        # A single moving trace reinforces the digital motif.
        x=80+(n/80)*1280
        d.line((x,449,min(x+35,1360),449),fill=ACCENT,width=2)
        if n==0:im.save(OUT/'terminal-static.png',optimize=True)
        frames.append(im)
    palette=frames[0].quantize(colors=64)
    frames=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
    frames[0].save(OUT/'terminal.gif',save_all=True,append_images=frames[1:],duration=80,loop=0,optimize=True,disposal=1)
    (OUT/'terminal-toolkit.svg').write_text('''<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="120" viewBox="0 0 1440 120"><rect width="1440" height="120" fill="#080a0d"/><text x="80" y="74" fill="#a4b0bd" font-family="monospace" font-size="28">// TECH STACK</text><path d="M400 65H1360" stroke="#25313d"/></svg>''')
    print('Generated terminal header:',(OUT/'terminal.gif').stat().st_size,'bytes')
if __name__=='__main__':main()
