/* Asset slot manifest.
 *
 * Every image on the portfolio is a named slot. `file` points to the
 * git-ignored local folder `assets/private/` (filled by
 * tools/extract_assets.py from the private source scan). When the file is
 * absent â€” e.g. on any public copy of this repo â€” the slot renders a clearly
 * labelled placeholder instead.
 *
 * `approved` must stay false until the owner signs off the asset in
 * docs/SOURCE_ATTRIBUTION_REGISTER.md. Only approved assets may ever be
 * moved to a published folder (see README, "Publishing gate").
 *
 * `ratio` = width / height of the source crop, so frames never distort art.
 */
window.LAZIMA_ASSETS = {
  "look-01": {
    file: "assets/published/look-01.png", ratio: 1472 / 2096, kind: "original",
    alt: "Look 01: fashion illustration of a long magenta dress with one ruffled sleeve and a high slit, figure under two teal spotlights on black.",
    credit: "Lazima C A. Original digital illustration, Paper Flower, 2023.",
    status: "Original student work. Owner approved for portfolio/GitHub publication on 10 Nov 2026.",
    approved: true
  },
  "look-02": {
    file: "assets/published/look-02.png", ratio: 1501 / 2132, kind: "original",
    alt: "Look 02: illustration of a cropped short-sleeve top with a tiered magenta midi skirt trimmed with small florets.",
    credit: "Lazima C A. Original digital illustration, Paper Flower, 2023.",
    status: "Original student work. Owner approved for portfolio/GitHub publication on 10 Nov 2026.",
    approved: true
  },
  "look-03": {
    file: "assets/published/look-03.png", ratio: 1489 / 2118, kind: "original",
    alt: "Look 03: illustration of a ruffle-sleeved crop top with flared magenta trousers.",
    credit: "Lazima C A. Original digital illustration, Paper Flower, 2023.",
    status: "Original student work. Owner approved for portfolio/GitHub publication on 10 Nov 2026.",
    approved: true
  },
  "look-04": {
    file: "assets/published/look-04.png", ratio: 1497 / 2128, kind: "original",
    alt: "Look 04: illustration of a cropped top and a red midi skirt with rows of floral appliquÃ©.",
    credit: "Lazima C A. Original digital illustration, Paper Flower, 2023.",
    status: "Original student work. Owner approved for portfolio/GitHub publication on 10 Nov 2026.",
    approved: true
  },
  "look-05": {
    file: "assets/published/look-05.png", ratio: 1434 / 2038, kind: "original",
    alt: "Look 05: illustration of a plum V-neck dress with ruffled shoulders and a tiered skirt, under teal spotlights.",
    credit: "Lazima C A. Original digital illustration, Paper Flower, 2023.",
    status: "Original student work. Owner approved for portfolio/GitHub publication on 10 Nov 2026.",
    approved: true
  },
  "spec-sheet": {
    file: "assets/published/spec-sheet.png", ratio: 1465 / 1930, kind: "original",
    alt: "Garment specification sheet for style SSRCO12 with front and back flat drawings of a V-neck dress with pleated sleeves, waistband and two-layer skirt.",
    credit: "Lazima C A. Garment specification sheet, Paper Flower, 26 July 2023.",
    status: "Original student work. Owner approved for portfolio/GitHub publication on 10 Nov 2026.",
    approved: true
  },
  "pattern-board": {
    file: "assets/private/pattern-board.jpg", ratio: 1230 / 2180, kind: "original",
    alt: "Photograph of hand-drafted paper pattern pieces: front body, back body, sleeves and waistband, with seam-allowance notes.",
    credit: "Lazima C A. Paper patterns, Paper Flower, 2023. Photographer to be confirmed.",
    status: "Student work. Photographer credit unconfirmed; owner approval pending.",
    approved: false
  },
  "production-board": {
    file: "assets/private/production-board.jpg", ratio: 1220 / 2160, kind: "photo-person",
    alt: "Collage of photographs of the finished plum dress with ruffled sleeves, worn outdoors over a black long-sleeve layer.",
    credit: "Finished garment, Paper Flower, 2023. Photographer and wearer to be credited.",
    status: "Identifiable person. Needs wearer consent and photographer credit before any publication. Shown unaltered.",
    approved: false
  },
  "board-inspiration": {
    file: "assets/private/board-inspiration.jpg", ratio: 1310 / 2332, kind: "compiled",
    alt: "Original inspiration board: close-ups of magenta bougainvillea bracts.",
    credit: "Inspiration board compiled by Lazima C A, 2023. Photo sources unconfirmed.",
    status: "Compiled board with third-party photographs. Private reference; do not publish.",
    approved: false
  },
  "board-theme": {
    file: "assets/private/board-theme.jpg", ratio: 1310 / 2332, kind: "compiled",
    alt: "Original theme board: bougainvillea climbing over walls and arches.",
    credit: "Theme board compiled by Lazima C A, 2023. Photo sources unconfirmed.",
    status: "Compiled board with third-party photographs. Private reference; do not publish.",
    approved: false
  },
  "board-colour": {
    file: "assets/private/board-colour.jpg", ratio: 1310 / 2338, kind: "compiled",
    alt: "Original colour board: blocks of raspberry, crimson and mulberry.",
    credit: "Colour board compiled by Lazima C A, 2023. Image sources unconfirmed.",
    status: "Compiled board. Image sources unconfirmed; private reference.",
    approved: false
  },
  "board-fabric": {
    file: "assets/private/board-fabric.jpg", ratio: 1307 / 2338, kind: "compiled",
    alt: "Original fabric board: draped and swirled magenta cloth with dried flowers.",
    credit: "Fabric board compiled by Lazima C A, 2023. Image sources unconfirmed.",
    status: "Compiled board. Image sources unconfirmed; private reference.",
    approved: false
  },
  "portrait": {
    file: null, ratio: 4 / 5, kind: "pending",
    alt: "",
    credit: "",
    status: "Placeholder. Needs an owner-approved, unedited portrait or workspace photo.",
    approved: false
  },
  "modest-hero": {
    file: null, ratio: 3 / 4, kind: "pending", alt: "", credit: "",
    status: "Placeholder. Needs an original modest-wear sketch with confirmed authorship.",
    approved: false
  },
  "modest-garment": {
    file: null, ratio: 3 / 4, kind: "pending", alt: "", credit: "",
    status: "Placeholder. Needs a finished-garment photo with wearer consent, photographer credit and, if employer work, written permission.",
    approved: false
  },
  "modest-textile": {
    file: null, ratio: 1, kind: "pending", alt: "", credit: "",
    status: "Placeholder. Needs a real textile or trim close-up.",
    approved: false
  },
  "workspace": {
    file: null, ratio: 3 / 4, kind: "pending", alt: "", credit: "",
    status: "Placeholder. Needs an approved workspace or process photo.",
    approved: false
  }
};

