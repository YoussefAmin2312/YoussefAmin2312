"""Render a seamless generative wire sculpture for the profile.
Requires Pillow. Run: python3 tools/generate_header_v2.py
Set PROFILE_FONT_DIR to a folder containing DejaVuSans.ttf and DejaVuSansMono.ttf
when the default Linux/macOS fonts are unavailable. All design tokens live here.
"""
from pathlib import Path
from functools import lru_cache
import math
import os
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parents[1] / 'assets'
W, H = 1440, 610
FRAMES, FRAME_MS = 120, 60
C = {'bg': '#10191c', 'line': '#293b3f', 'ink': '#edf1e9',
     'muted': '#a5b8b7', 'mint': '#accfba', 'dim': '#64827d'}

@lru_cache(maxsize=None)
def font(size, mono=False):
    root = Path(os.environ.get('PROFILE_FONT_DIR', '/usr/share/fonts/truetype/dejavu'))
    for p in [root / ('DejaVuSansMono.ttf' if mono else 'DejaVuSans.ttf'),
              Path('/System/Library/Fonts/Monaco.ttf' if mono else '/System/Library/Fonts/SFNS.ttf')]:
        if p.exists(): return ImageFont.truetype(str(p), size)
    raise RuntimeError('Set PROFILE_FONT_DIR to your DejaVu font directory.')

def mix(a, b, t):
    a = tuple(bytes.fromhex(a.lstrip('#')))
    b = tuple(bytes.fromhex(b.lstrip('#')))
    return tuple(round(x+(y-x)*t) for x,y in zip(a,b))

def base():
    im = Image.new('RGB', (W,H), C['bg'])
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((1,1,W-2,H-2),radius=22,outline=C['line'],width=2)
    # Sparse registration marks and a dot field add structure without visual noise.
    for x in range(834,1384,24):
        for y in range(122,480,24): d.point((x,y),fill='#29403f')
    d.line((52,79,1388,79),fill=C['line'])
    d.text((56,31),'YA /',font=font(21,True),fill=C['mint'])
    d.text((154,33),'PERSONAL README',font=font(16,True),fill=C['muted'])
    d.text((1180,33),'DUBAI, UAE',font=font(16,True),fill=C['muted'])
    d.text((55,132),'ENGINEERING × INTELLIGENCE',font=font(18,True),fill=C['mint'])
    d.text((48,171),'Youssef.',font=font(126),fill=C['ink'])
    d.text((57,330),'Software Engineer',font=font(36),fill=C['ink'])
    d.text((57,380),'& AI Product Developer',font=font(36),fill=C['mint'])
    d.line((58,465,92,465),fill=C['mint'],width=2)
    d.text((110,453),'Thoughtful by design. Precise by nature.',font=font(21),fill=C['muted'])
    d.line((52,520,1388,520),fill=C['line'])
    for x,number,label in [(56,'01','SOFTWARE'),(536,'02','INTELLIGENCE'),(1070,'03','CRAFT')]:
        d.text((x,553),number,font=font(16,True),fill=C['dim'])
        d.text((x+44,551),label,font=font(19,True),fill=C['muted'])
    for x in (490,1024): d.line((x,545,x,582),fill=C['line'])
    d.text((982,477),'FORM / CONTINUOUS',font=font(13,True),fill=C['dim'])
    return im

# A toroidal surface with a three-lobed twist; geometry is precomputed once.
TAU = math.tau
RINGS, SEGMENTS = 32, 84
GEOMETRY = []
for i in range(RINGS):
    u=TAU*i/RINGS
    ring=[]
    for j in range(SEGMENTS+1):
        v=TAU*j/SEGMENTS
        r=113+43*math.cos(v)
        x,y,z=r*math.cos(u), r*math.sin(u),43*math.sin(v)+18*math.sin(3*u)
        ring.append((x,y,z))
    GEOMETRY.append(ring)

def project(point, angle):
    x,y,z=point
    # Rotation is a full turn per loop; a fixed tilt makes the open center legible.
    co,si=math.cos(angle),math.sin(angle)
    x,y=x*co-y*si,x*si+y*co
    tilt=0.88
    y,z=y*math.cos(tilt)-z*math.sin(tilt),y*math.sin(tilt)+z*math.cos(tilt)
    roll=-0.43
    x,y=x*math.cos(roll)-y*math.sin(roll),x*math.sin(roll)+y*math.cos(roll)
    scale=1.26*(620/(620-z))
    return (1100+x*scale,285+y*scale,z)

def draw_sculpture(im, phase):
    d=ImageDraw.Draw(im)
    rings=[[project(p,phase) for p in ring] for ring in GEOMETRY]
    for ring in sorted(rings,key=lambda r:sum(p[2] for p in r)/len(r)):
        for a,b in zip(ring,ring[1:]):
            brightness=max(0.12,min(0.84,0.43+(a[2]+b[2])/400))
            color=mix(C['line'],C['mint'],brightness)
            d.line((a[0],a[1],b[0],b[1]),fill=color,width=1)
    # A travelling highlight gives the sculpture a deliberate signal-like pulse.
    for offset in (0,math.pi):
        p=project((156*math.cos(phase+offset),156*math.sin(phase+offset),18*math.sin(3*(phase+offset))),phase)
        x,y=p[:2]
        d.ellipse((x-6,y-6,x+6,y+6),fill='#375a4d')
        d.ellipse((x-2,y-2,x+2,y+2),fill=C['ink'])

def main():
    OUT.mkdir(exist_ok=True)
    fixed=base()
    palette=Image.new('RGB',(256,1))
    colors=[mix(C['bg'],C['mint'],i/191) for i in range(192)]
    colors += [mix(C['bg'],C['ink'],i/63) for i in range(64)]
    palette.putdata(colors)
    palette=palette.quantize(colors=256)
    frames=[]
    for i in range(FRAMES):
        im=fixed.copy()
        draw_sculpture(im,TAU*i/FRAMES)
        if i==0: im.save(OUT/'header-v2-static.png',optimize=True)
        frames.append(im.quantize(palette=palette,dither=Image.Dither.NONE))
    frames[0].save(OUT/'header-v2.gif',save_all=True,append_images=frames[1:],
                   duration=FRAME_MS,loop=0,optimize=True,disposal=1)
    print(f'{FRAMES} frames / {FRAMES*FRAME_MS/1000:.1f}s / {(OUT/"header-v2.gif").stat().st_size:,} bytes')

if __name__=='__main__': main()
