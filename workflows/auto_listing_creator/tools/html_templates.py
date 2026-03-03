# =============================================================================
# workflows/auto_listing_creator/tools/html_templates.py
#
# Product-type-specific HTML template functions.  Each returns a complete
# HTML string sized to (TMPL_W x TMPL_H) ready for Playwright screenshot.
# =============================================================================

from tools.design_constants import (
    FONTS_CSS, TMPL_W, TMPL_H,
    DARK_BG, DARK_CARD, ACCENT_ORANGE, ACCENT_GOLD, GOLD_FOIL, esc,
)


# -- Appointment Card (black + gold foil split with torn-paper edge) ---------

def tmpl_appointment_card():
    """Black + gold foil split appointment card with torn-paper diagonal edge.

    Matches the premium Etsy template aesthetic: left 38% gold foil texture,
    right 62% solid black, separated by an irregular torn-paper polygon.
    Front: script title, form fields (NAME/DATE/TIME), weekday selector.
    Back: circular logo placeholder, script title, contact block.
    """
    return f'''<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
{FONTS_CSS}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:{TMPL_W}px; height:{TMPL_H}px; overflow:hidden; }}
body {{
    background: #0D0D0D;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 50px;
    padding: 20px 50px;
}}

/* ---------- shared card shell ---------- */
.face {{
    position: relative;
    width: 880px; height: 890px;
    border-radius: 16px;
    overflow: hidden;
}}

/* ---------- gold / black split background ---------- */
.card-split {{
    position: absolute; inset: 0;
    display: flex;
}}
.gold-side {{
    width: 38%; height: 100%;
    background:
        url("data:image/svg+xml,%3Csvg viewBox='0 0 300 300' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='f'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='5' stitchTiles='stitch'/%3E%3CfeColorMatrix type='saturate' values='0.3'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23f)' opacity='0.18'/%3E%3C/svg%3E"),
        linear-gradient(135deg, #E8D5A8 0%, {GOLD_FOIL} 30%, #B8944A 55%, {GOLD_FOIL} 75%, #E8D5A8 100%);
}}
.black-side {{
    width: 62%; height: 100%;
    background: #0F0F0F;
}}

/* ---------- torn-paper diagonal edge overlay ---------- */
.torn-edge {{
    position: absolute;
    top: 0; left: 34%; width: 12%; height: 100%;
    z-index: 2;
    background: #0F0F0F;
    clip-path: polygon(
        40% 0%, 35% 2%, 42% 4%, 32% 6%, 44% 8%,
        30% 10%, 38% 12%, 28% 14%, 40% 16%, 26% 18%,
        36% 20%, 24% 22%, 38% 24%, 22% 26%, 34% 28%,
        20% 30%, 32% 32%, 18% 34%, 30% 36%, 16% 38%,
        28% 40%, 14% 42%, 26% 44%, 12% 46%, 24% 48%,
        10% 50%, 22% 52%, 8% 54%, 20% 56%, 6% 58%,
        18% 60%, 4% 62%, 16% 64%, 2% 66%, 14% 68%,
        0% 70%, 12% 72%, 0% 74%, 10% 76%, 0% 78%,
        8% 80%, 0% 82%, 6% 84%, 0% 86%, 4% 88%,
        0% 90%, 2% 92%, 0% 94%, 0% 96%, 0% 98%, 0% 100%,
        100% 100%, 100% 0%
    );
}}

/* ---------- content layer (above split) ---------- */
.card-content {{
    position: relative; z-index: 3;
    width: 100%; height: 100%;
    display: flex; flex-direction: column;
}}

/* === FRONT CARD === */
.front-body {{
    flex: 1;
    padding: 65px 55px 50px 400px;
    display: flex; flex-direction: column;
    justify-content: center;
    gap: 28px;
}}
.front-title {{
    font-family: 'Great Vibes', cursive;
    font-size: 52px;
    color: #FFFFFF;
    line-height: 1.2;
}}
.form-group {{
    display: flex; flex-direction: column; gap: 20px;
}}
.form-row {{
    display: flex; align-items: center; gap: 12px;
}}
.form-label {{
    font-family: 'Montserrat', sans-serif;
    font-size: 12px; font-weight: 700;
    color: #FFFFFF; letter-spacing: 2px;
    text-transform: uppercase;
    white-space: nowrap;
    min-width: 60px;
}}
.form-field {{
    flex: 1; height: 24px;
    background: #FFFFFF;
    border-radius: 4px;
}}
.weekday-row {{
    display: flex; gap: 10px;
    margin-top: 12px;
}}
.day-btn {{
    width: 62px; height: 30px;
    background: #FFFFFF;
    border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Montserrat', sans-serif;
    font-size: 10px; font-weight: 700;
    color: #1C1C1C; letter-spacing: 1px;
}}

/* === BACK CARD === */
.back-body {{
    flex: 1;
    padding: 50px 55px 50px 400px;
    display: flex; flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 20px;
}}
.logo-circle {{
    width: 150px; height: 150px;
    border-radius: 50%;
    border: 3px solid #FFFFFF;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    gap: 4px;
}}
.logo-text {{
    font-family: 'Montserrat', sans-serif;
    font-size: 10px; font-weight: 600;
    color: #FFFFFF; letter-spacing: 2px;
    text-transform: uppercase;
    text-align: center;
}}
.back-title {{
    font-family: 'Great Vibes', cursive;
    font-size: 42px;
    color: #FFFFFF;
    text-align: center;
}}
.contact-block {{
    display: flex; flex-direction: column;
    align-items: center; gap: 10px;
    margin-top: 10px;
}}
.contact-line {{
    font-family: 'Montserrat', sans-serif;
    font-size: 13px; color: #FFFFFF;
    letter-spacing: 0.5px;
}}
</style></head><body>

<!-- ====== FRONT CARD ====== -->
<div class="face">
    <div class="card-split">
        <div class="gold-side"></div>
        <div class="black-side"></div>
    </div>
    <div class="torn-edge"></div>
    <div class="card-content">
        <div class="front-body">
            <div class="front-title">Appointment Card</div>
            <div class="form-group">
                <div class="form-row">
                    <div class="form-label">NAME:</div>
                    <div class="form-field"></div>
                </div>
                <div class="form-row">
                    <div class="form-label">DATE:</div>
                    <div class="form-field"></div>
                </div>
                <div class="form-row">
                    <div class="form-label">TIME:</div>
                    <div class="form-field"></div>
                </div>
            </div>
            <div class="weekday-row">
                <div class="day-btn">MON</div>
                <div class="day-btn">TUE</div>
                <div class="day-btn">WED</div>
                <div class="day-btn">THU</div>
                <div class="day-btn">FRI</div>
                <div class="day-btn">SAT</div>
            </div>
        </div>
    </div>
</div>

<!-- ====== BACK CARD ====== -->
<div class="face">
    <div class="card-split">
        <div class="gold-side"></div>
        <div class="black-side"></div>
    </div>
    <div class="torn-edge"></div>
    <div class="card-content">
        <div class="back-body">
            <div class="logo-circle">
                <div class="logo-text">LOGO</div>
                <div class="logo-text">HERE</div>
            </div>
            <div class="back-title">Book Appointment</div>
            <div class="contact-block">
                <div class="contact-line">name@yourbusiness.com</div>
                <div class="contact-line">555-555-5555</div>
                <div class="contact-line">WWW.YOURBUSINESS.COM</div>
            </div>
        </div>
    </div>
</div>

</body></html>'''


