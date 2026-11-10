# LAZIMA PORTFOLIO · LAZIQUE

**Latest local project handoff:** [Complete source register](docs/CLAUDE_COMPLETE_SOURCE_HANDOFF.md) · [17-page layered A4 editorial plan](docs/LAYERED_EDITORIAL_PAGE_PLAN.md). Sadah professional images are the primary visual work; Paper Flower is solely academic. The complete image ZIPs, cover candidates, and mockup references are available to Claude Code on the authorized ASUS under git-ignored `source/private/` and are not in this public repository.

A **visual-first fashion portfolio** workspace for LAZIMA, with the complementary **LAZIQUE** creative identity.

**Creative motive (approved 10 November 2026):** Larger original sketches, richer layered moodboards, softer colour stories, bold editorial typography, and minimal text. **The work must look like a fashion designer’s visual book, not a corporate résumé.**

**Portfolio site: [`site/index.html`](site/index.html)** (12 A4 pages; responsive; prints to A4) · [Visual direction](docs/VISUAL_DIRECTION.md) · [Source register](docs/SOURCE_ATTRIBUTION_REGISTER.md) · [Canva production plan](docs/CANVA_PRODUCTION_PLAN.md)

The earlier [layout study](preview/index.html) is kept for reference and has been superseded by `site/`.

## Preview locally

```bash
npm run serve        # http://127.0.0.1:4173  (localhost only)
npm test             # structure, a11y basics, contrast, print rules, privacy guards
```

**With the original artwork (owner's machine only):** run `python tools/extract_assets.py "<path to the private scanned Paper Flower portfolio PDF>"`. Crops are written to `site/assets/private/`, which git ignores. Without that folder, every image slot shows a clearly labelled placeholder. That is what any public copy of this repo shows.

- **Source notes** (toolbar) shows the rights status on every image.
- **Print A4** (toolbar, or the browser's print dialog) produces one A4 page per sheet. Choose *Save as PDF*, margins *None*, *Background graphics* on.

## Publishing gate
Images are published only after the owner approves each asset in [the source register](docs/SOURCE_ATTRIBUTION_REGISTER.md): set `approved: true` in `site/assets/manifest.js` and move the file out of `assets/private/` in a reviewed PR. `npm test` fails if an unapproved asset could be published or if any image/document is tracked.

This repository contains **no images**. The site loads Lazima's original Paper Flower artwork only from a local, git-ignored folder; everywhere else it shows labelled placeholders.

> **Public repository notice:** This is a publication-safe working scaffold, **not** the complete private project archive and **not** a finished, fact-verified portfolio. Personal photographs, employer work files, detailed employment records, CVs, interview materials, and permission evidence are intentionally excluded.

## For Claude Code

**Start with [CLAUDE.md](CLAUDE.md).** Then use:
- [Project status](docs/STATUS.md) — what is ready, blocked, or awaiting confirmation
- [Portfolio storyboard](docs/PORTFOLIO_STORYBOARD.md) — A4, image-led portfolio plan
- [Visual direction](docs/VISUAL_DIRECTION.md) — approved visual-first brief, typography, layout and palette
- [Creative standards](docs/CREATIVE_STANDARDS.md) — LAZIQUE design and photo-preservation rules
- [Source and publishing rules](docs/PRIVACY_AND_SOURCES.md) — attribution, permission and privacy
- [Blank asset register](docs/ASSET_REGISTER_TEMPLATE.csv) — source-by-source provenance

## Two related workstreams

**Professional portfolio:** Fashion design, garment construction, original concepts, production / quality experience, and accurately credited case studies. Target master: **Canva-editable A4 portrait (210 × 297 mm)** with a reviewed PDF export.

**LAZIQUE:** Personal creative identity with a lowercase handwritten-style wordmark, refined editorial visuals and Windows 11 wallpapers. Proposed wallpaper sizes: **3840 × 2160** master and **1920 × 1080** preview.

The official wordmark and unchanged original photos are required for pixel-accurate compositions. No AI-generated resemblance may be represented as the original person.

## Current state

The earlier conversations and locally recovered files were consolidated into a **separate offline handoff archive**. That archive is not included in this public repository. Some older files and approval evidence remain missing. Do not claim a finalized portfolio, approved employment stories, uploaded raw assets, or working Canva project.

## Next step

Make this repository **private** before transferring original/source documents, even those contained in the existing handoff ZIP. Then reconcile permissions and upload only approved material through a reviewed commit or PR.

**Last project context update:** 10 November 2026.
