#!/usr/bin/env python3
"""
Car Detailing Animated Pin
  Step 1 — Write self-contained animated HTML (1000×1500, 10-second loop)
  Step 2 — Capture with Puppeteer-core + system Chromium → MP4
            Fallback: Pillow-generated frames → FFmpeg (same animation, no browser)
  Step 3 — Upload both files to DO Spaces under pinterest/

Run from project root:
    python scripts/build_car_detail_animated_pin.py
"""

import math
import os
import subprocess
import sys
import textwrap
import time
import urllib.request

import boto3
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont, ImageFilter

PROJECT    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(PROJECT, "outputs", "pinterest")
NPM_DIR    = "/tmp/anim-pin-npm"
NODE_SCRIPT= "/tmp/anim-pin-capture.mjs"
FRAMES_DIR = "/tmp/anim-pin-frames"
HTML_OUT   = os.path.join(OUTPUT_DIR, "car-detail-landing.html")
MP4_OUT    = os.path.join(OUTPUT_DIR, "car-detail-animated-pin.mp4")
CHROMIUM   = "/usr/bin/chromium-browser"

W, H  = 1000, 1500
FPS   = 25
SECS  = 10
TOTAL = FPS * SECS   # 250 frames

# ── Colours ───────────────────────────────────────────────────────────────────
BG      = (13, 13, 13)
RED     = (204, 0, 0)
WHITE   = (255, 255, 255)
SILVER  = (180, 180, 180)
PANEL   = (26, 26, 26)

# ── Fonts (for Pillow fallback) ───────────────────────────────────────────────
F_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F_REG  = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def fnt(size, bold=True):
    try:
        return ImageFont.truetype(F_BOLD if bold else F_REG, size)
    except Exception:
        return ImageFont.load_default()


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 1 — HTML LANDING PAGE
# ═══════════════════════════════════════════════════════════════════════════════
HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1000px;height:1500px;overflow:hidden;background:#0D0D0D;
  font-family:system-ui,-apple-system,Helvetica,Arial,sans-serif;color:#fff}
#topbar,#botbar{position:absolute;left:0;right:0;height:18px;background:#CC0000;z-index:200}
#topbar{top:0} #botbar{bottom:0}
#badge{position:absolute;bottom:4px;left:0;right:0;text-align:center;
  font-size:15px;color:#404040;z-index:201;letter-spacing:.5px}
.phase{position:absolute;top:0;left:0;width:1000px;height:1500px;
  opacity:0;display:flex;flex-direction:column;align-items:center}

/* ── Phase 1: Headline ── */
#p1{justify-content:center;gap:0}
#p1-eyebrow{font-size:20px;font-weight:700;color:#CC0000;letter-spacing:6px;
  margin-top:-120px;margin-bottom:24px;text-transform:uppercase}
#p1-l1,#p1-l2{font-size:100px;font-weight:900;line-height:1;color:#fff;
  letter-spacing:-2px;text-transform:uppercase}
#p1-l3{font-size:100px;font-weight:900;line-height:1;color:#CC0000;
  letter-spacing:-2px;text-transform:uppercase;margin-bottom:32px}
#p1-rule{width:600px;height:3px;background:#CC0000;margin:0 auto 24px}
#p1-sub{font-size:26px;color:#B4B4B4;margin-bottom:18px;font-weight:400}
#p1-cta{font-size:22px;color:#888;background:#1A1A1A;padding:10px 28px;
  border-radius:24px;letter-spacing:.5px}

/* ── Phase 2: Counter ── */
#p2{justify-content:center;gap:0}
#p2-pre{font-size:26px;color:#CC0000;font-weight:700;letter-spacing:8px;
  margin-top:-200px;margin-bottom:8px}
#p2-count{font-size:260px;font-weight:900;color:#fff;line-height:1;
  margin-bottom:0;
  text-shadow:0 0 60px rgba(204,0,0,.6),0 0 120px rgba(204,0,0,.3)}
#p2-plus{font-size:100px;font-weight:900;color:#CC0000;line-height:1;margin-bottom:8px}
#p2-u1{font-size:54px;font-weight:900;color:#fff;letter-spacing:2px;text-transform:uppercase}
#p2-u2{font-size:54px;font-weight:900;color:#CC0000;letter-spacing:2px;text-transform:uppercase;margin-bottom:24px}
#p2-rule{width:500px;height:2px;background:#CC0000;margin:16px auto}
#p2-sub{font-size:24px;color:#888;font-weight:400}

