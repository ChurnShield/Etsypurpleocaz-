/**
 * Hero thumbnail v2 — full local compositing.
 *
 * Canva's update_fill crops shadow padding, so we bypass it entirely:
 * 1. Export base design page 1 as the background
 * 2. Export dark + light cards as individual PNGs
 * 3. Apply dramatic shadow to each card locally (Sharp)
 * 4. Composite shadowed cards onto the background at correct positions
 * 5. Upload final result to Spaces
 */

import sharp from "sharp";
import axios from "axios";
import dotenv from "dotenv";
import { CanvaClient } from "../canva-client.js";
import { SpacesClient, SpacesConfig } from "../spaces-client.js";

dotenv.config();

// ─── Design IDs ──────────────────────────────────────────────────────────────

const DARK_CARD_DESIGN = "DAHD07F9MsY";
const LIGHT_CARD_DESIGN = "DAHD15IcxRs";
const BASE_DESIGN = "DAFx_dsWpTA";

// Card slot positions on page 1 (from design_registry.json, in Canva coords)
// These map 1:1 when exporting at width=3000
const FRONT_SLOT = { top: 197, left: 353, width: 1425, height: 814 };
const BACK_SLOT  = { top: 743, left: 936, width: 1451, height: 829 };

// Natural desk shadow — soft gaussian underneath the card
const SHADOW = {
  color: { r: 0, g: 0, b: 0 },
  opacity: 0.6,
  blur: 20,       // gaussian sigma — soft edges
  offset_x: 15,   // 15px right
  offset_y: 15,   // 15px down
  padding: 120,   // large padding so blur fades to full transparency before edge
};

function getSpacesConfig(): SpacesConfig {
  return {
    key: process.env.DO_SPACES_KEY!,
    secret: process.env.DO_SPACES_SECRET!,
    bucket: process.env.DO_SPACES_BUCKET!,
    region: process.env.DO_SPACES_REGION!,
    endpoint: process.env.DO_SPACES_ENDPOINT!,
  };
}

// ─── Shadow compositing ─────────────────────────────────────────────────────

async function applyShadow(cardBuffer: Buffer): Promise<Buffer> {
  const meta = await sharp(cardBuffer).metadata();
  const origW = meta.width!;
  const origH = meta.height!;

  const pad = SHADOW.padding;
  const canvasW = origW + pad * 2;
  const canvasH = origH + pad * 2;

  // Create shadow rectangle at high opacity
  const shadowRect = await sharp({
    create: {
      width: origW,
      height: origH,
      channels: 4,
      background: { ...SHADOW.color, alpha: SHADOW.opacity },
    },
  }).png().toBuffer();

  // Place shadow on transparent canvas at offset, then blur
  const shadowCanvas = await sharp({
    create: {
      width: canvasW,
      height: canvasH,
      channels: 4,
      background: { r: 0, g: 0, b: 0, alpha: 0 },
    },
  })
    .composite([{
      input: shadowRect,
      left: pad + SHADOW.offset_x,
      top: pad + SHADOW.offset_y,
    }])
    .blur(SHADOW.blur)
    .png()
    .toBuffer();

  // Composite original card on top of shadow
  return sharp(shadowCanvas)
    .composite([{
      input: cardBuffer,
      left: pad,
      top: pad,
    }])
    .png()
    .toBuffer();
}

// ─── Main pipeline ───────────────────────────────────────────────────────────

