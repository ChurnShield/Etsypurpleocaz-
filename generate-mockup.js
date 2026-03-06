#!/usr/bin/env node
import Replicate from "replicate";
import { writeFile, mkdir, readFile } from "fs/promises";
import { existsSync } from "fs";
import { resolve, join } from "path";
import { config } from "dotenv";
import { createServer } from "http";
import { readdir } from "fs/promises";

config();

const replicate = new Replicate({ auth: process.env.REPLICATE_API_TOKEN });

const DEFAULTS = {
  model: "black-forest-labs/flux-1.1-pro",
  width: 1024,
  height: 1024,
  outputDir: "./mockups",
};

// PurpleOcaz base scene — matches the brand flat-lay style guide
const PURPLEOCAZ_BASE = [
  "top-down flat-lay product photography",
  "soft beige linen textured background (#F5F0E8)",
  "a latte cup with foam art partially visible in top-left corner",
  "small green succulent in white pot top-right corner",
  "eucalyptus branches draping from bottom-left",
  "sleek black and gold pen diagonal bottom-right",
  "soft natural lighting with gentle drop shadows",
  "cozy workspace aesthetic",
  "4k commercial product photography",
].join(", ");

const ACCENT_MOODS = {
  beauty: "soft pink and rose tones (#F8D7E3), feminine elegance",
  edgy: "black and charcoal accent tones, bold contrast",
  energetic: "deep red and maroon accent tones, high energy",
  professional: "cool gray and slate accent tones, clean corporate feel",
  neutral: "warm taupe and darker beige accent tones, understated elegance",
};

function buildPrompt(templateType, style, customPrompt) {
  if (customPrompt) return customPrompt;

  const mood = ACCENT_MOODS[style] || ACCENT_MOODS.neutral;

  const mockupDesc = [
    `2 overlapping rectangular ${templateType} mockups (3.5x2 inch business card proportions)`,
    "fanned at slight angles with soft drop shadows and elevation",
    "occupying the central 65% of the frame",
  ].join(", ");

  return [
    PURPLEOCAZ_BASE,
    mockupDesc,
    mood,
    "realistic mockup style, NOT a screenshot, NO laptop or phone screens",
  ].join(". ");
}

function printUsage() {
  console.log(`
  PurpleOcaz Mockup Generator (FLUX.1 via Replicate)

  Usage:
    node generate-mockup.js <template-type> [options]

  Arguments:
    template-type    What the template is (e.g. "wedding invitation", "tattoo appointment card")

  Options:
    --style <name>   Accent mood: ${Object.keys(ACCENT_MOODS).join(", ")} (default: neutral)
    --prompt <text>  Full custom prompt (overrides template-type and style)
    --preset <file>  Load prompt from a file in prompts/ folder
    --width <n>      Image width in px (default: ${DEFAULTS.width})
    --height <n>     Image height in px (default: ${DEFAULTS.height})
    --count <n>      Number of variations to generate (default: 1)
    --name <text>    Output filename prefix (default: mockup)
    --serve          Start a local server to view images after generation
    --serve-only     Just start the image viewer server (no generation)
    --help           Show this help

  Examples:
    node generate-mockup.js "wedding invitation" --style beauty
    node generate-mockup.js "tattoo appointment card" --style edgy --serve
    node generate-mockup.js --preset tattoo-white-rect --name tattoo --serve
    node generate-mockup.js --serve-only
  `);
}

function parseArgs(args) {
  const opts = {
    count: 1,
    width: DEFAULTS.width,
    height: DEFAULTS.height,
    style: "neutral",
    name: "mockup",
    serve: false,
    serveOnly: false,
  };
  const positional = [];

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case "--style":      opts.style = args[++i]; break;
      case "--prompt":     opts.prompt = args[++i]; break;
      case "--preset":     opts.preset = args[++i]; break;
      case "--width":      opts.width = parseInt(args[++i]); break;
      case "--height":     opts.height = parseInt(args[++i]); break;
      case "--count":      opts.count = parseInt(args[++i]); break;
      case "--name":       opts.name = args[++i]; break;
      case "--serve":      opts.serve = true; break;
      case "--serve-only": opts.serveOnly = true; break;
      case "--help":       opts.help = true; break;
      default:             positional.push(args[i]);
    }
  }

  if (positional.length > 0) opts.templateType = positional.join(" ");
  return opts;
}

async function loadPreset(presetName) {
  const presetsDir = resolve("./prompts/presets");
  const filePath = join(presetsDir, `${presetName}.txt`);
  if (!existsSync(filePath)) {
    console.error(`  Preset not found: ${filePath}`);
    const files = existsSync(presetsDir)
      ? (await readdir(presetsDir)).filter((f) => f.endsWith(".txt"))
      : [];
    if (files.length) {
      console.log(`  Available presets: ${files.map((f) => f.replace(".txt", "")).join(", ")}`);
    }
    process.exit(1);
  }
  return (await readFile(filePath, "utf-8")).trim();
}

