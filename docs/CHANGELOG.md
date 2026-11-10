# Change log

## 2026-11-10 — A4 landscape final portfolio (feature/lazima-a4-landscape-final)
- Supersedes all A4-portrait plans and the "Sadah leads" direction: 16-page **A4 landscape**, sketch-led; Sadah limited to pp. 14–15.
- `tools/portfolio/build_master.py`: code-built editable PowerPoint master with named layers; original image bytes embedded unchanged, non-destructive crops, aspect lock, per-image PPI and SHA-256 layer map; 3 mm bleed variant.
- `tools/portfolio/export_pdf.ps1`: PDF export through Microsoft PowerPoint (COM).
- `tools/portfolio/produce.py`: print PDF with original-pixel image streams (PowerPoint's ~200 ppi downsampling replaced, 350 ppi cap) and Trim/Bleed boxes; digital PDF; contact sheet; asset register; QC report; ZIP. Outputs to git-ignored `deliverables/`.
- Cover rebuilt from the **original airplane photograph** (unretouched) instead of the earlier generated covers.
- Owner-attested web-sized sketches/flats added; signature and Pinterest-watermark questions raised during QC and confirmed by the owner. Third-party templates/moodboards/mockups excluded.
- Fonts: Bodoni MT + Gill Sans MT (static Office fonts); Bahnschrift dropped after PowerPoint substituted Calibri.
- See `docs/A4_LANDSCAPE_PRODUCTION.md`.

## 2026-11-10 — Editorial portfolio site (feature/editorial-portfolio-site)
- Audited local sources. One verified body of work: the scanned *Paper Flower* student portfolio. Recorded in `docs/SOURCE_ATTRIBUTION_REGISTER.md`; other folders classified as derived drafts or unverified references.
- Built `site/`: 12 A4 pages (cover, identity, moodboard, sketchbook, silhouettes, development, modest wear, colour & cloth, specification, collection, practice, closing), using container-query units so one composition serves phone, desktop spreads and A4 print.
- Named asset slots (`site/assets/manifest.js`) load originals from a git-ignored folder, with labelled placeholders otherwise. A source-notes toggle shows rights status.
- `tools/extract_assets.py`: crop-only extraction with a pixel-equality check, SHA-256 register (local only).
- `npm test` (35 checks): structure, alt text, WCAG contrast of all type/paper pairs, A4 print rules, external origins, no tracked images/documents, no private paths or contact patterns.
- Caption colour darkened from `#756257` to `#5A483F` to pass contrast on lilac and sage.
- `docs/CANVA_PRODUCTION_PLAN.md`: tokens, type scale, layer naming and page-by-page placement.

## 2026-11-10 — Visual-first direction approved
- Locked the user's motive: **larger sketches, richer moodboards, softer colours, bold typography and minimal text**.
- Shifted Claude instructions and 12-page storyboard from narrative-focused to image-led design.
- Added detailed visual direction, coordinated palette, layout recipes and public-safe HTML prototype.
- No actual artwork or personal photos published in this change; preview drawings are marked as placeholders.

## 2026-11-10 — Public-safe Claude handoff
- Initialized `LAZIMA-PORTFOLIO` as a Claude-readable source-controlled workspace.
- Added working production plan, rigorous image-integrity standards, evidence/rights controls and asset-register template.
- No personal photos, resumes, original employer assets, interview PDFs/PPTXs or private source archive uploaded.
- Portfolio content, Canva editable design, final exports and final approvals remain pending.