# -- Gift Certificate (elegant dark with gold accents) ----------------------

def tmpl_gift_certificate():
    """Dark gift certificate with gold border and decorative corners."""
    return f'''<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
{FONTS_CSS}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:{TMPL_W}px; height:{TMPL_H}px; overflow:hidden; }}
body {{
    background: {DARK_BG};
    display: flex; align-items: center; justify-content: center;
    padding: 25px;
}}
.cert {{
    width: 1920px; height: 900px;
    background: {DARK_CARD};
    border: 2px solid {ACCENT_GOLD};
    border-radius: 12px;
    position: relative;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    padding: 50px 80px;
}}
.cert::before {{
    content: ''; position: absolute;
    top: 12px; left: 12px; right: 12px; bottom: 12px;
    border: 1px solid rgba(201, 168, 76, 0.3);
    border-radius: 8px; pointer-events: none;
}}
.corner {{
    position: absolute; width: 40px; height: 40px;
    border-color: {ACCENT_GOLD}; border-style: solid;
}}
.c-tl {{ top: 24px; left: 24px; border-width: 2px 0 0 2px; }}
.c-tr {{ top: 24px; right: 24px; border-width: 2px 2px 0 0; }}
.c-bl {{ bottom: 24px; left: 24px; border-width: 0 0 2px 2px; }}
.c-br {{ bottom: 24px; right: 24px; border-width: 0 2px 2px 0; }}
.biz {{
    font-family: 'Montserrat', sans-serif;
    font-size: 14px; font-weight: 700;
    color: {ACCENT_GOLD}; letter-spacing: 8px;
    text-transform: uppercase; margin-bottom: 10px;
}}
.fl-top {{
    width: 180px; height: 2px;
    background: linear-gradient(90deg, transparent, {ACCENT_GOLD}, transparent);
    margin-bottom: 25px;
}}
.cert-title {{
    font-family: 'Playfair Display', serif;
    font-size: 68px; font-weight: 700;
    color: #FFF; letter-spacing: 3px;
    margin-bottom: 8px;
}}
.cert-sub {{
    font-family: 'Montserrat', sans-serif;
    font-size: 13px; color: #888;
    letter-spacing: 4px; text-transform: uppercase;
    margin-bottom: 25px;
}}
.fl-bot {{
    width: 120px; height: 2px;
    background: linear-gradient(90deg, transparent, {ACCENT_GOLD}, transparent);
    margin-bottom: 35px;
}}
.cert-fields {{
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 25px 80px; width: 100%; max-width: 1200px;
}}
.cf {{ display: flex; flex-direction: column; gap: 8px; }}
.cf-label {{
    font-family: 'Montserrat', sans-serif;
    font-size: 11px; font-weight: 700;
    color: {ACCENT_GOLD}; letter-spacing: 3px;
    text-transform: uppercase;
}}
.cf-line {{ height: 1px; background: #333; }}
.fine {{
    font-family: 'Montserrat', sans-serif;
    font-size: 11px; color: #555; font-style: italic;
    text-align: center; margin-top: 30px;
}}
</style></head><body>
<div class="cert">
    <div class="corner c-tl"></div>
    <div class="corner c-tr"></div>
    <div class="corner c-bl"></div>
    <div class="corner c-br"></div>
    <div class="biz">Your Studio Name</div>
    <div class="fl-top"></div>
    <div class="cert-title">Gift Certificate</div>
    <div class="cert-sub">Tattoo &amp; Body Art</div>
    <div class="fl-bot"></div>
    <div class="cert-fields">
        <div class="cf"><div class="cf-label">Recipient</div><div class="cf-line"></div></div>
        <div class="cf"><div class="cf-label">Amount</div><div class="cf-line"></div></div>
        <div class="cf"><div class="cf-label">From</div><div class="cf-line"></div></div>
        <div class="cf"><div class="cf-label">Valid Until</div><div class="cf-line"></div></div>
    </div>
    <div class="fine">This voucher is non-refundable and cannot be exchanged for cash</div>
</div>
</body></html>'''


