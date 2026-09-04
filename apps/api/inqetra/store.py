"""SQLAlchemy store: research-graph entities + matrices + jobs + audit.

Catalogue records are NOT duplicated here (served from versioned CSV seed).
Project<->dataset links store dataset_id + snapshot of provenance at link time.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import (Boolean, DateTime, ForeignKey, JSON, String, Text, create_engine)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker
import uuid

REPO_ROOT = Path(__file__).resolve().parents[3]


def database_url() -> str:
    url = os.getenv("DATABASE_URL", "").strip()
    if url:
        return url
    data_dir = REPO_ROOT / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{data_dir / 'app.db'}"


def _uid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Timestamped(Base):
    __abstract__ = True
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uid)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class Project(Timestamped):
    __tablename__ = "projects"
    title: Mapped[str] = mapped_column(String(300), default="Untitled project")
    geography: Mapped[str] = mapped_column(String(300), default="")
    start_date: Mapped[str] = mapped_column(String(20), default="")
    end_date: Mapped[str] = mapped_column(String(20), default="")
    domain: Mapped[str] = mapped_column(String(200), default="")
    status: Mapped[str] = mapped_column(String(40), default="active")
    problem: Mapped[str] = mapped_column(Text, default="")
    gap: Mapped[str] = mapped_column(Text, default="")
    background: Mapped[str] = mapped_column(Text, default="")
    export_path: Mapped[str] = mapped_column(String(60), default="")


class ResearchQuestion(Timestamped):
    __tablename__ = "research_questions"
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    order: Mapped[int] = mapped_column(default=0)
    text: Mapped[str] = mapped_column(Text, default="")
    question_type: Mapped[str] = mapped_column(String(120), default="")
    status: Mapped[str] = mapped_column(String(40), default="draft")


class Aim(Timestamped):
    __tablename__ = "aims"
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    order: Mapped[int] = mapped_column(default=0)
    title: Mapped[str] = mapped_column(String(300), default="")
    statement: Mapped[str] = mapped_column(Text, default="")
    expected_output: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(40), default="draft")


class Objective(Timestamped):
    __tablename__ = "objectives"
    aim_id: Mapped[str] = mapped_column(ForeignKey("aims.id", ondelete="CASCADE"), index=True)
    project_id: Mapped[str] = mapped_column(String(36), index=True, default="")
    text: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(40), default="draft")


class Hypothesis(Timestamped):
    __tablename__ = "hypotheses"
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    statement: Mapped[str] = mapped_column(Text, default="")
    null_statement: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(40), default="draft")


class Method(Timestamped):
    __tablename__ = "methods"
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(200), default="")
    purpose: Mapped[str] = mapped_column(Text, default="")
    software: Mapped[str] = mapped_column(String(200), default="")


class DatasetRequirement(Timestamped):
    __tablename__ = "dataset_requirements"
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(300), default="")
    research_role: Mapped[str] = mapped_column(String(120), default="")
    required_variables: Mapped[list] = mapped_column(JSON, default=list)
    geography: Mapped[str] = mapped_column(String(300), default="")
    start_date: Mapped[str] = mapped_column(String(20), default="")
    end_date: Mapped[str] = mapped_column(String(20), default="")
    desired_spatial_scale: Mapped[str] = mapped_column(String(120), default="")
    preferred_identifiers: Mapped[list] = mapped_column(JSON, default=list)
    preferred_formats: Mapped[list] = mapped_column(JSON, default=list)
    requirement_level: Mapped[str] = mapped_column(String(40), default="required")
    linked_aim_ids: Mapped[list] = mapped_column(JSON, default=list)
    linked_method_ids: Mapped[list] = mapped_column(JSON, default=list)


class ProjectDataset(Timestamped):
    __tablename__ = "project_datasets"
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    dataset_id: Mapped[str] = mapped_column(String(40), index=True)
    role: Mapped[str] = mapped_column(String(120), default="")
    rationale: Mapped[str] = mapped_column(Text, default="")
    priority: Mapped[str] = mapped_column(String(40), default="recommended")
    requirement_id: Mapped[str] = mapped_column(String(36), default="")
    provenance: Mapped[dict] = mapped_column(JSON, default=dict)


class MatrixLink(Timestamped):
    __tablename__ = "matrix_links"
    project_id: Mapped[str] = mapped_column(String(36), index=True)
    kind: Mapped[str] = mapped_column(String(40), index=True)  # rq_aim | aim_method | aim_dataset
    row_id: Mapped[str] = mapped_column(String(60), default="")
    col_id: Mapped[str] = mapped_column(String(60), default="")
    relationship_type: Mapped[str] = mapped_column(String(60), default="")
    rationale: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(40), default="active")
    created_by: Mapped[str] = mapped_column(String(120), default="researcher")


class Note(Timestamped):
    __tablename__ = "notes"
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    note_type: Mapped[str] = mapped_column(String(60), default="General")
    title: Mapped[str] = mapped_column(String(300), default="")
    body: Mapped[str] = mapped_column(Text, default="")
    links: Mapped[dict] = mapped_column(JSON, default=dict)


class Result(Timestamped):
    __tablename__ = "results"
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(300), default="")
    body: Mapped[str] = mapped_column(Text, default="")
    linked_aim_ids: Mapped[list] = mapped_column(JSON, default=list)


class Candidate(Timestamped):
    __tablename__ = "candidates"
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    url: Mapped[str] = mapped_column(String(1000), default="")
    source: Mapped[str] = mapped_column(String(300), default="")
    rationale: Mapped[str] = mapped_column(Text, default="")
    requirement_id: Mapped[str] = mapped_column(String(36), default="")
    status: Mapped[str] = mapped_column(String(40), default="inbox")  # inbox|resolved|rejected|curated
    licence_state: Mapped[str] = mapped_column(String(120), default="Unknown")


class KnowledgeGap(Timestamped):
    __tablename__ = "knowledge_gaps"
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    statement: Mapped[str] = mapped_column(Text, default="")
    evidence: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(40), default="open")


class Concept(Timestamped):
    __tablename__ = "concepts"
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    label: Mapped[str] = mapped_column(String(200), default="")
    kind: Mapped[str] = mapped_column(String(60), default="concept")  # exposure|outcome|mediator|control|method|dataset|context
    x: Mapped[int] = mapped_column(default=0)
    y: Mapped[int] = mapped_column(default=0)
    description: Mapped[str] = mapped_column(Text, default="")


class ConceptRelationship(Timestamped):
    __tablename__ = "concept_relationships"
    project_id: Mapped[str] = mapped_column(String(36), index=True)
    from_id: Mapped[str] = mapped_column(String(36), default="")
    to_id: Mapped[str] = mapped_column(String(36), default="")
    relation: Mapped[str] = mapped_column(String(80), default="influences")
    rationale: Mapped[str] = mapped_column(Text, default="")


class Methodology(Timestamped):
    __tablename__ = "methodologies"
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    design: Mapped[str] = mapped_column(String(200), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    ethics: Mapped[str] = mapped_column(Text, default="")
    limitations: Mapped[str] = mapped_column(Text, default="")


class VariableRequirement(Timestamped):
    __tablename__ = "variable_requirements"
    project_id: Mapped[str] = mapped_column(String(36), index=True)
    requirement_id: Mapped[str] = mapped_column(String(36), default="")
    name: Mapped[str] = mapped_column(String(200), default="")
    unit: Mapped[str] = mapped_column(String(80), default="")
    role_hint: Mapped[str] = mapped_column(String(80), default="")


class Transformation(Timestamped):
    __tablename__ = "transformations"
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    source_dataset_id: Mapped[str] = mapped_column(String(40), default="")
    target: Mapped[str] = mapped_column(String(300), default="")
    operation: Mapped[str] = mapped_column(Text, default="")
    join_strategy: Mapped[str] = mapped_column(String(300), default="")
    software: Mapped[str] = mapped_column(String(200), default="")


class AnalysisStep(Timestamped):
    __tablename__ = "analysis_steps"
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    order: Mapped[int] = mapped_column(default=0)
    stage: Mapped[str] = mapped_column(String(80), default="cleaning")  # acquisition|cleaning|transformation|joining|derived|analysis|validation|sensitivity|output
    description: Mapped[str] = mapped_column(Text, default="")
    inputs: Mapped[list] = mapped_column(JSON, default=list)
    outputs: Mapped[list] = mapped_column(JSON, default=list)
    software: Mapped[str] = mapped_column(String(200), default="")


class Contribution(Timestamped):
    __tablename__ = "contributions"
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    statement: Mapped[str] = mapped_column(Text, default="")
    kind: Mapped[str] = mapped_column(String(80), default="empirical")


class Citation(Timestamped):
    __tablename__ = "citations"
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    ctype: Mapped[str] = mapped_column(String(40), default="literature")  # literature|dataset
    dataset_id: Mapped[str] = mapped_column(String(40), default="")
    authors: Mapped[str] = mapped_column(String(500), default="")
    year: Mapped[str] = mapped_column(String(10), default="")
    title: Mapped[str] = mapped_column(String(500), default="")
    url: Mapped[str] = mapped_column(String(1000), default="")
    version: Mapped[str] = mapped_column(String(80), default="")


class ResearchKit(Timestamped):
    __tablename__ = "research_kits"
    slug: Mapped[str] = mapped_column(String(120), default="", index=True)
    title: Mapped[str] = mapped_column(String(300), default="")
    version: Mapped[str] = mapped_column(String(20), default="1.0")
    graph: Mapped[dict] = mapped_column(JSON, default=dict)  # questions/aims/methods/requirements/roles/caveats


class KitLink(Timestamped):
    __tablename__ = "kit_links"
    kit_slug: Mapped[str] = mapped_column(String(120), default="", index=True)
    from_node: Mapped[str] = mapped_column(String(200), default="")
    to_node: Mapped[str] = mapped_column(String(200), default="")
    relation: Mapped[str] = mapped_column(String(80), default="supports")


class Source(Timestamped):
    __tablename__ = "sources"
    name: Mapped[str] = mapped_column(String(300), default="")
    base_url: Mapped[str] = mapped_column(String(500), default="")
    source_type: Mapped[str] = mapped_column(String(80), default="")
    adapter: Mapped[str] = mapped_column(String(80), default="")
    trust_level: Mapped[str] = mapped_column(String(40), default="Tier C")
    active: Mapped[bool] = mapped_column(default=True)
    cadence: Mapped[str] = mapped_column(String(80), default="")
    rate_limit: Mapped[str] = mapped_column(String(80), default="1/s")
    robots_policy: Mapped[str] = mapped_column(String(200), default="respect robots.txt + terms")
    terms_notes: Mapped[str] = mapped_column(Text, default="")
    kill_switch: Mapped[bool] = mapped_column(default=False)


class SourceRun(Timestamped):
    __tablename__ = "source_runs"
    source_id: Mapped[str] = mapped_column(String(36), default="", index=True)
    status: Mapped[str] = mapped_column(String(40), default="done")  # running|done|failed
    added: Mapped[int] = mapped_column(default=0)
    changed: Mapped[int] = mapped_column(default=0)
    failed: Mapped[int] = mapped_column(default=0)
    detail: Mapped[str] = mapped_column(Text, default="")


class HarvestRecord(Timestamped):
    __tablename__ = "harvest_records"
    source_id: Mapped[str] = mapped_column(String(36), default="", index=True)
    external_id: Mapped[str] = mapped_column(String(300), default="")
    fingerprint: Mapped[str] = mapped_column(String(64), default="")
    raw: Mapped[dict] = mapped_column(JSON, default=dict)
    candidate_id: Mapped[str] = mapped_column(String(36), default="")


class DatasetCandidate(Timestamped):
    __tablename__ = "dataset_candidates"
    source_id: Mapped[str] = mapped_column(String(36), default="")
    title: Mapped[str] = mapped_column(String(500), default="")
    url: Mapped[str] = mapped_column(String(1000), default="")
    publisher: Mapped[str] = mapped_column(String(300), default="")
    licence_state: Mapped[str] = mapped_column(String(200), default="Unknown")
    provenance: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(40), default="staging")  # staging|curated|rejected


class Licence(Timestamped):
    __tablename__ = "licences"
    code: Mapped[str] = mapped_column(String(80), default="", index=True)
    name: Mapped[str] = mapped_column(String(300), default="")
    url: Mapped[str] = mapped_column(String(500), default="")
    family: Mapped[str] = mapped_column(String(80), default="Unknown")
    verified_state: Mapped[str] = mapped_column(String(80), default="source-declared")


class LinkCheck(Timestamped):
    __tablename__ = "link_checks"
    dataset_id: Mapped[str] = mapped_column(String(40), default="", index=True)
    url: Mapped[str] = mapped_column(String(1000), default="")
    final_url: Mapped[str] = mapped_column(String(1000), default="")
    http_status: Mapped[str] = mapped_column(String(20), default="")
    reachable: Mapped[bool] = mapped_column(default=False)
    error: Mapped[str] = mapped_column(String(500), default="")


class CompatRule(Timestamped):
    __tablename__ = "compatibility_rules"
    rule: Mapped[str] = mapped_column(String(60), default="", index=True)  # geography|time|granularity|identifiers|units|format|access|licence|freshness
    severity: Mapped[str] = mapped_column(String(20), default="warn")
    active: Mapped[bool] = mapped_column(default=True)
    description: Mapped[str] = mapped_column(Text, default="")


class CompatResult(Timestamped):
    __tablename__ = "compatibility_results"
    project_id: Mapped[str] = mapped_column(String(36), default="", index=True)
    requirement_id: Mapped[str] = mapped_column(String(36), default="")
    dataset_id: Mapped[str] = mapped_column(String(40), default="")
    overall: Mapped[str] = mapped_column(String(20), default="UNKNOWN")
    detail: Mapped[dict] = mapped_column(JSON, default=dict)


class User(Timestamped):
    __tablename__ = "users"
    email: Mapped[str] = mapped_column(String(300), default="")
    display_name: Mapped[str] = mapped_column(String(200), default="")
    role: Mapped[str] = mapped_column(String(40), default="researcher")


class Submission(Timestamped):
    __tablename__ = "submissions"
    url: Mapped[str] = mapped_column(String(1000), default="")
    title: Mapped[str] = mapped_column(String(500), default="")
    publisher: Mapped[str] = mapped_column(String(300), default="")
    status: Mapped[str] = mapped_column(String(40), default="pending")  # pending|accepted|rejected
    moderator_notes: Mapped[str] = mapped_column(Text, default="")


class DatasetThumb(Timestamped):
    __tablename__ = "dataset_thumbs"
    dataset_id: Mapped[str] = mapped_column(String(40), default="", index=True, unique=True)
    image_url: Mapped[str] = mapped_column(String(1500), default="")
    source: Mapped[str] = mapped_column(String(60), default="")  # og:image|twitter:image|link:image_src|img|placeholder
    note: Mapped[str] = mapped_column(Text, default="")


class AbstractDraft(Timestamped):
    __tablename__ = "abstract_drafts"
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    mode: Mapped[str] = mapped_column(String(60), default="proposal")
    word_limit: Mapped[int] = mapped_column(default=250)
    text: Mapped[str] = mapped_column(Text, default="")
    traces: Mapped[list] = mapped_column(JSON, default=list)


class Job(Timestamped):
    __tablename__ = "jobs"
    kind: Mapped[str] = mapped_column(String(80), default="export")
    project_id: Mapped[str] = mapped_column(String(36), default="")
    status: Mapped[str] = mapped_column(String(40), default="queued")  # queued|running|done|failed
    detail: Mapped[str] = mapped_column(Text, default="")
    payload: Mapped[dict] = mapped_column(JSON, default=dict)


class AuditEvent(Timestamped):
    __tablename__ = "audit_log"
    actor: Mapped[str] = mapped_column(String(120), default="local")
    action: Mapped[str] = mapped_column(String(120), default="")
    entity: Mapped[str] = mapped_column(String(120), default="")
    entity_id: Mapped[str] = mapped_column(String(60), default="")
    detail: Mapped[str] = mapped_column(Text, default="")


_engine = None
_Session = None


def engine():
    global _engine
    if _engine is None:
        from sqlalchemy.pool import NullPool
        url = database_url()
        connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
        # Route handlers open sessions directly (no Depends teardown) and rely on
        # GC to return connections; a finite QueuePool then deadlocks once capped.
        # NullPool opens a fresh connection per checkout — no cap, no stall.
        _engine = create_engine(url, poolclass=NullPool,
                                **({"connect_args": connect_args} if connect_args else {}))
        Base.metadata.create_all(_engine)
        from sqlalchemy import text
        try:  # additive migration for existing databases (v0.2.2 document paths)
            with _engine.begin() as c:
                c.execute(text("ALTER TABLE projects ADD COLUMN export_path VARCHAR(60) DEFAULT ''"))
        except Exception:  # column already exists
            pass
    return _engine


def session():
    global _Session
    if _Session is None:
        from sqlalchemy.orm import sessionmaker as _sm
        _Session = _sm(bind=engine(), expire_on_commit=False)
    return _Session()


def reset_engine_for_tests(tmp_path: str):
    global _engine, _Session
    _engine = None
    _Session = None
    os.environ["DATABASE_URL"] = f"sqlite:///{tmp_path}/test.db"
    return session()
