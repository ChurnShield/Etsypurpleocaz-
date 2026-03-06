# =============================================================================
# workflows/auto_listing_creator/tools/html_templates.py
#
# Product-type-specific HTML template functions.  Each returns a complete
# HTML string sized to (TMPL_W x TMPL_H) ready for Playwright screenshot.
# =============================================================================

from tools.design_constants import (
    FONTS_CSS, TMPL_W, TMPL_H,
    DARK_BG, DARK_CARD, ACCENT_ORANGE, ACCENT_GOLD, esc,
)


# -- Appointment Card (two-panel front/back with torn paper edges) -----------

def tmpl_appointment_card():
    """B&W appointment card with torn paper edges on black background."""
    return f'''<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
{FONTS_CSS}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:{TMPL_W}px; height:{TMPL_H}px; overflow:hidden; }}
body {{
    background: #000;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 50px;
    padding: 20px 50px;
}}
.face {{
    position: relative;
    width: 880px; height: 890px;
}}
.front-card, .back-card {{
    width: 100%; height: 100%;
    background: #F5F2ED;
    clip-path: polygon(
        0% 1%, 2% 0%, 5% 1.5%, 7% 0.3%, 10% 1%, 13% 0%,
        16% 1.2%, 19% 0.5%, 22% 1.8%, 25% 0%, 28% 0.8%,
        31% 0.2%, 34% 1.5%, 37% 0%, 40% 1%, 43% 0.3%,
        46% 1.2%, 49% 0%, 52% 1.6%, 55% 0.4%, 58% 1%,
        61% 0%, 64% 1.3%, 67% 0.2%, 70% 0.9%, 73% 0%,
        76% 1.5%, 79% 0.3%, 82% 1.1%, 85% 0%, 88% 0.7%,
        91% 0.1%, 94% 1.4%, 97% 0%, 100% 0.8%,
        100% 2%, 99.5% 5%, 100% 8%, 99.3% 11%, 100% 14%,
        99.7% 17%, 100% 20%, 99.4% 23%, 100% 26%, 99.8% 29%,
        100% 32%, 99.2% 35%, 100% 38%, 99.6% 41%, 100% 44%,
        99.3% 47%, 100% 50%, 99.7% 53%, 100% 56%, 99.1% 59%,
        100% 62%, 99.5% 65%, 100% 68%, 99.4% 71%, 100% 74%,
        99.8% 77%, 100% 80%, 99.2% 83%, 100% 86%, 99.6% 89%,
        100% 92%, 99.3% 95%, 100% 98%, 99.5% 100%,
        97% 99.2%, 94% 100%, 91% 99.5%, 88% 100%, 85% 99.1%,
        82% 100%, 79% 99.6%, 76% 100%, 73% 99.3%, 70% 100%,
        67% 99.8%, 64% 100%, 61% 99.2%, 58% 100%, 55% 99.5%,
        52% 100%, 49% 99.7%, 46% 100%, 43% 99.1%, 40% 100%,
        37% 99.4%, 34% 100%, 31% 99.6%, 28% 100%, 25% 99.2%,
        22% 100%, 19% 99.8%, 16% 100%, 13% 99.3%, 10% 100%,
        7% 99.7%, 4% 100%, 1% 99.1%, 0% 100%,
        0.5% 97%, 0% 94%, 0.7% 91%, 0% 88%, 0.4% 85%,
        0% 82%, 0.8% 79%, 0% 76%, 0.3% 73%, 0% 70%,
        0.6% 67%, 0% 64%, 0.5% 61%, 0% 58%, 0.9% 55%,
        0% 52%, 0.4% 49%, 0% 46%, 0.7% 43%, 0% 40%,
        0.3% 37%, 0% 34%, 0.8% 31%, 0% 28%, 0.5% 25%,
        0% 22%, 0.6% 19%, 0% 16%, 0.4% 13%, 0% 10%,
        0.7% 7%, 0% 4%
    );
    display: flex; flex-direction: column;
}}
.front-card::before, .back-card::before {{
    content: '';
    position: absolute; inset: 0;
    background: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.03'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 1;
}}
.front-body {{
    flex: 1; padding: 60px 55px 50px;
    display: flex; flex-direction: column;
    justify-content: space-between;
    position: relative;
}}
.studio-name {{
    font-family: 'Oswald', sans-serif;
    font-size: 48px; font-weight: 700;
    color: #111; letter-spacing: 4px;
    text-transform: uppercase; line-height: 1.1;
}}
.studio-sub {{
    font-family: 'Montserrat', sans-serif;
    font-size: 13px; font-weight: 600;
    color: #555; letter-spacing: 6px;
    text-transform: uppercase; margin-top: 12px;
}}
.front-line {{
    width: 80px; height: 3px;
    background: #111; margin: 30px 0;
}}
.contacts {{ display: flex; flex-direction: column; gap: 16px; }}
.c-row {{
    display: flex; align-items: center; gap: 14px;
    font-family: 'Montserrat', sans-serif;
    font-size: 14px; color: #444; letter-spacing: 0.5px;
}}
.c-icon {{
    width: 20px; height: 20px;
    display: flex; align-items: center;
    justify-content: center;
    flex-shrink: 0;
    font-size: 14px; color: #222;
}}
.back-body {{
    flex: 1; padding: 55px 55px 45px;
    display: flex; flex-direction: column;
    position: relative;
}}
.appt-h {{
    font-family: 'Oswald', sans-serif;
    font-size: 40px; font-weight: 700;
    color: #111; letter-spacing: 8px;
    text-transform: uppercase; text-align: center;
}}
.appt-sub {{
    font-family: 'Montserrat', sans-serif;
    font-size: 11px; color: #777;
    text-align: center; letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 8px; margin-bottom: 35px;
}}
.back-line {{
    width: 50px; height: 3px;
    background: #111;
    margin: 0 auto 35px;
}}
.fields {{ flex: 1; display: flex; flex-direction: column; justify-content: space-between; }}
.fg {{ display: flex; flex-direction: column; gap: 8px; }}
.fl {{
    font-family: 'Montserrat', sans-serif;
    font-size: 11px; font-weight: 700;
    color: #333; letter-spacing: 3px;
    text-transform: uppercase;
}}
.fline {{ height: 1px; background: #CCC; }}
.corner-brand {{
    position: absolute; bottom: 30px; right: 40px;
    font-family: 'Montserrat', sans-serif;
    font-size: 9px; color: #BBB;
    letter-spacing: 3px; text-transform: uppercase;
}}
</style></head><body>
<div class="face">
    <div class="front-card">
        <div class="front-body">
            <div>
                <div class="studio-name">Your Studio<br>Name</div>
                <div class="studio-sub">Tattoo &amp; Piercing</div>
                <div class="front-line"></div>
            </div>
            <div class="contacts">
                <div class="c-row"><div class="c-icon">&#9993;</div> email@yourstudio.com</div>
                <div class="c-row"><div class="c-icon">&#9742;</div> +1 (234) 567-890</div>
                <div class="c-row"><div class="c-icon">&#9758;</div> www.yourstudio.com</div>
                <div class="c-row"><div class="c-icon">&#9679;</div> 123 Ink Street, Any City</div>
            </div>
            <div class="corner-brand">Editable Template</div>
        </div>
    </div>
</div>
<div class="face">
    <div class="back-card">
        <div class="back-body">
            <div class="appt-h">Appointment</div>
            <div class="appt-sub">Please keep this card for your records</div>
            <div class="back-line"></div>
            <div class="fields">
                <div class="fg"><div class="fl">Client Name</div><div class="fline"></div></div>
                <div class="fg"><div class="fl">Date</div><div class="fline"></div></div>
                <div class="fg"><div class="fl">Time</div><div class="fline"></div></div>
                <div class="fg"><div class="fl">Artist</div><div class="fline"></div></div>
                <div class="fg"><div class="fl">Notes</div><div class="fline"></div></div>
            </div>
            <div class="corner-brand">Editable Template</div>
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
