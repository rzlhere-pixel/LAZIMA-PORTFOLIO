// Minimal static server for local preview of site/ (no dependencies).
// Binds to 127.0.0.1 only: private assets must never be exposed on a network.
import { createServer } from "node:http";
import { readFile, stat } from "node:fs/promises";
import { extname, join, normalize, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(fileURLToPath(new URL("../site", import.meta.url)));
const PORT = Number(process.env.PORT || 4173);
const ALLOWED_HOSTS = new Set([`127.0.0.1:${PORT}`, `localhost:${PORT}`]);
const TYPES = {
  ".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8", ".jpg": "image/jpeg", ".png": "image/png",
  ".svg": "image/svg+xml", ".webp": "image/webp",
};

createServer(async (req, res) => {
  try {
    // DNS-rebinding guard: only answer requests addressed to this machine.
    if (!ALLOWED_HOSTS.has(req.headers.host || "")) { res.writeHead(403).end("Forbidden host"); return; }
    if (req.headers["sec-fetch-site"] === "cross-site") { res.writeHead(403).end(); return; }
    const url = new URL(req.url, "http://localhost");
    let path = normalize(join(ROOT, decodeURIComponent(url.pathname)));
    if (path !== ROOT && !path.startsWith(ROOT + sep)) { res.writeHead(403).end(); return; }
    if ((await stat(path)).isDirectory()) path = join(path, "index.html");
    const body = await readFile(path);
    res.writeHead(200, { "content-type": TYPES[extname(path)] || "application/octet-stream", "cache-control": "no-store" });
    res.end(body);
  } catch {
    res.writeHead(404, { "content-type": "text/plain" }).end("Not found");
  }
}).listen(PORT, "127.0.0.1", () => console.log(`Portfolio preview: http://127.0.0.1:${PORT}/`));
