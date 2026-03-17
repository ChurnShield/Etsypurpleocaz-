import axios, { AxiosInstance, AxiosError } from "axios";
import * as fs from "fs";
import * as path from "path";

const CANVA_API_BASE = "https://api.canva.com/rest/v1";
const POLL_INTERVAL_MS = 2000;
const MAX_POLL_ATTEMPTS = 30;

// Token file paths (relative to project root)
const PROJECT_ROOT = path.resolve(__dirname, "../..");
const TOKEN_FILE = path.join(
  PROJECT_ROOT,
  "workflows/auto_listing_creator/canva_tokens.json"
);
const MCP_ENV_FILE = path.join(PROJECT_ROOT, "purpleocaz-canva-mcp/.env");

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
  private refreshed = false;

  constructor(accessToken: string) {
    this.accessToken = accessToken;
    this.http = this.createHttp(accessToken);
  }

  private createHttp(token: string): AxiosInstance {
    return axios.create({
      baseURL: CANVA_API_BASE,
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });
  }

  /**
   * Refresh the access token using the stored refresh token.
   * Updates canva_tokens.json and MCP .env, then rebuilds the HTTP client.
   */
  private async refreshAccessToken(): Promise<void> {
    const clientId = process.env.CANVA_CLIENT_ID ?? "";
    const clientSecret = process.env.CANVA_CLIENT_SECRET ?? "";
    let refreshToken = process.env.CANVA_REFRESH_TOKEN ?? "";

    // Also try the token file for the refresh token
    if (!refreshToken && fs.existsSync(TOKEN_FILE)) {
      const tokens = JSON.parse(fs.readFileSync(TOKEN_FILE, "utf-8"));
      refreshToken = tokens.refresh_token ?? "";
    }

    if (!clientId || !clientSecret || !refreshToken) {
      throw new Error(
        "Cannot refresh: missing CANVA_CLIENT_ID, CANVA_CLIENT_SECRET, or refresh token"
      );
    }

    const credentials = Buffer.from(`${clientId}:${clientSecret}`).toString(
      "base64"
    );

    const { data: newTokens } = await axios.post(
      `${CANVA_API_BASE}/oauth/token`,
      new URLSearchParams({
        grant_type: "refresh_token",
        refresh_token: refreshToken,
      }).toString(),
      {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          Authorization: `Basic ${credentials}`,
        },
      }
    );

    this.accessToken = newTokens.access_token;
    this.http = this.createHttp(this.accessToken);
    this.refreshed = true;

    // Persist tokens
    this.saveTokens(newTokens);

    console.log("  [canva-client] Access token refreshed successfully");
  }

  private saveTokens(tokenData: Record<string, unknown>): void {
    // Save to canva_tokens.json
    try {
      fs.writeFileSync(TOKEN_FILE, JSON.stringify(tokenData, null, 2));
    } catch {
      // Token file may not exist in all environments
    }

    // Sync to MCP .env
    try {
      if (fs.existsSync(MCP_ENV_FILE)) {
        const lines = fs.readFileSync(MCP_ENV_FILE, "utf-8").split("\n");
        const updated = lines.map((line) => {
          if (line.startsWith("CANVA_ACCESS_TOKEN=")) {
            return `CANVA_ACCESS_TOKEN=${tokenData.access_token ?? ""}`;
          }
          if (line.startsWith("CANVA_REFRESH_TOKEN=")) {
            return `CANVA_REFRESH_TOKEN=${tokenData.refresh_token ?? ""}`;
          }
          return line;
        });
        fs.writeFileSync(MCP_ENV_FILE, updated.join("\n"));
      }
    } catch {
      // Non-fatal — MCP .env sync is best-effort
    }

    // Update process.env so subsequent CanvaClient instances get the new token
    if (tokenData.access_token) {
      process.env.CANVA_ACCESS_TOKEN = tokenData.access_token as string;
    }
    if (tokenData.refresh_token) {
      process.env.CANVA_REFRESH_TOKEN = tokenData.refresh_token as string;
    }
  }

  /**
   * Wrapper that retries once on 401 after refreshing the token.
   */
  private async withAutoRefresh<T>(fn: () => Promise<T>): Promise<T> {
    try {
      return await fn();
    } catch (err) {
      const axiosErr = err as AxiosError;
      if (axiosErr.response?.status === 401 && !this.refreshed) {
        console.log("  [canva-client] Got 401 — attempting token refresh...");
        await this.refreshAccessToken();
        return await fn();
      }
      throw err;
    }
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
    return this.withAutoRefresh(async () => {
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
    });
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
    return this.withAutoRefresh(async () => {
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
    });
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}