/* ── Phase 3: Categories ── */
#p3{justify-content:flex-start;padding-top:80px}
#p3-t1{font-size:84px;font-weight:900;color:#CC0000;text-transform:uppercase;line-height:1}
#p3-t2{font-size:84px;font-weight:900;color:#fff;text-transform:uppercase;line-height:1;margin-bottom:12px}
#p3-rule{width:800px;height:3px;background:#CC0000;margin:0 auto 22px}
#p3-list{display:flex;flex-direction:column;width:900px;gap:8px}
.cat-item{display:flex;align-items:center;background:#1A1A1A;border-radius:12px;
  height:74px;padding:0 20px;opacity:0;transform:translateX(-70px)}
.cat-bar{width:6px;height:42px;background:#CC0000;border-radius:3px;margin-right:18px;flex-shrink:0}
.cat-name{font-size:30px;font-weight:700;color:#fff;flex:1}
.cat-badge{background:#CC0000;color:#fff;font-size:20px;font-weight:700;
  padding:4px 14px;border-radius:10px;min-width:44px;text-align:center}
#p3-total{font-size:22px;color:#666;margin-top:6px;letter-spacing:1px}

/* ── Phase 4: Price ── */
#p4{justify-content:center;gap:0}
#p4-pre{font-size:28px;color:#888;font-weight:400;letter-spacing:4px;
  margin-top:-180px;margin-bottom:24px;text-transform:uppercase}
#p4-price{font-size:170px;font-weight:900;color:#CC0000;line-height:1;
  margin-bottom:12px;display:inline-block;transform-origin:center}
#p4-was{font-size:28px;color:#666;margin-bottom:8px}
#p4-rule{width:600px;height:2px;background:#CC0000;margin:12px auto}
#p4-save{font-size:68px;font-weight:900;color:#CC0000;text-transform:uppercase;line-height:1}
#p4-note{font-size:22px;color:#666;margin-top:24px}

/* ── Phase 5: CTA ── */
#p5{justify-content:center;gap:0}
#p5-h1{font-size:80px;font-weight:900;color:#fff;text-transform:uppercase;line-height:1;
  margin-top:-220px}
#p5-h2{font-size:80px;font-weight:900;color:#CC0000;text-transform:uppercase;line-height:1;
  margin-bottom:30px}
#p5-btn{background:#CC0000;color:#fff;font-size:36px;font-weight:900;
  padding:22px 60px;border-radius:60px;display:inline-block;
  letter-spacing:1px;text-align:center;margin-bottom:30px;
  transform-origin:center}
#p5-dl{font-size:64px;font-weight:900;color:#fff;text-transform:uppercase;
  letter-spacing:2px;line-height:1;margin-bottom:18px}
#p5-rule{width:700px;height:2px;background:#333;margin:12px auto 18px}
#p5-cats{font-size:22px;color:#666;text-align:center;line-height:1.7}
#p5-url{font-size:28px;font-weight:700;color:#888;margin-top:24px}
#p5-price{font-size:26px;color:#CC0000;margin-top:6px}
</style>
</head>
<body>

<div id="topbar"></div>
<div id="botbar"></div>
<div id="badge">PurpleOcaz  ·  purpleocaz.etsy.com</div>

<!-- Phase 1: Headline -->
<div id="p1" class="phase">
  <div id="p1-eyebrow">Car Detailing</div>
  <div id="p1-l1">COMPLETE</div>
  <div id="p1-l2">CAR DETAILING</div>
  <div id="p1-l3">BUSINESS KIT</div>
  <div id="p1-rule"></div>
  <div id="p1-sub">53 professional Canva templates</div>
  <div id="p1-cta">Editable in Canva &nbsp;·&nbsp; Instant Download</div>
</div>

<!-- Phase 2: Counter -->
<div id="p2" class="phase">
  <div id="p2-pre">You Get</div>
  <div id="p2-count">0</div>
  <div id="p2-u1">PROFESSIONAL</div>
  <div id="p2-u2">CANVA TEMPLATES</div>
  <div id="p2-rule"></div>
  <div id="p2-sub">in one instant download</div>
</div>

<!-- Phase 3: Categories -->
<div id="p3" class="phase">
  <div id="p3-t1">EVERYTHING</div>
  <div id="p3-t2">COVERED</div>
  <div id="p3-rule"></div>
  <div id="p3-list">
    <div class="cat-item"><div class="cat-bar"></div><div class="cat-name">Client Forms</div><div class="cat-badge">8</div></div>
    <div class="cat-item"><div class="cat-bar"></div><div class="cat-name">Social Media Posts</div><div class="cat-badge">20</div></div>
    <div class="cat-item"><div class="cat-bar"></div><div class="cat-name">Branding Kit</div><div class="cat-badge">6</div></div>
    <div class="cat-item"><div class="cat-bar"></div><div class="cat-name">Email Templates</div><div class="cat-badge">6</div></div>
    <div class="cat-item"><div class="cat-bar"></div><div class="cat-name">Marketing Flyers</div><div class="cat-badge">4</div></div>
    <div class="cat-item"><div class="cat-bar"></div><div class="cat-name">Job Forms</div><div class="cat-badge">3</div></div>
    <div class="cat-item"><div class="cat-bar"></div><div class="cat-name">Appointment Cards</div><div class="cat-badge">2</div></div>
    <div class="cat-item"><div class="cat-bar"></div><div class="cat-name">Visual Templates</div><div class="cat-badge">4</div></div>
  </div>
  <div id="p3-total">53 TEMPLATES TOTAL</div>
