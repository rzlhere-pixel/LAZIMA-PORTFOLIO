"""Build the LAZIMA C A - Fashion Design Portfolio 2026 editable master (A4 landscape).

Every page is assembled from independent, named PowerPoint objects:
background and surface shapes, live text boxes, and image objects that embed
the ORIGINAL source file bytes unchanged. Cropping is non-destructive
(PowerPoint srcRect), so the full original stays inside the file and can be
re-cropped in PowerPoint. No pixels are generated, retouched or resampled here.

Usage:
    python tools/portfolio/build_master.py <out.pptx> [--bleed 3] [--map layer_map.json]

Source images live in git-ignored folders (source/private, site/assets/private).
The script refuses to run when an asset is missing instead of substituting it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Mm, Pt

ROOT = Path(__file__).resolve().parents[2]
SP = ROOT / "source" / "private"
AC = SP / "academic" / "assets"
PF = ROOT / "site" / "assets" / "private"
SD = SP / "professional-sadah" / "work"

W, H = 297.0, 210.0  # trim size, mm

# ---------------------------------------------------------------- palette
C = {
    "ivory": "F6F2EC", "rose": "E9D9D6", "lilac": "CFC7D7", "sage": "C4CBBE",
    "blue": "D5DFE5", "plum": "312734", "wine": "5A1A2A", "wine_deep": "43121F",
    "cocoa": "756257", "white": "FFFFFF", "rose_on_dark": "D9B8BC",
}
# Static Office fonts (installed with Microsoft Office on Windows); variable fonts are
# avoided because PowerPoint does not resolve their named instances from file XML.
SERIF = "Bodoni MT"
SANS = "Gill Sans MT"
SANS_LIGHT = "Gill Sans MT"
SANS_COND = "Gill Sans MT Condensed"

# ---------------------------------------------------------------- assets
# id: (path, category, short description, authorship basis)
ASSETS = {
    "COVER-SELFIE": (SP / "cover/original/lazima original selfie.jpeg", "Personal photograph",
                     "Original airplane selfie of Lazima C A", "Subject: Lazima C A; supplied by owner"),
    "SK-01": (AC / "hand skettch illustration.jpg", "Academic/personal sketch",
              "Graphite two-figure evening gown study", "Owner-attested original, 10 Nov 2026; top-right signature confirmed by owner as Lazima's"),
    "SK-02": (AC / "hand skech illustration.jpg", "Academic/personal sketch",
              "Graphite tiered ruffle gown study", "Owner-attested original, 10 Nov 2026; signature confirmed by owner as Lazima's"),
    "SK-03": (AC / "hand sketch illlustration.jpg", "Academic/personal sketch",
              "Graphite mermaid gown study with bag", "Owner-attested original, 10 Nov 2026; signature confirmed by owner as Lazima's"),
    "SK-04": (AC / "hand sketch illustration.jpg", "Academic/personal sketch",
              "Graphite one-shoulder draped gown study", "Owner-attested original, 10 Nov 2026"),
    "DG-01": (AC / "technical illustration (2).jpg", "Digital illustration",
              "Tailored blazer illustration", "Owner-attested original, 10 Nov 2026"),
    "TF-01": (AC / "technical illustration.jpg", "Technical drawing",
              "Corset gown technical illustration, front/back", "Owner-attested original, 10 Nov 2026"),
    "MW-01": (AC / "technical abaya illustration.jpg", "Modest-wear illustration",
              "Nine-abaya illustration line-up", "Owner-attested original, 10 Nov 2026; carries Pinterest watermark, account confirmed by owner as Lazima's"),
    "SP-05": (AC / "Garment Specification sheet (1).jpg", "Technical specification",
              "Spec sheet style 5: blazer and trousers", "Owner-attested original, 10 Nov 2026"),
    "SP-01": (AC / "Garment Specification sheet.jpg", "Technical specification",
              "Spec sheet style 01: cropped jacket and trousers", "Owner-attested original, 10 Nov 2026"),
    **{f"PF-L{i}": (PF / f"look-0{i}.png", "Academic - Paper Flower 2023",
                    f"Paper Flower look {i:02d}, digital illustration",
                    "Scanned student portfolio p%d; designer named on spec sheet" % (13 + i))
       for i in range(1, 6)},
    "PF-SPEC": (PF / "spec-sheet.png", "Academic - Paper Flower 2023",
                "Garment specification sheet SSRCO12, 26-07-2023", "Scanned student portfolio p12; 'Designer: Lazima C.A.'"),
    "PF-PATTERN": (PF / "pattern-board.png", "Academic - Paper Flower 2023",
                   "Pattern board: front body, back body, waistband", "Scanned student portfolio p13; photographer unconfirmed"),
    "PF-GARMENT": (PF / "production-board.png", "Academic - Paper Flower 2023",
                   "Production board: finished garment in wear", "Scanned student portfolio p19; wearer/photographer unconfirmed"),
    "PF-COLOUR": (PF / "board-colour.png", "Academic - Paper Flower 2023",
                  "Colour board", "Scanned student portfolio p8; compiled by Lazima, image sources unconfirmed"),
    "PF-FABRIC": (PF / "board-fabric.png", "Academic - Paper Flower 2023",
                  "Fabric board", "Scanned student portfolio p9; compiled by Lazima, image sources unconfirmed"),
    "SD-LACE": (SD / "869798453_18361088752220891_5933139657016082102_n.jpg", "Professional - Sadah archive",
                "Black lace abaya, side profile", "Sadah Fashion Design archive; not Lazima's design claim"),
    "SD-SCALLOP": (SD / "869940941_18361096171220891_2683962713235055231_n.jpg", "Professional - Sadah archive",
                   "Cocoa abaya with scalloped edge", "Sadah Fashion Design archive; not Lazima's design claim"),
    "SD-DETAIL": (SD / "Price_1890_AED_vat_included_Abudhabi_UAE_Dubai_GCC (1).jpg", "Professional - Sadah archive",
                  "Sleeve and front-edge beading detail", "Sadah Fashion Design archive; not Lazima's design claim"),
    "SD-COCOA": (SD / "870461734_18361100437220891_5880383654442305691_n.jpg", "Professional - Sadah archive",
                 "Cocoa abaya with beaded edge, half length", "Sadah Fashion Design archive; not Lazima's design claim"),
    "SD-NUDE": (SD / "871123009_18361098265220891_5213438645920451757_n.jpg", "Professional - Sadah archive",
                "Nude abaya set, half length", "Sadah Fashion Design archive; not Lazima's design claim"),
}

_sha_cache: dict[Path, str] = {}


def sha256(p: Path) -> str:
    if p not in _sha_cache:
        _sha_cache[p] = hashlib.sha256(p.read_bytes()).hexdigest()
    return _sha_cache[p]


def sheet_crop(asset_id, thresh=190, pad=4):
    """Crop fractions that trim the white paper margin around a printed sheet.
    Measures dark pixels only; the image itself is never modified."""
    import numpy as np
    with Image.open(ASSETS[asset_id][0]) as im:
        g = np.asarray(im.convert("L"))
    ys, xs = np.where(g < thresh)
    h, w = g.shape
    x0, x1 = max(0, xs.min() - pad), min(w, xs.max() + 1 + pad)
    y0, y1 = max(0, ys.min() - pad), min(h, ys.max() + 1 + pad)
    return (x0 / w, y0 / h, (w - x1) / w, (h - y1) / h)


# ---------------------------------------------------------------- builder
class Page:
    def __init__(self, deck: "Deck", number: int, title: str, bg: str):
        self.deck, self.no, self.title = deck, number, title
        self.slide = deck.prs.slides.add_slide(deck.blank)
        self.layers: list[dict] = []
        self._names: dict[str, int] = {}
        self.rect("BG", 0, 0, W, H, bg)

    # unique, readable layer names
    def _name(self, base: str) -> str:
        n = self._names.get(base, 0) + 1
        self._names[base] = n
        return base if n == 1 else f"{base}-{n}"

    def _xy(self, x, y, w, h, bleed_extend: bool):
        b = self.deck.bleed
        X, Y = x + b, y + b
        if bleed_extend:  # shapes touching the trim edge run out into the bleed
            left, right = x <= 1e-6, x + w >= W - 1e-6
            top, bottom = y <= 1e-6, y + h >= H - 1e-6
            X -= b * left
            Y -= b * top
            w += b * (left + right)
            h += b * (top + bottom)
        return X, Y, w, h

    def rect(self, layer, x, y, w, h, fill=None, line=None, line_pt=0.5, alpha=None):
        X, Y, Wd, Ht = self._xy(x, y, w, h, bleed_extend=True)
        s = self.slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Mm(X), Mm(Y), Mm(Wd), Mm(Ht))
        s.shadow.inherit = False
        if fill:
            s.fill.solid()
            s.fill.fore_color.rgb = RGBColor.from_string(fill)
            if alpha is not None:
                clr = s.fill._xPr.find(qn("a:solidFill")).find(qn("a:srgbClr"))
                a = clr.makeelement(qn("a:alpha"), {"val": str(int(alpha * 100000))})
                clr.append(a)
        else:
            s.fill.background()
        if line:
            s.line.color.rgb = RGBColor.from_string(line)
            s.line.width = Pt(line_pt)
        else:
            s.line.fill.background()
        s.text_frame.text = ""
        name = self._name(layer)
        s.name = name
        self.layers.append({"layer": name, "kind": "shape", "bbox_mm": [round(x, 2), round(y, 2), round(w, 2), round(h, 2)],
                            "fill": fill, "line": line, "alpha": alpha})
        return s

    def text(self, layer, x, y, w, h, runs, size=10, font=SANS_LIGHT, color="plum", align="l",
             spacing=0.0, line=1.0, anchor="t", italic=False, para_space=0):
        """runs: str | list of paragraphs; each paragraph str or list of (text, overrides)."""
        X, Y, Wd, Ht = self._xy(x, y, w, h, bleed_extend=False)
        tb = self.slide.shapes.add_textbox(Mm(X), Mm(Y), Mm(Wd), Mm(Ht))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.auto_size = MSO_AUTO_SIZE.NONE
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE, "b": MSO_ANCHOR.BOTTOM}[anchor]
        paras = runs if isinstance(runs, list) else [runs]
        plain = []
        for i, para in enumerate(paras):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}[align]
            p.line_spacing = line
            if para_space:
                p.space_after = Pt(para_space)
            segs = para if isinstance(para, list) else [(para, {})]
            for seg, ov in segs:
                r = p.add_run()
                r.text = seg
                plain.append(seg)
                f = r.font
                f.name = ov.get("font", font)
                f.size = Pt(ov.get("size", size))
                f.italic = ov.get("italic", italic)
                f.bold = ov.get("bold", False)
                f.color.rgb = RGBColor.from_string(C.get(ov.get("color", color), ov.get("color", color)))
                sp = ov.get("spacing", spacing)
                if sp:
                    r._r.get_or_add_rPr().set("spc", str(int(sp * 100)))
        name = self._name(layer)
        tb.name = name
        self.layers.append({"layer": name, "kind": "text", "bbox_mm": [round(x, 2), round(y, 2), round(w, 2), round(h, 2)],
                            "font": font, "size_pt": size, "text": " / ".join(plain)})
        return tb

    def image(self, asset_id, x, y, w=None, h=None, crop=(0, 0, 0, 0), shadow=None, mask_frame=None):
        """Place original asset; crop = fractions (left, top, right, bottom), non-destructive."""
        path, cat, desc, basis = ASSETS[asset_id]
        if not path.exists():
            sys.exit(f"Missing source for {asset_id}: {path}")
        with Image.open(path) as im:
            pw, ph = im.size
        l, t, r, b = crop
        cw, ch = pw * (1 - l - r), ph * (1 - t - b)
        ar = cw / ch
        if w is None:
            w = h * ar
        elif h is None:
            h = w / ar
        else:
            raise ValueError("give w or h, never both (aspect ratio is locked)")
        if shadow:
            dx, dy, col, al = shadow
            self.rect(f"IMAGE-SHADOW-{asset_id}", x + dx, y + dy, w, h, col, alpha=al)
        X, Y, _, _ = self._xy(x, y, w, h, bleed_extend=False)
        pic = self.slide.shapes.add_picture(str(path), Mm(X), Mm(Y), Mm(w), Mm(h))
        pic.crop_left, pic.crop_top, pic.crop_right, pic.crop_bottom = l, t, r, b
        # python-pptx sizes the frame before cropping; restore exact frame
        pic.width, pic.height = Mm(w), Mm(h)
        name = self._name(f"IMAGE-ORIGINAL-{asset_id}")
        pic.name = name
        ppi = min(cw / (w / 25.4), ch / (h / 25.4))
        self.layers.append({
            "layer": name, "kind": "image", "asset_id": asset_id, "source": str(path.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256(path), "source_px": [pw, ph], "crop_fraction_ltrb": [round(v, 4) for v in crop],
            "cropped_px": [round(cw), round(ch)], "bbox_mm": [round(x, 2), round(y, 2), round(w, 2), round(h, 2)],
            "effective_ppi": round(ppi, 1), "mask": "non-destructive srcRect crop on picture object",
        })
        self.deck.usage.setdefault(asset_id, []).append({"page": self.no, "ppi": round(ppi, 1), "crop": crop})
        if mask_frame:
            off, col, pt = mask_frame
            self.rect(f"IMAGE-MASK-{asset_id}", x - off, y - off, w + 2 * off, h + 2 * off, None, line=col, line_pt=pt)
        return (x, y, w, h)

    def folio(self, section, dark=False, dark_right=None):
        col = "rose_on_dark" if dark else "cocoa"
        colr = col if dark_right is None else ("rose_on_dark" if dark_right else "cocoa")
        self.text("FOLIO", 14, 199.5, 150, 4, "LAZIMA C A   ·   FASHION DESIGN PORTFOLIO 2026",
                  size=6.5, font=SANS, color=col, spacing=1.4)
        self.text("FOLIO", 150, 199.5, 133, 4, [[(section.upper() + "    ", {}), (f"{self.no:02d} / 16", {"spacing": 1})]],
                  size=6.5, font=SANS, color=colr, spacing=1.4, align="r")


class Deck:
    def __init__(self, bleed: float):
        self.bleed = bleed
        self.prs = Presentation()
        self.prs.slide_width = Mm(W + 2 * bleed)
        self.prs.slide_height = Mm(H + 2 * bleed)
        self.blank = self.prs.slide_layouts[6]
        self.pages: list[Page] = []
        self.usage: dict[str, list] = {}

    def page(self, title, bg):
        p = Page(self, len(self.pages) + 1, title, bg)
        self.pages.append(p)
        return p


SH = lambda col="plum", al=0.16: (1.6, 1.6, C[col], al)  # soft offset shadow layer


def caption(p, x, y, w, txt, color="cocoa", size=7.5, align="l", h=8):
    p.text("CAPTION", x, y, w, h, txt, size=size, font=SANS_LIGHT, color=color, align=align)


def credit(p, x, y, w, txt, color="cocoa", align="l"):
    p.text("SOURCE-CREDIT", x, y, w, 5, txt, size=6.5, font=SANS_LIGHT, color=color, align=align, italic=False)


def label(p, x, y, w, txt, color="cocoa", size=7.5, align="l"):
    p.text("SUBTITLE", x, y, w, 5, txt.upper(), size=size, font=SANS, color=color, spacing=2.2, align=align)


# ================================================================ pages
def build(deck: Deck):
    # ---- 01 COVER --------------------------------------------------------
    p = deck.page("Cover", C["wine"])
    p.rect("SURFACE", 176, 0, W - 176, H, C["wine_deep"])
    p.image("COVER-SELFIE", 157, 21, h=168, mask_frame=(4, C["rose_on_dark"], 0.5))
    p.text("TITLE", 14, 30, 140, 32, "LAZIMA", size=78, font=SERIF, color="ivory", line=0.85)
    p.text("TITLE", 14, 60, 140, 32, "C A", size=78, font=SERIF, color="rose_on_dark", italic=True, line=0.85)
    p.text("SUBTITLE", 15, 118, 138, 10, "FASHION DESIGN", size=22, font=SANS_COND, color="ivory", spacing=7)
    p.text("SUBTITLE", 15, 130, 138, 10, "PORTFOLIO", size=22, font=SANS_COND, color="ivory", spacing=7)
    p.text("TITLE", 15, 170, 80, 14, "2026", size=30, font=SERIF, color="rose_on_dark")
    credit(p, 157, 192.5, 126, "Portrait: original photograph, unretouched", color="rose_on_dark")

    # ---- 02 INTRODUCTION --------------------------------------------------
    p = deck.page("Designer introduction", C["ivory"])
    p.rect("SURFACE", 186, 0, W - 186, H, C["rose"])
    p.image("PF-L1", 168, 26, h=152, shadow=SH())
    label(p, 14, 16, 120, "Introduction")
    p.text("TITLE", 14, 30, 150, 24, "Lazima C A", size=54, font=SERIF, color="plum")
    p.text("SUBTITLE", 14, 55, 145, 10, "Fashion design · illustration · technical design · garment production",
           size=13, font=SERIF, italic=True, color="cocoa")
    p.text("BODY", 14, 72, 138, 30,
           "A fashion designer trained in illustration, pattern making, draping and garment construction, "
           "with production experience across abaya, modest and occasion wear at Sadah Fashion Design, "
           "Abu Dhabi — reviewing samples, fit and finish from sample to production.",
           size=10.5, font=SANS_LIGHT, color="plum", line=1.25)
    cols = [
        ("Education", ["Diploma in Fashion Design", "& Garment Technology", "Jul 2021 – Jul 2023", "",
                       "BBA, Rabindranath", "Tagore University", "Completed Feb 2026"]),
        ("Experience", ["Production Analyst", "Sadah Fashion Design", "Abu Dhabi, UAE", "Mar 2024 – Jul 2026"]),
        ("Practice", ["Fashion illustration", "Technical flats", "Pattern making · Draping", "Garment construction",
                      "Fit & quality review", "Adobe Illustrator", "Adobe Photoshop"]),
    ]
    for i, (hdr, lines) in enumerate(cols):
        x = 14 + i * 49
        label(p, x, 118, 46, hdr, size=7)
        p.text("BODY", x, 125, 46, 50, lines, size=8.5, font=SANS_LIGHT, color="plum", line=1.2)
    caption(p, 168, 181, 110, "Paper Flower · look 01 · digital illustration, 2023")
    p.folio("Introduction")

    # ---- 03 SKETCHBOOK HERO ---------------------------------------------
    p = deck.page("Sketchbook introduction", C["ivory"])
    p.rect("SURFACE", 130, 0, W - 130, H, C["lilac"])
    p.image("SK-01", 150, 20, h=165, shadow=SH())
    label(p, 14, 16, 100, "01 — Sketchbook")
    p.text("TITLE", 14, 62, 112, 20, "The", size=40, font=SERIF, italic=True, color="cocoa")
    p.text("TITLE", 14, 78, 116, 24, "Sketchbook", size=48, font=SERIF, color="plum")
    p.text("BODY", 14, 104, 100, 30, "Graphite studies for evening wear — line, volume and movement, drawn by hand.",
           size=11, font=SANS_LIGHT, color="plum", line=1.25)
    caption(p, 150, 188, 124, "Two-figure evening gown study · graphite on sketch paper")
    p.folio("Sketchbook")

    # ---- 04 HAND SKETCHES -------------------------------------------------
    p = deck.page("Original hand sketches", C["ivory"])
    p.rect("SURFACE", 0, 70, W, H - 70, C["sage"])
    label(p, 14, 16, 100, "02 — Hand sketches")
    p.text("TITLE", 14, 24, 160, 20, "Hand sketches", size=34, font=SERIF, color="plum")
    p.text("BODY", 186, 22, 97, 24, "Silhouette first: tiers that build volume toward the hem, and a fitted mermaid line finished with a train.",
           size=9.5, font=SANS_LIGHT, color="plum", line=1.25)
    a = p.image("SK-02", 44, 48, h=138, shadow=SH())
    b = p.image("SK-03", 44 + a[2] + 12, 48, h=138, shadow=SH())
    caption(p, a[0], 188, a[2], "Tiered ruffle gown · graphite", color="plum")
    caption(p, b[0], 188, b[2], "Mermaid gown with clutch · graphite", color="plum")
    p.folio("Hand sketches")

    # ---- 05 DRAPE STUDY --------------------------------------------------
    p = deck.page("Fashion silhouette development", C["rose"])
    label(p, 14, 16, 100, "03 — Drape & volume")
    p.text("TITLE", 14, 58, 88, 22, "Drape", size=44, font=SERIF, color="plum")
    p.text("TITLE", 14, 77, 88, 22, "& volume", size=44, font=SERIF, italic=True, color="cocoa")
    p.text("BODY", 14, 104, 80, 40, "A one-shoulder gown: a sculpted puff sleeve balanced against a draped, asymmetric bodice and a long, fluid skirt.",
           size=10, font=SANS_LIGHT, color="plum", line=1.25)
    a = p.image("SK-04", 106, 24, h=160, shadow=SH())
    d = p.image("SK-04", 216, 40, w=50, crop=(0.24, 0.10, 0.20, 0.585), shadow=SH())
    caption(p, a[0], 187, 90, "One-shoulder draped gown · graphite", color="plum")
    caption(p, d[0], d[1] + d[3] + 3, 60, "Detail · sleeve and drape at the shoulder", color="plum")
    p.folio("Silhouette")

    # ---- 06 TECHNICAL DRAWING ---------------------------------------------
    p = deck.page("Technical drawing", C["blue"])
    label(p, 14, 16, 100, "04 — Technical drawing")
    p.text("TITLE", 14, 52, 110, 22, "Technical", size=44, font=SERIF, color="plum")
    p.text("TITLE", 14, 71, 110, 22, "drawing", size=44, font=SERIF, italic=True, color="cocoa")
    p.text("BODY", 14, 98, 100, 22, "Front and back views with construction call-outs.", size=10.5,
           font=SANS_LIGHT, color="plum", line=1.25)
    p.text("BODY", 14, 116, 100, 60, [
        "Hand-embellished high neckline",
        "Sculpted corset bodice, internal boning",
        "Corset-style lace-up back, tie at waist",
        "High-cut leg line, illusion effect",
        "Beaded-fringe tulle skirt, sweep train",
    ], size=9, font=SANS_LIGHT, color="plum", line=1.25, para_space=3)
    t = p.image("TF-01", 147, 19, h=170, shadow=SH())
    p.folio("Technical")

    # ---- 07 DIGITAL ILLUSTRATION ------------------------------------------
    p = deck.page("Digital illustrations", C["ivory"])
    p.rect("SURFACE", 0, 0, 152, H, C["lilac"])
    a = p.image("DG-01", 22, 18, h=172, shadow=SH())
    label(p, 166, 16, 110, "05 — Digital illustration")
    p.text("TITLE", 166, 40, 116, 22, "Digital", size=44, font=SERIF, color="plum")
    p.text("TITLE", 166, 59, 116, 22, "illustration", size=44, font=SERIF, italic=True, color="cocoa")
    p.text("BODY", 166, 86, 110, 24, "Sharp tailoring rendered digitally: a sculpted-waist blazer, sheer patterned hosiery and a structured bag.",
           size=10, font=SANS_LIGHT, color="plum", line=1.25)
    d = p.image("DG-01", 166, 116, w=58, crop=(0.22, 0.18, 0.30, 0.52), shadow=SH())
    caption(p, d[0] + d[2] + 6, d[1] + d[3] - 8, 46, "Detail · corseted waist and lapel")
    p.folio("Digital")

    # ---- 08 MODEST WEAR ---------------------------------------------------
    p = deck.page("Modest-wear design studies", C["ivory"])
    p.rect("SURFACE", 0, 0, 122, H, C["sage"])
    label(p, 14, 16, 100, "06 — Modest wear")
    p.text("TITLE", 14, 58, 104, 22, "Modest", size=44, font=SERIF, color="plum")
    p.text("TITLE", 14, 77, 104, 22, "wear", size=44, font=SERIF, italic=True, color="cocoa")
    p.text("BODY", 14, 104, 96, 40, "Nine abaya studies exploring embroidered panels, contrast trims, colour and sleeve volume.",
           size=10, font=SANS_LIGHT, color="plum", line=1.25)
    m = p.image("MW-01", 134, 17, h=176, shadow=SH())
    c1 = p.image("MW-01", 246, 30, w=37, crop=(0.0, 2 / 3, 2 / 3, 0.0), shadow=SH())
    c2 = p.image("MW-01", 246, 30 + c1[3] + 14, w=37, crop=(2 / 3, 0.0, 0.0, 2 / 3), shadow=SH())
    caption(p, 246, c1[1] + c1[3] + 2, 37, "Bell-sleeve abaya, embroidered cuffs", size=7)
    caption(p, 246, c2[1] + c2[3] + 2, 37, "Botanical panel abaya", size=7)
    p.folio("Modest wear")

    # ---- 09 SPEC SHEETS ---------------------------------------------------
    p = deck.page("Specification sheets", C["blue"])
    label(p, 14, 16, 100, "07 — Specification")
    p.text("TITLE", 14, 24, 200, 20, "Specification sheets", size=34, font=SERIF, color="plum")
    p.text("BODY", 196, 22, 87, 26, "Measurements, front and back flats, colour palette, Sashiko embroidery swatches and fabric selection for two tailored sets.",
           size=9, font=SANS_LIGHT, color="plum", line=1.25)
    s1 = p.image("SP-05", 17, 58, w=126, crop=sheet_crop("SP-05"), shadow=SH())
    s2 = p.image("SP-01", 154, 58, w=126, crop=sheet_crop("SP-01"), shadow=SH())
    caption(p, s1[0], s1[1] + s1[3] + 4, 120, "Style 5 · single-breasted blazer and pleated trousers · gabardine", color="plum")
    caption(p, s2[0], s2[1] + s2[3] + 4, 120, "Style 01 · cropped jacket and wide trousers · gabardine and crepe", color="plum")
    p.folio("Specification")

    # ---- 10 PAPER FLOWER OPENER ---------------------------------------------
    p = deck.page("Paper Flower academic collection", C["rose"])
    p.rect("SURFACE", 152, 0, W - 152, H, C["plum"])
    label(p, 14, 16, 130, "08 — Academic collection")
    p.text("TITLE", 14, 28, 140, 30, "Paper", size=64, font=SERIF, color="plum", line=0.9)
    p.text("TITLE", 14, 52, 140, 30, "Flower", size=64, font=SERIF, italic=True, color="cocoa", line=0.9)
    p.text("SUBTITLE", 15, 82, 135, 6, "ACADEMIC FASHION DESIGN COLLECTION, 2023", size=8, font=SANS, color="plum", spacing=2)
    p.text("BODY", 15, 92, 128, 24, "A summer womenswear study built around Bougainvillea glabra — the ‘paper flower’ — in ruffles, tiers and appliquéd blooms.",
           size=10, font=SANS_LIGHT, color="plum", line=1.25)
    a = p.image("PF-COLOUR", 15, 124, h=62, shadow=SH())
    b = p.image("PF-FABRIC", 15 + a[2] + 6, 124, h=62, shadow=SH())
    p.text("BODY", b[0] + b[2] + 8, 128, 52, 40, "“Glabra, from Brazil, is called paper flower.”", size=13,
           font=SERIF, italic=True, color="plum", line=1.15)
    caption(p, b[0] + b[2] + 8, 164, 52, "From the collection concept note", size=7)
    caption(p, a[0], 188, 90, "Colour board · fabric board")
    credit(p, a[0], 192.5, 120, "Boards compiled by Lazima, 2023; source images not confirmed")
    p.image("PF-L3", 163.5, 18, h=170)
    caption(p, 163.5, 191, 119, "Look 03 · digital illustration", color="rose_on_dark")
    p.folio("Paper Flower", dark=False, dark_right=True)

    # ---- 11 FIVE LOOKS ---------------------------------------------------
    p = deck.page("Paper Flower illustrations", C["plum"])
    label(p, 14, 16, 130, "Paper Flower — five looks", color="rose_on_dark")
    p.text("TITLE", 14, 22, 200, 18, "The collection", size=30, font=SERIF, color="ivory")
    p.text("BODY", 196, 22, 87, 16, "Digital illustrations, 2023. Shown in full figure, cropped only at the backdrop.",
           size=8.5, font=SANS_LIGHT, color="rose_on_dark", line=1.25)
    centres = {1: 0.485, 2: 0.528, 3: 0.56, 4: 0.514, 5: 0.468}
    names = ["Ruffle-sleeve gown, thigh-high slit", "Crop top, tiered skirt, flower appliqué",
             "Ruffle-sleeve top, flared trousers", "Crop top, wrap skirt, appliqué edge", "V-neck two-tier dress"]
    half, hh, gap = 0.28, 126, 4.5
    x = None
    widths = []
    for i in range(1, 6):
        c = centres[i]
        widths.append((2 * half) * 1472 / 2096 * hh)
    total = sum(widths) + gap * 4
    x = (W - total) / 2
    for i in range(1, 6):
        c = centres[i]
        r = p.image(f"PF-L{i}", x, 46, h=hh, crop=(c - half, 0, 1 - c - half, 0))
        p.text("CAPTION", r[0], 178, r[2], 4, f"LOOK 0{i}", size=7, font=SANS, color="rose_on_dark", spacing=1.5)
        p.text("CAPTION", r[0], 183, r[2], 10, names[i - 1], size=7.5, font=SANS_LIGHT, color="ivory", line=1.15)
        x += r[2] + gap
    p.folio("Paper Flower", dark=True)

    # ---- 12 SKETCH TO SPEC --------------------------------------------------
    p = deck.page("Technical design", C["ivory"])
    p.rect("SURFACE", 64, 26, W - 64, 158, C["blue"])
    label(p, 14, 16, 120, "Paper Flower — technical")
    p.text("TITLE", 14, 40, 48, 60, ["From", "sketch", "to spec"], size=28, font=SERIF, color="plum", line=0.95)
    p.text("BODY", 14, 82, 46, 90, [
        "Style SSRCO12", "Summer · S / M / L / XL", "Dated 26-07-2023", "",
        "V-neck bodice with front pleats, attached waistband, two-tier skirt, pleated sleeves.",
    ], size=8.5, font=SANS_LIGHT, color="plum", line=1.25)
    a = p.image("PF-L5", 74, 37, h=136, shadow=SH())
    b = p.image("PF-SPEC", 74 + a[2] + 10, 37, h=136, shadow=SH())
    caption(p, a[0], 176, a[2], "Look 05 · illustration", color="plum")
    caption(p, b[0], 176, b[2], "Garment specification sheet · front and back flats", color="plum")
    p.folio("Technical design")

    # ---- 13 PATTERN TO GARMENT ---------------------------------------------
    p = deck.page("Pattern and construction", C["sage"])
    label(p, 14, 16, 120, "Paper Flower — process")
    p.text("TITLE", 14, 32, 88, 30, ["Pattern", "to garment"], size=32, font=SERIF, color="plum", line=0.95)
    steps = [("01", "Research", "colour and fabric boards"), ("02", "Illustration", "five looks"),
             ("03", "Specification", "flats and description"), ("04", "Pattern", "front body, back body, waistband"),
             ("05", "Garment", "the finished two-tier dress")]
    for i, (n, t1, t2) in enumerate(steps):
        y = 78 + i * 20
        p.text("BODY", 14, y, 12, 8, n, size=16, font=SERIF, italic=True, color="cocoa")
        p.text("BODY", 28, y + 0.5, 70, 14, [[(t1, {"font": SANS, "size": 9, "bold": True})], [(t2, {})]], size=8.5,
               font=SANS_LIGHT, color="plum", line=1.2)
    a = p.image("PF-PATTERN", 104, 26, h=150, shadow=SH())
    b = p.image("PF-GARMENT", 104 + a[2] + 8, 26, h=150, shadow=SH())
    caption(p, a[0], 180, a[2], "Hand-drafted paper patterns", color="plum")
    caption(p, b[0], 180, b[2], "Production board · the finished garment in wear", color="plum")
    credit(p, b[0], 185, b[2], "Photographs: photographer and wearer to be credited", color="plum")
    p.folio("Pattern & construction")

    # ---- 14 SADAH ----------------------------------------------------------
    p = deck.page("Sadah experience", C["plum"])
    label(p, 14, 16, 120, "Professional experience — Sadah", color="rose_on_dark")
    p.text("TITLE", 14, 34, 70, 40, ["Professional", "experience"], size=27, font=SERIF, color="ivory", line=1.0)
    p.text("TITLE", 14, 58, 76, 14, "— Sadah", size=27, font=SERIF, italic=True, color="rose_on_dark")
    p.text("BODY", 14, 82, 72, 40, [
        [("Production Analyst", {"font": SANS, "size": 10.5, "bold": True, "color": "ivory"})],
        "SADAH FASHION DESIGN -", "SOLE PROPRIETORSHIP L.L.C.", "Abu Dhabi, UAE", "March 2024 – July 2026",
    ], size=8.5, font=SANS_LIGHT, color="rose_on_dark", line=1.3)
    p.text("BODY", 14, 128, 72, 50, "Selected garment imagery from the Sadah Fashion Design archive, presented in connection with Lazima’s production and garment-development experience.",
           size=9, font=SERIF, italic=True, color="ivory", line=1.3)
    asp = 0.58
    hh = 162
    for k, (aid, cx, cap) in enumerate([("SD-LACE", 0.5, "Black lace abaya · evening"),
                                        ("SD-SCALLOP", 0.53, "Cocoa abaya · scalloped front edge")]):
        frac = asp * 4096 / 3072 if aid != "SD-LACE" else asp * 4096 / 3152
        side = (1 - frac)
        l = max(0.0, min(side, cx - frac / 2))
        r = p.image(aid, 88 + k * (hh * asp + 6), 22, h=hh, crop=(l, 0, side - l, 0))
        caption(p, r[0], 187, r[2], cap, color="rose_on_dark")
    p.folio("Professional", dark=True)

    # ---- 15 PROFESSIONAL PRACTICE ----------------------------------------
    p = deck.page("Professional practice", C["ivory"])
    label(p, 14, 16, 120, "Professional practice")
    p.text("TITLE", 14, 30, 88, 40, ["Fit, finish", "& production"], size=30, font=SERIF, color="plum", line=1.0)
    p.text("BODY", 14, 66, 82, 110, [
        [("Sample & fit review", {"font": SANS, "size": 8.5, "bold": True, "color": "cocoa"})],
        "Garment samples and fittings reviewed for fit, construction and quality; corrections communicated before production approval.",
        [("Production coordination", {"font": SANS, "size": 8.5, "bold": True, "color": "cocoa"})],
        "Daily work with tailors, pattern makers and production staff, from sample review through production.",
        [("Tracking", {"font": SANS, "size": 8.5, "bold": True, "color": "cocoa"})],
        "Production status and quality trackers in Excel and Google Sheets.",
        [("Categories", {"font": SANS, "size": 8.5, "bold": True, "color": "cocoa"})],
        "Womenswear · abaya & modest wear · evening & occasion · casual · ethnic wear.",
    ], size=8.5, font=SANS_LIGHT, color="plum", line=1.25, para_space=2)
    credit(p, 14, 186, 90, "Imagery: Sadah Fashion Design archive")
    a = p.image("SD-COCOA", 104, 16, h=82, crop=(0.13, 0, 0.13, 0.08), shadow=SH())
    b = p.image("SD-NUDE", 104, 16 + 82 + 7, h=82, crop=(0.13, 0.04, 0.13, 0.04), shadow=SH())
    d = p.image("SD-DETAIL", 104 + a[2] + 8, 16, h=171, crop=(0.03, 0, 0.03, 0), shadow=SH())
    caption(p, d[0], 190, d[2], "Detail · beaded sleeve and front edge", color="plum", h=5)
    p.folio("Professional")

    # ---- 16 CLOSING --------------------------------------------------------
    p = deck.page("Closing", C["wine"])
    p.rect("SURFACE", 0, 0, 120, H, C["wine_deep"])
    p.image("SK-03", 30, 30, h=150, mask_frame=(4, C["rose_on_dark"], 0.5))
    p.text("TITLE", 150, 62, 133, 30, "LAZIMA C A", size=52, font=SERIF, color="ivory")
    p.text("SUBTITLE", 151, 88, 130, 8, "FASHION DESIGN PORTFOLIO 2026", size=11, font=SANS_COND, color="ivory", spacing=4)
    p.text("TITLE", 150, 112, 130, 16, "Thank you", size=24, font=SERIF, italic=True, color="rose_on_dark")
    p.text("BODY", 151, 132, 120, 14, "Abu Dhabi, UAE · contact details available on request", size=9, font=SANS_LIGHT, color="rose_on_dark")
    p.folio("Closing", dark=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--bleed", type=float, default=0.0)
    ap.add_argument("--map")
    a = ap.parse_args()
    deck = Deck(a.bleed)
    build(deck)
    assert len(deck.pages) == 16, len(deck.pages)
    deck.prs.core_properties.title = "LAZIMA C A — Fashion Design Portfolio 2026"
    deck.prs.core_properties.author = "Lazima C A"
    for pg in deck.pages:
        notes = [l for l in pg.layers if l["kind"] == "image"]
        pg.slide.notes_slide.notes_text_frame.text = (
            f"Page {pg.no:02d} — {pg.title}. Image layers: " +
            "; ".join(f"{l['asset_id']} ({l['source']}, {l['effective_ppi']} ppi)" for l in notes))
    deck.prs.save(a.out)
    if a.map:
        data = {
            "document": "LAZIMA C A — Fashion Design Portfolio 2026",
            "trim_mm": [W, H], "bleed_mm": a.bleed, "page_count": len(deck.pages),
            "coordinates": "mm from trim top-left; layers listed bottom-to-top (z-order)",
            "pages": [{"page": pg.no, "title": pg.title, "layers": pg.layers} for pg in deck.pages],
            "asset_usage": deck.usage,
        }
        Path(a.map).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {a.out}: {len(deck.pages)} pages, bleed {a.bleed} mm")


if __name__ == "__main__":
    main()
