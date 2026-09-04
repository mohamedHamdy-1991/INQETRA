# API Specification

## Catalogue
GET `/api/v1/datasets`; GET `/datasets/{slug}`; GET `/datasets/{id}/variables`; GET `/datasets/{id}/related`; POST `/datasets/compare`; GET `/publishers`; GET `/sources`; GET `/geographies/search`.

## Projects
POST `/projects`; GET/PATCH `/projects/{id}`; CRUD `/projects/{id}/questions`; `/aims`; `/objectives`; `/methods`; `/requirements`; `/notes`; `/results`; `/datasets`.

## Relationships
GET/PATCH `/projects/{id}/matrices/rq-aim`; `/aim-method`; `/aim-dataset`.

## Evaluation
POST `/projects/{id}/evaluate`; GET `/projects/{id}/compatibility`; GET `/projects/{id}/gaps`; POST `/projects/{id}/requirements/{rid}/find-data`.

## Candidate inbox
GET `/projects/{id}/candidates`; POST `/candidates/{id}/resolve`; POST `/candidates/{id}/reject`.

## Abstract/reports
POST `/projects/{id}/abstract/draft`; GET `/projects/{id}/abstract/traces`; POST `/exports`; GET `/projects/{id}/report-model`.

## Admin
CRUD sources; run harvester; source-run logs; candidate moderation; duplicate merge; licence queue; broken links; kit editor; rule editor; audit log.

All endpoints return typed error codes and provenance where relevant. Publish OpenAPI automatically.
