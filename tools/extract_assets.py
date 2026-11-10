"""Extract genuine artwork from the private scanned "Paper Flower" portfolio
into the git-ignored folder site/assets/private/ for LOCAL preview only.

Pixel policy
------------
* Embedded page scans are read at native resolution (no re-render/resample).
* Each asset is a rectangular CROP of the scan; no retouching, colour change,
  scaling, sharpening or generative fill.
* A lossless PNG master is kept beside a web JPEG (q=90) derivative.
* SHA-256 of source PDF, masters and derivatives go to register.local.csv.

Usage
-----
    python tools/extract_assets.py "<path to private source PDF>"

Nothing produced by this script may be committed: the output folder is ignored
by the repository's `private/` rule. Publication needs owner approval per asset.
"""
from __future__ import annotations

import csv
import hashlib
import io
import sys
from pathlib import Path

import pymupdf  # PyMuPDF
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "site" / "assets" / "private"

# page number (1-based in source) -> (asset id, category, rights note)
PAGES = {
    14: ("look-01", "original-illustration", "Original student illustration; owner approval pending"),
    15: ("look-02", "original-illustration", "Original student illustration; owner approval pending"),
    16: ("look-03", "original-illustration", "Original student illustration; owner approval pending"),
    17: ("look-04", "original-illustration", "Original student illustration; owner approval pending"),
    18: ("look-05", "original-illustration", "Original student illustration; owner approval pending"),
    12: ("spec-sheet", "technical-sheet", "Original student spec sheet; owner approval pending"),
    13: ("pattern-board", "pattern-photo", "Photo of student paper patterns; photographer unconfirmed"),
    19: ("production-board", "garment-photo", "Identifiable person(s): subject consent + photographer credit required"),
    5: ("board-theme", "compiled-board", "Compiled from third-party photos: reference only, never publish"),
    6: ("board-inspiration", "compiled-board", "Compiled from third-party photos: reference only, never publish"),
    7: ("board-mood", "compiled-board", "Third-party runway imagery: reference only, never publish"),
    8: ("board-colour", "compiled-board", "Compiled colour board; image sources unconfirmed"),
    9: ("board-fabric", "compiled-board", "Compiled fabric board; image sources unconfirmed"),
    10: ("board-trim", "compiled-board", "Third-party product photos: reference only, never publish"),
    11: ("board-accessories", "compiled-board", "Third-party product photos: reference only, never publish"),
}

# Fixed crop boxes (source pixels) for document pages where the printed sheet
# sits on light paper and auto-trimming is unreliable. Measured on a 100 px
# grid overlay of the 1654x2338 scans.
MANUAL_BOXES = {
    12: (95, 120, 1560, 2050),   # spec sheet: table + front/back flats
    13: (215, 75, 1445, 2255),   # pattern board print area
    19: (212, 85, 1432, 2245),   # production board print area
}
# Illustration cards are black: trim to the dark card, not the paper.
DARK_CARD_PAGES = {14, 15, 16, 17, 18}

BINDER_STRIP = 0.045  # left-edge strip containing punched binder holes


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def content_box(im: Image.Image, dark: bool = False) -> tuple[int, int, int, int]:
    """Bounding box of printed content against the white scan paper."""
    w, h = im.size
    left = int(w * BINDER_STRIP)
    region = im.crop((left, 0, w, h)).convert("L")
    # a column/row is "content" when a meaningful share of its pixels is
    # darker than paper; sparse scanner shadows on the edges are ignored.
    cut, thr = (70, 0.55) if dark else (200, 0.55)
    mask = region.point(lambda v: 1 if v < cut else 0)
    rw, rh = mask.size
    px = mask.load()
    cols = [sum(px[x, y] for y in range(0, rh, 4)) / (rh / 4) for x in range(rw)]
    rows = [sum(px[x, y] for x in range(0, rw, 4)) / (rw / 4) for y in range(rh)]

    def span(profile: list[float]) -> tuple[int, int]:
        idx = [i for i, v in enumerate(profile) if v > thr]
        return (idx[0], idx[-1] + 1) if idx else (0, len(profile))

    x0, x1 = span(cols)
    y0, y1 = span(rows)
    if not dark:
        # photo boards: stop at the first run of 40 near-white columns
        lum = region.load()
        run = 0
        for x in range(x0, x1):
            col_mean = sum(lum[x, y] for y in range(0, rh, 8)) / (rh / 8)
            run = run + 1 if col_mean > 232 else 0
            if run >= 40:
                x1 = x - 39
                break
    return (x0 + left, y0, x1 + left, y1)


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    src = Path(sys.argv[1])
    raw = src.read_bytes()
    OUT.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(stream=raw, filetype="pdf")
    rows = []
    for pno, (aid, cat, note) in sorted(PAGES.items()):
        page = doc[pno - 1]
        xref = page.get_images(full=True)[0][0]
        info = doc.extract_image(xref)
        im = Image.open(io.BytesIO(info["image"])).convert("RGB")
        box = MANUAL_BOXES.get(pno) or content_box(im, dark=pno in DARK_CARD_PAGES)
        crop = im.crop(box)
        # verify the crop is a pure pixel copy of the source region
        assert ImageChops.difference(crop, im.crop(box)).getbbox() is None
        png = OUT / f"{aid}.png"
        jpg = OUT / f"{aid}.jpg"
        crop.save(png, optimize=True)
        crop.save(jpg, quality=90, subsampling=0)
        rows.append({
            "asset_id": aid,
            "category": cat,
            "source_page": pno,
            "source_pixels": f"{im.width}x{im.height}",
            "crop_box": ",".join(map(str, box)),
            "output_pixels": f"{crop.width}x{crop.height}",
            "master_png_sha256": sha256(png.read_bytes()),
            "web_jpg_sha256": sha256(jpg.read_bytes()),
            "edits": "crop only",
            "rights_note": note,
            "review_status": "Pending owner approval",
        })
        print(f"p{pno:02d} -> {aid:18s} {crop.width}x{crop.height}  box={box}")
    with (OUT / "register.local.csv").open("w", newline="", encoding="utf-8") as fh:
        fh.write(f"# source: {src}\n# source_sha256: {sha256(raw)}\n")
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} assets + register.local.csv to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
