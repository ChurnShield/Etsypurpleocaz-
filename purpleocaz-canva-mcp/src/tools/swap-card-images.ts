/**
 * swap-card-images — Upload a local image to Canva as an asset,
 * then swap it into a business card design's image frame.
 *
 * Step 1 (this tool):  Upload image → Canva asset_id
 * Step 2 (MCP tools):  start-editing-transaction → update_fill → commit
 *
 * The Canva REST editing API returns 404, so Step 2 must use the
 * Canva MCP tools (start-editing-transaction, perform-editing-operations,
 * commit-editing-transaction).
 *
 * Usage:
 *   npx ts-node src/tools/swap-card-images.ts <image_path> [design_id]
 *
 * Element ID map (from start-editing-transaction inspection):
 *   DAHD07F9MsY (dark BC)  → image frame: PBwdJPdRSxNJvVSz-LBdTn8WTgTDmwTJt
 *   DAHD15IcxRs (light BC) → TBD (run inspection to discover)
 */

import * as fs from "fs";
import * as path from "path";
import dotenv from "dotenv";
import { CanvaClient } from "../canva-client.js";

dotenv.config({ path: path.resolve(__dirname, "../../.env") });

// Known image frame element IDs per design
export const IMAGE_FRAME_ELEMENTS: Record<string, string> = {
  "DAHD07F9MsY": "PBwdJPdRSxNJvVSz-LBdTn8WTgTDmwTJt",  // dark BC page 1
  // "DAHD15IcxRs": "TBD",  // light BC — run inspection to discover
};

export interface SwapResult {
  asset_id: string;
  design_id: string;
  element_id: string;
  asset_name: string;
}

/**
 * Upload a local image file to Canva as an asset.
 * Returns the asset_id and the target element_id for the design.
 */
export async function uploadForSwap(
  imagePath: string,
  designId: string = "DAHD07F9MsY"
): Promise<SwapResult> {
  const elementId = IMAGE_FRAME_ELEMENTS[designId];
  if (!elementId) {
    throw new Error(
      `No image frame element ID mapped for design ${designId}. ` +
      `Run start-editing-transaction to inspect the design and add the mapping.`
    );
  }

  if (!fs.existsSync(imagePath)) {
    throw new Error(`Image file not found: ${imagePath}`);
  }

  const buffer = fs.readFileSync(imagePath);
  const basename = path.basename(imagePath, path.extname(imagePath));
  // Canva asset name max 50 chars
  const assetName = `swap_${designId}_${basename}`.slice(0, 50);

  console.log(`[swap-card-images] Uploading ${imagePath} (${(buffer.length / 1024).toFixed(0)} KB)...`);
  console.log(`  Design:  ${designId}`);
  console.log(`  Element: ${elementId}`);
  console.log(`  Asset name: ${assetName}`);

  const canva = new CanvaClient(process.env.CANVA_ACCESS_TOKEN!);
  const result = await canva.uploadAsset(assetName, buffer);

  console.log(`\n[swap-card-images] Upload complete!`);
  console.log(`  Asset ID: ${result.assetId}`);
  console.log(`\nNext step — use Canva MCP tools:`);
  console.log(`  1. start-editing-transaction  design_id="${designId}"`);
  console.log(`  2. perform-editing-operations  update_fill  element_id="${elementId}"  asset_id="${result.assetId}"`);
  console.log(`  3. commit-editing-transaction`);

  return {
    asset_id: result.assetId,
    design_id: designId,
    element_id: elementId,
    asset_name: assetName,
  };
}

// CLI runner
if (
  process.argv[1]?.endsWith("swap-card-images.ts") ||
  process.argv[1]?.endsWith("swap-card-images.js")
) {
  const imagePath = process.argv[2];
  const designId = process.argv[3] || "DAHD07F9MsY";

  if (!imagePath) {
    console.error("Usage: npx ts-node src/tools/swap-card-images.ts <image_path> [design_id]");
    process.exit(1);
  }

  uploadForSwap(imagePath, designId)
    .then((result) => {
      console.log("\n=== Result ===");
      console.log(JSON.stringify(result, null, 2));
    })
    .catch((err) => {
      console.error("\nFAILED:", err.message);
      if (err.response?.data) {
        console.error("API:", JSON.stringify(err.response.data, null, 2));
      }
      process.exit(1);
    });
}