# -- Price List / Service Menu -----------------------------------------------

def tmpl_price_list():
    """Dark service menu with categories and dotted-line pricing."""
    return f'''<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
{FONTS_CSS}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:{TMPL_W}px; height:{TMPL_H}px; overflow:hidden; }}
body {{
    background: {DARK_BG};
    display: flex; align-items: center; justify-content: center;
    padding: 25px;
}}
.menu {{
    width: 1920px; height: 900px;
    background: {DARK_CARD};
    border: 1px solid #333; border-radius: 12px;
    padding: 45px 80px;
    display: flex; flex-direction: column;
}}
.menu-header {{ text-align: center; margin-bottom: 30px; }}
.menu-biz {{
    font-family: 'Montserrat', sans-serif;
    font-size: 12px; font-weight: 700;
    color: {ACCENT_ORANGE}; letter-spacing: 6px;
    text-transform: uppercase; margin-bottom: 10px;
}}
.menu-title {{
    font-family: 'Oswald', sans-serif;
    font-size: 48px; font-weight: 700;
    color: #FFF; letter-spacing: 6px;
    text-transform: uppercase;
}}
.menu-line {{
    width: 80px; height: 2px;
    background: {ACCENT_ORANGE};
    margin: 12px auto 0;
}}
.cols {{
    flex: 1; display: grid;
    grid-template-columns: 1fr 1fr; gap: 0 80px;
}}
.cat {{ margin-bottom: 22px; }}
.cat-name {{
    font-family: 'Oswald', sans-serif;
    font-size: 16px; font-weight: 600;
    color: {ACCENT_ORANGE}; letter-spacing: 4px;
    text-transform: uppercase;
    margin-bottom: 12px; padding-bottom: 6px;
    border-bottom: 1px solid #333;
}}
.mi {{
    display: flex; justify-content: space-between;
    align-items: baseline; padding: 5px 0;
    font-family: 'Montserrat', sans-serif;
}}
.mi-name {{ font-size: 13px; color: #CCC; }}
.mi-dots {{
    flex: 1; border-bottom: 1px dotted #444;
    margin: 0 10px; min-width: 20px;
}}
.mi-price {{ font-size: 13px; color: #FFF; font-weight: 600; }}
</style></head><body>
<div class="menu">
    <div class="menu-header">
        <div class="menu-biz">Your Studio Name</div>
        <div class="menu-title">Service Menu</div>
        <div class="menu-line"></div>
    </div>
    <div class="cols">
        <div>
            <div class="cat"><div class="cat-name">Tattoo</div>
                <div class="mi"><span class="mi-name">Small (up to 2")</span><span class="mi-dots"></span><span class="mi-price">$80</span></div>
                <div class="mi"><span class="mi-name">Medium (2-4")</span><span class="mi-dots"></span><span class="mi-price">$150</span></div>
                <div class="mi"><span class="mi-name">Large (4-6")</span><span class="mi-dots"></span><span class="mi-price">$250</span></div>
                <div class="mi"><span class="mi-name">Half Sleeve</span><span class="mi-dots"></span><span class="mi-price">$800+</span></div>
                <div class="mi"><span class="mi-name">Full Sleeve</span><span class="mi-dots"></span><span class="mi-price">$1500+</span></div>
            </div>
            <div class="cat"><div class="cat-name">Touch-Up</div>
                <div class="mi"><span class="mi-name">Minor Touch-Up</span><span class="mi-dots"></span><span class="mi-price">$50</span></div>
                <div class="mi"><span class="mi-name">Major Touch-Up</span><span class="mi-dots"></span><span class="mi-price">$100</span></div>
            </div>
        </div>
        <div>
            <div class="cat"><div class="cat-name">Piercing</div>
                <div class="mi"><span class="mi-name">Ear Lobe</span><span class="mi-dots"></span><span class="mi-price">$30</span></div>
                <div class="mi"><span class="mi-name">Helix / Cartilage</span><span class="mi-dots"></span><span class="mi-price">$45</span></div>
                <div class="mi"><span class="mi-name">Nose</span><span class="mi-dots"></span><span class="mi-price">$40</span></div>
                <div class="mi"><span class="mi-name">Septum</span><span class="mi-dots"></span><span class="mi-price">$50</span></div>
            </div>
            <div class="cat"><div class="cat-name">Consultation</div>
                <div class="mi"><span class="mi-name">Design Consultation</span><span class="mi-dots"></span><span class="mi-price">Free</span></div>
                <div class="mi"><span class="mi-name">Custom Design</span><span class="mi-dots"></span><span class="mi-price">$50/hr</span></div>
            </div>
        </div>
    </div>
</div>
</body></html>'''