async function run() {
  const canva = new CanvaClient(process.env.CANVA_ACCESS_TOKEN!);
  const spaces = new SpacesClient(getSpacesConfig());
  const ts = Date.now();

  // ── 1. Export base design page 1 as background ─────────────────────────
  console.log(`[1/6] Exporting base design ${BASE_DESIGN} page 1 at 3000px...`);
  const bgExport = await canva.exportDesign(BASE_DESIGN, 1, { width: 3000 });
  const bgResp = await axios.get(bgExport.downloadUrl, { responseType: "arraybuffer" });
  const bgBuffer = Buffer.from(bgResp.data);
  const bgMeta = await sharp(bgBuffer).metadata();
  console.log(`  Background: ${bgMeta.width}x${bgMeta.height}`);

  // ── 2. Export dark card ────────────────────────────────────────────────
  console.log(`\n[2/6] Exporting dark card ${DARK_CARD_DESIGN}...`);
  const darkExport = await canva.exportDesign(DARK_CARD_DESIGN, 1, { width: 2100 });
  const darkResp = await axios.get(darkExport.downloadUrl, { responseType: "arraybuffer" });
  const darkRaw = Buffer.from(darkResp.data);
  const darkMeta = await sharp(darkRaw).metadata();
  console.log(`  Dark card: ${darkMeta.width}x${darkMeta.height}`);

  // ── 3. Export light card ───────────────────────────────────────────────
  console.log(`\n[3/6] Exporting light card ${LIGHT_CARD_DESIGN}...`);
  const lightExport = await canva.exportDesign(LIGHT_CARD_DESIGN, 1, { width: 2100 });
  const lightResp = await axios.get(lightExport.downloadUrl, { responseType: "arraybuffer" });
  const lightRaw = Buffer.from(lightResp.data);
  const lightMeta = await sharp(lightRaw).metadata();
  console.log(`  Light card: ${lightMeta.width}x${lightMeta.height}`);

  // ── 4. Apply dramatic shadow to both cards ─────────────────────────────
  console.log(`\n[4/6] Applying dramatic shadow (blur=${SHADOW.blur}, opacity=${SHADOW.opacity}, offset=${SHADOW.offset_x},${SHADOW.offset_y})...`);

  // Scale dark card to fit front slot dimensions BEFORE adding shadow
  const darkScaled = await sharp(darkRaw)
    .resize(FRONT_SLOT.width, FRONT_SLOT.height, { fit: "fill" })
    .png()
    .toBuffer();
  const darkShadowed = await applyShadow(darkScaled);
  const darkShadowMeta = await sharp(darkShadowed).metadata();
  console.log(`  Dark shadowed: ${darkShadowMeta.width}x${darkShadowMeta.height}`);

  // Scale light card to fit back slot — but pull it left so it's not cropped
  const lightScaled = await sharp(lightRaw)
    .resize(BACK_SLOT.width, BACK_SLOT.height, { fit: "fill" })
    .png()
    .toBuffer();
  const lightShadowed = await applyShadow(lightScaled);
  const lightShadowMeta = await sharp(lightShadowed).metadata();
  console.log(`  Light shadowed: ${lightShadowMeta.width}x${lightShadowMeta.height}`);

  // ── 5. Composite shadowed cards onto background ────────────────────────
  console.log(`\n[5/6] Compositing shadowed cards onto background...`);

  // Position: card slot position minus shadow padding (so card lands in the right spot)
  const darkLeft = FRONT_SLOT.left - SHADOW.padding;
  const darkTop = FRONT_SLOT.top - SHADOW.padding;

  // Light card: ensure the full shadowed card (including shadow bleed) fits within frame
  const lightShadowedWidth = lightShadowMeta.width!;
  const lightShadowedHeight = lightShadowMeta.height!;
  const pageWidth = bgMeta.width!;
  const pageHeight = bgMeta.height!;

  let lightLeft = BACK_SLOT.left - SHADOW.padding;
  let lightTop = BACK_SLOT.top - SHADOW.padding;

  // Clamp right edge
  if (lightLeft + lightShadowedWidth > pageWidth) {
    lightLeft = pageWidth - lightShadowedWidth;
    console.log(`  Light card shifted left to ${lightLeft} to prevent right crop`);
  }
  // Clamp bottom edge
  if (lightTop + lightShadowedHeight > pageHeight) {
    lightTop = pageHeight - lightShadowedHeight;
    console.log(`  Light card shifted up to ${lightTop} to prevent bottom crop`);
  }
  // Ensure not negative
  lightLeft = Math.max(0, lightLeft);
  lightTop = Math.max(0, lightTop);

  console.log(`  Dark card at (${darkLeft}, ${darkTop})`);
  console.log(`  Light card at (${lightLeft}, ${lightTop})`);

  const heroBuffer = await sharp(bgBuffer)
    .composite([
      { input: darkShadowed, left: darkLeft, top: darkTop },
      { input: lightShadowed, left: lightLeft, top: lightTop },
    ])
    .png()
    .toBuffer();

  const heroMeta = await sharp(heroBuffer).metadata();
  console.log(`  Hero: ${heroMeta.width}x${heroMeta.height} (${(heroBuffer.length / 1024).toFixed(0)} KB)`);

  // ── 6. Upload to Spaces ────────────────────────────────────────────────
  console.log(`\n[6/6] Uploading hero thumbnail to Spaces...`);
  const heroKey = `thumbnails/tattoo_business_card_hero_v2_${ts}.png`;
  const heroUrl = await spaces.uploadBuffer(heroBuffer, heroKey, "image/png");

  console.log(`\n${"=".repeat(60)}`);
  console.log(`DONE! Hero thumbnail URL:`);
  console.log(heroUrl);
  console.log(`${"=".repeat(60)}`);
}

run().catch((err) => {
  console.error("\nPIPELINE FAILED:", err.message);
  if (err.response?.data) {
    console.error("API:", JSON.stringify(err.response.data, null, 2));
  }
  process.exit(1);
});
