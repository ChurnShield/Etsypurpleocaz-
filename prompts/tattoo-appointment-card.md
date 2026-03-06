# Tattoo Studio Appointment Card - Etsy Thumbnail Prompts

## LATEST (White Rectangular Cards - Gold Foil)
Status: Ready to generate - needs Replicate credit top-up

```
Ultra-sharp 8K flat-lay product photography, square format. Warm beige linen fabric background with gentle natural folds and subtle creases. Diffused warm top-left lighting with soft natural shadows.

Props: Partial white coffee cup with latte art foam top-left corner. Small green succulent in white pot top-right corner. Eucalyptus branches draping from bottom-left. Sleek black and gold pen diagonal bottom-right touching the cards.

Center: Two BRIGHT WHITE rectangular business cards (standard 3.5 x 2 inch horizontal rectangle shape, clearly wider than tall) overlapping with realistic thick cardstock texture, visible card edges, and soft drop shadows on the beige fabric. Front card larger, centered, slight 4 degree tilt. Back card 80% scale, rotated 11 degrees clockwise, tucked behind front card with 3D elevation and cast shadow.

FRONT CARD is CRISP WHITE with GOLD METALLIC FOIL text and thin gold border:
Top center large gold cursive script: Your Studio Name
Thin gold horizontal line below with spacing
Six perfectly aligned rows of thin gold sans-serif uppercase labels with gold underlines:
CLIENT NAME _______________
DATE _______________
TIME _______________
ARTIST _______________
SERVICE _______________
NOTES _______________
Bottom small gold text: @yourhandle www.yourstudio.com
Corner: tiny gold circle text LOGO
NO flowers NO mandalas NO decorations. Pure minimalist white card with gold typography only.

BACK CARD is CRISP WHITE with thin gold border and only small centered gold text: YOUR STUDIO NAME. Clean and minimal.

Full-width deep charcoal banner across bottom 27% of image, sharp horizontal line. Large bold white sans-serif centered: TATTOO STUDIO APPOINTMENT CARDS. Below smaller white uppercase: KEEP CLIENTS ORGANIZED IN PREMIUM STYLE. Bottom-right dark circle badge white text: EDIT IN CANVA.

Gold has realistic metallic foil shine with reflections. High contrast. Edgy luxury tattoo aesthetic. Commercial mockup photography, Etsy Star Seller quality.
```

## BEST BLACK CARD VERSION (tattoo-hero)
The strongest result from this session - good composition, readable text, all props correct.

```
Photorealistic top-down flat-lay on warm beige linen fabric. Coffee cup with latte art top-left. Succulent in white pot top-right. Eucalyptus bottom-left. Black gold pen bottom-right.

Two matte black business cards overlapping in center with gold foil and soft shadows. Front card slightly tilted, back card rotated 10 degrees behind it.

FRONT CARD black with gold foil text:
Your Studio Name
in elegant gold script across the top.
Gold line below.
Six form field rows in thin gold sans-serif:
CLIENT NAME ____________
DATE ____________
TIME ____________
ARTIST ____________
SERVICE ____________
NOTES ____________
Small gold text at bottom: @yourhandle | yourstudio.com

BACK CARD black with centered gold geometric mandala and small gold text STUDIO NAME below.

Full-width dark charcoal banner across bottom 28% of image. Large white bold text: TATTOO STUDIO APPOINTMENT CARD. Smaller white text below: KEEP CLIENTS ORGANIZED IN STYLE. Circle badge bottom-right: EDIT IN CANVA.

Luxury gold foil shine, sharp typography, realistic shadows, 4k commercial photography, Etsy Star Seller quality. No snakes, no swords, no roses, no gibberish.
```

## BEST WHITE CARD VERSION (tattoo-white2)
Clean result - readable script, gold mandala on back, banner worked well.

```
Top-down flat-lay photography on warm beige linen fabric. Coffee cup with latte art top-left. Succulent in white pot top-right. Eucalyptus bottom-left. Black gold pen bottom-right.

CENTER: Two bright crisp WHITE thick cardstock business cards with STRONG visible edges and soft drop shadows, overlapping at angles on the beige fabric. Cards must be clearly visible and distinct from background.

FRONT CARD (white card, gold text, tilted 5 degrees):
Large elegant gold script at top: Your Studio Name
Gold horizontal line divider
Gold sans-serif form fields evenly spaced:
CLIENT NAME ____________
DATE ____________
TIME ____________
ARTIST ____________
SERVICE ____________
NOTES ____________
Small gold text bottom: @yourhandle | yourstudio.com
Thin gold border around card edge

BACK CARD (white card, rotated 10 degrees behind front card):
Centered gold geometric mandala design
Small gold text: YOUR STUDIO NAME
Thin gold border

Dark charcoal banner bottom 28% of image with white bold text: TATTOO STUDIO APPOINTMENT CARD. Below: KEEP CLIENTS ORGANIZED IN STYLE. Circle badge: EDIT IN CANVA.

Premium gold foil, sharp text, realistic shadows, 4k product photography.
```

## Generation Settings
- Model: black-forest-labs/flux-1.1-pro
- Size: 1024x1024 (upscale to 2000x2000 after)
- Cost: ~$0.05 per image
- Command: `node generate-mockup.js --name <name> --prompt '<prompt>'`

## Prompt Tips Learned
1. Structured line-by-line layout instructions produce better typography
2. ALL CAPS labels render more cleanly than mixed case
3. Keep prompts under ~200 words for best results - FLUX loses focus on long prompts
4. White cards on beige need "STRONG visible edges" and "thin gold border" to not disappear
5. Specify "NO flowers NO mandalas" etc explicitly or FLUX adds decorations
6. Bottom banner text renders well when kept short and bold