# -- Aftercare Card (numbered steps) ----------------------------------------

def tmpl_aftercare_card():
    """Dark aftercare card with numbered instruction steps."""
    return f'''<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
{FONTS_CSS}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:{TMPL_W}px; height:{TMPL_H}px; overflow:hidden; }}
body {{
    background: {DARK_BG};
    display: flex; align-items: center; justify-content: center;
    padding: 25px;
}}
.card {{
    width: 1920px; height: 900px;
    background: {DARK_CARD};
    border: 1px solid #333; border-radius: 12px;
    overflow: hidden;
    display: flex; flex-direction: column;
}}
.card-stripe {{ height: 6px; background: {ACCENT_ORANGE}; flex-shrink: 0; }}
.card-body {{
    flex: 1; padding: 40px 80px;
    display: flex; flex-direction: column;
}}
.card-header {{ text-align: center; margin-bottom: 25px; }}
.card-biz {{
    font-family: 'Montserrat', sans-serif;
    font-size: 12px; font-weight: 700;
    color: {ACCENT_ORANGE}; letter-spacing: 6px;
    text-transform: uppercase; margin-bottom: 8px;
}}
.card-title {{
    font-family: 'Oswald', sans-serif;
    font-size: 42px; font-weight: 700;
    color: #FFF; letter-spacing: 5px;
    text-transform: uppercase;
}}
.card-line {{
    width: 60px; height: 2px;
    background: {ACCENT_ORANGE};
    margin: 12px auto 25px;
}}
.steps {{
    flex: 1; display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 18px 60px; align-content: start;
}}
.step {{
    display: flex; align-items: flex-start; gap: 16px;
}}
.step-num {{
    width: 32px; height: 32px;
    background: {ACCENT_ORANGE}; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Montserrat', sans-serif;
    font-size: 14px; font-weight: 700; color: #FFF;
    flex-shrink: 0;
}}
.step-text {{
    font-family: 'Montserrat', sans-serif;
    font-size: 14px; color: #CCC; line-height: 1.5;
    padding-top: 5px;
}}
.card-footer {{
    background: #111; padding: 12px 80px;
    display: flex; justify-content: center; gap: 40px;
    font-family: 'Montserrat', sans-serif;
    font-size: 12px; color: #555;
}}
</style></head><body>
<div class="card">
    <div class="card-stripe"></div>
    <div class="card-body">
        <div class="card-header">
            <div class="card-biz">Your Studio Name</div>
            <div class="card-title">Tattoo Aftercare</div>
        </div>
        <div class="card-line"></div>
        <div class="steps">
            <div class="step"><div class="step-num">1</div><div class="step-text">Keep bandage on for 2-4 hours after your session</div></div>
            <div class="step"><div class="step-num">2</div><div class="step-text">Wash gently with warm water and fragrance-free soap</div></div>
            <div class="step"><div class="step-num">3</div><div class="step-text">Pat dry and apply a thin layer of recommended ointment</div></div>
            <div class="step"><div class="step-num">4</div><div class="step-text">Repeat washing and moisturising 2-3 times daily for 2 weeks</div></div>
            <div class="step"><div class="step-num">5</div><div class="step-text">Avoid swimming, saunas and direct sunlight while healing</div></div>
            <div class="step"><div class="step-num">6</div><div class="step-text">Do not pick, scratch or peel the healing skin</div></div>
            <div class="step"><div class="step-num">7</div><div class="step-text">Wear loose clothing over the tattooed area</div></div>
            <div class="step"><div class="step-num">8</div><div class="step-text">Contact your artist if you notice signs of infection</div></div>
        </div>
    </div>
    <div class="card-footer">
        <span>email@yourstudio.com</span>
        <span>+1 (234) 567-890</span>
        <span>www.yourstudio.com</span>
    </div>
</div>
</body></html>'''


