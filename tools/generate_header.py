"""Generate the profile masthead. Requires Pillow; optionally set PROFILE_FONT_DIR.
Run from any directory: python3 tools/generate_header.py
"""
from pathlib import Path
import math
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets'
W, H = 1280, 420
COLORS = {'bg': '#11191c', 'line': '#29383c', 'text': '#ecf0ea',
          'muted': '#a5b4b4', 'accent': '#a6c7b4', 'dim': '#5b7375'}

def font(size, mono=False):
    supplied = Path(os.environ.get('PROFILE_FONT_DIR', '/usr/share/fonts/truetype/dejavu'))
    candidates = [supplied / ('DejaVuSansMono.ttf' if mono else 'DejaVuSans.ttf'),
                  Path('/System/Library/Fonts/Monaco.ttf' if mono else '/System/Library/Fonts/SFNS.ttf')]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    raise RuntimeError('Set PROFILE_FONT_DIR to a directory containing DejaVuSans.ttf and DejaVuSansMono.ttf')

def base_image():
    im = Image.new('RGB', (W, H), COLORS['bg'])
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((1, 1, W-2, H-2), radius=20, outline=COLORS['line'], width=2)
    d.line((54, 56, 86, 56), fill=COLORS['accent'], width=3)
    d.text((102, 44), 'YOUSSEF / SOFTWARE ENGINEER', font=font(17, True), fill=COLORS['muted'])
    d.text((52, 98), 'Ideas into software.', font=font(71), fill=COLORS['text'])
    d.text((56, 207), 'AI products. Thoughtful interfaces.', font=font(28), fill=COLORS['accent'])
    d.text((56, 248), 'Built with curiosity. Refined with care.', font=font(22), fill=COLORS['muted'])
    d.line((56, 327, 1224, 327), fill=COLORS['line'], width=1)
    d.text((56, 356), 'DUBAI, UAE', font=font(15, True), fill=COLORS['muted'])
    d.text((842, 356), 'AI  /  WEB  /  MOBILE', font=font(15, True), fill=COLORS['muted'])
    # A quiet signal diagram: three connected layers, one shared center.
    cx, cy = 1050, 179
    for r in (48, 82, 117):
        d.ellipse((cx-r, cy-r, cx+r, cy+r), outline=COLORS['line'], width=2)
    d.line((cx-135, cy, cx+135, cy), fill=COLORS['line'])
    d.line((cx, cy-135, cx, cy+135), fill=COLORS['line'])
    d.rounded_rectangle((cx-29, cy-23, cx+29, cy+23), radius=10, fill='#1e2d2d', outline=COLORS['dim'])
    d.text((cx-20, cy-15), '</>', font=font(20, True), fill=COLORS['accent'])
    return im

def main():
    OUT.mkdir(exist_ok=True)
    base = base_image()
    frames = []
    for i in range(64):
        im = base.copy()
        d = ImageDraw.Draw(im)
        for radius, phase, speed in [(48, 0, 1), (82, 2.2, -1), (117, 4.3, 1)]:
            a = phase + speed * 2 * math.pi * i / 64
            x, y = 1050 + radius * math.cos(a), 179 + radius * math.sin(a)
            d.ellipse((x-7,y-7,x+7,y+7), fill='#213733')
            d.ellipse((x-3,y-3,x+3,y+3), fill=COLORS['accent'])
        frames.append(im)
    frames[0].save(OUT / 'header-static.png', optimize=True)
    # One shared palette keeps the background stable and file size modest.
    palette = frames[0].quantize(colors=96)
    indexed = [f.quantize(palette=palette, dither=Image.Dither.NONE) for f in frames]
    indexed[0].save(OUT / 'header.gif', save_all=True, append_images=indexed[1:],
                    duration=100, loop=0, optimize=True, disposal=1)
    print(f'Generated {len(frames)} frames; {(OUT / "header.gif").stat().st_size:,} bytes')

if __name__ == '__main__':
    main()
