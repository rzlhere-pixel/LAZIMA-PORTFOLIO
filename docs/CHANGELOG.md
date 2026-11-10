# Change log

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
