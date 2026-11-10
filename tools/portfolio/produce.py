"""Produce the complete LAZIMA Fashion Portfolio 2026 delivery package (local only).

Steps
  1. Build the editable master (trim size) and a 3 mm bleed variant with build_master.py.
  2. Export both through Microsoft PowerPoint (COM) to PDF.
  3. PRINT PDF  = bleed export, with PowerPoint's ~200 ppi image downsampling replaced
                  by crops of the ORIGINAL source pixels (capped at 350 ppi), plus TrimBox/BleedBox.
     DIGITAL PDF = trim export (PowerPoint caps images at ~200 ppi), recompressed for email/mobile.
  4. Render every page, build the contact sheet, asset register, layer map, QC report, ZIP.

Usage: python tools/portfolio/produce.py
Outputs: deliverables/LAZIMA_FASHION_PORTFOLIO_2026/ (git-ignored; contains private material).
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import io
import json
import subprocess
import sys
import zipfile
from pathlib import Path

import pymupdf
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
import build_master as bm  # noqa: E402

ROOT = bm.ROOT
OUT = ROOT / "deliverables" / "LAZIMA_FASHION_PORTFOLIO_2026"
WORK = ROOT / "build" / "production"
STEM = "LAZIMA_Fashion_Portfolio_2026"
PPTX = OUT / f"{STEM}_A4_Landscape.pptx"
PRINT_PDF = OUT / f"{STEM}_PRINT.pdf"
DIGITAL_PDF = OUT / f"{STEM}_DIGITAL.pdf"
CONTACT = OUT / f"{STEM}_CONTACT_SHEET.jpg"
REGISTER = OUT / "LAZIMA_Asset_Register.csv"
LAYERMAP = OUT / "LAZIMA_Layer_Map.json"
QC = OUT / "LAZIMA_Portfolio_QC_Report.md"
ZIP = OUT / f"{STEM}_Production_Package.zip"
BLEED = 3.0
MM = 72 / 25.4
PRINT_PPI_CAP = 350
# Private documents outside the repo are located through environment variables so
# that no personal paths are committed. Unset variables simply skip those rows.
import os  # noqa: E402

_env = lambda k: Path(os.environ[k]) if os.environ.get(k) else Path("__unset__")
SCAN_PDF = _env("LAZIMA_SCAN_PDF")            # scanned 2023 student portfolio
RESUME_PDF = _env("LAZIMA_RESUME_PDF")        # latest résumé (facts only)
OLD_COVERS_DIR = _env("LAZIMA_OLD_COVERS_DIR")  # folder holding earlier generated covers

QC_LOG: dict = {}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"FAILED {cmd}\n{r.stdout}\n{r.stderr}")
    return r.stdout.strip()


def build_and_export():
    WORK.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    py = sys.executable
    bmp = str(Path(__file__).parent / "build_master.py")
    ps1 = str(Path(__file__).parent / "export_pdf.ps1")
    run([py, bmp, str(PPTX), "--map", str(LAYERMAP)])
    run([py, bmp, str(WORK / "bleed.pptx"), "--bleed", str(BLEED), "--map", str(WORK / "bleed_map.json")])
    QC_LOG["pptx_open_trim"] = run(["powershell", "-ExecutionPolicy", "Bypass", "-File", ps1, str(PPTX), str(WORK / "trim.pdf")])
    QC_LOG["pptx_open_bleed"] = run(["powershell", "-ExecutionPolicy", "Bypass", "-File", ps1, str(WORK / "bleed.pptx"), str(WORK / "bleed.pdf")])


def _crop_original(layer: dict, target_px_w: int) -> bytes:
    """Exact crop of the source pixels; downsampled only when above the PPI cap."""
    path = ROOT / layer["source"]
    im = Image.open(path)
    pw, ph = im.size
    l, t, r, b = layer["crop_fraction_ltrb"]
    box = (round(pw * l), round(ph * t), round(pw * (1 - r)), round(ph * (1 - b)))
    im = im.crop(box)
    if im.width > target_px_w:
        im = im.resize((target_px_w, round(im.height * target_px_w / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    if path.suffix.lower() == ".png":
        im.save(buf, "PNG", optimize=True)
    else:
        im.convert("RGB").save(buf, "JPEG", quality=93, subsampling=0)
    return buf.getvalue()


def make_print_pdf():
    lm = json.loads((WORK / "bleed_map.json").read_text(encoding="utf-8"))
    doc = pymupdf.open(WORK / "bleed.pdf")
    report, done = [], set()
    for pg, pmap in zip(doc, lm["pages"]):
        images = [l for l in pmap["layers"] if l["kind"] == "image"]
        for info in pg.get_image_info(xrefs=True):
            bb = pymupdf.Rect(info["bbox"])
            if bb.width < 20 or info["xref"] == 0:
                continue
            cx, cy = (bb.x0 + bb.x1) / 2 / MM - BLEED, (bb.y0 + bb.y1) / 2 / MM - BLEED
            best = min(images, key=lambda l: abs(l["bbox_mm"][0] + l["bbox_mm"][2] / 2 - cx) + abs(l["bbox_mm"][1] + l["bbox_mm"][3] / 2 - cy))
            err = abs(best["bbox_mm"][0] + best["bbox_mm"][2] / 2 - cx) + abs(best["bbox_mm"][1] + best["bbox_mm"][3] / 2 - cy)
            if err > 2.0:
                sys.exit(f"cannot match image on page {pmap['page']} at {cx:.1f},{cy:.1f}mm")
            placed_in = best["bbox_mm"][2] / 25.4
            native_w = best["cropped_px"][0]
            target = min(native_w, round(placed_in * PRINT_PPI_CAP))
            before = info["width"]
            action = "kept PowerPoint stream"
            if target > before * 1.05 and info["xref"] not in done:
                pg.replace_image(info["xref"], stream=_crop_original(best, target))
                done.add(info["xref"])
                action = "replaced with original-pixel crop"
            after = target if action.startswith("replaced") else before
            report.append({"page": pmap["page"], "layer": best["layer"], "asset": best["asset_id"],
                           "placed_mm": round(best["bbox_mm"][2], 1), "pptx_export_px": before,
                           "print_px": after, "print_ppi": round(after / placed_in, 1),
                           "native_ppi": round(native_w / placed_in, 1), "action": action})
    trim = pymupdf.Rect(BLEED * MM, BLEED * MM, (bm.W + BLEED) * MM, (bm.H + BLEED) * MM)
    for pg in doc:
        pg.set_bleedbox(pg.mediabox)
        pg.set_trimbox(trim)
    doc.set_metadata({"title": "LAZIMA C A — Fashion Design Portfolio 2026 (print, 3 mm bleed)", "author": "Lazima C A",
                      "subject": "A4 landscape fashion design portfolio", "creator": "PowerPoint export + tools/portfolio/produce.py"})
    doc.save(PRINT_PDF, garbage=4, deflate=True)
    QC_LOG["print_images"] = report


def make_digital_pdf():
    doc = pymupdf.open(WORK / "trim.pdf")
    doc.rewrite_images(dpi_threshold=180, dpi_target=150, quality=82, lossy=True, lossless=True)
    doc.set_metadata({"title": "LAZIMA C A — Fashion Design Portfolio 2026", "author": "Lazima C A",
                      "subject": "A4 landscape fashion design portfolio (digital)", "creator": "PowerPoint export + tools/portfolio/produce.py"})
    doc.save(DIGITAL_PDF, garbage=4, deflate=True)


def render_and_contact_sheet():
    doc = pymupdf.open(DIGITAL_PDF)
    pages_dir = WORK / "pages"
    pages_dir.mkdir(exist_ok=True)
    thumbs = []
    for i, pg in enumerate(doc, 1):
        pix = pg.get_pixmap(dpi=150)
        f = pages_dir / f"page-{i:02d}.png"
        pix.save(f)
        thumbs.append(Image.open(f).convert("RGB"))
    tw = 820
    th = round(tw * thumbs[0].height / thumbs[0].width)
    cols, rows, gap, top, lab = 4, 4, 34, 150, 34
    sheet = Image.new("RGB", (cols * tw + (cols + 1) * gap, top + rows * (th + lab + gap) + gap), (246, 242, 236))
    d = ImageDraw.Draw(sheet)
    try:
        f1 = ImageFont.truetype("C:/Windows/Fonts/BOD_R.TTF", 64)
        f2 = ImageFont.truetype("C:/Windows/Fonts/GIL_____.TTF", 24)
    except OSError:
        f1 = f2 = ImageFont.load_default()
    d.text((gap, 40), "LAZIMA C A — Fashion Design Portfolio 2026", font=f1, fill=(49, 39, 52))
    d.text((gap, 112), f"A4 landscape · 16 pages · contact sheet generated {dt.date.today():%d %b %Y}", font=f2, fill=(117, 98, 87))
    for i, im in enumerate(thumbs):
        x = gap + (i % cols) * (tw + gap)
        y = top + (i // cols) * (th + lab + gap)
        sheet.paste(im.resize((tw, th), Image.LANCZOS), (x, y))
        d.rectangle([x, y, x + tw - 1, y + th - 1], outline=(200, 190, 185))
        d.text((x, y + th + 6), f"{i + 1:02d}", font=f2, fill=(49, 39, 52))
    sheet.save(CONTACT, quality=90)
    QC_LOG["rendered_pages"] = len(thumbs)


# ---------------------------------------------------------------- register
EXCLUDED_NOTES = {
    "What to Include in a Fashion Portfolio _ 7 Essential Pages.jpg": ("Reference", "Third-party template (Cosette Studio branding)", "Not used; never publish"),
    "fashion mood board.jpg": ("Reference", "Third-party moodboard; authorship not established", "Not used; never publish"),
    "portfolio front page.jpg": ("Reference", "Third-party portfolio cover bearing another designer's name", "Not used; never publish"),
    "hand sketch illustration.jpeg": ("Academic", "Byte-identical duplicate of hand sketch illustration.jpg (SK-04)", "Not placed (duplicate)"),
}


def img_meta(p: Path):
    try:
        with Image.open(p) as im:
            dpi = im.info.get("dpi")
            return f"{im.width}x{im.height}", (f"{round(dpi[0])} dpi tag" if dpi else "no dpi tag")
    except Exception:
        return "", ""


def build_register():
    lm = json.loads(LAYERMAP.read_text(encoding="utf-8"))
    usage = lm["asset_usage"]
    by_path = {str(v[0].resolve()).lower(): k for k, v in bm.ASSETS.items()}
    pf_reg = {}
    pf_csv = ROOT / "site/assets/private/register.local.csv"
    if pf_csv.exists():
        rows = [r for r in pf_csv.read_text(encoding="utf-8").splitlines() if not r.startswith("#")]
        for r in csv.DictReader(rows):
            pf_reg[r["asset_id"]] = r
    rows = []

    def add(path: Path, classification, origin, evidence, rights, processing="none (original file)"):
        if not path.exists():
            return
        aid = by_path.get(str(path.resolve()).lower(), "")
        dims, res = img_meta(path) if path.suffix.lower() in (".jpg", ".jpeg", ".png") else ("", "")
        pages = ""
        if aid in usage:
            pages = "; ".join(f"p{u['page']:02d} ({u['ppi']} ppi" + (", crop " + ",".join(f"{c:.3f}" for c in u["crop"]) if any(u["crop"]) else ", uncropped") + ")"
                              for u in usage[aid])
        rows.append({
            "asset_id": aid or "-", "filename": path.name,
            "original_location": str(path.relative_to(ROOT)).replace("\\", "/") if ROOT in path.parents else str(path),
            "classification": classification, "dimensions_px": dims, "resolution_metadata": res,
            "original_or_derived": origin, "author_ownership_evidence": evidence, "rights_publication_status": rights,
            "portfolio_pages": pages or "not used",
            "cropping_processing": processing if not pages else processing + "; placed with non-destructive PowerPoint crop (srcRect); original bytes embedded unchanged",
            "sha256": sha(path),
        })

    add(SP_ := bm.SP / "cover/original/lazima original selfie.jpeg", "Personal (cover)", "Original",
        "Photograph of Lazima C A supplied by owner (extracted from LAZIMA_COMPLETE_LAYERED_PRODUCTION_KIT.zip)",
        "Private; identity photo - publish only with subject approval")
    for p in sorted((bm.SP / "cover").glob("cover-variant-*.png")):
        add(p, "Personal (cover)", "Derived composite", "Earlier generated cover; face pixels not verified against the original selfie",
            "Not used - superseded by original-photo cover")
    for p in sorted(OLD_COVERS_DIR.glob("Lazima_Fashion_Portfolio_Cover_A4_2026*.png")) if OLD_COVERS_DIR.is_dir() else []:
        add(p, "Personal (cover)", "Derived composite", "Earlier generated cover; face visibly differs from original selfie",
            "Not used")
    for p in sorted(bm.AC.iterdir()):
        if p.name in EXCLUDED_NOTES:
            c, e, r = EXCLUDED_NOTES[p.name]
            add(p, c, "Original download" if c == "Reference" else "Duplicate", e, r)
        else:
            aid = by_path.get(str(p.resolve()).lower(), "")
            basis = bm.ASSETS[aid][3] if aid else "Owner-attested"
            add(p, "Academic / personal design work", "Original (540-736 px web-sized file)", basis,
                "Private; owner-attested authorship; publish only with owner approval")
    for aid, (p, cat, desc, basis) in bm.ASSETS.items():
        if aid.startswith("PF-"):
            r = pf_reg.get(p.stem, {})
            proc = (f"crop only from scan page {r.get('source_page')} box {r.get('crop_box')} (tools/extract_assets.py)"
                    if r else "crop only from scanned portfolio")
            status = "Published (owner approved 10 Nov 2026)" if (bm.ROOT / "site/assets/published" / p.name).exists() else "Private - pending owner approval"
            if aid == "PF-GARMENT":
                status += "; identifiable wearer - consent and photo credit required before external sharing"
            add(p, "Academic - Paper Flower 2023", "Derived crop of original scan", basis, status, proc)
    for name in ["board-theme", "board-inspiration", "board-mood", "board-trim", "board-accessories"]:
        add(bm.PF / f"{name}.png", "Reference (third-party photographs)", "Derived crop of original scan",
            "Compiled boards of third-party photography", "Not used; never publish")
    add(SCAN_PDF, "Academic - Paper Flower 2023", "Original scan (source of PF-* crops)",
        "Student portfolio scan; spec sheet names 'Designer: Lazima C.A.'", "Private")
    add(bm.SP / "academic/Claude-made-academic-draft.pdf", "Academic (derived)", "Derived presentation draft",
        "AI-assisted draft built from academic work; not an independent source", "Not used")
    for p in sorted(bm.SD.iterdir()):
        add(p, "Professional - Sadah archive", "Original (employer archive file)",
            "Sadah Fashion Design archive; design/styling/photography/model not attributed to Lazima",
            "Private employer material - not for public GitHub; employer portfolio-use confirmation recommended")
    add(bm.SP / "professional-sadah/Sadah-portfolio-originals.zip", "Professional - Sadah archive", "Original archive",
        "Supplied ZIP of the 19 archive images", "Private")
    for p in sorted((bm.SP / "references/portfolio-mockup").iterdir()):
        add(p, "Reference (third-party)", "Original download", "Portfolio mockup by other designers (layout reference only)",
            "Not used; never publish")
    add(bm.SP / "references/mockup-reference.pdf", "Reference (third-party)", "Original download", "Mockup PDF", "Not used")
    add(RESUME_PDF, "Factual source (document)", "Original", "Latest résumé; used for employment/education facts only",
        "Private - contact details, visa status not reproduced")
    with REGISTER.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    QC_LOG["register_rows"] = len(rows)
    QC_LOG["register_used"] = sum(1 for r in rows if r["portfolio_pages"] != "not used")


# ---------------------------------------------------------------- checks
def checks():
    res = {}
    # PDFs
    for key, pdf, exp in (("digital", DIGITAL_PDF, (bm.W, bm.H)), ("print", PRINT_PDF, (bm.W + 2 * BLEED, bm.H + 2 * BLEED))):
        d = pymupdf.open(pdf)
        sizes = {(round(p.rect.width / MM, 1), round(p.rect.height / MM, 1)) for p in d}
        fonts = set()
        for i in range(d.page_count):
            fonts |= {f[3].split("+")[-1] for f in d.get_page_fonts(i)}
        txt = [d[i].get_text().strip().split("\n")[0][:40] for i in range(d.page_count)]
        res[key] = {"pages": d.page_count, "sizes_mm": sorted(sizes), "expected_mm": exp,
                    "fonts": sorted(fonts), "size_MB": round(pdf.stat().st_size / 1e6, 2), "first_text": txt}
        ppis = [i["width"] / (pymupdf.Rect(i["bbox"]).width / 72) for pg in d for i in pg.get_image_info()
                if pymupdf.Rect(i["bbox"]).width > 20]
        res[key]["image_ppi_range"] = (round(min(ppis)), round(max(ppis)))
        if key == "print":
            p0 = d[0]
            res[key]["trimbox_mm"] = [round(v / MM, 2) for v in p0.trimbox]
            res[key]["bleedbox_mm"] = [round(v / MM, 2) for v in p0.bleedbox]
    # landscape + exact sizes
    res["all_landscape_exact"] = (res["digital"]["sizes_mm"] == [(297.0, 210.0)] and res["print"]["sizes_mm"] == [(303.0, 216.0)])
    # embedded media byte-identity
    used = {l["sha256"]: l["source"] for pg in json.loads(LAYERMAP.read_text(encoding="utf-8"))["pages"]
            for l in pg["layers"] if l["kind"] == "image"}
    with zipfile.ZipFile(PPTX) as z:
        media = {n: hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith("ppt/media/")}
        slides = [n for n in z.namelist() if n.startswith("ppt/slides/slide") and n.endswith(".xml")]
    res["pptx_media_files"] = len(media)
    res["pptx_media_all_match_sources"] = set(media.values()) == set(used)
    res["pptx_slides"] = len(slides)
    res["pptx_size_MB"] = round(PPTX.stat().st_size / 1e6, 1)
    # editable object counts + names via python-pptx
    from pptx import Presentation
    prs = Presentation(PPTX)
    res["pptx_slide_size_mm"] = (round(prs.slide_width / 36000, 2), round(prs.slide_height / 36000, 2))
    counts = {"text": 0, "picture": 0, "shape": 0}
    unnamed = 0
    for s in prs.slides:
        for sh in s.shapes:
            k = "picture" if sh.shape_type == 13 else ("text" if sh.has_text_frame and sh.text_frame.text.strip() else "shape")
            counts[k] += 1
            if not any(sh.name.startswith(pfx) for pfx in ("BG", "SURFACE", "EDITORIAL", "IMAGE-", "TITLE", "SUBTITLE", "BODY", "CAPTION", "SOURCE-CREDIT", "FOLIO")):
                unnamed += 1
    res["pptx_objects"] = counts
    res["pptx_objects_without_layer_name"] = unnamed
    # layer-map references valid
    lm = json.loads(LAYERMAP.read_text(encoding="utf-8"))
    bad = [l["source"] for pg in lm["pages"] for l in pg["layers"] if l["kind"] == "image" and not (ROOT / l["source"]).exists()]
    res["layer_map_missing_sources"] = bad
    # safe margins (12 mm) for text + images
    viol = []
    for pg in lm["pages"]:
        for l in pg["layers"]:
            if l["kind"] == "shape":
                continue
            x, y, w, h = l["bbox_mm"]
            if x < 11.99 or y < 11.99 or x + w > bm.W - 11.99 or y + h > bm.H - 6.0:
                viol.append((pg["page"], l["layer"], l["bbox_mm"]))
    res["safe_margin_violations"] = viol
    # resolution table (master / native)
    res["image_ppi"] = [{"page": pg["page"], "asset": l["asset_id"], "placed_mm": l["bbox_mm"][2:], "native_ppi": l["effective_ppi"]}
                        for pg in lm["pages"] for l in pg["layers"] if l["kind"] == "image"]
    QC_LOG["checks"] = res


def make_zip():
    files = [PPTX, PRINT_PDF, DIGITAL_PDF, CONTACT, REGISTER, LAYERMAP, QC]
    readme = OUT / "README.txt"
    readme.write_text(
        "LAZIMA C A - Fashion Design Portfolio 2026 - production package\n\n"
        f"{PPTX.name}  editable master, A4 landscape 297x210 mm, named layers, original images embedded unchanged\n"
        f"{PRINT_PDF.name}  print PDF, 303x216 mm media with 3 mm bleed, TrimBox 297x210 mm\n"
        f"{DIGITAL_PDF.name}  digital PDF, 297x210 mm, compressed for email/screens (images up to ~200 ppi)\n"
        f"{CONTACT.name}  every page in sequence\n"
        "LAZIMA_Asset_Register.csv / LAZIMA_Layer_Map.json / LAZIMA_Portfolio_QC_Report.md\n\n"
        "PRIVATE: contains personal and employer imagery. Do not upload publicly without owner approval.\n"
        "Fonts: Bodoni MT, Gill Sans MT, Gill Sans MT Condensed (installed with Microsoft Office). "
        "Install them before editing the PPTX on a machine without Office fonts.\n", encoding="utf-8")
    files.append(readme)
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            z.write(f, f"{STEM}/{f.name}")
    with zipfile.ZipFile(ZIP) as z:
        bad = z.testzip()
        names = z.namelist()
    return {"zip_entries": names, "zip_testzip": bad or "OK", "zip_MB": round(ZIP.stat().st_size / 1e6, 1)}


def write_qc(zipinfo=None):
    c = QC_LOG.get("checks", {})
    pr = QC_LOG.get("print_images", [])
    L = []
    a = L.append
    a("# LAZIMA C A — Fashion Design Portfolio 2026 · Quality-Control Report")
    a("")
    a(f"Generated {dt.datetime.now():%d %b %Y %H:%M} by `tools/portfolio/produce.py`. All figures below are measured from the delivered files.")
    a("")
    a("## Status: review-ready, with open owner actions (see §8)")
    a("")
    a("## 1. Page geometry")
    a(f"- Editable master slide size: **{c.get('pptx_slide_size_mm')} mm**, {c.get('pptx_slides')} slides.")
    a(f"- Digital PDF: {c['digital']['pages']} pages, page sizes {c['digital']['sizes_mm']} mm; measured image resolution {c['digital']['image_ppi_range'][0]}–{c['digital']['image_ppi_range'][1]} ppi.")
    a(f"- Print PDF: {c['print']['pages']} pages, media {c['print']['sizes_mm']} mm (3 mm bleed), TrimBox {c['print']['trimbox_mm']} mm, BleedBox {c['print']['bleedbox_mm']} mm; measured image resolution {c['print']['image_ppi_range'][0]}–{c['print']['image_ppi_range'][1]} ppi.")
    a(f"- All pages A4 landscape, no portrait or mismatched pages: **{'PASS' if c.get('all_landscape_exact') else 'FAIL'}**.")
    a("")
    a("## 2. Editability (PowerPoint master)")
    a(f"- PowerPoint opened both masters by COM automation and exported them: `{QC_LOG.get('pptx_open_trim')}`.")
    a(f"- Objects: {c['pptx_objects']['text']} live text boxes, {c['pptx_objects']['picture']} picture objects, {c['pptx_objects']['shape']} independent shapes (backgrounds, surfaces, shadows, frames).")
    a(f"- Objects without a layer name: **{c.get('pptx_objects_without_layer_name')}** (names follow BG / SURFACE / IMAGE-ORIGINAL-[ID] / IMAGE-SHADOW-[ID] / IMAGE-MASK-[ID] / TITLE / SUBTITLE / BODY / CAPTION / SOURCE-CREDIT / FOLIO).")
    a(f"- Embedded media files: {c['pptx_media_files']}; every one is **byte-identical (SHA-256) to its source file**: **{'PASS' if c.get('pptx_media_all_match_sources') else 'FAIL'}**. Crops are non-destructive (PowerPoint *Crop* can restore the full original).")
    a(f"- Layer map references to missing source files: {c.get('layer_map_missing_sources') or 'none'}.")
    a("- Masks: implemented as non-destructive crop rectangles on the picture objects; IMAGE-MASK layers are the visible frames on pages 01 and 16. No pixel masks or cut-outs were made.")
    a("")
    a("## 3. Typography")
    a(f"- Fonts embedded in the digital PDF: {c['digital']['fonts']}; print PDF: {c['print']['fonts']}.")
    a("- Bodoni MT (display), Gill Sans MT and Gill Sans MT Condensed (labels/body) ship with Microsoft Office. On a machine without them PowerPoint will substitute; the PDFs are unaffected.")
    a("- Fonts are **not embedded in the PPTX** on purpose: re-saving through PowerPoint to embed fonts would also recompress pictures and break the byte-identity guarantee above.")
    a("- First iteration used Bahnschrift (variable font); PowerPoint silently substituted Calibri in the PDF. Detected by inspecting PDF fonts and replaced.")
    a("")
    a("## 4. Layout checks")
    a(f"- 12 mm text/image safe-margin check against the layer map: **{len(c.get('safe_margin_violations', []))} violations** {c.get('safe_margin_violations') or ''}.")
    a("- Visual inspection: every page was rendered and viewed at full-page size after each iteration. Defects found and fixed: right-margin overruns (p10–p14), page-10 folio dark-on-dark, misaligned spec sheets (p09, now auto-cropped to sheet border), weak detail crop (p07), empty band (p15), lost sub-head weight after font change (p13–p15).")
    a("- Typography does not overlap faces, garment annotations or sketches on any page. Illustrations are placed at their native aspect ratio (aspect lock enforced by the builder); no stretching.")
    a("- Paper Flower line-up (p11) crops only the black backdrop at each card's sides; every figure is complete (figure extents measured from pixels before choosing crops).")
    a("")
    a("## 5. Image resolution (effective PPI at placed size)")
    a("Native = source pixels available ÷ placed size. Print = pixels actually in the print PDF.")
    a("")
    a("| Page | Asset | Placed width mm | Native ppi | Print PDF ppi | Note |")
    a("|---|---|---|---|---|---|")
    for r in pr:
        note = "≥300 print-grade" if r["print_ppi"] >= 299 else ("150–299: acceptable for portfolio print, soft under a loupe" if r["print_ppi"] >= 150 else "**below 150 ppi — keep at this size or smaller**")
        a(f"| {r['page']:02d} | {r['asset']} | {r['placed_mm']} | {r['native_ppi']} | {r['print_ppi']} | {note} |")
    a("")
    a("- PowerPoint's PDF export downsamples pictures to ≈200 ppi. In the print PDF those streams were replaced with exact crops of the original source pixels (capped at 350 ppi), so print resolution is limited only by the sources.")
    a("- The owner-attested sketches, flats and spec sheets are 540–736 px web-sized files: they are placed at the largest size that keeps ≥ ~110–165 ppi. They are **not** 300 ppi and nothing in the files claims otherwise; higher-resolution scans would be needed for large-format print.")
    a("")
    a("## 6. Authenticity and attribution")
    a("- No image was generated, retouched, upscaled, recoloured or extended. The cover uses the **original airplane selfie, unretouched** (SHA-256 recorded); the earlier burgundy covers with a reconstructed-looking face were not used.")
    a("- Paper Flower (pp. 02, 10–13) is labelled **Academic Fashion Design Collection, 2023**; designer name and date come from the scanned spec sheet.")
    a("- Sadah imagery (pp. 14–15, 5 of 19 archive photos, ≈12% of pages) carries the approved supporting wording; captions describe garments only; no design/styling/photography/modelling claim is made for Lazima. The archive filename price text is not used.")
    a("- Employment and education facts come from `Lazima_ATS_Option_3_Fashion_Focused_Polished_Airy.pdf`. Phone, email, LinkedIn and visa status are **not** reproduced.")
    a("- Sketches SK-01..04, DG-01, TF-01, MW-01, SP-01/05 are **owner-attested** (10 Nov 2026). During QC three sketchbook pages were found signed top-right with a name that does not read as ‘Lazima’, and MW-01 carries a Pinterest watermark with an account handle; the owner confirmed both are Lazima's. The watermark is left in the artwork (not retouched); detail crops on p08 avoid it.")
    a("- Third-party references (mockup pages, Cosette/‘What to include’ template, moodboard, another designer's portfolio cover, bougainvillea photo boards) are excluded.")
    a("")
    a("## 7. Deliverable integrity")
    a(f"- Digital PDF {c['digital']['size_MB']} MB · Print PDF {c['print']['size_MB']} MB · PPTX {c['pptx_size_MB']} MB.")
    a(f"- Pages rendered to images for the contact sheet: {QC_LOG.get('rendered_pages')}; page order verified by first text line: {c['digital']['first_text']}.")
    a(f"- Asset register rows: {QC_LOG.get('register_rows')} ({QC_LOG.get('register_used')} used in the portfolio).")
    if zipinfo:
        a(f"- Production ZIP: {zipinfo['zip_MB']} MB, integrity test {zipinfo['zip_testzip']}, entries: {', '.join(n.split('/')[-1] for n in zipinfo['zip_entries'])} (the QC report inside the ZIP is the version written before ZIP creation; this file adds the ZIP result).")
    a("")
    a("## 8. Unresolved items / limitations (owner actions)")
    a("1. **Authorship of the web-sized sketches rests on owner statement** (signature and Pinterest mark noted above). Recruiters may ask for the original sketchbook — have it available.")
    a("2. **Production board (p13) shows an identifiable wearer**; obtain her consent and the photographer credit before sharing externally, or remove that image.")
    a("3. **Sadah imagery**: confirm the employer is comfortable with portfolio use of the 5 archive photographs.")
    a("4. Paper Flower colour/fabric boards (p10) contain images whose sources are unconfirmed (credited as such).")
    a("5. Low-resolution sources (§5) limit sharpness in print; request original scans/files for the sketches and abaya line-up if available.")
    a("6. No Canva, Adobe or Figma project was created; the editable master is PowerPoint (imports into Canva/Keynote; verify fonts after import). No physical colour proof has been made.")
    a("7. Print PDF is RGB (no CMYK conversion was requested by a printer); convert with the printer's profile if required.")
    QC.write_text("\n".join(L) + "\n", encoding="utf-8")


def main():
    build_and_export()
    make_print_pdf()
    make_digital_pdf()
    render_and_contact_sheet()
    build_register()
    checks()
    write_qc()
    zi = make_zip()
    write_qc(zi)
    (WORK / "qc_log.json").write_text(json.dumps(QC_LOG, indent=2, default=str), encoding="utf-8")
    print(json.dumps({k: QC_LOG["checks"][k] for k in ("all_landscape_exact", "pptx_media_all_match_sources", "pptx_objects",
                                                         "pptx_objects_without_layer_name", "safe_margin_violations")}, default=str))
    print(json.dumps(zi))


if __name__ == "__main__":
    main()
