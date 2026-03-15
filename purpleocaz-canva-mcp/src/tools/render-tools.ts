import sharp from "sharp";
import axios from "axios";
import dotenv from "dotenv";
import { CanvaClient } from "../canva-client.js";
import { SpacesClient, SpacesConfig } from "../spaces-client.js";
import {
  ETSY_CARD_SHADOW_PRESET,
  ETSY_CARD_SHADOW_ANGLED_PRESET,
} from "../config/niches.js";

dotenv.config();

function getSpacesConfig(): SpacesConfig {
  return {
    key: process.env.DO_SPACES_KEY!,
    secret: process.env.DO_SPACES_SECRET!,
    bucket: process.env.DO_SPACES_BUCKET!,
    region: process.env.DO_SPACES_REGION!,
    endpoint: process.env.DO_SPACES_ENDPOINT!,
  };
}

// ─── TOOL 1: purpleocaz_render_card_with_shadow ─────────────────────────────

export interface RenderShadowInput {
  spaces_key: string;
  shadow_offset_x?: number;
  shadow_offset_y?: number;
  shadow_blur?: number;
  shadow_opacity?: number;
  shadow_color?: string;
  padding?: number;
}

export interface RenderShadowResult {
  spaces_url: string;
  asset_id: string;
}

export async function renderCardWithShadow(
  input: RenderShadowInput
): Promise<RenderShadowResult> {
  const {
    spaces_key,
    shadow_offset_x = 10,
    shadow_offset_y = 12,
    shadow_blur = 20,
    shadow_opacity = 0.6,
    shadow_color = "0,0,0",
    padding = 30,
  } = input;

  const opts: ShadowOpts = {
    shadow_color,
    shadow_opacity,
    shadow_blur,
    shadow_offset_x,
    shadow_offset_y,
    pad_top: padding,
    pad_right: padding,
    pad_bottom: padding,
    pad_left: padding,
  };

  const canva = new CanvaClient(process.env.CANVA_ACCESS_TOKEN!);
  const spaces = new SpacesClient(getSpacesConfig());

  console.log(`[1/4] Downloading from Spaces: ${spaces_key}`);
  const originalBuffer = await spaces.downloadBuffer(spaces_key);
  const meta = await sharp(originalBuffer).metadata();
  console.log(`  Original: ${meta.width}x${meta.height}`);

  console.log(`[2/4] Applying shadow...`);
  const { result, width, height } = await applyShadowToBuffer(originalBuffer, opts);
  console.log(`  Result: ${width}x${height}, ${(result.length / 1024).toFixed(1)} KB`);

  const shadowKey = spaces_key.replace(/\.png$/, "_shadow.png");
  console.log(`[3/4] Uploading to Spaces: ${shadowKey}`);
  const spacesUrl = await spaces.uploadBuffer(result, shadowKey, "image/png");
  console.log(`  Spaces URL: ${spacesUrl}`);

  const rawName = shadowKey.replace(/\//g, "_").replace(/\.png$/, "");
  const assetName = rawName.length > 50 ? rawName.slice(-50) : rawName;
  console.log(`[4/4] Uploading to Canva as asset: ${assetName}`);
  const uploadResult = await canva.uploadAsset(assetName, result);
  console.log(`  Asset ID: ${uploadResult.assetId}`);

  return {
    spaces_url: spacesUrl,
    asset_id: uploadResult.assetId,
  };
}

// ─── TOOL 2: purpleocaz_export_full_card ────────────────────────────────────

export interface ExportFullCardInput {
  design_id: string;
  page_number?: number;
}

export interface ExportFullCardResult {
  spaces_url: string;
  asset_id: string;
  width: number;
  height: number;
}

export async function exportFullCard(
  input: ExportFullCardInput
): Promise<ExportFullCardResult> {
  const { design_id, page_number = 1 } = input;

  const canva = new CanvaClient(process.env.CANVA_ACCESS_TOKEN!);
  const spaces = new SpacesClient(getSpacesConfig());

  // 1. Export full design from Canva at high resolution
  console.log(`[1/4] Exporting full design ${design_id} page ${page_number} (high-res)...`);
  const exportResult = await canva.exportDesign(design_id, page_number, {
    width: 2100,
  });
  console.log(`  Download URL ready`);

  // 2. Download to memory
  console.log(`[2/4] Downloading PNG to memory...`);
  const response = await axios.get(exportResult.downloadUrl, {
    responseType: "arraybuffer",
  });
  const buffer = Buffer.from(response.data);

  // Get actual dimensions from the image
  const metadata = await sharp(buffer).metadata();
  const width = metadata.width ?? 0;
  const height = metadata.height ?? 0;
  console.log(`  Downloaded ${(buffer.length / 1024).toFixed(1)} KB (${width}x${height})`);

  // 3. Upload to Spaces
  const timestamp = Date.now();
  const key = `designs/${design_id}/full_page${page_number}_${timestamp}.png`;
  console.log(`[3/4] Uploading to Spaces: ${key}`);
  const spacesUrl = await spaces.uploadBuffer(buffer, key, "image/png");
  console.log(`  Spaces URL: ${spacesUrl}`);

  // 4. Upload to Canva as asset
  const assetName = `full_${design_id}_page${page_number}`;
  console.log(`[4/4] Uploading to Canva as asset: ${assetName}`);
  const uploadResult = await canva.uploadAsset(assetName, buffer);
  console.log(`  Asset ID: ${uploadResult.assetId}`);

  return {
    spaces_url: spacesUrl,
    asset_id: uploadResult.assetId,
    width,
    height,
  };
}

// ─── TOOL 3: purpleocaz_apply_etsy_shadow ───────────────────────────────────

export interface EtsyShadowInput {
  spaces_key: string;
  shadow_color?: string;
  shadow_opacity?: number;
  shadow_blur?: number;
  shadow_offset_x?: number;
  shadow_offset_y?: number;
  padding?: number;
  extra_right_padding?: number;
  extra_bottom_padding?: number;
}

export interface EtsyShadowResult {
  spaces_url: string;
  asset_id: string;
  width: number;
  height: number;
}

interface ShadowOpts {
  shadow_color: string;
  shadow_opacity: number;
  shadow_blur: number;
  shadow_offset_x: number;
  shadow_offset_y: number;
  pad_top: number;
  pad_right: number;
  pad_bottom: number;
  pad_left: number;
}

async function applyShadowToBuffer(
  originalBuffer: Buffer,
  opts: ShadowOpts
): Promise<{ result: Buffer; width: number; height: number }> {
  const [sr, sg, sb] = opts.shadow_color.split(",").map(Number);
  const metadata = await sharp(originalBuffer).metadata();
  const origW = metadata.width!;
  const origH = metadata.height!;

  const canvasW = opts.pad_left + origW + opts.pad_right;
  const canvasH = opts.pad_top + origH + opts.pad_bottom;

  // Shadow rectangle at specified opacity
  const shadowRect = await sharp({
    create: {
      width: origW,
      height: origH,
      channels: 4,
      background: { r: sr, g: sg, b: sb, alpha: opts.shadow_opacity },
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
        left: opts.pad_left + opts.shadow_offset_x,
        top: opts.pad_top + opts.shadow_offset_y,
      },
    ])
    .blur(opts.shadow_blur)
    .png()
    .toBuffer();

  // Composite original card on top
  const result = await sharp(shadowOnCanvas)
    .composite([
      {
        input: originalBuffer,
        left: opts.pad_left,
        top: opts.pad_top,
      },
    ])
    .png()
    .toBuffer();

  return { result, width: canvasW, height: canvasH };
}

export async function applyEtsyShadow(
  input: EtsyShadowInput
): Promise<EtsyShadowResult> {
  const basePad = input.padding ?? ETSY_CARD_SHADOW_PRESET.padding;
  const extraRight = input.extra_right_padding ?? 80;
  const extraBottom = input.extra_bottom_padding ?? 40;

  const opts: ShadowOpts = {
    shadow_color: input.shadow_color ?? ETSY_CARD_SHADOW_PRESET.shadow_color,
    shadow_opacity:
      input.shadow_opacity ?? ETSY_CARD_SHADOW_PRESET.shadow_opacity,
    shadow_blur: input.shadow_blur ?? ETSY_CARD_SHADOW_PRESET.shadow_blur,
    shadow_offset_x:
      input.shadow_offset_x ?? ETSY_CARD_SHADOW_PRESET.shadow_offset_x,
    shadow_offset_y:
      input.shadow_offset_y ?? ETSY_CARD_SHADOW_PRESET.shadow_offset_y,
    pad_top: basePad,
    pad_left: basePad,
    pad_right: basePad + extraRight,
    pad_bottom: basePad + extraBottom,
  };

  const canva = new CanvaClient(process.env.CANVA_ACCESS_TOKEN!);
  const spaces = new SpacesClient(getSpacesConfig());

  // 1. Download original
  console.log(`[1/4] Downloading from Spaces: ${input.spaces_key}`);
  const originalBuffer = await spaces.downloadBuffer(input.spaces_key);
  const meta = await sharp(originalBuffer).metadata();
  console.log(`  Original: ${meta.width}x${meta.height}`);

  // 2. Apply shadow
  console.log(`[2/4] Applying Etsy shadow (blur=${opts.shadow_blur}, opacity=${opts.shadow_opacity}, pad T${opts.pad_top}/R${opts.pad_right}/B${opts.pad_bottom}/L${opts.pad_left})...`);
  const { result, width, height } = await applyShadowToBuffer(
    originalBuffer,
    opts
  );
  console.log(`  Result: ${width}x${height}, ${(result.length / 1024).toFixed(1)} KB`);

  // 3. Upload to Spaces
  const shadowKey = input.spaces_key.replace(/\.png$/, "_etsy_shadow.png");
  console.log(`[3/4] Uploading to Spaces: ${shadowKey}`);
  const spacesUrl = await spaces.uploadBuffer(result, shadowKey, "image/png");
  console.log(`  Spaces URL: ${spacesUrl}`);

  // 4. Upload to Canva
  const rawName = shadowKey.replace(/\//g, "_").replace(/\.png$/, "");
  const assetName = rawName.length > 50 ? rawName.slice(-50) : rawName;
  console.log(`[4/4] Uploading to Canva as asset: ${assetName}`);
  const uploadResult = await canva.uploadAsset(assetName, result);
  console.log(`  Asset ID: ${uploadResult.assetId}`);

  return {
    spaces_url: spacesUrl,
    asset_id: uploadResult.assetId,
    width,
    height,
  };
}

// ─── TOOL 4: purpleocaz_apply_etsy_shadow_angled ────────────────────────────

export interface EtsyShadowAngledInput {
  spaces_key: string;
  rotation_degrees?: number;
  shadow_color?: string;
  shadow_opacity?: number;
  shadow_blur?: number;
  shadow_offset_x?: number;
  shadow_offset_y?: number;
  padding?: number;
}

export async function applyEtsyShadowAngled(
  input: EtsyShadowAngledInput
): Promise<EtsyShadowResult> {
  const rotation =
    input.rotation_degrees ?? ETSY_CARD_SHADOW_ANGLED_PRESET.rotation_degrees;
  const pad = input.padding ?? ETSY_CARD_SHADOW_ANGLED_PRESET.padding;
  const opts: ShadowOpts = {
    shadow_color:
      input.shadow_color ?? ETSY_CARD_SHADOW_ANGLED_PRESET.shadow_color,
    shadow_opacity:
      input.shadow_opacity ?? ETSY_CARD_SHADOW_ANGLED_PRESET.shadow_opacity,
    shadow_blur:
      input.shadow_blur ?? ETSY_CARD_SHADOW_ANGLED_PRESET.shadow_blur,
    shadow_offset_x:
      input.shadow_offset_x ?? ETSY_CARD_SHADOW_ANGLED_PRESET.shadow_offset_x,
    shadow_offset_y:
      input.shadow_offset_y ?? ETSY_CARD_SHADOW_ANGLED_PRESET.shadow_offset_y,
    pad_top: pad,
    pad_right: pad,
    pad_bottom: pad,
    pad_left: pad,
  };

  const canva = new CanvaClient(process.env.CANVA_ACCESS_TOKEN!);
  const spaces = new SpacesClient(getSpacesConfig());

  // 1. Download original
  console.log(`[1/5] Downloading from Spaces: ${input.spaces_key}`);
  const originalBuffer = await spaces.downloadBuffer(input.spaces_key);
  const meta = await sharp(originalBuffer).metadata();
  console.log(`  Original: ${meta.width}x${meta.height}`);

  // 2. Rotate the card
  console.log(`[2/5] Rotating card ${rotation} degrees...`);
  const rotatedBuffer = await sharp(originalBuffer)
    .rotate(rotation, { background: { r: 0, g: 0, b: 0, alpha: 0 } })
    .png()
    .toBuffer();
  const rotatedMeta = await sharp(rotatedBuffer).metadata();
  console.log(`  Rotated: ${rotatedMeta.width}x${rotatedMeta.height}`);

  // 3. Apply shadow to rotated card
  console.log(`[3/5] Applying Etsy shadow (blur=${opts.shadow_blur}, opacity=${opts.shadow_opacity})...`);
  const { result, width, height } = await applyShadowToBuffer(
    rotatedBuffer,
    opts
  );
  console.log(`  Result: ${width}x${height}, ${(result.length / 1024).toFixed(1)} KB`);

  // 4. Upload to Spaces
  const shadowKey = input.spaces_key.replace(/\.png$/, "_etsy_angled.png");
  console.log(`[4/5] Uploading to Spaces: ${shadowKey}`);
  const spacesUrl = await spaces.uploadBuffer(result, shadowKey, "image/png");
  console.log(`  Spaces URL: ${spacesUrl}`);

  // 5. Upload to Canva
  const rawName = shadowKey.replace(/\//g, "_").replace(/\.png$/, "");
  const assetName = rawName.length > 50 ? rawName.slice(-50) : rawName;
  console.log(`[5/5] Uploading to Canva as asset: ${assetName}`);
  const uploadResult = await canva.uploadAsset(assetName, result);
  console.log(`  Asset ID: ${uploadResult.assetId}`);

  return {
    spaces_url: spacesUrl,
    asset_id: uploadResult.assetId,
    width,
    height,
  };
}

// ─── CLI runner ─────────────────────────────────────────────────────────────

if (
  process.argv[1]?.endsWith("render-tools.ts") ||
  process.argv[1]?.endsWith("render-tools.js")
) {
  const command = process.argv[2] || "export-full";

  if (command === "export-full") {
    const designId = process.argv[3] || "DAHD07F9MsY";
    const page = parseInt(process.argv[4] || "1", 10);
    console.log(`\n=== purpleocaz_export_full_card ===`);
    console.log(`Design: ${designId}, Page: ${page}\n`);
    exportFullCard({ design_id: designId, page_number: page })
      .then((r) => {
        console.log("\n=== Result ===");
        console.log(JSON.stringify(r, null, 2));
      })
      .catch((e) => {
        console.error("\nFAILED:", e.message);
        if (e.response?.data)
          console.error("API:", JSON.stringify(e.response.data, null, 2));
        process.exit(1);
      });
  } else if (command === "shadow") {
    const spacesKey = process.argv[3];
    if (!spacesKey) {
      console.error("Usage: render-tools.ts shadow <spaces_key>");
      process.exit(1);
    }
    console.log(`\n=== purpleocaz_render_card_with_shadow ===`);
    console.log(`Key: ${spacesKey}\n`);
    renderCardWithShadow({ spaces_key: spacesKey })
      .then((r) => {
        console.log("\n=== Result ===");
        console.log(JSON.stringify(r, null, 2));
      })
      .catch((e) => {
        console.error("\nFAILED:", e.message);
        if (e.response?.data)
          console.error("API:", JSON.stringify(e.response.data, null, 2));
        process.exit(1);
      });
  } else if (command === "etsy-shadow") {
    const spacesKey = process.argv[3];
    if (!spacesKey) {
      console.error("Usage: render-tools.ts etsy-shadow <spaces_key>");
      process.exit(1);
    }
    console.log(`\n=== purpleocaz_apply_etsy_shadow ===`);
    console.log(`Key: ${spacesKey}\n`);
    applyEtsyShadow({ spaces_key: spacesKey })
      .then((r) => {
        console.log("\n=== Result ===");
        console.log(JSON.stringify(r, null, 2));
      })
      .catch((e) => {
        console.error("\nFAILED:", e.message);
        if (e.response?.data)
          console.error("API:", JSON.stringify(e.response.data, null, 2));
        process.exit(1);
      });
  } else if (command === "etsy-angled") {
    const spacesKey = process.argv[3];
    if (!spacesKey) {
      console.error("Usage: render-tools.ts etsy-angled <spaces_key>");
      process.exit(1);
    }
    console.log(`\n=== purpleocaz_apply_etsy_shadow_angled ===`);
    console.log(`Key: ${spacesKey}\n`);
    applyEtsyShadowAngled({ spaces_key: spacesKey })
      .then((r) => {
        console.log("\n=== Result ===");
        console.log(JSON.stringify(r, null, 2));
      })
      .catch((e) => {
        console.error("\nFAILED:", e.message);
        if (e.response?.data)
          console.error("API:", JSON.stringify(e.response.data, null, 2));
        process.exit(1);
      });
  } else {
    console.error(`Unknown command: ${command}`);
    console.error(
      "Usage: render-tools.ts [export-full|shadow|etsy-shadow|etsy-angled] ..."
    );
    process.exit(1);
  }
}