async function generateWithRetry(prompt, width, height, maxRetries = 3) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      console.log(`  Generating with FLUX.1-pro...`);
      const output = await replicate.run(DEFAULTS.model, {
        input: { prompt, width, height, prompt_upsampling: true, safety_tolerance: 2 },
      });
      return output;
    } catch (err) {
      if (err.message?.includes("429") && attempt < maxRetries) {
        const wait = attempt * 10;
        console.log(`  Rate limited. Waiting ${wait}s before retry (${attempt}/${maxRetries})...`);
        await new Promise((r) => setTimeout(r, wait * 1000));
      } else {
        throw err;
      }
    }
  }
}

async function saveFromOutput(output, outputDir, namePrefix) {
  const timestamp = Date.now();
  const filename = `${namePrefix}-${timestamp}.webp`;
  const filepath = join(outputDir, filename);

  if (typeof output === "string") {
    const response = await fetch(output);
    const buffer = Buffer.from(await response.arrayBuffer());
    await writeFile(filepath, buffer);
  } else if (output && typeof output[Symbol.asyncIterator] === "function") {
    const chunks = [];
    for await (const chunk of output) chunks.push(chunk);
    const buffer = Buffer.concat(chunks.map((c) => (typeof c === "string" ? Buffer.from(c) : c)));
    await writeFile(filepath, buffer);
  } else if (output?.url) {
    const response = await fetch(output.url);
    const buffer = Buffer.from(await response.arrayBuffer());
    await writeFile(filepath, buffer);
  } else {
    const url = Array.isArray(output) ? output[0]?.url || output[0] : output?.output;
    if (!url) {
      console.error("  Could not extract image from response");
      return null;
    }
    const response = await fetch(typeof url === "string" ? url : url[0]);
    const buffer = Buffer.from(await response.arrayBuffer());
    await writeFile(filepath, buffer);
  }

  return filepath;
}

function startServer(dir, port = 8080) {
  const mimeTypes = { ".webp": "image/webp", ".png": "image/png", ".jpg": "image/jpeg" };

  const server = createServer(async (req, res) => {
    if (req.url === "/" || req.url === "/index.html") {
      const files = (await readdir(dir)).filter((f) => /\.(webp|png|jpg)$/i.test(f)).reverse();
      const html = `<!DOCTYPE html><html><head><title>PurpleOcaz Mockups</title>
        <style>body{font-family:sans-serif;background:#1a1a1a;color:#fff;padding:20px;max-width:1200px;margin:0 auto}
        h1{color:#C9B87C}img{max-width:100%;border-radius:8px;margin:10px 0;box-shadow:0 4px 20px rgba(0,0,0,0.5)}
        .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(450px,1fr));gap:20px}
        .card{background:#222;padding:15px;border-radius:12px}
        .card p{color:#999;font-size:13px;word-break:break-all}</style></head>
        <body><h1>PurpleOcaz Mockup Gallery</h1><div class="grid">
        ${files.map((f) => `<div class="card"><img src="/${f}" loading="lazy"><p>${f}</p></div>`).join("")}
        </div></body></html>`;
      res.writeHead(200, { "Content-Type": "text/html" });
      res.end(html);
    } else {
      const filePath = join(dir, decodeURIComponent(req.url.slice(1)));
      if (existsSync(filePath)) {
        const ext = filePath.substring(filePath.lastIndexOf("."));
        const data = await readFile(filePath);
        res.writeHead(200, { "Content-Type": mimeTypes[ext] || "application/octet-stream" });
        res.end(data);
      } else {
        res.writeHead(404);
        res.end("Not found");
      }
    }
  });

  server.listen(port, "0.0.0.0", () => {
    console.log(`\n  Gallery: http://167.99.90.58:${port}`);
    console.log(`  Press Ctrl+C to stop\n`);
  });
}

async function main() {
  const opts = parseArgs(process.argv.slice(2));

  if (opts.help) { printUsage(); process.exit(0); }

  const outputDir = resolve(DEFAULTS.outputDir);
  if (!existsSync(outputDir)) await mkdir(outputDir, { recursive: true });

  if (opts.serveOnly) {
    startServer(outputDir);
    return;
  }

  if (!opts.templateType && !opts.prompt && !opts.preset) {
    printUsage();
    process.exit(1);
  }

  if (!process.env.REPLICATE_API_TOKEN) {
    console.error("Error: REPLICATE_API_TOKEN not set in .env");
    process.exit(1);
  }

  let prompt;
  if (opts.preset) {
    prompt = await loadPreset(opts.preset);
  } else {
    prompt = buildPrompt(opts.templateType, opts.style, opts.prompt);
  }

  console.log(`\n  Prompt: "${prompt.substring(0, 150)}..."\n`);

  for (let i = 0; i < opts.count; i++) {
    const label = opts.count > 1 ? ` (${i + 1}/${opts.count})` : "";
    console.log(`  Image${label}:`);

    const output = await generateWithRetry(prompt, opts.width, opts.height);
    const filepath = await saveFromOutput(output, outputDir, opts.name);

    if (filepath) {
      console.log(`  Saved: ${filepath}\n`);
    }
  }

  console.log("  Done!");

  if (opts.serve) {
    startServer(outputDir);
  }
}

main().catch((err) => {
  console.error("Error:", err.message);
  process.exit(1);
});
