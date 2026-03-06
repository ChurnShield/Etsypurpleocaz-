#!/usr/bin/env node
import Replicate from "replicate";
import { writeFile, mkdir } from "fs/promises";
import { existsSync } from "fs";
import { resolve, join } from "path";
import { config } from "dotenv";

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
  "a latte cup with foam art partially visible in bottom-left",
  "small green plant sprigs in top-left and top-right corners",
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

const PROP_EXTRAS = {
  pen: "a rose-gold pen placed diagonally in bottom-right",
  glasses: "tortoise shell glasses resting in bottom-right",
  notebook: "a small notebook as filler prop",
  succulent: "a tiny succulent plant as filler",
};

function buildPrompt(templateType, style, customPrompt, opts = {}) {
  if (customPrompt) return customPrompt;

  const mood = ACCENT_MOODS[style] || ACCENT_MOODS.neutral;
  const extras = opts.props
    ? opts.props.map((p) => PROP_EXTRAS[p]).filter(Boolean).join(", ")
    : "a rose-gold pen placed diagonally in bottom-right";

  const mockupDesc = [
    `2-3 overlapping printed ${templateType} mockups fanned at slight angles`,
    "with soft drop shadows and slight elevation",
    "occupying the central 65% of the frame",
  ].join(", ");

  return [
    PURPLEOCAZ_BASE,
    mockupDesc,
    mood,
    extras,
    "realistic mockup style, NOT a screenshot, NO laptop or phone screens",
  ].join(". ");
}

function printUsage() {
  console.log(`
  PurpleOcaz Mockup Generator (FLUX.1 via Replicate)

  Usage:
    node generate-mockup.js <template-type> [options]

  Arguments:
    template-type    What the template is (e.g. "wedding invitation", "birthday card", "resume template")

  Options:
    --style <name>   Accent mood: ${Object.keys(ACCENT_MOODS).join(", ")} (default: neutral)
    --prompt <text>  Full custom prompt (overrides template-type and style)
    --width <n>      Image width in px (default: ${DEFAULTS.width})
    --height <n>     Image height in px (default: ${DEFAULTS.height})
    --count <n>      Number of variations to generate (default: 1)
    --name <text>    Output filename prefix (default: mockup)
    --help           Show this help

  Examples:
    node generate-mockup.js "wedding invitation" --style beauty
    node generate-mockup.js "nail tech price list" --style beauty --count 3
    node generate-mockup.js "boxing fitness flyer" --style energetic
    node generate-mockup.js "resume template" --style professional --name resume
  `);
}

function parseArgs(args) {
  const opts = { count: 1, width: DEFAULTS.width, height: DEFAULTS.height, style: "neutral", name: "mockup", props: [] };
  const positional = [];

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case "--style":   opts.style = args[++i]; break;
      case "--prompt":  opts.prompt = args[++i]; break;
      case "--width":   opts.width = parseInt(args[++i]); break;
      case "--height":  opts.height = parseInt(args[++i]); break;
      case "--count":   opts.count = parseInt(args[++i]); break;
      case "--name":    opts.name = args[++i]; break;
      case "--props":   opts.props = args[++i].split(","); break;
      case "--help":    opts.help = true; break;
      default:          positional.push(args[i]);
    }
  }

  if (positional.length > 0) opts.templateType = positional.join(" ");
  return opts;
}

async function generateImage(prompt, width, height) {
  console.log(`  Generating with FLUX.1-pro...`);

  const output = await replicate.run(DEFAULTS.model, {
    input: {
      prompt,
      width,
      height,
      prompt_upsampling: true,
      safety_tolerance: 2,
    },
  });

  return output;
}

async function saveImage(url, filepath) {
  const response = await fetch(url);
  const buffer = Buffer.from(await response.arrayBuffer());
  await writeFile(filepath, buffer);
}

async function main() {
  const opts = parseArgs(process.argv.slice(2));

  if (opts.help || (!opts.templateType && !opts.prompt)) {
    printUsage();
    process.exit(opts.help ? 0 : 1);
  }

  if (!process.env.REPLICATE_API_TOKEN) {
    console.error("Error: REPLICATE_API_TOKEN not set in .env");
    process.exit(1);
  }

  const outputDir = resolve(DEFAULTS.outputDir);
  if (!existsSync(outputDir)) await mkdir(outputDir, { recursive: true });

  const prompt = buildPrompt(opts.templateType, opts.style, opts.prompt, opts);
  console.log(`\n  Prompt: "${prompt}"\n`);

  for (let i = 0; i < opts.count; i++) {
    const label = opts.count > 1 ? ` (${i + 1}/${opts.count})` : "";
    console.log(`  Image${label}:`);

    const output = await generateImage(prompt, opts.width, opts.height);

    const timestamp = Date.now();
    const filename = `${opts.name}-${timestamp}.webp`;
    const filepath = join(outputDir, filename);

    console.log("  Raw output:", JSON.stringify(output, null, 2));

    let imageUrl;
    if (typeof output === "string") {
      imageUrl = output;
    } else if (output instanceof ReadableStream || (output && typeof output.read === "function")) {
      // Replicate may return a stream — collect it
      const chunks = [];
      for await (const chunk of output) chunks.push(chunk);
      const buffer = Buffer.concat(chunks.map((c) => (typeof c === "string" ? Buffer.from(c) : c)));
      const timestamp = Date.now();
      const filename = `${opts.name}-${timestamp}.webp`;
      const filepath = join(outputDir, filename);
      await writeFile(filepath, buffer);
      console.log(`  Saved: ${filepath}\n`);
      continue;
    } else if (output?.url) {
      imageUrl = output.url;
    } else if (Array.isArray(output)) {
      imageUrl = output[0]?.url || output[0];
    } else if (output?.output) {
      imageUrl = typeof output.output === "string" ? output.output : output.output?.[0];
    }

    if (!imageUrl) {
      console.error("  Error: Could not extract image from response");
      continue;
    }

    await saveImage(imageUrl, filepath);
    console.log(`  Saved: ${filepath}\n`);
  }

  console.log("  Done!");
}

main().catch((err) => {
  console.error("Error:", err.message);
  process.exit(1);
});