</div>

<!-- Phase 4: Price -->
<div id="p4" class="phase">
  <div id="p4-pre">Complete Kit</div>
  <div id="p4-price">£39.99</div>
  <div id="p4-was">Worth over £60 individually</div>
  <div id="p4-rule"></div>
  <div id="p4-save">SAVE 70%+</div>
  <div id="p4-note">Instant download · No subscription needed</div>
</div>

<!-- Phase 5: CTA -->
<div id="p5" class="phase">
  <div id="p5-h1">READY TO LOOK</div>
  <div id="p5-h2">PROFESSIONAL?</div>
  <div id="p5-btn">Editable in FREE Canva</div>
  <div id="p5-dl">INSTANT DOWNLOAD</div>
  <div id="p5-rule"></div>
  <div id="p5-cats">53 Templates · 8 Categories<br>Forms, Social, Branding, Email, Flyers &amp; More</div>
  <div id="p5-url">purpleocaz.etsy.com</div>
  <div id="p5-price">£39.99 — Shop Now</div>
</div>

<script>
(function(){
  function clamp(v,a,b){return Math.max(a,Math.min(b,v))}
  function easeOut(t){t=clamp(t,0,1);return 1-Math.pow(1-t,3)}
  function easeInOut(t){t=clamp(t,0,1);return t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2}

  function phaseAlpha(t,s,e,f){
    f=f||.32;
    if(t<=s||t>=e)return 0;
    var d=e-s,l=t-s;
    if(l<f)return easeOut(l/f);
    if(l>d-f)return easeOut((d-l)/f);
    return 1;
  }

  var cats=document.querySelectorAll('.cat-item');

  window.setAnimationTime=function(t){
    t=((t%10)+10)%10;

    /* ── Phase 1: Headline (0-2s) ── */
    var a1=phaseAlpha(t,0,2);
    var p1=document.getElementById('p1');
    p1.style.opacity=a1;
    if(a1>0){
      var l1=clamp((t-0)/2,0,1);
      var sy=Math.round(40*(1-easeOut(clamp(l1/.4,0,1))))+'px';
      document.getElementById('p1-l1').style.transform='translateY('+sy+')';
      document.getElementById('p1-l2').style.transform='translateY('+sy+')';
      document.getElementById('p1-l3').style.transform='translateY('+sy+')';
      document.getElementById('p1-rule').style.opacity=easeOut(clamp((l1-.38)/.25,0,1));
      document.getElementById('p1-sub').style.opacity=easeOut(clamp((l1-.5)/.25,0,1));
      document.getElementById('p1-cta').style.opacity=easeOut(clamp((l1-.65)/.25,0,1));
    }

    /* ── Phase 2: Counter (2-4s) ── */
    var a2=phaseAlpha(t,2,4);
    var p2=document.getElementById('p2');
    p2.style.opacity=a2;
    if(a2>0){
      var l2=clamp((t-2)/2,0,1);
      var count=Math.round(53*easeInOut(clamp(l2/.72,0,1)));
      document.getElementById('p2-count').textContent=count;
      document.getElementById('p2-sub').style.opacity=easeOut(clamp((l2-.52)/.28,0,1));
    }

    /* ── Phase 3: Categories (4-6s) ── */
    var a3=phaseAlpha(t,4,6);
    var p3=document.getElementById('p3');
    p3.style.opacity=a3;
    if(a3>0){
      var l3=clamp((t-4)/2,0,1);
      cats.forEach(function(c,i){
        var start=i/8*.68;
        var ia=easeOut(clamp((l3-start)/.14,0,1));
        c.style.opacity=ia;
        c.style.transform='translateX('+(-70*(1-ia))+'px)';
      });
      document.getElementById('p3-total').style.opacity=easeOut(clamp((l3-.75)/.2,0,1));
    }

    /* ── Phase 4: Price (6-8s) ── */
    var a4=phaseAlpha(t,6,8);
    var p4=document.getElementById('p4');
    p4.style.opacity=a4;
    if(a4>0){
      var l4=clamp((t-6)/2,0,1);
      var scale;
      if(l4<.38)scale=easeOut(l4/.38)*1.16;
      else if(l4<.54)scale=1.16-0.16*easeOut((l4-.38)/.16);
      else scale=1;
      document.getElementById('p4-price').style.transform='scale('+scale+')';
      var rev=easeOut(clamp((l4-.36)/.32,0,1));
      document.getElementById('p4-was').style.opacity=rev;
      document.getElementById('p4-rule').style.opacity=rev;
      document.getElementById('p4-save').style.opacity=rev;
      document.getElementById('p4-note').style.opacity=easeOut(clamp((l4-.62)/.26,0,1));
    }

    /* ── Phase 5: CTA (8-10s) ── */
    var a5=phaseAlpha(t,8,10);
    var p5=document.getElementById('p5');
    p5.style.opacity=a5;
    if(a5>0){
      var l5=clamp((t-8)/2,0,1);
      var pulse=1+0.042*Math.sin(l5*Math.PI*4);
      document.getElementById('p5-btn').style.transform='scale('+pulse+')';
      var fa=easeOut(clamp(l5/.28,0,1));
      document.getElementById('p5-h1').style.opacity=fa;
      document.getElementById('p5-h2').style.opacity=fa;
      document.getElementById('p5-dl').style.opacity=easeOut(clamp((l5-.22)/.28,0,1));
      document.getElementById('p5-rule').style.opacity=easeOut(clamp((l5-.38)/.22,0,1));
      document.getElementById('p5-cats').style.opacity=easeOut(clamp((l5-.42)/.24,0,1));
      document.getElementById('p5-url').style.opacity=easeOut(clamp((l5-.56)/.22,0,1));
      document.getElementById('p5-price').style.opacity=easeOut(clamp((l5-.68)/.2,0,1));
    }
  };

  /* Autoplay */
  var t0=null;
  function frame(ts){
    if(!t0)t0=ts;
    window.setAnimationTime(((ts-t0)/1000)%10);
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
})();
</script>
</body>
</html>"""


def write_html():
    print("[HTML] Writing car-detail-landing.html...")
    with open(HTML_OUT, "w") as f:
        f.write(HTML)
    print(f"  Saved: {HTML_OUT}")
    return HTML_OUT


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 2A — PUPPETEER CAPTURE
# ═══════════════════════════════════════════════════════════════════════════════
NODE_CAPTURE = f"""
import puppeteer from '{NPM_DIR}/node_modules/puppeteer-core/lib/esm/puppeteer/puppeteer-core.js';
import {{ execFileSync }} from 'child_process';
import {{ writeFileSync, mkdirSync, rmSync, statSync }} from 'fs';
import path from 'path';
import {{ fileURLToPath }} from 'url';

const CHROMIUM = '{CHROMIUM}';
const HTML     = '{HTML_OUT}';
const FRAMES   = '{FRAMES_DIR}';
const MP4      = '{MP4_OUT}';
const FPS      = {FPS};
const SECS     = {SECS};
const TOTAL    = FPS * SECS;

mkdirSync(FRAMES, {{ recursive: true }});

console.log('[Puppeteer] Launching Chromium...');
const browser = await puppeteer.launch({{
  executablePath: CHROMIUM,
  headless: 'new',
  args: [
    '--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu',
    '--disable-dev-shm-usage', '--no-first-run', '--no-zygote',
    '--disable-background-timer-throttling',
    '--disable-renderer-backgrounding',
    '--disable-backgrounding-occluded-windows'
  ]
}});

const page = await browser.newPage();
await page.setViewport({{ width: 1000, height: 1500, deviceScaleFactor: 1 }});
await page.goto('file://' + HTML, {{ waitUntil: 'networkidle0', timeout: 15000 }});

// Let animations initialise
await new Promise(r => setTimeout(r, 600));

console.log(`[Puppeteer] Capturing ${{TOTAL}} frames at ${{FPS}}fps...`);
for (let i = 0; i < TOTAL; i++) {{
  const t = i / FPS;
  await page.evaluate((time) => window.setAnimationTime(time), t);
  // Small yield for DOM paint
  await new Promise(r => setTimeout(r, 8));
  const frame = path.join(FRAMES, 'frame_' + String(i).padStart(4,'0') + '.png');
  await page.screenshot({{ path: frame, type: 'png' }});
  if (i % 50 === 0) process.stdout.write(`  ${{i}}/${{TOTAL}} frames\\r`);
}}
await browser.close();
console.log(`\\n[Puppeteer] Capture complete.`);

// FFmpeg stitch
console.log('[FFmpeg] Stitching frames...');
execFileSync('ffmpeg', [
  '-y', '-framerate', String(FPS),
  '-i', path.join(FRAMES, 'frame_%04d.png'),
  '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '22', '-preset', 'fast',
  MP4
], {{ stdio: 'inherit' }});

const mb = (statSync(MP4).size / 1024 / 1024).toFixed(1);
console.log(`[FFmpeg] Done — ${{MP4}} (${{mb}} MB)`);

// Clean frames
rmSync(FRAMES, {{ recursive: true }});
"""


def try_puppeteer():
    """Attempt: npm install puppeteer-core, then run Node capture script."""
    print("\n[Puppeteer] Installing puppeteer-core...")
    r = subprocess.run(
        ["npm", "install", "puppeteer-core", "--prefix", NPM_DIR,
         "--no-save", "--prefer-offline"],
        capture_output=True, text=True, timeout=120
    )
    if r.returncode != 0:
        raise RuntimeError(f"npm install failed: {r.stderr[:400]}")
    print("  puppeteer-core installed.")

    # Write ES module capture script
    with open(NODE_SCRIPT, "w") as f:
        f.write(NODE_CAPTURE)

    print("[Puppeteer] Running capture (250 frames × 1000×1500)...")
    r2 = subprocess.run(
        ["node", "--experimental-vm-modules", NODE_SCRIPT],
        capture_output=False,   # let stdout/stderr through
        timeout=300
    )
    if r2.returncode != 0:
        raise RuntimeError(f"Node capture exited with code {r2.returncode}")

    return MP4_OUT


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 2B — PILLOW FALLBACK
# ═══════════════════════════════════════════════════════════════════════════════
def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3

def ease_in_out(t):
    t = max(0.0, min(1.0, t))
    return 4*t**3 if t < 0.5 else 1 - (-2*t+2)**3/2

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def phase_alpha(t, s, e, f=0.32):
    if t <= s or t >= e:
        return 0.0
    d, l = e - s, t - s
    if l < f:   return ease_out(l / f)
    if l > d-f: return ease_out((d-l) / f)
    return 1.0

def layer_rgba():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))

def comp(base, layer, master=1.0):
    """Alpha-composite an RGBA layer over an RGB base, with optional master alpha."""
    if master <= 0:
        return base
    if master < 1:
        r, g, b, a = layer.split()
        a = a.point(lambda x: int(x * master))
        layer = Image.merge("RGBA", (r, g, b, a))
    return Image.alpha_composite(base.convert("RGBA"), layer).convert("RGB")

def cxd(draw, text, y, font, color, alpha=1.0):
    """Draw centred text with alpha on an RGBA draw context."""
    bb = draw.textbbox((0, 0), text, font=font)
    tw = bb[2] - bb[0]
    draw.text(((W - tw) // 2, y), text, fill=(*color, int(255 * alpha)), font=font)

def glow_text(base, text, x, y, font, color, radius=18):
    """Draw text with a coloured glow behind it on RGB base."""
    gl = layer_rgba()
    gd = ImageDraw.Draw(gl)
    gd.text((x-3, y-3), text, fill=(*color, 100), font=font)
    gl = gl.filter(ImageFilter.GaussianBlur(radius=radius))
    base = comp(base, gl)
    draw = ImageDraw.Draw(base)
    draw.text((x, y), text, fill=color, font=font)
    return base

def make_base():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # Top/bottom bars (always visible)
    d.rectangle([0, 0, W, 18], fill=RED)
    d.rectangle([0, H-18, W, H], fill=RED)
    # Badge
    f = fnt(16, bold=False)
    badge = "PurpleOcaz  ·  purpleocaz.etsy.com"
    bb = d.textbbox((0, 0), badge, font=f)
    d.text(((W - (bb[2]-bb[0])) // 2, H-16), badge, fill=(60, 60, 60), font=f)
    return img


CATS = [
    ("Client Forms", "8"),
    ("Social Media Posts", "20"),
    ("Branding Kit", "6"),
    ("Email Templates", "6"),
    ("Marketing Flyers", "4"),
    ("Job Forms", "3"),
    ("Appointment Cards", "2"),
    ("Visual Templates", "4"),
]

def draw_phase1(base, t):
    """Headline slide (t=0-2s)."""
    a = phase_alpha(t, 0, 2)
    if a <= 0:
        return base
    l = clamp((t - 0) / 2, 0, 1)
    slide_y = int(40 * (1 - ease_out(clamp(l / 0.4, 0, 1))))

    layer = layer_rgba()
    ld = ImageDraw.Draw(layer)

    # Eyebrow
    ey_a = ease_out(clamp(l / 0.3, 0, 1))
    f_ey = fnt(22)
    cxd(ld, "CAR DETAILING", 250 + slide_y, f_ey, RED, ey_a)

    # Headline lines
    f_h = fnt(96)
    cxd(ld, "COMPLETE",      290 + slide_y, f_h, WHITE, ease_out(clamp(l / 0.35, 0, 1)))
    cxd(ld, "CAR DETAILING", 392 + slide_y, fnt(80), WHITE, ease_out(clamp(l / 0.35, 0, 1)))
    cxd(ld, "BUSINESS KIT",  478 + slide_y, fnt(80), RED,   ease_out(clamp(l / 0.35, 0, 1)))

    # Rule
    rule_a = ease_out(clamp((l - 0.38) / 0.25, 0, 1))
    ld.rectangle([60, 580, W-60, 583], fill=(*RED, int(255*rule_a)))

    # Sub + CTA
    sub_a = ease_out(clamp((l - 0.5) / 0.25, 0, 1))
    cxd(ld, "53 professional Canva templates", 600, fnt(26, bold=False), SILVER, sub_a)
    cta_a = ease_out(clamp((l - 0.65) / 0.25, 0, 1))
    f_cta = fnt(22, bold=False)
    cta = "Editable in Canva  ·  Instant Download"
    bb = ld.textbbox((0, 0), cta, font=f_cta)
    tw = bb[2] - bb[0]
    px, py = (W-tw)//2 - 20, 644
    ld.rounded_rectangle([px, py, px+tw+40, py+38], radius=19, fill=(26, 26, 26, int(255*cta_a)))
    cxd(ld, cta, 652, f_cta, SILVER, cta_a)

    return comp(base, layer, a)


def draw_phase2(base, t):
    """Counter slide (t=2-4s)."""
    a = phase_alpha(t, 2, 4)
    if a <= 0:
        return base
    l = clamp((t - 2) / 2, 0, 1)
    count = int(53 * ease_in_out(clamp(l / 0.72, 0, 1)))

    f_pre = fnt(26)
    f_u = fnt(54)
    f_sub = fnt(24, bold=False)

    layer = layer_rgba()
    ld = ImageDraw.Draw(layer)

    # "YOU GET"
    cxd(ld, "YOU GET", 280, f_pre, RED, ease_out(clamp(l / 0.2, 0, 1)))

    # Giant count — glow handled after composite
    f_big = fnt(230)
    s = str(count)
    bb = ld.textbbox((0, 0), s, font=f_big)
    tw = bb[2] - bb[0]
    cx_n = (W - tw) // 2
    cy_n = 300
    ld.text((cx_n, cy_n), s, fill=(*WHITE, 255), font=f_big)

    cxd(ld, "PROFESSIONAL",   640, f_u, WHITE)
    cxd(ld, "CANVA TEMPLATES",700, f_u, RED)
    ld.rectangle([60, 768, W-60, 770], fill=(*RED, 255))
    sub_a = ease_out(clamp((l - 0.5) / 0.3, 0, 1))
    cxd(ld, "in one instant download bundle", 786, f_sub, SILVER, sub_a)

    result = comp(base, layer, a)

    # Add glow on top (needs to be on RGB)
    if a > 0.05:
        s = str(count)
        f_big = fnt(230)
        bb = ImageDraw.Draw(result).textbbox((0, 0), s, font=f_big)
        tw = bb[2] - bb[0]
        cx_n = (W - tw) // 2
        gl = layer_rgba()
        gd = ImageDraw.Draw(gl)
        gd.text((cx_n-5, 295), s, fill=(*RED, int(90*a)), font=f_big)
        gl = gl.filter(ImageFilter.GaussianBlur(radius=22))
        result = comp(result, gl)
    return result


def draw_phase3(base, t):
    """Categories slide (t=4-6s)."""
    a = phase_alpha(t, 4, 6)
    if a <= 0:
        return base
    l = clamp((t - 4) / 2, 0, 1)

    layer = layer_rgba()
    ld = ImageDraw.Draw(layer)

    cxd(ld, "EVERYTHING", 80, fnt(84), RED)
    cxd(ld, "COVERED",   166, fnt(84), WHITE)
    ld.rectangle([60, 264, W-60, 267], fill=(*RED, 255))

    f_cat = fnt(30)
    f_num = fnt(24, bold=False)
    y = 285
    row_h = 98
    for i, (name, count) in enumerate(CATS):
        item_start = i / 8 * 0.68
        ia = ease_out(clamp((l - item_start) / 0.14, 0, 1))
        if ia <= 0:
            y += row_h
            continue
        sx = int(70 * (1 - ia))
        ld.rounded_rectangle([40-sx, y+4, W-40-sx, y+76], radius=12,
                              fill=(26, 26, 26, int(220 * ia)))
        ld.rectangle([40-sx, y+4, 47-sx, y+76], fill=(*RED, int(255*ia)))
        ld.text((62-sx, y+14), name, fill=(*WHITE, int(255*ia)), font=f_cat)
        bb = ld.textbbox((0, 0), count, font=f_num)
        cw = bb[2] - bb[0]
        bx = W - 100 - sx
        ld.rounded_rectangle([bx-8, y+20, bx+cw+10, y+58],
                              radius=10, fill=(*RED, int(255*ia)))
        ld.text((bx, y+22), count, fill=(*WHITE, int(255*ia)), font=f_num)
        y += row_h

    total_a = ease_out(clamp((l - 0.75) / 0.2, 0, 1))
    cxd(ld, "53 TEMPLATES TOTAL", y+10, fnt(22, bold=False), (100, 100, 100), total_a)

    return comp(base, layer, a)


def draw_phase4(base, t):
    """Price punch-in (t=6-8s)."""
    a = phase_alpha(t, 6, 8)
    if a <= 0:
        return base
    l = clamp((t - 6) / 2, 0, 1)

    if l < 0.38:
        scale = ease_out(l / 0.38) * 1.16
    elif l < 0.54:
        scale = 1.16 - 0.16 * ease_out((l - 0.38) / 0.16)
    else:
        scale = 1.0

    layer = layer_rgba()
    ld = ImageDraw.Draw(layer)

    pre_a = ease_out(clamp(l / 0.3, 0, 1))
    cxd(ld, "COMPLETE KIT", 260, fnt(32, bold=False), SILVER, pre_a)

    # Price with scale (approximate by font size)
    price_size = max(10, int(160 * scale))
    try:
        f_p = fnt(price_size)
        bb = ld.textbbox((0, 0), "£39.99", font=f_p)
        pw, ph = bb[2]-bb[0], bb[3]-bb[1]
        px = (W - pw) // 2
        ld.text((px, 310), "£39.99", fill=(*RED, 255), font=f_p)
    except Exception:
        pass

    rev = ease_out(clamp((l - 0.36) / 0.32, 0, 1))
    cxd(ld, "Worth over £60 individually", 570, fnt(28, bold=False), SILVER, rev)
    ld.rectangle([60, 612, W-60, 615], fill=(*RED, int(255*rev)))
    cxd(ld, "SAVE 70%+", 628, fnt(68), RED, rev)
    note_a = ease_out(clamp((l - 0.62) / 0.26, 0, 1))
    cxd(ld, "Instant download · No subscription needed", 718, fnt(22, bold=False), SILVER, note_a)

    result = comp(base, layer, a)

    # Red glow behind price
    if a > 0.05:
        try:
            f_p2 = fnt(price_size)
            bb2 = ImageDraw.Draw(result).textbbox((0, 0), "£39.99", font=f_p2)
            pw2 = bb2[2] - bb2[0]
            px2 = (W - pw2) // 2
            gl = layer_rgba()
            gd = ImageDraw.Draw(gl)
            gd.text((px2-4, 306), "£39.99", fill=(*RED, int(70*a)), font=f_p2)
            gl = gl.filter(ImageFilter.GaussianBlur(radius=20))
            result = comp(result, gl)
        except Exception:
            pass
    return result


def draw_phase5(base, t):
    """CTA pulse (t=8-10s)."""
    a = phase_alpha(t, 8, 10)
    if a <= 0:
        return base
    l = clamp((t - 8) / 2, 0, 1)
    pulse = 1 + 0.042 * math.sin(l * math.pi * 4)

    layer = layer_rgba()
    ld = ImageDraw.Draw(layer)

    fa = ease_out(clamp(l / 0.28, 0, 1))
    cxd(ld, "READY TO LOOK",  220, fnt(76), WHITE, fa)
    cxd(ld, "PROFESSIONAL?",  302, fnt(76), RED,   fa)

    # Button with pulse (approximate scale via padding)
    btn_text = "Editable in FREE Canva"
    f_btn = fnt(36)
    bb = ld.textbbox((0, 0), btn_text, font=f_btn)
    bw, bh = bb[2]-bb[0], bb[3]-bb[1]
    base_pad = 50
    pad = int(base_pad * pulse)
    bx = (W - bw - pad*2) // 2
    by = 408
    btn_h = int(80 * pulse)
    ld.rounded_rectangle([bx, by, bx+bw+pad*2, by+btn_h],
                          radius=btn_h//2, fill=(*RED, 255))
    ld.text((bx+pad, by+(btn_h-bh)//2-2), btn_text, fill=(*WHITE, 255), font=f_btn)

    dl_a = ease_out(clamp((l - 0.22) / 0.28, 0, 1))
    cxd(ld, "INSTANT DOWNLOAD", 522, fnt(58), WHITE, dl_a)
    ld.rectangle([60, 600, W-60, 602], fill=(*SILVER, int(60*dl_a)))
    cat_a = ease_out(clamp((l - 0.42) / 0.24, 0, 1))
    cxd(ld, "53 Templates · 8 Categories", 616, fnt(24, bold=False), (100,100,100), cat_a)
    cxd(ld, "Forms, Social, Branding, Email, Flyers & More", 658, fnt(22, bold=False), (80,80,80), cat_a)
    url_a = ease_out(clamp((l - 0.56) / 0.22, 0, 1))
    cxd(ld, "purpleocaz.etsy.com", 716, fnt(28, bold=False), SILVER, url_a)
    cxd(ld, "£39.99 — Shop Now", 758, fnt(26, bold=False), RED, url_a)

    return comp(base, layer, a)


def generate_frame(t):
    base = make_base()
    base = draw_phase1(base, t)
    base = draw_phase2(base, t)
    base = draw_phase3(base, t)
    base = draw_phase4(base, t)
    base = draw_phase5(base, t)
    return base


def pillow_fallback():
    print("\n[Fallback] Generating Pillow frames (250 × 1000×1500)...")
    os.makedirs(FRAMES_DIR, exist_ok=True)
    paths = []
    for i in range(TOTAL):
        t = i / FPS
        img = generate_frame(t)
        p = os.path.join(FRAMES_DIR, f"frame_{i:04d}.png")
        img.save(p, "PNG")
        paths.append(p)
        if i % 50 == 0:
            print(f"  {i}/{TOTAL} frames", end="\r", flush=True)
    print(f"  {TOTAL}/{TOTAL} frames — done.")

    print("[FFmpeg] Stitching frames...")
    subprocess.run([
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", os.path.join(FRAMES_DIR, "frame_%04d.png"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "22", "-preset", "fast",
        MP4_OUT
    ], check=True)

    import shutil
    shutil.rmtree(FRAMES_DIR, ignore_errors=True)

    size = os.path.getsize(MP4_OUT) / 1024 / 1024
    print(f"[FFmpeg] Done — {os.path.basename(MP4_OUT)} ({size:.1f} MB)")
    return MP4_OUT


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 3 — SPACES UPLOAD
# ═══════════════════════════════════════════════════════════════════════════════
def load_spaces():
    env = os.path.join(PROJECT, "purpleocaz-canva-mcp", ".env")
    if os.path.exists(env):
        with open(env) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

def get_s3():
    return boto3.client(
        "s3",
        endpoint_url=os.environ["DO_SPACES_ENDPOINT"],
        aws_access_key_id=os.environ["DO_SPACES_KEY"],
        aws_secret_access_key=os.environ["DO_SPACES_SECRET"],
        region_name=os.environ["DO_SPACES_REGION"],
    )

def upload(s3, local, key):
    bucket = os.environ.get("DO_SPACES_BUCKET", "purpleocaz-assets")
    ext = os.path.splitext(local)[1].lower()
    ct = {"html": "text/html", "mp4": "video/mp4"}.get(ext.lstrip("."), "application/octet-stream")
    s3.upload_file(local, bucket, key, ExtraArgs={"ACL": "public-read", "ContentType": ct})
    cdn = os.environ.get("DO_SPACES_CDN_BASE",
                         "https://purpleocaz-assets.lon1.digitaloceanspaces.com")
    url = f"{cdn}/{key}"
    print(f"  ↑ {os.path.basename(local)} → {url}")
    return url


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    print("=" * 62)
    print("CAR DETAILING ANIMATED PIN BUILD")
    print("=" * 62)

    # Step 1: HTML
    print("\n=== Step 1: HTML Landing Page ===")
    write_html()

    # Step 2: Video
    print("\n=== Step 2: Video Pin (Puppeteer or Pillow fallback) ===")
    mp4_path = None
    try:
        mp4_path = try_puppeteer()
        print("[Puppeteer] SUCCESS")
    except Exception as e:
        print(f"[Puppeteer] FAILED ({e}) — using Pillow fallback")
        mp4_path = pillow_fallback()

    # Step 3: Upload
    print("\n=== Step 3: Upload to DO Spaces ===")
    load_spaces()
    s3 = get_s3()
    html_url = upload(s3, HTML_OUT, "pinterest/car-detail-landing.html")
    mp4_url  = upload(s3, mp4_path,  "pinterest/car-detail-animated-pin.mp4")

    # Verify
    print("\n=== Step 4: Verify ===")
    for label, url in [("HTML", html_url), ("MP4", mp4_url)]:
        req = urllib.request.Request(url, method="HEAD")
        resp = urllib.request.urlopen(req)
        sz  = resp.headers.get("Content-Length", "?")
        print(f"  {label}: HTTP {resp.status} OK  ({int(sz)//1024 if sz != '?' else '?'} KB)")

    print("\n" + "=" * 62)
    print("DONE")
    print(f"  HTML : {html_url}")
    print(f"  MP4  : {mp4_url}")
    print("=" * 62)


if __name__ == "__main__":
    main()
