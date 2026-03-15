import dotenv from "dotenv";
import { resolve } from "path";

dotenv.config({ path: resolve(__dirname, "../.env") });

import { canvaExportAndStage } from "../src/tools/asset-tools.js";

const DESIGN_ID = "DAHD07F9MsY";
const PAGE_NUMBER = 1;

async function main() {
  console.log("\n=== Session 1 Final Test: Export & Stage ===\n");
  console.log(`Design: ${DESIGN_ID}`);
  console.log(`Page:   ${PAGE_NUMBER}\n`);

  const result = await canvaExportAndStage(DESIGN_ID, PAGE_NUMBER);

  console.log("\n=== RESULT ===");
  console.log(JSON.stringify(result, null, 2));
  console.log("\nSession 1 test PASSED!");
}

main().catch((err) => {
  console.error("\nFAILED:", err.message);
  if (err.response?.data) {
    const data = err.response.data;
    console.error("API response:", typeof data === "string" ? data : JSON.stringify(data, null, 2));
  }
  process.exit(1);
});
