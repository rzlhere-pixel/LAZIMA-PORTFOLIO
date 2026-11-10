# LAZIMA C A — Fashion Design Portfolio 2026 · A4 Landscape Production

**Status:** produced locally 10 Nov 2026 on branch `feature/lazima-a4-landscape-final`. This document **supersedes** the A4-portrait plans (`LAYERED_EDITORIAL_PAGE_PLAN.md`, `PORTFOLIO_STORYBOARD.md`) and the earlier "Sadah leads" direction. The deliverables themselves contain private personal and employer imagery and are **not in this repository**.

## Format
- A4 landscape, 297 × 210 mm (3508 × 2480 px at 300 dpi). Print PDF: 303 × 216 mm media, 3 mm bleed, TrimBox 297 × 210.
- 12 mm safe margin for type and images (checked automatically). Folio band at 199.5 mm.
- 16 pages. Sketch-led: pages 03–13 are original illustration, technical and Paper Flower process work; Sadah is limited to pages 14–15.

## Page sequence

| # | Page | Lead visual |
|---|---|---|
| 01 | Cover: LAZIMA C A / FASHION DESIGN PORTFOLIO / 2026 | Original airplane photograph, unretouched, framed on wine |
| 02 | Introduction | Paper Flower look 01; short profile, education, experience, practice |
| 03 | The Sketchbook | Two-figure evening gown, graphite (hero) |
| 04 | Hand sketches | Tiered ruffle gown + mermaid gown, side by side |
| 05 | Drape & volume | One-shoulder draped gown + sleeve detail |
| 06 | Technical drawing | Corset gown front/back flats with call-outs |
| 07 | Digital illustration | Tailored blazer + waist detail |
| 08 | Modest wear | Nine-abaya line-up + two enlarged studies |
| 09 | Specification sheets | Two tailored-set spec sheets |
| 10 | Paper Flower opener | Look 03, colour & fabric boards, concept quote |
| 11 | The collection | Five looks, one line-up |
| 12 | From sketch to spec | Look 05 beside spec sheet SSRCO12 |
| 13 | Pattern to garment | Pattern board + production board, 5-step process |
| 14 | Professional experience — Sadah | Two archive garments, role facts, supporting wording |
| 15 | Professional practice | Three archive images + résumé responsibilities |
| 16 | Closing | Sketch + name, "contact details available on request" |

## Design system
- **Palette:** Milk Ivory `#F6F2EC` (paper), Powder Rose `#E9D9D6` (sketch/Paper Flower), Dusty Lilac `#CFC7D7` (sketchbook/digital), Muted Sage `#C4CBBE` (modest wear/process), Misty Blue `#D5DFE5` (technical), Deep Plum `#312734` (type, dark chapters), Wine `#5A1A2A` / `#43121F` (cover, closing), Cocoa `#756257` (captions), soft rose-on-dark `#D9B8BC`.
- **Type:** Bodoni MT / Bodoni MT Italic display; Gill Sans MT body, labels and captions; Gill Sans MT Condensed letter-spaced for the cover/closing line. All are static fonts installed with Microsoft Office. Bahnschrift (variable) was rejected: PowerPoint substituted Calibri on export.
- **Layer names** (every object): `BG`, `SURFACE`, `IMAGE-SHADOW-[ID]`, `IMAGE-ORIGINAL-[ID]`, `IMAGE-MASK-[ID]` (frames), `TITLE`, `SUBTITLE`, `BODY`, `CAPTION`, `SOURCE-CREDIT`, `FOLIO`.

## Pipeline (`tools/portfolio/`)
| Script | Role |
|---|---|
| `build_master.py` | Builds the PPTX from code. Embeds the **original source files byte-for-byte**, crops non-destructively (srcRect), locks aspect ratios, writes a layer map with per-image effective PPI and SHA-256. `--bleed 3` builds the print variant. Refuses to run if a source is missing. |
| `export_pdf.ps1` | Opens the PPTX in Microsoft PowerPoint (COM) and saves PDF. |
| `produce.py` | Runs the whole package: masters, PowerPoint exports, print PDF (replaces PowerPoint's ~200 ppi downsampled image streams with exact crops of the original pixels, capped at 350 ppi; sets Trim/Bleed boxes), digital PDF, page renders, contact sheet, asset register, QC checks and report, ZIP. |

Run on the owner's machine (needs the git-ignored sources and PowerPoint):

```bash
pip install python-pptx pymupdf pillow numpy
# optional: register rows for private documents kept outside the repo
export LAZIMA_SCAN_PDF="<path to scanned 2023 student portfolio PDF>"
export LAZIMA_RESUME_PDF="<path to latest résumé PDF>"
export LAZIMA_OLD_COVERS_DIR="<folder with earlier generated covers>"
python tools/portfolio/produce.py     # -> deliverables/LAZIMA_FASHION_PORTFOLIO_2026/
```

## Source rules applied
- Only verified or owner-attested work is presented as Lazima's. Paper Flower crops come from the scanned 2023 student portfolio (designer named on the spec sheet).
- The web-sized sketches, flats, abaya line-up and spec sheets are owner-attested (10 Nov 2026). Three sketchbook pages carry a top-right signature and the abaya line-up a Pinterest watermark; the owner confirmed both as Lazima's. Nothing was retouched out.
- Excluded: third-party templates, moodboards, mockup pages, a portfolio cover with another designer's name, bougainvillea photo boards, earlier generated covers.
- Sadah: 5 of 19 archive photos, captioned as garments only, with the approved attribution sentence. No design/styling/photography/modelling claim.
- Résumé facts only (role, employer, dates, education, skills). No phone, email, LinkedIn or visa status.

## Open owner actions
1. Wearer consent + photographer credit for the Paper Flower production board (p13).
2. Employer comfort with portfolio use of the 5 Sadah photographs.
3. Higher-resolution originals of the web-sized sketches/spec sheets for large print (currently 119–181 ppi at placed size).
4. Approve before any public upload; the repository stays free of images.
