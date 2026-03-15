import axios from "axios";
import dotenv from "dotenv";
import { CanvaClient } from "../canva-client.js";
import { SpacesClient, SpacesConfig } from "../spaces-client.js";

dotenv.config();

export interface ExportAndStageResult {
  asset_id: string;
  spaces_url: string;
  width: number;
  height: number;
}

/**
 * Export a Canva design page, stage it on DO Spaces, and upload back to Canva as an asset.
 */
export async function canvaExportAndStage(
  designId: string,
  pageNumber: number
): Promise<ExportAndStageResult> {
  const canva = new CanvaClient(process.env.CANVA_ACCESS_TOKEN!);

  const spacesConfig: SpacesConfig = {
    key: process.env.DO_SPACES_KEY!,
    secret: process.env.DO_SPACES_SECRET!,
    bucket: process.env.DO_SPACES_BUCKET!,
    region: process.env.DO_SPACES_REGION!,
    endpoint: process.env.DO_SPACES_ENDPOINT!,
  };
  const spaces = new SpacesClient(spacesConfig);

  // 1. Export from Canva
  console.log(`[1/4] Exporting design ${designId} page ${pageNumber}...`);
  const exportResult = await canva.exportDesign(designId, pageNumber);
  console.log(`  Download URL: ${exportResult.downloadUrl}`);

  // 2. Download PNG to memory
  console.log(`[2/4] Downloading PNG to memory...`);
  const response = await axios.get(exportResult.downloadUrl, {
    responseType: "arraybuffer",
  });
  const buffer = Buffer.from(response.data);
  console.log(`  Downloaded ${(buffer.length / 1024).toFixed(1)} KB`);

  // 3. Upload to DO Spaces
  const timestamp = Date.now();
  const key = `designs/${designId}/page${pageNumber}_${timestamp}.png`;
  console.log(`[3/4] Uploading to Spaces: ${key}`);
  const spacesUrl = await spaces.uploadBuffer(buffer, key, "image/png");
  console.log(`  Spaces URL: ${spacesUrl}`);

  // 4. Upload back to Canva as asset
  const assetName = `design_${designId}_page${pageNumber}`;
  console.log(`[4/4] Uploading to Canva as asset: ${assetName}`);
  const uploadResult = await canva.uploadAsset(assetName, buffer);
  console.log(`  Asset ID: ${uploadResult.assetId}`);

  return {
    asset_id: uploadResult.assetId,
    spaces_url: spacesUrl,
    width: exportResult.width,
    height: exportResult.height,
  };
}

// CLI runner
if (process.argv[1]?.endsWith("asset-tools.ts") || process.argv[1]?.endsWith("asset-tools.js")) {
  const designId = process.argv[2] || "DAHD07F9MsY";
  const pageNumber = parseInt(process.argv[3] || "1", 10);

  console.log(`\n=== canva_export_and_stage ===`);
  console.log(`Design: ${designId}, Page: ${pageNumber}\n`);

  canvaExportAndStage(designId, pageNumber)
    .then((result) => {
      console.log("\n=== Result ===");
      console.log(JSON.stringify(result, null, 2));
    })
    .catch((err) => {
      console.error("\nFAILED:", err.message);
      if (err.response?.data) {
        console.error("API response:", JSON.stringify(err.response.data, null, 2));
      }
      process.exit(1);
    });
}
