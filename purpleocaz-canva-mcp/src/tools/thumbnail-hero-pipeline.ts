/**
 * Corrected hero thumbnail pipeline.
 *
 * Shadow is applied to INDIVIDUAL card PNGs before compositing,
 * not to the final exported image.
 *
 * Flow:
 * 1. Export dark card → apply dramatic shadow → upload to Spaces + Canva asset
 * 2. Export light card → apply dramatic shadow → upload to Spaces + Canva asset
 * 3. Swap both shadowed assets into base design DAFx_dsWpTA
 * 4. Export composite page 1 (no shadow) → upload to Spaces
 * 5. Return CDN URL
 */

import sharp from "sharp";
import axios from "axios";
import dotenv from "dotenv";
import { CanvaClient } from "../canva-client.js";
import { SpacesClient, SpacesConfig } from "../spaces-client.js";

dotenv.config();

// ─── Config from design_registry.json ────────────────────────────────────────

const DARK_CARD_DESIGN = "DAHD07F9MsY";
const LIGHT_CARD_DESIGN = "DAHD15IcxRs";
const BASE_DESIGN = "DAFx_dsWpTA";

// Element IDs for card slots on page 1 of the base design
const FRONT_CARD_ELEMENT = "PBYdP0fP9tx4c7Hw-LBStl4Tz3Wf18JQg";
const BACK_CARD_ELEMENT = "PBYdP0fP9tx4c7Hw-LBYSdstM3fGX4Vqg";

