import {
  S3Client,
  PutObjectCommand,
  DeleteObjectCommand,
  GetObjectCommand,
} from "@aws-sdk/client-s3";
import { readFile } from "fs/promises";
import { lookup } from "mime-types";
import path from "path";

export interface SpacesConfig {
  key: string;
  secret: string;
  bucket: string;
  region: string;
  endpoint: string;
}

export class SpacesClient {
  private client: S3Client;
  private bucket: string;
  private cdnBase: string;

  constructor(config: SpacesConfig) {
    this.bucket = config.bucket;
    this.cdnBase = `https://${config.bucket}.${config.region}.digitaloceanspaces.com`;

    this.client = new S3Client({
      endpoint: config.endpoint,
      region: config.region,
      credentials: {
        accessKeyId: config.key,
        secretAccessKey: config.secret,
      },
      forcePathStyle: false,
    });
  }

  /**
   * Upload a local file to Spaces, returns the permanent public URL.
   */
  async uploadFile(localPath: string, key: string): Promise<string> {
    const body = await readFile(localPath);
    const contentType = lookup(localPath) || "application/octet-stream";

    await this.client.send(
      new PutObjectCommand({
        Bucket: this.bucket,
        Key: key,
        Body: body,
        ContentType: contentType,
        ACL: "public-read",
      })
    );

    return `${this.cdnBase}/${key}`;
  }

  /**
   * Upload a buffer directly to Spaces, returns the permanent public URL.
   */
  async uploadBuffer(
    buffer: Buffer,
    key: string,
    contentType: string = "application/octet-stream"
  ): Promise<string> {
    await this.client.send(
      new PutObjectCommand({
        Bucket: this.bucket,
        Key: key,
        Body: buffer,
        ContentType: contentType,
        ACL: "public-read",
      })
    );

    return `${this.cdnBase}/${key}`;
  }

  /**
   * Download an object from Spaces as a Buffer.
   */
  async downloadBuffer(key: string): Promise<Buffer> {
    const response = await this.client.send(
      new GetObjectCommand({
        Bucket: this.bucket,
        Key: key,
      })
    );
    const bytes = await response.Body?.transformToByteArray();
    if (!bytes) throw new Error(`Empty response downloading ${key}`);
    return Buffer.from(bytes);
  }

  /**
   * Delete an object from Spaces.
   */
  async deleteFile(key: string): Promise<void> {
    await this.client.send(
      new DeleteObjectCommand({
        Bucket: this.bucket,
        Key: key,
      })
    );
  }

  /**
   * Get the public URL for a given key (without uploading).
   */
  getPublicUrl(key: string): string {
    return `${this.cdnBase}/${key}`;
  }
}
