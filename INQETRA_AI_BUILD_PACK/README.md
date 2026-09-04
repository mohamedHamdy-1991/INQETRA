# INQETRA — AI Build Pack

**INQETRA** is a research-design and dataset-intelligence platform that takes a researcher from a question to an executable, citable research data plan and a traceable abstract draft.

The current original app mark is [`assets/inqetra-logo-mark-v2.png`](assets/inqetra-logo-mark-v2.png). Its application guidance is in [`assets/README.md`](assets/README.md).

This directory is intentionally written so an autonomous coding agent can build the product with minimal product-design decisions.

## Start here
1. Read `00_START_HERE.md`.
2. Load `01_MASTER_BUILD_PROMPT.md` as the root coding-agent instruction.
3. Treat `data/datasets_seed.csv` as **seed metadata only**, not verified production truth.
4. Apply `design/inqetra_tokens.css` and `design/inqetra_components.css` globally before page implementation.
5. Use `prototype/landing.html` as the visual/interaction source for the landing page.

## Dataset seed
Current seed records: **751**. The catalogue deliberately mixes direct official records, official collection entries, official portal search records, and documented dataset partitions. Every current landing URL is covered by the reproducible HTTP health report at `data/link_health/catalogue_link_health.csv`; that health check is not a substitute for resource-level metadata, licence or access validation. Production ingestion must resolve/revalidate each record and preserve its verification state.

For a ready-to-use catalogue file, open [`data/INQETRA_751_DATASETS_WITH_TESTED_LINKS.csv`](data/INQETRA_751_DATASETS_WITH_TESTED_LINKS.csv). It includes each dataset’s landing URL, final URL, HTTP response and verification timestamp.

## Requested local destination
`/Users/mohamedali/Library/CloudStorage/OneDrive-LeedsBeckettUniversity/Work/GITHUB REPO/INQETRA`

This ChatGPT runtime cannot directly write into a local macOS OneDrive path. `scripts/install_to_target.sh` is included so the generated pack can be copied there on the Mac after download/extraction.
