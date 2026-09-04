# QA & Acceptance Criteria

## E2E golden journey
Create project → problem → RQ → aims → methodology → requirements → catalogue search → basket → Aim×Dataset → compatibility → data gap → candidate search → comparison → selection → note/result → abstract → report export.

## Release checks
- every route loads and is deep-linkable;
- forms persist/recover draft state;
- 20+ datasets/project works;
- relationship matrices keyboard-operable;
- geography/time/licence/identifier rules explain results;
- no source without provenance/last checked in production;
- crawler failure cannot corrupt published record;
- candidate external record cannot auto-publish;
- abstract cannot invent missing results;
- exports include dataset IDs/source URLs/versions/timestamps;
- WCAG 2.2 AA automated + manual;
- tested 1440/1024/768/390 widths;
- no mobile horizontal overflow from hard shadows;
- reduced motion respected;
- print/export preserves labels/units/provenance;
- security tests for malicious URLs/imported metadata.

## Performance targets
Common catalogue search server response <500ms under normal load; interactive page <2.5s typical broadband; background harvester outages do not break public catalogue.
