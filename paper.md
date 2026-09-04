---
title: 'INQETRA: a research-design studio linking built-environment research questions to authoritative UK open data'
tags:
  - Python
  - TypeScript
  - research design
  - open data
  - built environment
  - data management
authors:
  - name: Mohamed Hamdy Ali
    affiliation: 1
affiliations:
  - name: Leeds Beckett University, United Kingdom
    index: 1
date: 4 September 2026
bibliography: paper.bib
---

# Summary

Researchers in the built-environment sciences routinely begin a project with an
under-specified question and lose weeks discovering which authoritative datasets
exist, whether they are licensed for reuse, and how they can be joined. Existing
catalogues answer "where is a dataset?" but not "does this dataset answer my
question, and can I lawfully and technically combine it with the others I need?"
INQETRA is a web-based research-design studio that closes this gap: it treats the
path from research problem to executable data plan as a graph of linked, auditable
objects — knowledge gaps, research questions, aims, methods, dataset requirements,
a dataset basket, an aim-by-dataset matrix, transformations and analysis steps —
and it records provenance, licence state and link health for every dataset along
the way. A researcher finishes an INQETRA session with a reproducible, exportable
Research Data Plan rather than a folder of bookmarks.

# Statement of need

Graduate researchers and practitioners in fields such as building performance,
energy, housing and climate adaptation must repeatedly assemble evidence bases from
fragmented public sources: national statistical portals, mapping agencies, and
meteorological services [@metofficehadukgrid; @mhclgepc]. Two failure modes are common. First, datasets are chosen
by availability rather than by derivation from the research questions, which
weakens the eventual inference; methodologists have long argued that data
management should follow the research design rather than accompany it, as
codified in the FAIR principles [@wilkinson2016fair]. Second, the legality and
mechanical compatibility of combinations — spatial scale mismatches, identifier
incompatibilities, licence restrictions — are discovered late, after analysis has
begun. Built-environment research adds a domain-specific burden: simulation-based
workflows [e.g. @crawley2008contrasting] and overheating risk assessment [@cibse2017tm59]
depend on weather and building-stock data whose provenance and versioning directly
affect the defensibility of results.

No existing open tool connects the research-design layer (questions, aims, methods)
to a curated UK dataset catalogue with mechanical compatibility checking, gap
analysis and evidence-traced drafting. Spreadsheets and generic notebooks record
the outcome of design decisions but not the decisions themselves. INQETRA addresses
both failure modes in one place: requirements are derived from aims, candidate
datasets are matched against explicit requirements, a rule-based engine reports
mechanical compatibility (coverage, geography, granularity, identifiers, units,
format, access, licence, freshness), and an export renders the full plan with every
dataset claim traceable to its landing page and review date.

# State of the field

General-purpose research-data catalogues and registries (for example data.gov.uk
and the Office for National Statistics portals) provide search over metadata but
no linkage to research design. Data-management-plan assistants operate at the level
of institutional policy rather than per-project dataset selection. Reference-manager
and qualitative-analysis tools cover citations, and computational notebooks cover
analysis, but the design layer between question and dataset — requirements,
compatibility and gap analysis — remains unmanaged in common practice. INQETRA is
complementary to these tools: it produces structured plans that feed analysis
workflows rather than replacing them.

# Key features and implementation

INQETRA is a two-part web application. The backend (Python/FastAPI [@fastapi], SQLAlchemy)
serves a catalogue of 751 curated UK datasets spanning 18 domains — each record
carrying publisher, landing URL, link type, verification state, access mode,
licence and last review date, with CSV/JSON/Markdown parity views. Beyond the
catalogue it exposes the research-design graph (projects, questions, aims,
objectives, hypotheses, methods, dataset requirements, a basket, an aim-by-dataset
matrix, notes, results, transformations and ordered analysis steps), a rule-based
compatibility engine with a data-gap radar, a candidate inbox for external
discoveries that are never auto-published, robots-aware thumbnail extraction,
an optional provider-neutral AI assistant restricted to deterministic tool
outputs, and document "paths" (doctoral thesis, master's dissertation, research
grant, journal and conference papers) that tailor section skeletons, word targets
and tool emphasis. Compatibility rules and research-kit templates are editable
first-class records, and users can author custom kits. The frontend (TypeScript,
Next.js [@nextjs], React) renders the studio, catalogue, comparison and administration
interfaces, is adaptive to mobile viewports, and exports project reports and
basket coverage reports as print-ready PDF documents in a deliberately high-
contrast visual design.

Three policies are enforced throughout: (i) landing-page reachability never
implies download access, licence permission or scientific fitness — every dataset
claim carries its source URL and verification state; (ii) external discoveries
enter a staging inbox and require curator review with provenance and link health
before becoming catalogue records; (iii) AI assistance is optional,
provider-neutral and restricted to structuring deterministic tool outputs, so it
cannot invent datasets, licences or results. Abstract drafts and exports render
only researcher-entered results; absent results are marked unresolved rather than
fabricated.

# Quality control

The repository contains a 33-test automated suite (pytest) covering catalogue
minimum counts and parity, required metadata fields, twelve domain filters, a
full golden-journey integration test from problem statement to exported plan,
compatibility and gap analysis, kit instantiation, harvester staging semantics,
resolver exact-match rules, thumbnail robots compliance (network mocked), AI-tool
provenance, submissions moderation and document paths. Continuous quality is
verified locally or on any external CI at the author's discretion; the test suite
runs in seconds against an in-memory database. `CONTRIBUTING.md` documents the
development setup and `CODE_OF_CONDUCT.md` the community standard.

# References