// Dramatic shadow preset (from Andy's spec)
const SHADOW = {
  color: "0,0,0",
  opacity: 0.9,
  blur: 25,
  offset_x: 30,
  offset_y: 30,
  padding: 60,
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

// ─── Shadow compositing (transparent PNG output for Canva swap) ──────────────

async function applyShadow(originalBuffer: Buffer): Promise<Buffer> {
  const [sr, sg, sb] = SHADOW.color.split(",").map(Number);
  const meta = await sharp(originalBuffer).metadata();
  const origW = meta.width!;
  const origH = meta.height!;

  const pad = SHADOW.padding;
  const canvasW = pad + origW + pad;
  const canvasH = pad + origH + pad;

  // Shadow rectangle at specified opacity
  const shadowRect = await sharp({
    create: {
      width: origW,
      height: origH,
      channels: 4,
      background: { r: sr, g: sg, b: sb, alpha: SHADOW.opacity },
    },
  })
    .png()
    .toBuffer();

  // Place shadow on transparent canvas at offset, then blur
  const shadowOnCanvas = await sharp({
    create: {
      width: canvasW,
      height: canvasH,
      channels: 4,
      background: { r: 0, g: 0, b: 0, alpha: 0 },
    },
  })
    .composite([
      {
        input: shadowRect,
        left: pad + SHADOW.offset_x,
        top: pad + SHADOW.offset_y,
      },
    ])
    .blur(SHADOW.blur)
    .png()
    .toBuffer();

  // Composite original card on top — keep transparent background
  const result = await sharp(shadowOnCanvas)
    .composite([
      {
        input: originalBuffer,
        left: pad,
        top: pad,
      },
    ])
    .png()
    .toBuffer();

  return result;
}

// ─── Canva editing helpers (one transaction per swap) ────────────────────────

async function swapElement(
  canva: CanvaClient,
  designId: string,
  elementId: string,
  assetId: string,
  label: string
): Promise<void> {
  console.log(`  Starting editing session for ${label}...`);

  // Use the Canva REST API directly for editing operations
  const token = process.env.CANVA_ACCESS_TOKEN!;
  const base = "https://api.canva.com/rest/v1";

  // Start session
  const { data: sessionResp } = await axios.post(
    `${base}/designs/${designId}/editing_sessions`,
    {},
    { headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" } }
  );
  const sessionId = sessionResp.editing_session.id;
  console.log(`  Session: ${sessionId}`);

  // Update fill
  await axios.post(
    `${base}/designs/${designId}/editing_sessions/${sessionId}/operations`,
    {
      operations: [
        {
          type: "update_fill",
          element_id: elementId,
          asset_type: "image",
          asset_id: assetId,
          alt_text: label,
        },
      ],
    },
    { headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" } }
  );
  console.log(`  Fill updated`);

  // Commit
  await axios.post(
    `${base}/designs/${designId}/editing_sessions/${sessionId}/commit`,
    {},
    { headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" } }
  );
  console.log(`  Committed`);
}

// ─── Main pipeline ───────────────────────────────────────────────────────────

async function run() {
  const canva = new CanvaClient(process.env.CANVA_ACCESS_TOKEN!);
  const spaces = new SpacesClient(getSpacesConfig());
  const ts = Date.now();

  // ── STEP 1: Export dark card ───────────────────────────────────────────
  console.log(`\n[1/9] Exporting dark card ${DARK_CARD_DESIGN} page 1...`);
  const darkExport = await canva.exportDesign(DARK_CARD_DESIGN, 1, { width: 2100 });
  const darkResp = await axios.get(darkExport.downloadUrl, { responseType: "arraybuffer" });
  const darkBuffer = Buffer.from(darkResp.data);
  const darkMeta = await sharp(darkBuffer).metadata();
  console.log(`  Dark card: ${darkMeta.width}x${darkMeta.height} (${(darkBuffer.length / 1024).toFixed(0)} KB)`);

  // ── STEP 2: Apply shadow to dark card ──────────────────────────────────
  console.log(`\n[2/9] Applying dramatic shadow to dark card...`);
  const darkShadowed = await applyShadow(darkBuffer);
  const darkShadowMeta = await sharp(darkShadowed).metadata();
  console.log(`  Shadowed: ${darkShadowMeta.width}x${darkShadowMeta.height} (${(darkShadowed.length / 1024).toFixed(0)} KB)`);

  // ── STEP 3: Upload shadowed dark card to Spaces + Canva ────────────────
  console.log(`\n[3/9] Uploading shadowed dark card...`);
  const darkKey = `designs/${DARK_CARD_DESIGN}/shadowed_card_${ts}.png`;
  const darkSpacesUrl = await spaces.uploadBuffer(darkShadowed, darkKey, "image/png");
  console.log(`  Spaces: ${darkSpacesUrl}`);

  const darkAsset = await canva.uploadAsset(`shadow_dark_card_${ts}`, darkShadowed);
  console.log(`  Canva asset: ${darkAsset.assetId}`);

  // ── STEP 4: Export light card ──────────────────────────────────────────
  console.log(`\n[4/9] Exporting light card ${LIGHT_CARD_DESIGN} page 1...`);
  const lightExport = await canva.exportDesign(LIGHT_CARD_DESIGN, 1, { width: 2100 });
  const lightResp = await axios.get(lightExport.downloadUrl, { responseType: "arraybuffer" });
  const lightBuffer = Buffer.from(lightResp.data);
  const lightMeta = await sharp(lightBuffer).metadata();
  console.log(`  Light card: ${lightMeta.width}x${lightMeta.height} (${(lightBuffer.length / 1024).toFixed(0)} KB)`);

  // ── STEP 5: Apply shadow to light card ─────────────────────────────────
  console.log(`\n[5/9] Applying dramatic shadow to light card...`);
  const lightShadowed = await applyShadow(lightBuffer);
  const lightShadowMeta = await sharp(lightShadowed).metadata();
  console.log(`  Shadowed: ${lightShadowMeta.width}x${lightShadowMeta.height} (${(lightShadowed.length / 1024).toFixed(0)} KB)`);

  // ── STEP 6: Upload shadowed light card to Spaces + Canva ──────────────
  console.log(`\n[6/9] Uploading shadowed light card...`);
  const lightKey = `designs/${LIGHT_CARD_DESIGN}/shadowed_card_${ts}.png`;
  const lightSpacesUrl = await spaces.uploadBuffer(lightShadowed, lightKey, "image/png");
  console.log(`  Spaces: ${lightSpacesUrl}`);

  const lightAsset = await canva.uploadAsset(`shadow_light_card_${ts}`, lightShadowed);
  console.log(`  Canva asset: ${lightAsset.assetId}`);

  // ── STEP 7: Swap both shadowed assets into base design ─────────────────
  console.log(`\n[7/9] Swapping shadowed dark card into front slot...`);
  await swapElement(canva, BASE_DESIGN, FRONT_CARD_ELEMENT, darkAsset.assetId, "shadowed dark front");

  // Wait between transactions (LESSONS.md: one transaction per operation)
  await new Promise((r) => setTimeout(r, 2000));

  console.log(`\n[7b/9] Swapping shadowed light card into back slot...`);
  await swapElement(canva, BASE_DESIGN, BACK_CARD_ELEMENT, lightAsset.assetId, "shadowed light back");

  await new Promise((r) => setTimeout(r, 2000));

  // ── STEP 8: Export the final composite (NO shadow on composite) ────────
  console.log(`\n[8/9] Exporting final composite from ${BASE_DESIGN} page 1...`);
  const heroExport = await canva.exportDesign(BASE_DESIGN, 1, { width: 3000 });
  const heroResp = await axios.get(heroExport.downloadUrl, { responseType: "arraybuffer" });
  const heroBuffer = Buffer.from(heroResp.data);
  const heroMeta = await sharp(heroBuffer).metadata();
  console.log(`  Hero: ${heroMeta.width}x${heroMeta.height} (${(heroBuffer.length / 1024).toFixed(0)} KB)`);

  // ── STEP 9: Upload hero to Spaces ─────────────────────────────────────
  console.log(`\n[9/9] Uploading hero thumbnail to Spaces...`);
  const heroKey = `thumbnails/tattoo_business_card_hero_${ts}.png`;
  const heroUrl = await spaces.uploadBuffer(heroBuffer, heroKey, "image/png");

  console.log(`\n${"=".repeat(60)}`);
  console.log(`DONE! Hero thumbnail URL:`);
  console.log(heroUrl);
  console.log(`${"=".repeat(60)}`);

  // Summary
  console.log(`\nAssets created:`);
  console.log(`  Dark shadowed:  ${darkSpacesUrl}`);
  console.log(`  Light shadowed: ${lightSpacesUrl}`);
  console.log(`  Hero composite: ${heroUrl}`);
  console.log(`  Dark Canva asset:  ${darkAsset.assetId}`);
  console.log(`  Light Canva asset: ${lightAsset.assetId}`);
}

run().catch((err) => {
  console.error("\nPIPELINE FAILED:", err.message);
  if (err.response?.data) {
    console.error("API response:", JSON.stringify(err.response.data, null, 2));
  }
  process.exit(1);
});
