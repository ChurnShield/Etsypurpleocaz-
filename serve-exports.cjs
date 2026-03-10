const http = require("http");
const fs = require("fs");
const path = require("path");

const EXPORTS = path.join(__dirname, "workflows/auto_listing_creator/exports");
const PORT = 8080;

const MIME = {
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".pdf": "application/pdf",
  ".html": "text/html",
};

function buildGallery() {
  const files = fs.readdirSync(EXPORTS).filter((f) => !fs.statSync(path.join(EXPORTS, f)).isDirectory());

  // Group by product (strip suffix like _page1.png, _mockup.png, etc.)
  const products = new Map();
  for (const f of files) {
    const match = f.match(/^(.+?)_(mockup|page1|page2|template|band|badge|download)\./);
    if (!match) continue;
    const key = match[1];
    if (!products.has(key)) products.set(key, []);
    products.get(key).push(f);
  }

  let html = `<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>PurpleOcaz Exports</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, sans-serif; background: #111; color: #eee; padding: 20px; }
  h1 { text-align: center; margin-bottom: 30px; color: #c084fc; }
  .stats { text-align: center; color: #888; margin-bottom: 30px; }
  .product { background: #1a1a2e; border-radius: 12px; padding: 20px; margin-bottom: 30px; }
  .product h2 { font-size: 16px; color: #c084fc; margin-bottom: 15px; word-break: break-all; }
  .images { display: flex; gap: 15px; flex-wrap: wrap; align-items: flex-start; }
  .images a { display: block; text-decoration: none; }
  .images img { height: 250px; border-radius: 8px; border: 1px solid #333; transition: transform 0.2s; }
  .images img:hover { transform: scale(1.05); }
  .files { margin-top: 12px; display: flex; gap: 10px; flex-wrap: wrap; }
  .files a { color: #93c5fd; font-size: 13px; padding: 4px 10px; background: #222; border-radius: 6px; text-decoration: none; }
  .files a:hover { background: #333; }
  .download-all { display: block; text-align: center; margin: 30px auto; padding: 12px 30px;
    background: #7c3aed; color: white; border-radius: 8px; text-decoration: none; font-size: 16px; }
  .download-all:hover { background: #6d28d9; }
  .tag { font-size: 11px; padding: 2px 8px; border-radius: 4px; margin-left: 8px; }
  .tag-ai { background: #7c3aed; color: white; }
  .tag-html { background: #2563eb; color: white; }
</style></head><body>
<h1>PurpleOcaz — Generated Exports</h1>
<div class="stats">${products.size} products &middot; ${files.length} files</div>`;

  for (const [name, productFiles] of products) {
    const isAI = productFiles.some((f) => f.includes("_mockup"));
    const tag = isAI ? '<span class="tag tag-ai">Ideogram AI</span>' : '<span class="tag tag-html">HTML</span>';
    html += `<div class="product"><h2>${name}${tag}</h2><div class="images">`;

    // Show hero and mockup images as previews
    const previews = productFiles.filter((f) => f.match(/_(page1|page2|mockup)\./));
    for (const f of previews) {
      html += `<a href="/file/${encodeURIComponent(f)}" target="_blank"><img src="/file/${encodeURIComponent(f)}" loading="lazy"></a>`;
    }

    html += `</div><div class="files">`;
    for (const f of productFiles) {
      const label = f.match(/_(mockup|page1|page2|template|band|badge|download)\./)?.[1] || "file";
      const ext = path.extname(f);
      html += `<a href="/file/${encodeURIComponent(f)}" download>${label}${ext}</a>`;
    }
    html += `</div></div>`;
  }

  html += `</body></html>`;
  return html;
}

const server = http.createServer((req, res) => {
  if (req.url === "/" || req.url === "/index.html") {
    res.writeHead(200, { "Content-Type": "text/html" });
    res.end(buildGallery());
    return;
  }

  if (req.url.startsWith("/file/")) {
    const filename = decodeURIComponent(req.url.slice(6));
    const filepath = path.join(EXPORTS, filename);
    // Prevent directory traversal
    if (!filepath.startsWith(EXPORTS)) {
      res.writeHead(403);
      res.end("Forbidden");
      return;
    }
    if (!fs.existsSync(filepath)) {
      res.writeHead(404);
      res.end("Not found");
      return;
    }
    const ext = path.extname(filename).toLowerCase();
    const mime = MIME[ext] || "application/octet-stream";
    res.writeHead(200, { "Content-Type": mime });
    fs.createReadStream(filepath).pipe(res);
    return;
  }

  res.writeHead(404);
  res.end("Not found");
});

server.listen(PORT, () => {
  console.log(`Gallery server running at http://167.99.90.58:${PORT}`);
  console.log(`Serving files from: ${EXPORTS}`);
  console.log(`Press Ctrl+C to stop`);
});
