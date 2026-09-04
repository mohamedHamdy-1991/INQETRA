"""Explicit acceptance-filter mapping (D-05).

The seed stores one `domain` per row; acceptance requires 12 facets to work.
This map matches against domain+subdomain+title+research_roles WITHOUT mutating
stored metadata. Responses include `filter_matched_by` for transparency.
"""
from __future__ import annotations

FILTERS: dict[str, list[str]] = {
    "climate": ["climat", "haduk", "haduk-grid", "ukcp", "met office", "ceda"],
    "weather": ["weather", "haduk", "met office", "rainfall", "temperature", "midas"],
    "climate change": ["climate change", "ukcp", "projection", "net zero", "carbon", "emissions"],
    "environment": ["environment", "defra", "environment agency", "ecolog", "biodiversity"],
    "air quality": ["air quality", "aqm", "aurn", "defra air", "emissions"],
    "flooding": ["flood", "hazard", "risk of flooding", "fluvial", "coastal erosion"],
    "buildings": ["build", "dwelling", "epc", "property", "housing", "stock"],
    "housing": ["hous", "dwelling", "epc", "rent", "affordability", "homeless"],
    "building performance": ["epc", "energy performance", "dec ", "retrofit", "overheating", "sap"],
    "energy/carbon": ["energy", "carbon", "emissions", "electricity", "gas", "epc", "retrofit", "net zero"],
    "planning": ["planning", "land use", "constraint", "brownfield", "conservation area", "listed build"],
    "geospatial": ["geograph", "boundary", "uprn", "os ", "ordnance", "gis", "postcode", "lsoa", "msoa", "oa "],
}


def haystack(row: dict) -> str:
    return " ".join([row.get("domain", ""), row.get("subdomain", ""),
                     row.get("title", ""), row.get("research_roles", ""),
                     row.get("methods_supported", "")]).lower()


def matches(row: dict, facet: str) -> tuple[bool, str]:
    keys = FILTERS.get(facet.lower(), [])
    hay = haystack(row)
    for k in keys:
        if k in hay:
            return True, k
    return False, ""
