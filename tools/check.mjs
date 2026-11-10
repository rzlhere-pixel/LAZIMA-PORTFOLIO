// Portfolio checks: structure, accessibility basics, contrast, print rules
// and public-repo privacy guards. Run: npm test   (no dependencies)
import { readFileSync, existsSync } from "node:fs";
import { execSync } from "node:child_process";
import vm from "node:vm";

const root = new URL("../", import.meta.url);
const read = (p) => readFileSync(new URL(p, root), "utf8");
let failures = 0, passes = 0;
const ok = (cond, msg) => { if (cond) { passes++; console.log("  ✓ " + msg); } else { failures++; console.log("  ✗ " + msg); } };

const html = read("site/index.html");
const css = read("site/css/portfolio.css") + read("site/css/tokens.css");
const sandbox = { window: {} };
vm.runInNewContext(read("site/assets/manifest.js"), sandbox);
const assets = sandbox.window.LAZIMA_ASSETS;

console.log("Structure");
const pages = [...html.matchAll(/<section class="page (p\d\d)" id="([\w-]+)" aria-labelledby="(t\d\d)"/g)];
ok(pages.length === 12, `12 A4 pages (found ${pages.length})`);
ok(pages.every(([, , , t]) => html.includes(`id="${t}"`)), "every page heading id resolves");
ok((html.match(/<h1[\s>]/g) || []).length === 1, "exactly one h1");
const navTargets = [...html.matchAll(/<a href="#([\w-]+)"/g)].map((m) => m[1]);
ok(navTargets.every((id) => html.includes(`id="${id}"`)), "all in-page links resolve");
ok(/<html lang="en">/.test(html) && /name="viewport"/.test(html), "lang + viewport set");

console.log("Asset slots");
const slots = [...html.matchAll(/data-slot="([\w-]+)"/g)].map((m) => m[1]);
ok(slots.every((s) => assets[s]), `all ${slots.length} slots defined in manifest`);
ok([...html.matchAll(/<figure[^>]*data-slot[^>]*>/g)].every((m) => /data-label="[^"]+"/.test(m[0])), "every slot has a visible placeholder label");
ok(Object.values(assets).every((a) => !a.file || a.alt.length > 20), "every real asset has descriptive alt text");
ok(Object.values(assets).every((a) => !a.file || a.file.startsWith("assets/private/") || a.approved === true), "unapproved assets only load from the ignored private folder");
ok(Object.values(assets).every((a) => a.approved === false || (a.file?.startsWith("assets/published/") && /Owner approved/.test(a.status))), "approved assets have owner sign-off and use the published folder");
ok(Object.values(assets).every((a) => a.status && a.status.length > 10), "every slot carries a rights/status note");

console.log("Privacy (public repo)");
const tracked = execSync("git ls-files", { cwd: root }).toString().trim().split("\n");
ok(!tracked.some((f) => /assets\/private\//.test(f)), "no private assets tracked by git");
ok(!tracked.some((f) => /\.(pdf|docx?|pptx|psd|heic)$/i.test(f) || (/\.(jpe?g|png|webp|gif|tiff?)$/i.test(f) && !/^site\/assets\/published\//.test(f))), "only approved published image assets may be tracked; no private documents are tracked");
const ignored = execSync("git check-ignore site/assets/private/look-01.jpg || true", { cwd: root }).toString();
ok(ignored.includes("look-01.jpg"), "site/assets/private is git-ignored");
const textFiles = tracked.filter((f) => /\.(html|css|js|mjs|md|json|csv|py)$/.test(f) && existsSync(new URL(f, root)));
const leaks = textFiles.filter((f) => {
  const t = read(f);
  return /[\w.+-]+@(gmail|yahoo|hotmail|outlook)\.com/i.test(t) || /\+?\b(971|91)[\s-]?\d{2,3}[\s-]?\d{3}[\s-]?\d{4}\b/.test(t);
});
ok(leaks.length === 0, "no personal email/phone patterns in tracked text" + (leaks.length ? `: ${leaks}` : ""));
ok(!/C:\\Users|\/c\/Users|CVs & Portfolios/i.test(textFiles.filter((f) => !f.startsWith("tools/")).map(read).join("")), "no private local paths in published files");

console.log("External resources");
const origins = [...html.matchAll(/(?:src|href)="(https?:\/\/[^/"]+)/g)].map((m) => m[1]);
ok(origins.every((o) => /fonts\.(googleapis|gstatic)\.com$/.test(o)), "only Google Fonts loaded externally");
ok(!/<script[^>]+src="https?:/.test(html), "no third-party scripts");

console.log("Contrast (WCAG 2.x, text on page colour)");
const tok = Object.fromEntries([...css.matchAll(/--([\w-]+):\s*(#[0-9a-f]{6})/gi)].map((m) => [m[1], m[2]]));
const lum = (hex) => { const c = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255).map((v) => v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4); return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]; };
const ratio = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05); };
const pairs = [
  ["plum", "ivory"], ["plum", "rose"], ["plum", "lilac"], ["plum", "sage"], ["plum", "mist"],
  ["cocoa", "ivory"], ["cocoa", "rose"], ["cocoa", "lilac"], ["cocoa", "sage"], ["cocoa", "mist"],
  ["ivory", "mulberry"], ["ivory", "plum"],
];
for (const [fg, bg] of pairs) { const r = ratio(tok[fg], tok[bg]); ok(r >= 4.5, `${fg} on ${bg}: ${r.toFixed(2)}:1`); }

console.log("Print");
ok(/@page\s*\{\s*size:\s*A4;\s*margin:\s*0;?\s*\}/.test(css), "@page A4, zero margin");
ok(/width:\s*210mm;\s*height:\s*297mm/.test(css), "pages print at 210 × 297 mm");
ok(/break-after:\s*page/.test(css) && /print-color-adjust:\s*exact/.test(css), "page breaks + exact colour");
ok(/aspect-ratio:\s*210\s*\/\s*297/.test(css), "screen pages keep A4 proportion");
ok(/prefers-reduced-motion/.test(css) && /:focus-visible/.test(css), "reduced motion + visible focus");

console.log(`\n${passes} passed, ${failures} failed`);
process.exit(failures ? 1 : 0);
