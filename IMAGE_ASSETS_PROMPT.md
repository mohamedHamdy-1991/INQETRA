# IMAGE_ASSETS_PROMPT.md — INQETRA rich-website image pack
**Created 2026-09-04 · For: Mohamed's AI image generator · Worker will wire them into the site when you say "images are ready".**

---

## WHERE TO SAVE THE GENERATED IMAGES (important)

Save **every** finished image as a **PNG, sRGB, exact filename as given**, into this folder (create it if missing — it is on your local SSD, easy to reach in Finder):

```
/Users/mohamedali/INQETRA-image-assets/
```

- Flat folder — no subfolders needed. Filename must match **exactly** (lowercase, hyphens).
- Wrong name = the worker can't auto-wire it.
- Don't resize/compress yourself — the worker does intake (resize, compress, copy into `apps/web/public/img/…`, update the code, rebuild, verify).
- When all (or the P0 batch) are saved, just tell the worker: **"images are ready"**.

A copy of this file is also at `/Users/mohamedali/INQETRA-image-assets/IMAGE_ASSETS_PROMPT.md`.

---

## GLOBAL STYLE (prepend to every prompt below)

> Neo-Brutalist flat vector illustration, 3px solid black (#161616) outlines on every shape, hard offset shadows (no blur), flat fills only — NO gradients, NO photorealism, NO 3D render look. Palette: cream background #F6E8D2, off-white surface #FBFAF6, ink #161616, yellow #FCDD28, orange #F36D30, pink #FF4F85, teal #12C8B0, violet #8167F5, green #4BD14A, muted sand #D8CCB9. Bold geometric shapes, chunky rounded-square cards, generous negative space, confident thick linework. PNG, sRGB.

**Text rule:** AI-generated text comes out mangled. Only generate text where a prompt explicitly lists SHORT words. Everywhere else keep imagery text-free.

**Priority key:** P0 = do first (site looks rich with just these 14) · P1 = second wave · P2 = polish wave.

---

## A. BRAND & SYSTEM (5)

| # | Filename | Size | P | Used at | Prompt |
|---|----------|------|---|---------|--------|
| A1 | `brand-og-card.png` | 1200×630 | **P0** | Social/OG share card (`layout.tsx` metadata) | Neo-brutalist share card: big cream panel with a giant stylised black magnifier-"Q" mark (circle with orbital dots and one node as a small yellow square) top-left, three overlapping chunky cards labelled with abstract bar-chart blocks in violet, teal and yellow (no readable text), thick black borders, 8px offset shadows, small black tag shapes as decorative labels. Text-free. |
| A2 | `brand-favicon-source.png` | 512×512 | **P0** | Source for favicon set (worker downsizes) | Single bold icon, centred: magnifier-"Q" formed by a thick black open circle with 3 orbital dots (yellow, pink, teal) and a small black square handle at 4 o'clock, flat cream #F6E8D2 background filling the square, 3px ink outline around the whole square. Minimal, high contrast, no text. |
| A3 | `brand-pattern-tile.png` | 480×480 | P1 | Seamless background tile (`public/img/pattern.png`) | Seamless repeating tile pattern on cream #F6E8D2: sparse grid of small neo-brutalist doodads — tiny black crosses, 8px yellow squares with ink outline, teal dots, violet plus-signs, pink triangles — evenly scattered, equal margins so the tile repeats perfectly on all edges. |
| A4 | `brand-mascot-copilot.png` | 512×512 | P1 | AI copilot avatar (`public/img/mascot.png`) | Friendly geometric robot head mascot, neo-brutalist flat vector: square off-white head with 3px ink outline, two round teal eyes, small yellow antenna with black dot, tiny violet bow-tie rectangle below, hard 6px offset ink shadow, cream background. Cheerful, minimal, no text. |
| A5 | `brand-404.png` | 1200×630 | P2 | 404 / not-found page art | Neo-brutalist scene: a large black magnifier lying over a scattered pile of chunky pastel dataset cards (yellow, teal, violet, pink) with abstract table-line marks (no readable text), one card torn in half, small question-mark-shaped dotted trail in ink, cream background, hard offset shadows. |

## B. HERO & LANDING BLOCKS (4)

| # | Filename | Size | P | Used at | Prompt |
|---|----------|------|---|---------|--------|
| B1 | `hero-landing.png` | 2000×1100 | **P0** | Home hero, right side (`app/page.tsx`) | Wide hero illustration: stylised UK terraced-street skyline in flat ink outlines along the bottom, floating above it a cluster of five chunky data cards (off-white, 3px ink borders, hard shadows) containing abstract charts — violet bar chart, teal line chart, yellow donut, pink map-pin cluster, green checklist ticks — connected by thick black dotted lines to a central black magnifier-"Q" mark. Cream background, airy top-left space for headline text. No readable text. |
| B2 | `block-journey.png` | 1200×800 | **P0** | Home "how it works" 10-step journey block | Vertical pipeline illustration: ten chunky rounded cards in a winding path connected by thick black arrows, each card a different flat pastel (palette above) with one simple pictogram — question mark, target, flask, database cylinder, basket, grid matrix, funnel, chart, document, export box — all 3px ink outlines with hard offset shadows, cream background. No text. |
| B3 | `block-studio.png` | 1200×800 | P1 | Home feature block "research studio" | Neo-brutalist workbench illustration: an off-white dashboard window (3px ink border, yellow title-strip with three dots) showing abstract research-graph panels — a node graph (5 dots linked by black lines), a two-column matrix with green ticks, a stacked requirements list — surrounded by floating chunky tool cards (ruler, flask, pin). Cream background, no readable text. |
| B4 | `cta-start-project.png` | 1600×600 | **P0** | Home bottom CTA + `/projects/new` header | Wide banner: left side a big chunky yellow arrow pointing right into a stack of three off-white project cards with ink borders; right side a flat violet sun and two abstract buildings; dotted black path connecting them; hard offset shadows, cream background, generous left space for a button. No text. |

## C. PAGE BANNERS (12) — all 1600×500, saved flat as named

Each: wide neo-brutalist banner, single centred-left motif on cream, 3px ink outlines, hard shadows, **no text**. Worker overlays real titles in HTML.

| # | Filename | P | Page (repo path) | Motif prompt (append to global style) |
|---|----------|---|------------------|----------------------------------------|
| C1 | `banner-datasets.png` | **P0** | `/datasets` | A tall stack of chunky dataset cards with abstract table rows, one card tilted, a yellow bookmark tab on top. |
| C2 | `banner-catalogue.png` | P1 | `/datasets/all` | An A→Z motif: three big off-white index cards with comb-like tab edges, black divider lines, a few violet/teal/yellow dots as entries. |
| C3 | `banner-projects.png` | P1 | `/projects` | Two overlapping project folders with chunky tabs, a green tick badge and an orange clock badge floating. |
| C4 | `banner-kits.png` | **P0** | `/kits` | An open box releasing eight small connected blocks joined by black dotted lines (a research starter-kit metaphor). |
| C5 | `banner-map.png` | P1 | `/map` | A folded paper map with thick ink roads, teal river band, yellow district polygons and three black map pins with pink heads. |
| C6 | `banner-compare.png` | P2 | `/compare` | Two side-by-side columns of abstract rows with a big black "versus" hourglass shape between them (no letters). |
| C7 | `banner-basket.png` | **P0** | `/basket` + drawer | A chunky shopping basket woven in ink outlines, filled with colourful dataset cubes (yellow, teal, violet, pink) sticking out the top. |
| C8 | `banner-publishers.png` | P2 | `/publishers` | Three neat office-building façades in flat ink outline with pastel window grids and small flag rectangles. |
| C9 | `banner-sources.png` | P2 | `/sources` | A radar-dish on a tripod beaming dotted black arcs toward three floating server blocks with pastel LED dots. |
| C10 | `banner-methodology.png` | P1 | `/methodology` | A big flask and a ruler crossed like heraldic symbols above a shield-shaped off-white card with a green tick. |
| C11 | `banner-about.png` | P2 | `/about` | A friendly collage: compass, open book, location pin and a cup of tea on one giant off-white card. |
| C12 | `banner-developers.png` | P2 | `/developers` | A chunky terminal window with `</>` shapes made of geometry (no readable code), a yellow bracket and teal dot motif. |

## D. RESEARCH KIT COVERS (8) — all 800×450, `P1`

Scene-style covers, one theme each, same global style, **no text**. Used on `/kits` cards + `/kits/[slug]` headers (`public/img/kits/kit-<slug>.png`).

| # | Filename | Theme prompt (append to global style) |
|---|----------|----------------------------------------|
| D1 | `kit-urban-heat-island.png` | City blocks seen from above with a glowing thermometer-shaped heat haze band in orange/pink rising from dark roof rectangles, yellow sun corner. |
| D2 | `kit-residential-overheating.png` | A cut-away terraced house with a big orange thermometer inside the bedroom and wavy heat lines through the window, small moon shape. |
| D3 | `kit-housing-energy-vulnerability.png` | A terraced house with a violet energy-bolt hole in the wall and a green pound-coin stack beside a meter box, winter scarf on the fence. |
| D4 | `kit-building-stock-retrofit.png` | Row of three houses: middle one wrapped in yellow insulation blanket with black stitching, a teal toolbox and ladder leaning on it. |
| D5 | `kit-walkability-accessibility.png` | Top-view pavement network with two feet pictograms, a wheelchair wheel motif, zebra crossing stripes and a pink route line with pins. |
| D6 | `kit-flood-housing-risk.png` | A terrace on a blue-teal water band with wavy ink lines, sandbags at the door, an umbrella and floating measuring stick. |
| D7 | `kit-health-built-environment.png` | A green park with trees, benches and a first-aid cross kite flying over small houses, dotted path looping through. |
| D8 | `kit-property-place-analysis.png` | A giant magnifier over a street of varied house façades, tiny price-tag shapes (blank) hanging from two roofs. |

## E. DOMAIN PLACEHOLDER ART (18) — all 640×360, `P1`

These replace the plain SVG placeholder on dataset cards when a publisher preview is missing (`public/img/domains/domain-<slug>.png`). One flat pictogram scene each, global style, **no text**.

| # | Filename | Motif |
|---|----------|-------|
| E1 | `domain-air-quality.png` | Cloud with dotted emission swirls and a teal wind sock. |
| E2 | `domain-buildings-housing.png` | Three terraced house façades, one window lit yellow. |
| E3 | `domain-climate-change.png` | Split globe: half cool teal, half warm orange, thermometer beside. |
| E4 | `domain-crime-safety.png` | Police-light cube and a shield with a keyhole, dotted trail. |
| E5 | `domain-energy-carbon.png` | Violet lightning bolt into a battery, small CO₂ cloud made of dots (no letters). |
| E6 | `domain-environment.png` | Leaf, tree and a ladybird-style beetle on a big leaf. |
| E7 | `domain-flooding-hazards.png` | Wavy teal water band swallowing a lamppost, warning triangle. |
| E8 | `domain-geospatial-gis.png` | Grid-ruled map with polygon shapes and crosshair target. |
| E9 | `domain-health-wellbeing.png` | Heart with pulse line and a green apple on a bandage-plaster. |
| E10 | `domain-heritage.png` | Columned classical building with a bunting garland. |
| E11 | `domain-housing-vulnerability.png` | House with a crack line and an empty bowl shape on the step. |
| E12 | `domain-land-property.png` | Ownership map parcel shapes with a fence and a small post box. |
| E13 | `domain-planning-development.png` | Blueprint roll unrolling to reveal a small housing layout. |
| E14 | `domain-policy-governance.png` | Podium with three microphones and a scroll with wax seal. |
| E15 | `domain-population-demographics.png` | Crowd of diverse simple figures, one in yellow, one in violet. |
| E16 | `domain-topography-terrain.png` | Layered contour lines forming a hill with a flag on top. |
| E17 | `domain-transport-mobility.png` | Bus front, bicycle wheel and a rail track converging. |
| E18 | `domain-weather-climate.png` | Sun behind a rain cloud with a rainbow arc and umbrella. |

## F. EMPTY STATES & INFO BLOCKS (5) — all 900×600, `P2`

Friendly "nothing here yet" scenes, global style, **no text**.

| # | Filename | Used at | Prompt motif |
|---|----------|---------|--------------|
| F1 | `empty-basket.png` | Basket drawer/page empty state | An empty woven basket lying on its side, one lone yellow cube rolling toward it along a dotted path. |
| F2 | `empty-candidates.png` | Candidate inbox empty | An open letter tray with a single paper plane circling above it on a dotted loop. |
| F3 | `empty-results.png` | Abstract/results empty state | A clipboard with blank table rows and a flask beside it with one green drop falling. |
| F4 | `block-licence.png` | Licence/access awareness block | Two cards: one with an open padlock (green), one with a closed padlock (orange), separated by a balanced scale silhouette. |
| F5 | `block-ai-optional.png` | "AI optional" block | A small friendly robot sleeping on a shelf while a checklist card with green ticks glows beside it — deterministic tools do the work. |

## G. STICKER SHEET (1) — `P2`

| # | Filename | Size | Prompt |
|---|----------|------|--------|
| G1 | `stickers-set.png` | 1200×800 | A sticker sheet on cream: six chunky rotated badge shapes (circle, starburst, rounded square, hexagon, tag, seal) each with 3px ink outline and hard shadow, flat single-colour fills (yellow, teal, violet, pink, green, orange). Inside each, ONE very short word in bold black Arial-Black-style type, exactly: `EVIDENCE`, `751`, `OPEN`, `TRACEABLE`, `REPRODUCIBLE`, `UK`. Keep the words large, centred and correctly spelled — nothing else written anywhere. (Worker slices this into `public/img/stickers/`.) |

---

## INTAKE — WHAT THE WORKER DOES WHEN YOU SAY "IMAGES ARE READY"

1. Verifies every file exists in `/Users/mohamedali/INQETRA-image-assets/` with the exact names (reports any missing/wrong-named ones).
2. Resizes + compresses (`sips`), converts where needed, copies into `apps/web/public/img/…` inside the repo working copy.
3. Wires references into the pages (heroes, banners, kit covers, domain placeholders, empty states, OG card, favicon set, stickers), with `alt` text, lazy-loading and the deterministic SVG kept as final fallback for dataset previews.
4. Rebuilds the site, runs the full verification gates, shows you before/after.

**Minimum useful batch = all P0 rows (14 files):** A1, A2, B1, B2, B4, C1, C4, C7 + any 6 of your choice.
