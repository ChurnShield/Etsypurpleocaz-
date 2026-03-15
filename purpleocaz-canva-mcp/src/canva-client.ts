import axios, { AxiosInstance } from "axios";

const CANVA_API_BASE = "https://api.canva.com/rest/v1";
const POLL_INTERVAL_MS = 2000;
const MAX_POLL_ATTEMPTS = 30;

export interface ExportResult {
  downloadUrl: string;
  width: number;
  height: number;
}

export interface UploadAssetResult {
  assetId: string;
}

export class CanvaClient {
  private http: AxiosInstance;
  private accessToken: string;

  constructor(accessToken: string) {
    this.accessToken = accessToken;
    this.http = axios.create({
      baseURL: CANVA_API_BASE,
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
    });
  }

  /**
   * Export a design page as PNG.
   * Optionally specify width or height for high-res output (max 25000).
   * Polls until the export job completes.
   */
  async exportDesign(
    designId: string,
    pageNumber: number,
    options?: { width?: number; height?: number }
  ): Promise<ExportResult> {
    const format: Record<string, unknown> = {
      type: "png",
      export_quality: "pro",
      pages: [pageNumber],
    };
    if (options?.width) format.width = options.width;
    if (options?.height) format.height = options.height;

    // Start the export job
    const { data: job } = await this.http.post("/exports", {
      design_id: designId,
      format,
    });

    const jobId = job.job.id;
    console.log(`  Export job started: ${jobId}`);

    // Poll until done
    for (let i = 0; i < MAX_POLL_ATTEMPTS; i++) {
      await this.sleep(POLL_INTERVAL_MS);

      const { data: status } = await this.http.get(`/exports/${jobId}`);
      const jobStatus = status.job.status;

      if (jobStatus === "success") {
        const urls = status.job.urls;
        if (!urls || urls.length === 0) {
          throw new Error("Export succeeded but no URLs returned");
        }
        return {
          downloadUrl: urls[0],
          width: 0,
          height: 0,
        };
      }

      if (jobStatus === "failed") {
        const error = status.job.error;
        throw new Error(
          `Export failed: ${error?.code ?? "unknown"} - ${error?.message ?? "no details"}`
        );
      }

      console.log(`  Polling export... (${i + 1}/${MAX_POLL_ATTEMPTS})`);
    }

    throw new Error(`Export timed out after ${MAX_POLL_ATTEMPTS} polls`);
  }

  /**
   * Upload a binary buffer as a Canva asset.
   * Uses the binary upload API with octet-stream content type.
   * Polls until the upload job completes.
   */
  async uploadAsset(
    name: string,
    buffer: Buffer
  ): Promise<UploadAssetResult> {
    const nameBase64 = Buffer.from(name).toString("base64");
    const metadata = JSON.stringify({ name_base64: nameBase64 });

    const { data: job } = await axios.post(
      `${CANVA_API_BASE}/asset-uploads`,
      buffer,
      {
        headers: {
          Authorization: `Bearer ${this.accessToken}`,
          "Content-Type": "application/octet-stream",
          "Asset-Upload-Metadata": metadata,
        },
      }
    );

    const jobId = job.job.id;
    console.log(`  Asset upload job started: ${jobId}`);

    // Poll until done
    for (let i = 0; i < MAX_POLL_ATTEMPTS; i++) {
      await this.sleep(POLL_INTERVAL_MS);

      const { data: status } = await this.http.get(`/asset-uploads/${jobId}`);
      const jobStatus = status.job.status;

      if (jobStatus === "success") {
        const assetId = status.job.asset?.id;
        if (!assetId) {
          throw new Error("Upload succeeded but no asset ID returned");
        }
        return { assetId };
      }

      if (jobStatus === "failed") {
        const error = status.job.error;
        throw new Error(
          `Asset upload failed: ${error?.code ?? "unknown"} - ${error?.message ?? "no details"}`
        );
      }

      console.log(`  Polling upload... (${i + 1}/${MAX_POLL_ATTEMPTS})`);
    }

    throw new Error(`Asset upload timed out after ${MAX_POLL_ATTEMPTS} polls`);
  }

  private generateJobId(): string {
    return `pocaz_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}