# -- Generic (covers consent forms, business cards, etc.) --------------------

def tmpl_generic(product_type):
    """Versatile dark template that adapts fields to the product type."""
    display_name = product_type.strip().title()
    if not display_name:
        display_name = "Template"

    if "consent" in product_type:
        fields_html = (
            '<div class="fg"><div class="fl">Client Name</div><div class="fline"></div></div>'
            '<div class="fg"><div class="fl">Date of Birth</div><div class="fline"></div></div>'
            '<div class="fg"><div class="fl">Phone</div><div class="fline"></div></div>'
            '<div class="fg"><div class="fl">Email</div><div class="fline"></div></div>'
            '<div class="fg"><div class="fl">Medical Conditions</div><div class="fline"></div></div>'
            '<div class="fg"><div class="fl">Allergies</div><div class="fline"></div></div>'
            '<div class="fg"><div class="fl">Signature</div><div class="fline"></div></div>'
            '<div class="fg"><div class="fl">Date</div><div class="fline"></div></div>'
        )
    elif "business" in product_type:
        fields_html = (
            '<div class="fg"><div class="fl">Your Name</div><div class="fline"></div></div>'
            '<div class="fg"><div class="fl">Title / Role</div><div class="fline"></div></div>'
            '<div class="fg"><div class="fl">Phone</div><div class="fline"></div></div>'
            '<div class="fg"><div class="fl">Email</div><div class="fline"></div></div>'
            '<div class="fg"><div class="fl">Website</div><div class="fline"></div></div>'
            '<div class="fg"><div class="fl">Address</div><div class="fline"></div></div>'
        )
    elif "social" in product_type or "instagram" in product_type:
        fields_html = (
            '<div class="fg"><div class="fl">Studio Name</div><div class="fline"></div></div>'
            '<div class="fg"><div class="fl">Handle / Username</div><div class="fline"></div></div>'
            '<div class="fg"><div class="fl">Your Photo Here</div><div class="fline"></div></div>'
            '<div class="fg"><div class="fl">Call to Action</div><div class="fline"></div></div>'
        )
    else:
        fields_html = (
            '<div class="fg"><div class="fl">Name</div><div class="fline"></div></div>'
            '<div class="fg"><div class="fl">Date</div><div class="fline"></div></div>'
            '<div class="fg"><div class="fl">Phone</div><div class="fline"></div></div>'
            '<div class="fg"><div class="fl">Email</div><div class="fline"></div></div>'
            '<div class="fg"><div class="fl">Details</div><div class="fline"></div></div>'
            '<div class="fg"><div class="fl">Notes</div><div class="fline"></div></div>'
        )

    return f'''<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
{FONTS_CSS}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:{TMPL_W}px; height:{TMPL_H}px; overflow:hidden; }}
body {{
    background: {DARK_BG};
    display: flex; align-items: center; justify-content: center;
    padding: 25px;
}}
.card {{
    width: 1920px; height: 900px;
    background: {DARK_CARD};
    border: 1px solid #333; border-radius: 12px;
    overflow: hidden;
    display: flex; flex-direction: column;
}}
.card-stripe {{ height: 6px; background: {ACCENT_ORANGE}; flex-shrink: 0; }}
.card-body {{
    flex: 1; padding: 45px 80px;
    display: flex; flex-direction: column;
}}
.card-header {{ text-align: center; margin-bottom: 25px; }}
.card-biz {{
    font-family: 'Montserrat', sans-serif;
    font-size: 12px; font-weight: 700;
    color: {ACCENT_ORANGE}; letter-spacing: 6px;
    text-transform: uppercase; margin-bottom: 8px;
}}
.card-title {{
    font-family: 'Oswald', sans-serif;
    font-size: 44px; font-weight: 700;
    color: #FFF; letter-spacing: 5px;
    text-transform: uppercase;
}}
.card-sub {{
    font-family: 'Montserrat', sans-serif;
    font-size: 13px; color: #666;
    letter-spacing: 2px; margin-top: 8px;
}}
.card-divider {{
    width: 60px; height: 2px;
    background: {ACCENT_ORANGE};
    margin: 0 auto 25px;
}}
.card-fields {{
    flex: 1; display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 22px 80px; align-content: start;
}}
.fg {{ display: flex; flex-direction: column; gap: 8px; }}
.fl {{
    font-family: 'Montserrat', sans-serif;
    font-size: 11px; font-weight: 700;
    color: {ACCENT_ORANGE}; letter-spacing: 3px;
    text-transform: uppercase;
}}
.fline {{ height: 1px; background: #333; }}
.card-footer {{
    background: #111; padding: 12px 80px;
    display: flex; justify-content: space-between;
    font-family: 'Montserrat', sans-serif;
    font-size: 12px; color: #555;
}}
</style></head><body>
<div class="card">
    <div class="card-stripe"></div>
    <div class="card-body">
        <div class="card-header">
            <div class="card-biz">Your Studio Name</div>
            <div class="card-title">{esc(display_name)}</div>
            <div class="card-sub">Fully editable in Canva</div>
        </div>
        <div class="card-divider"></div>
        <div class="card-fields">
            {fields_html}
        </div>
    </div>
    <div class="card-footer">
        <span>email@yourstudio.com</span>
        <span>+1 (234) 567-890</span>
        <span>www.yourstudio.com</span>
        <span>123 Ink Street, Any City</span>
    </div>
</div>
</body></html>'''
