from PIL import Image, ImageDraw, ImageFilter, ImageFont
import numpy as np
import os

EXPORTS = '/root/NEW-AI-PROJECT/exports'
W, H = 2700, 2700
canvas = Image.new('RGB', (2700, 2700), (28, 28, 28))

# Load real Canva thumbnails
dark = Image.open(os.path.join(EXPORTS, 'dark_thumb.png'))
light_raw = Image.open(os.path.join(EXPORTS, 'light_thumb.png'))

# Light card: 600x343 showing two pages side by side. Left 300x343 = front face
light = light_raw.crop((0, 0, 300, 343))

# Resize dark to 1100px wide, maintain aspect ratio
from PIL import ImageOps
TARGET_W = 1100
dark = dark.resize((TARGET_W, int(TARGET_W * dark.height / dark.width)), Image.LANCZOS)

# Resize light to 550px wide (half), maintain aspect ratio, then pad to 1100x628 with cream
light = light.resize((550, int(550 * light.height / light.width)), Image.LANCZOS)
# Pad equally left and right to match dark card dimensions
left_pad = (dark.width - light.width) // 2
right_pad = dark.width - light.width - left_pad
top_pad = (dark.height - light.height) // 2
bottom_pad = dark.height - light.height - top_pad
light = ImageOps.expand(light, border=(left_pad, top_pad, right_pad, bottom_pad), fill='#FDFBF7')

print(f"Dark: {dark.size}, Light: {light.size}")

# Card centres - evenly spaced, no overlap
DARK_CX, DARK_CY = 750, 1350
LIGHT_CX, LIGHT_CY = 1950, 1350

def add_shadow(base_canvas, card, cx, cy, angle):
    rotated = card.rotate(-angle, expand=True, resample=Image.BICUBIC)
    shadow = Image.new('RGBA', rotated.size, (0,0,0,0))
    sd = ImageDraw.Draw(shadow)
    sd.rectangle([0,0,rotated.width,rotated.height], fill=(0,0,0,160))
    shadow = shadow.filter(ImageFilter.GaussianBlur(20))
    sx = cx - rotated.width//2 + 20
    sy = cy - rotated.height//2 + 20
    tmp = base_canvas.convert('RGBA')
    tmp.paste(shadow, (sx, sy), shadow)
    return tmp.convert('RGB'), rotated

canvas, dark_rot = add_shadow(canvas, dark, DARK_CX, DARK_CY, 5)
canvas, light_rot = add_shadow(canvas, light, LIGHT_CX, LIGHT_CY, -5)

# Cream glow behind light card
glow = Image.new('RGBA', (light_rot.width+60, light_rot.height+60), (0,0,0,0))
gd = ImageDraw.Draw(glow)
gd.rectangle([0,0,light_rot.width+60,light_rot.height+60], fill=(245,240,232,100))
glow = glow.filter(ImageFilter.GaussianBlur(25))
tmp = canvas.convert('RGBA')
tmp.paste(glow, (LIGHT_CX - light_rot.width//2 - 30, LIGHT_CY - light_rot.height//2 - 30), glow)
canvas = tmp.convert('RGB')

# Paste cards
def paste_card(base, card, cx, cy):
    tmp = base.convert('RGBA')
    tmp.paste(card.convert('RGBA'), (cx - card.width//2, cy - card.height//2), card.convert('RGBA'))
    return tmp.convert('RGB')

canvas = paste_card(canvas, dark_rot, DARK_CX, DARK_CY)
canvas = paste_card(canvas, light_rot, LIGHT_CX, LIGHT_CY)

draw = ImageDraw.Draw(canvas)

# Gold divider
draw.line([(1350, 900), (1350, 1800)], fill='#C9A84C', width=2)
for y in [900, 1800]:
    draw.polygon([(1342,y),(1350,y-12),(1358,y),(1350,y+12)], fill='#C9A84C')

# Fonts
try:
    f_title = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf', 108)
    f_sub = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', 62)
    f_lbl = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 54)
    f_btn = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 70)
except:
    f_title = f_sub = f_lbl = f_btn = ImageFont.load_default()

def ctext(d, text, y, font, color):
    bb = d.textbbox((0,0), text, font=font)
    x = (W - (bb[2]-bb[0]))//2
    d.text((x, y), text, fill=color, font=font)

def ctext_at(d, text, cx, y, font, color):
    bb = d.textbbox((0,0), text, font=font)
    x = cx - (bb[2]-bb[0])//2
    d.text((x, y), text, fill=color, font=font)

# Top text
draw.line([(W//2-55,158),(W//2+55,158)], fill='#C9A84C', width=2)
ctext(draw, '2  DESIGNS  INCLUDED', 185, f_title, '#C9A84C')
ctext(draw, 'Tattoo Business Card Template  \u00b7  Digital Download', 315, f_sub, '#F5F0E8')

# Edition labels
ctext_at(draw, 'DARK EDITION', DARK_CX, DARK_CY+370, f_lbl, '#C9A84C')
ctext_at(draw, 'LIGHT EDITION', LIGHT_CX, LIGHT_CY+370, f_lbl, '#C9A84C')

# Bottom text
ctext(draw, 'Tattoo Business Card Template', 2420, f_sub, '#F5F0E8')

# Gradient Canva badge
BW, BH = 620, 108
arr = np.zeros((BH, BW, 3), dtype=np.uint8)
for x in range(BW):
    t = x/BW
    arr[:,x] = [int(0+t*125), int(196+t*(42-196)), int(204+t*(232-204))]
badge = Image.fromarray(arr)
mask = Image.new('L', (BW,BH), 0)
ImageDraw.Draw(mask).rounded_rectangle([0,0,BW,BH], radius=54, fill=255)
badge_rgba = badge.convert('RGBA')
badge_rgba.putalpha(mask)
bd = ImageDraw.Draw(badge_rgba)
tb = bd.textbbox((0,0), 'Edit with Canva', font=f_btn)
bd.text(((BW-(tb[2]-tb[0]))//2, (BH-(tb[3]-tb[1]))//2-4), 'Edit with Canva', fill='white', font=f_btn)
tmp = canvas.convert('RGBA')
tmp.paste(badge_rgba, ((W-BW)//2, 2560), badge_rgba)
canvas = tmp.convert('RGB')

canvas = canvas.crop((0, 0, 2700, 2700))
print(f"FINAL: {canvas.size}")
assert canvas.size == (2700, 2700), f"Canvas is wrong size: {canvas.size}"

canvas.save(os.path.join(EXPORTS, 'listing_1.png'), 'PNG')
print(f"Done: {canvas.size}")
