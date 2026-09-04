#!/usr/bin/env python3
"""Apply the audited climate, environment and built-environment seed upgrade.

The script is deliberately idempotent. It preserves all existing records, fixes
only known broken landing-page links by downgrading them to working official
collection links, appends curated records, and regenerates the JSON and Markdown
representations from the CSV authority.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CSV_PATH = DATA / "datasets_seed.csv"
JSON_PATH = DATA / "datasets_seed.json"
MD_PATH = DATA / "DATASET_CATALOGUE.md"
CHECKED = "2026-09-04"

PLANNING_COLLECTION = "https://www.planning.data.gov.uk/dataset/"
OS_COLLECTION = "https://www.ordnancesurvey.co.uk/products/open-data"
ENV_COLLECTION = "https://environment.data.gov.uk/"
BUS_COLLECTION = "https://www.gov.uk/government/collections/bus-open-data-service"

REPAIRS = {
    "inq-0016": (PLANNING_COLLECTION, "official_collection", "collection_record_link_checked", "Exact Planning Data slug returned 404 on 2026-09-04; retained as a collection record pending resolver confirmation."),
    "inq-0026": (PLANNING_COLLECTION, "official_collection", "collection_record_link_checked", "Exact Planning Data slug returned 404 on 2026-09-04; retained as a collection record pending resolver confirmation."),
    "inq-0043": (PLANNING_COLLECTION, "official_collection", "collection_record_link_checked", "Exact Planning Data slug returned 404 on 2026-09-04; retained as a collection record pending resolver confirmation."),
    "inq-0044": (PLANNING_COLLECTION, "official_collection", "collection_record_link_checked", "Exact Planning Data slug returned 404 on 2026-09-04; retained as a collection record pending resolver confirmation."),
    "inq-0106": (PLANNING_COLLECTION, "official_collection", "collection_record_link_checked", "Exact Planning Data slug returned 404 on 2026-09-04; retained as a collection record pending resolver confirmation."),
    "inq-0110": (PLANNING_COLLECTION, "official_collection", "collection_record_link_checked", "Exact Planning Data slug returned 404 on 2026-09-04; retained as a collection record pending resolver confirmation."),
    "inq-0568": (OS_COLLECTION, "official_collection", "collection_record_link_checked", "Legacy product URL returned 404 on 2026-09-04; official OpenData collection link substituted pending current product resolution."),
    "inq-0571": (OS_COLLECTION, "official_collection", "collection_record_link_checked", "Legacy product URL returned 404 on 2026-09-04; official OpenData collection link substituted pending current product resolution."),
    "inq-0583": (OS_COLLECTION, "official_collection", "collection_record_link_checked", "Legacy product URL returned 404 on 2026-09-04; official OpenData collection link substituted pending current product resolution."),
    "inq-0616": (ENV_COLLECTION, "official_collection", "collection_record_link_checked", "Portal root substituted after legacy dataset URL returned 404 on 2026-09-04; resolve a current dataset UUID before publication."),
    "inq-0617": (ENV_COLLECTION, "official_collection", "collection_record_link_checked", "Portal root substituted after legacy dataset URL returned 404 on 2026-09-04; resolve a current dataset UUID before publication."),
    "inq-0618": (ENV_COLLECTION, "official_collection", "collection_record_link_checked", "Portal root substituted after legacy dataset URL returned 404 on 2026-09-04; resolve a current dataset UUID before publication."),
    "inq-0619": (ENV_COLLECTION, "official_collection", "collection_record_link_checked", "Portal root substituted after legacy dataset URL returned 404 on 2026-09-04; resolve a current dataset UUID before publication."),
    "inq-0620": (ENV_COLLECTION, "official_collection", "collection_record_link_checked", "Portal root substituted after legacy dataset URL returned 404 on 2026-09-04; resolve a current dataset UUID before publication."),
    "inq-0621": (ENV_COLLECTION, "official_collection", "collection_record_link_checked", "Portal root substituted after legacy dataset URL returned 404 on 2026-09-04; resolve a current dataset UUID before publication."),
    "inq-0622": (ENV_COLLECTION, "official_collection", "collection_record_link_checked", "Portal root substituted after legacy dataset URL returned 404 on 2026-09-04; resolve a current dataset UUID before publication."),
    "inq-0623": (ENV_COLLECTION, "official_collection", "collection_record_link_checked", "Portal root substituted after legacy dataset URL returned 404 on 2026-09-04; resolve a current dataset UUID before publication."),
    "inq-0624": (ENV_COLLECTION, "official_collection", "collection_record_link_checked", "Portal root substituted after legacy dataset URL returned 404 on 2026-09-04; resolve a current dataset UUID before publication."),
    "inq-0625": (ENV_COLLECTION, "official_collection", "collection_record_link_checked", "Portal root substituted after legacy dataset URL returned 404 on 2026-09-04; resolve a current dataset UUID before publication."),
    "inq-0626": (ENV_COLLECTION, "official_collection", "collection_record_link_checked", "Portal root substituted after legacy dataset URL returned 404 on 2026-09-04; resolve a current dataset UUID before publication."),
    "inq-0627": (ENV_COLLECTION, "official_collection", "collection_record_link_checked", "Portal root substituted after legacy dataset URL returned 404 on 2026-09-04; resolve a current dataset UUID before publication."),
    "inq-0698": (BUS_COLLECTION, "official_collection", "collection_record_link_checked", "The bus-data landing page blocked the automated health check on 2026-09-04; a GOV.UK collection page is used pending service-specific resolution."),
    "inq-0699": (BUS_COLLECTION, "official_collection", "collection_record_link_checked", "The bus-data landing page blocked the automated health check on 2026-09-04; a GOV.UK collection page is used pending service-specific resolution."),
    "inq-0700": (BUS_COLLECTION, "official_collection", "collection_record_link_checked", "The bus-data landing page blocked the automated health check on 2026-09-04; a GOV.UK collection page is used pending service-specific resolution."),
}

FIELDS = ["id", "title", "publisher", "source_portal", "country", "uk_nation", "domain", "subdomain", "research_roles", "methods_supported", "spatial_scale", "temporal_resolution", "coverage", "formats", "access_type", "licence", "authority_level", "landing_url", "link_type", "verification_state", "variables", "notes", "last_catalogue_review"]


def record(num: int, title: str, publisher: str, portal: str, nation: str, domain: str, subdomain: str, roles: str, methods: str, scale: str, temporal: str, coverage: str, formats: str, access: str, licence: str, url: str, link_type: str, variables: str, notes: str) -> dict[str, str]:
    return {"id": f"inq-{num:04d}", "title": title, "publisher": publisher, "source_portal": portal, "country": "United Kingdom", "uk_nation": nation, "domain": domain, "subdomain": subdomain, "research_roles": roles, "methods_supported": methods, "spatial_scale": scale, "temporal_resolution": temporal, "coverage": coverage, "formats": formats, "access_type": access, "licence": licence, "authority_level": "Official", "landing_url": url, "link_type": link_type, "verification_state": "official_landing_page_link_checked", "variables": variables, "notes": notes, "last_catalogue_review": CHECKED}


ADDITIONS = [
    record(738, "Scottish House Condition Survey", "Scottish Government", "gov.scot", "Scotland", "Buildings & Housing", "Housing condition and energy efficiency", "Outcome | Exposure | Context", "Survey analysis | Descriptive statistics | Small-area analysis", "Dwelling / local authority", "Annual", "Scotland", "HTML | XLSX", "Open", "Open Government Licence", "https://www.gov.scot/collections/scottish-house-condition-survey/", "official_collection", "dwelling condition | energy efficiency | fuel poverty | disrepair", "Official collection; landing page link checked 2026-09-04. Microdata access is separately controlled."),
    record(739, "Scottish House Condition Survey Local Authority Tables 2022-2024", "Scottish Government", "gov.scot", "Scotland", "Buildings & Housing", "Housing condition local statistics", "Outcome | Context | Validation/reference", "Descriptive statistics | Spatial comparison", "Local authority", "Annual", "Scotland", "HTML | XLSX", "Open", "Open Government Licence", "https://www.gov.scot/publications/scottish-house-condition-survey-local-authority-tables-2022-2024/", "direct_dataset", "housing stock | insulation | energy efficiency | fuel poverty | damp | disrepair", "Official statistical tables; landing page link checked 2026-09-04."),
    record(740, "Welsh Housing Conditions Survey", "Welsh Government", "GOV.WALES", "Wales", "Buildings & Housing", "Housing condition and energy efficiency", "Outcome | Exposure | Context", "Survey analysis | Descriptive statistics", "Dwelling / Wales", "Survey wave", "Wales", "HTML | XLSX", "Open", "Open Government Licence", "https://www.gov.wales/welsh-housing-conditions-survey", "official_collection", "housing condition | energy efficiency | fuel poverty | hazards", "Official survey collection; landing page link checked 2026-09-04."),
    record(741, "Energy performance and the presence of hazards in dwellings", "Welsh Government", "StatsWales", "Wales", "Buildings & Housing", "Housing energy and health hazards", "Outcome | Exposure | Context", "Descriptive statistics | Spatial comparison", "Local authority / Wales", "Survey wave", "Wales", "HTML | CSV", "Open", "Open Government Licence", "https://stats.gov.wales/en-GB/491241a0-aaaf-48bb-ad46-4a4ea2e3e792/start", "direct_dataset", "energy performance | repair cost | fuel poverty | HHSRS", "StatsWales dataset; landing page link checked 2026-09-04."),
    record(742, "Welsh Index of Multiple Deprivation 2025 housing-domain indicators", "Welsh Government", "StatsWales", "Wales", "Housing Vulnerability", "Housing affordability, condition and energy", "Outcome | Predictor | Context", "Deprivation analysis | Spatial comparison", "LSOA / local authority", "Static", "Wales", "HTML | CSV", "Open", "Open Government Licence", "https://stats.gov.wales/en-GB/8c4e387a-d221-4a24-9fd4-50bdaacbe273", "direct_dataset", "overcrowding | housing affordability | poor-quality housing | SAP | hazards | disrepair", "StatsWales dataset; landing page link checked 2026-09-04."),
    record(743, "UK greenhouse gas emissions: local authority and regional", "Department for Energy Security and Net Zero", "National Data Library", "UK", "Energy & Carbon", "Local and regional emissions", "Outcome | Baseline | Context", "Carbon accounting | Spatial comparison | Trend analysis", "Local authority / region", "Annual", "United Kingdom", "CSV | XLSX", "Open", "Open Government Licence", "https://www.data.gov.uk/dataset/723c243d-2f1a-4d27-8b61-cdb93e5b10ff/local_authority_carbon_dioxide_emissions", "direct_dataset", "greenhouse gas emissions | sector | local authority", "Official catalogue record; landing page link checked 2026-09-04."),
    record(744, "UK climate projections", "Met Office", "National Data Library", "UK", "Climate Change", "Climate projection collection", "Scenario | Exposure | Future projection", "Climate scenario analysis | Downscaling | Risk assessment", "Raster cell / region", "Projection period", "United Kingdom", "XLSX | maps", "Open", "Licence stated by publisher", "https://www.data.gov.uk/collections/environment/climate-projections", "official_collection", "temperature | precipitation | sea-level rise | climate scenarios", "Official collection page; landing page link checked 2026-09-04. Confirm resource-specific terms before reuse."),
    record(745, "UKCP18 convection-permitting rainfall-event summaries", "Environmental Information Data Centre", "National Data Library", "Great Britain", "Climate Change", "Extreme rainfall projections", "Exposure | Scenario | Future projection", "Climate risk analysis | Extreme-event analysis", "Raster cell / event", "Projection period", "Mainland Great Britain", "ZIP | CSV", "Open", "Licence stated by publisher", "https://www.data.gov.uk/dataset/f4dc2240-1f45-4834-86fb-75fce65edc85/uk-climate-projections-2018-ukcp18-convection-permitting-model-cpm-and-empirical-copu-2060-2080", "direct_dataset", "peak daily rainfall | event summaries | ensemble member", "Official catalogue record; landing page link checked 2026-09-04."),
    record(746, "UKCP18 climate projections and clay shrink-swell susceptibility", "British Geological Survey", "National Data Library", "Great Britain", "Climate Change", "Climate-related ground hazard", "Exposure | Scenario | Future projection", "GIS | Hazard mapping | Risk assessment", "Raster cell", "Projection period", "Great Britain", "GIS | raster", "Commercial", "Licence stated by publisher", "https://www.data.gov.uk/dataset/c90f8455-5ed7-4170-946a-d0de97acf9f9/ukcp18-climate-projections-and-clay-shrink-swell-susceptibility-premium", "direct_dataset", "clay shrink-swell susceptibility | climate scenario", "Official catalogue record; premium access/reuse terms must be checked before use."),
    record(747, "UK Air Quality Measurements Bulk Data Download", "Department for Environment, Food and Rural Affairs", "National Data Library", "UK", "Air Quality", "Monitoring observations", "Exposure | Outcome | Validation/reference", "Time-series analysis | Exposure assessment", "Monitoring station", "Hourly | daily | annual", "United Kingdom", "XML | CSV", "Open", "Open Government Licence", "https://www.data.gov.uk/dataset/bfaf890c-0ebc-42f7-954d-9cde251902a2/uk-air-quality-measurements-bulk-data-download", "direct_dataset", "PM10 | PM2.5 | NO2 | O3 | SO2 | monitoring station", "Official catalogue record; landing page link checked 2026-09-04."),
    record(748, "Air Quality Statistics", "Department for Environment, Food and Rural Affairs", "National Data Library", "UK", "Air Quality", "National air pollution statistics", "Exposure | Outcome | Context", "Trend analysis | Environmental health analysis", "Monitoring station / UK", "Annual", "United Kingdom", "HTML | CSV", "Open", "Open Government Licence", "https://www.data.gov.uk/dataset/90768ec4-9e1d-43be-bdc0-36e47cc42d9a/air_quality_statistics", "direct_dataset", "PM10 | PM2.5 | NO2 | O3 | SO2", "Official catalogue record; landing page link checked 2026-09-04."),
    record(749, "Air quality", "Department for Environment, Food and Rural Affairs", "National Data Library", "UK", "Air Quality", "National air quality collection", "Exposure | Outcome | Context", "Exposure assessment | Time-series analysis", "Monitoring station / UK", "Hourly | daily | annual", "United Kingdom", "HTML | CSV", "Open", "Open Government Licence", "https://www.data.gov.uk/collections/environment/air-quality", "official_collection", "air pollution | monitoring stations | hourly concentrations", "Official collection page; landing page link checked 2026-09-04."),
    record(750, "ICP Forests Level II UK air-quality data", "Forestry Commission", "Defra Data Services Platform", "UK", "Environment", "Forest and air-quality monitoring", "Exposure | Validation/reference | Context", "Environmental monitoring | Time-series analysis", "Monitoring plot", "Every four weeks", "United Kingdom", "ZIP | GIS", "Open", "Open Government Licence", "https://environment.data.gov.uk/dataset/ad0794ed-3184-4765-b173-b31959ef8272", "direct_dataset", "ozone | ammonia | nitrogen dioxide | forest plot", "Official dataset record; landing page link checked 2026-09-04."),
    record(751, "CS-N0W projected river-flow modelling outputs", "Environment Agency", "Defra Data Services Platform", "UK", "Flooding & Hazards", "Future hydrological projections", "Scenario | Exposure | Future projection", "Hydrological modelling | Climate-risk analysis", "River reach / catchment", "Projection period", "United Kingdom", "HTML | model outputs", "Open", "Licence stated by publisher", "https://environment.data.gov.uk/future-water/portal/modelling", "official_collection", "river flow | climate projection | abstraction | discharge", "Official modelling portal; landing page link checked 2026-09-04. Resolve individual model-output resources before production publication."),
]


def render_markdown(rows: list[dict[str, str]]) -> str:
    lines = ["# INQETRA Dataset Seed Catalogue", "", f"Generated: {CHECKED}. Records: **{len(rows)}**.", "", "This is a **seed metadata catalogue**, not a mirrored data store. Every landing page was HTTP-checked on 2026-09-04; the reproducible result is `link_health/catalogue_link_health.csv`. A reachable landing page does not certify a download, metadata field, licence or reuse right. The `verification_state` and `link_type` fields are mandatory. The ingestion agent must re-check resource URLs before publishing a record to production.", "", "| ID | Dataset | Publisher | Domain | Coverage | Access | Link | State |", "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        safe = lambda value: value.replace("|", "&#124;")
        lines.append(f"| {safe(r['id'])} | {safe(r['title'])} | {safe(r['publisher'])} | {safe(r['domain'])} | {safe(r['coverage'])} | {safe(r['access_type'])} | [Official source]({r['landing_url']}) | {safe(r['verification_state'])} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    with CSV_PATH.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    by_id = {row["id"]: row for row in rows}
    for record_id, (url, link_type, state, note) in REPAIRS.items():
        row = by_id[record_id]
        row.update({"landing_url": url, "link_type": link_type, "verification_state": state, "notes": note, "last_catalogue_review": CHECKED})
    titles = {row["title"].casefold() for row in rows}
    for addition in ADDITIONS:
        if addition["title"].casefold() not in titles:
            rows.append(addition)
            titles.add(addition["title"].casefold())
    with CSV_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    JSON_PATH.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    MD_PATH.write_text(render_markdown(rows), encoding="utf-8")
    print(f"Wrote {len(rows)} records to CSV, JSON and Markdown.")


if __name__ == "__main__":
    main()
