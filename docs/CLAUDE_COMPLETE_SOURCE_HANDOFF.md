# LAZIMA — Complete Source Handoff for Claude Code

**Prepared:** 10 November 2026
**Primary goal:** A visual-first A4 portfolio: large high-resolution photography, layered fashion compositions, bold editorial typography, minimal supporting copy. Professional Sadah work is primary; Academic Paper Flower work is secondary.

## Files now physically available on ASUS

All source files below are **local to this workstation** and intentionally git-ignored while the GitHub repository is public. Claude Code running from this repository can inspect them directly.

| Category | Local relative path | Contents | Editorial status |
| --- | --- | --- | --- |
| Sadah professional/employer archive | `source/private/professional-sadah/work/` | 19 high-resolution photographs, mostly 3072 × 4096 px | Primary visual story. Work supplied as Sadah archive; no unsupported individual design claims |
| Sadah ZIP original | `source/private/professional-sadah/Sadah-portfolio-originals.zip` | Original supplied ZIP | Original evidence; do not rewrite |
| Academic assets | `source/private/academic/assets/` | 13 jpg/jpeg samples: sketches, technical drawings, moodboard and external references | Mixed references, NOT all Lazima originals. Classify individually |
| Claude-generated academic PDF | `source/private/academic/Claude-made-academic-draft.pdf` | 12-page generated draft | Academic work only; visual reference, **not** professional work |
| Mockup pages | `source/private/references/portfolio-mockup/` | 8 pages from supplied mockup ZIP | Art-direction reference only. Do not borrow other designer identity/artwork |
| Mockup PDF | `source/private/references/mockup-reference.pdf` | Portfolio mockup source PDF | Reference only |
| Cover candidates | `source/private/cover/` | Three burgundy editorial cover images | Source as user-supplied. Preserve images; identity pixel accuracy is **unverified** |

Publicly published academic originals already in `site/assets/published/`: five Paper Flower student illustrations and one spec sheet.

## Core classification

**ACADEMIC:** Paper Flower, student illustrations, course-era design studies, student technical flat/specification, academic moodboards, patterns; keep to ~20% of final editorial pages. The Claude-made PDF is a *presentation derived from academic works*, not an authoritative raw asset and not professional evidence.

**PROFESSIONAL / EMPLOYER:** Sadah/Sada supplied fashion campaign images. Use as professional archive visuals with accurate wording, e.g. 'Selected work from Sadah Fashion Design archive, during Lazima’s employment'. Do **not** claim that Lazima alone designed, styled, photographed or modeled the garments. Employer/photographer/model attribution remains to be confirmed. The filename's price information is not a price claim for Lazima's portfolio.

**REFERENCE:** assets ZIP mixed Pinterest-style examples and mockup ZIP. Use only as composition references unless Lazima provides original authorship and reproduction clearance. Never transfer another designer's identity/biography into final pages.

**COVER:** Keep the user-selected burgundy visual, but do not assert that facial pixels are unchanged from the original airplane selfie without a proper pixel comparison. For exact identity preservation, perform non-generative compositing from the source photo.

## Layer-by-layer build requirements

Target native A4 portrait 210 × 297 mm. Create independent named layers for: BG / TONAL-SURFACE / PHOTO-[asset-id] / MASK / SHADOW / DISPLAY-TITLE / CAPTION / PAGE-FOLIO. Every photo remains an independent, original-pixel source object; never use AI to reconstruct, retouch or alter people. No new body poses or fabricated clothing.

Refer to [the 17-page production map](LAYERED_EDITORIAL_PAGE_PLAN.md). Build professional chapters first and keep academic evidence compact. Use minimum 9pt print-size readable captions, print proof, mobile reading proof, and verify visual alignment/crop at 100% zoom.

## Required next actions for Claude Code

1. Inspect all 19 Sadah JPEGs, 13 academic references, eight mockup pages, three covers and the academic PDF **locally**.
2. Build a full source manifest with checksum, resolution, rights notes and use status; don't flatten distinct categories.
3. Improve current HTML A4 layout and create edit-friendly layered outputs. Use true garment photography prominently. Keep original photo pixels and actual crop/aspect ratio.
4. Confirm use rights before adding employer photos, borrowed moodboard images, or identifiable people to **public GitHub**. Local work may use the supplied sources for owner review.
5. Maintain existing working feature branch, tests, source register and the GitHub project's visual direction. Report all actual deliverables and limitations.

## Publishing policy

This GitHub repo is currently **public**. The private asset archive is intentionally not tracked. Do not run `git add --force source/private`, do not publish 48MB of borrowed mockups, and do not mistake local visibility to Claude Code for public GitHub publication. Once rights and privacy are confirmed, release only reviewed assets into `site/assets/published/` via a separate PR.

## Reference implementation

The private layered PowerPoint production master and PDF exported in this ChatGPT conversation are separate deliverables. They are **not automatically synchronized** to ASUS by ChatGPT. They can be copied manually into `exports/private/` without pushing source images into the public repository.
