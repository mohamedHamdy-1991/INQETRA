"use client";
import Link from "next/link";
import { useRef, useState } from "react";
import { useFetch } from "../../../../hooks/hooks";
import { api } from "../../../../lib/api";

const SECTIONS: [string, string][] = [
  ["problem", "01 Research Problem"], ["questions", "02 Research Questions"],
  ["aims", "03 Aims & Objectives"], ["hypotheses", "04 Hypotheses"],
  ["kgaps", "05 Knowledge Gaps"], ["concepts", "05B Concept Map"],
  ["methods", "06 Methodology"], ["transformations", "06B Transformations"],
  ["requirements", "07 Dataset Requirements"], ["basket", "08 Dataset Basket"],
  ["matrix", "09 Aim × Dataset Matrix"], ["analysis", "10 Analysis Steps"],
  ["notes", "11 Notes"], ["citations", "12 Literature / Citations"],
  ["gaps", "13 Data Gaps"], ["contrib", "13B Contributions"],
  ["abstract", "14 Abstract Builder"], ["report", "15 Research Data Plan"], ["export", "16 Export"],
];

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8123";

function Field({ label, value, onChange, textarea }: { label: string; value: string; onChange: (v: string) => void; textarea?: boolean }) {
  return (
    <label className="f">{label}
      {textarea
        ? <textarea value={value} onChange={(e) => onChange(e.target.value)} />
        : <input value={value} onChange={(e) => onChange(e.target.value)} />}
    </label>
  );
}

function Select({ label, value, options, onChange }: { label: string; value: string; options: string[]; onChange: (v: string) => void }) {
  return (
    <label className="f">{label}
      <select value={value} onChange={(e) => onChange(e.target.value)}>
        {options.map((o) => <option key={o} value={o}>{o || "— choose —"}</option>)}
      </select>
    </label>
  );
}

export default function Studio({ params }: { params: { id: string } }) {
  const id = params.id;
  const proj = useFetch(() => api.project(id), [id]);
  const [form, setForm] = useState<Record<string, string>>({});
  const [msg, setMsg] = useState("");
  const set = (k: string, v: string) => setForm((f) => ({ ...f, [k]: v }));

  async function call<T>(fn: () => Promise<T>, ok = "Saved.") {
    try { await fn(); setMsg(ok); window.location.reload(); }
    catch (e) { setMsg(String(e)); }
  }

  if (proj.loading) return <p role="status">Loading studio…</p>;
  if (proj.error) return <p className="warn" role="alert">{String(proj.error)}</p>;
  const p = proj.data;

  return (
    <div>
      <p><Link href="/projects">← Projects</Link> · <strong>{p.title}</strong> · readiness {p.readiness.complete}/{p.readiness.of} ({p.readiness.note})</p>
      <h1>RESEARCH STUDIO</h1>
      <div className="studio">
        <nav className="subrail" aria-label="Studio sections"><ol>{SECTIONS.map(([a, l]) => <li key={a}><a href={`#${a}`}>{l}</a></li>)}</ol></nav>
        <div>
          <section className="block" id="problem" tabIndex={-1}>
            <h2>01 Research Problem</h2>
            <Field label="Background" textarea value={form.background ?? p.background} onChange={(v) => set("background", v)} />
            <Field label="Problem statement" textarea value={form.problem ?? p.problem} onChange={(v) => set("problem", v)} />
            <Field label="Knowledge gap" textarea value={form.gap ?? p.gap} onChange={(v) => set("gap", v)} />
            <Field label="Geography" value={form.geography ?? p.geography} onChange={(v) => set("geography", v)} />
            <button className="nb-btn" onClick={() => call(() => api.patchProject(id, { background: form.background ?? p.background, problem: form.problem ?? p.problem, gap: form.gap ?? p.gap, geography: form.geography ?? p.geography }))}>SAVE PROBLEM</button>
          </section>

          <section className="block" id="questions" tabIndex={-1}>
            <h2>02 Research Questions</h2>
            {(p.questions || []).map((q: Record<string, string>) => <p key={q.id}>• {q.text}</p>)}
            <Field label="New question" textarea value={form.q || ""} onChange={(v) => set("q", v)} />
            <button className="nb-btn" onClick={() => call(() => api.post(`/api/v1/projects/${id}/questions`, { text: form.q }))}>ADD QUESTION</button>
          </section>

          <section className="block" id="aims" tabIndex={-1}>
            <h2>03 Aims & Objectives</h2>
            {(p.aims || []).map((a: Record<string, string>) => <p key={a.id}>• <strong>{a.title}</strong> — {a.statement}</p>)}
            <Field label="Aim title" value={form.aim || ""} onChange={(v) => set("aim", v)} />
            <Field label="Aim statement" textarea value={form.aimstmt || ""} onChange={(v) => set("aimstmt", v)} />
            <button className="nb-btn" onClick={() => call(() => api.post(`/api/v1/projects/${id}/aims`, { title: form.aim, statement: form.aimstmt }))}>ADD AIM</button>
          </section>

          <section className="block" id="hypotheses" tabIndex={-1}>
            <h2>04 Hypotheses</h2>
            {(p.hypotheses || []).map((h: Record<string, string>) => <p key={h.id}>• {h.statement}</p>)}
            <Field label="Hypothesis" textarea value={form.hyp || ""} onChange={(v) => set("hyp", v)} />
            <button className="nb-btn" onClick={() => call(() => api.post(`/api/v1/projects/${id}/hypotheses`, { statement: form.hyp }))}>ADD HYPOTHESIS</button>
          </section>

          <section className="block" id="kgaps" tabIndex={-1}>
            <h2>05 Knowledge Gaps</h2>
            {(p.kgaps || []).map((g: Record<string, string>) => (
              <p key={g.id}>• <strong>{g.statement}</strong>{g.evidence ? ` — ${g.evidence}` : ""} <span className="tag">[{g.status}]</span></p>
            ))}
            {!((p.kgaps || []).length) && <p>No knowledge gaps recorded yet.</p>}
            <Field label="Gap statement" textarea value={form.kgap || ""} onChange={(v) => set("kgap", v)} />
            <Field label="Evidence / source of the gap" textarea value={form.kgapev || ""} onChange={(v) => set("kgapev", v)} />
            <button className="nb-btn" onClick={() => call(() => api.post(`/api/v1/projects/${id}/kgaps`, { statement: form.kgap, evidence: form.kgapev }))}>ADD GAP</button>
          </section>

          <section className="block" id="concepts" tabIndex={-1}>
            <h2>05B Concept Map</h2>
            <p>Drag nodes to arrange; every position, node and edge is stored.</p>
            <ConceptBoard projectId={id} nodes={p.concepts || []} edges={p.edges || []} onMsg={setMsg} />
            <div className="grid">
              <Field label="New node label" value={form.clabel || ""} onChange={(v) => set("clabel", v)} />
              <Select label="Node kind" value={form.ckind || ""} options={["", "exposure", "outcome", "mediator", "control", "method", "dataset", "context"]} onChange={(v) => set("ckind", v)} />
              <button className="nb-btn" onClick={() => call(() => api.post(`/api/v1/projects/${id}/concepts`, { label: form.clabel, kind: form.ckind || "concept" }))}>ADD NODE</button>
            </div>
            <EdgeForm projectId={id} nodes={p.concepts || []} call={call} />
          </section>

          <section className="block" id="methods" tabIndex={-1}>
            <h2>06 Methodology & Methods</h2>
            <MethodologyForm projectId={id} meth={p.methodology} call={call} />
            {(p.methods || []).map((m: Record<string, string>) => <p key={m.id}>• <strong>{m.name}</strong> — {m.purpose}</p>)}
            <Field label="Method name" value={form.method || ""} onChange={(v) => set("method", v)} />
            <Field label="Purpose" value={form.purpose || ""} onChange={(v) => set("purpose", v)} />
            <button className="nb-btn" onClick={() => call(() => api.post(`/api/v1/projects/${id}/methods`, { name: form.method, purpose: form.purpose }))}>ADD METHOD</button>
          </section>

          <section className="block" id="transformations" tabIndex={-1}>
            <h2>06B Transformations & Joins</h2>
            {(p.transformations || []).map((t: Record<string, string>) => (
              <p key={t.id}>• <strong>{t.target}</strong> ← {t.source_dataset_id}: {t.operation} [{t.join_strategy} · {t.software}]</p>
            ))}
            {!((p.transformations || []).length) && <p>No transformations recorded yet.</p>}
            <Field label="Source dataset ID (e.g. inq-0001)" value={form.tsrc || ""} onChange={(v) => set("tsrc", v)} />
            <Field label="Target table / layer" value={form.ttgt || ""} onChange={(v) => set("ttgt", v)} />
            <Field label="Operation" textarea value={form.top || ""} onChange={(v) => set("top", v)} />
            <div className="grid">
              <Field label="Join strategy" value={form.tjoin || ""} onChange={(v) => set("tjoin", v)} />
              <Field label="Software" value={form.tsoft || ""} onChange={(v) => set("tsoft", v)} />
            </div>
            <button className="nb-btn" onClick={() => call(() => api.post(`/api/v1/projects/${id}/transformations`, { source_dataset_id: form.tsrc, target: form.ttgt, operation: form.top, join_strategy: form.tjoin, software: form.tsoft }))}>ADD TRANSFORMATION</button>
          </section>

          <section className="block" id="requirements" tabIndex={-1}>
            <h2>07 Dataset Requirements (requirements first)</h2>
            {(p.requirements || []).map((r: Record<string, string>) => <p key={r.id}>• <strong>{r.title}</strong> ({r.research_role}) — {r.geography}</p>)}
            <Field label="Requirement title" value={form.req || ""} onChange={(v) => set("req", v)} />
            <Field label="Research role" value={form.role || ""} onChange={(v) => set("role", v)} />
            <Field label="Geography" value={form.rgeo || p.geography || ""} onChange={(v) => set("rgeo", v)} />
            <Field label="Variables (comma-separated)" value={form.vars || ""} onChange={(v) => set("vars", v)} />
            <button className="nb-btn" onClick={() => call(() => api.post(`/api/v1/projects/${id}/requirements`, {
              title: form.req, research_role: form.role || "Climate / exposure", geography: form.rgeo || p.geography,
              required_variables: (form.vars || "").split(",").map((s) => s.trim()).filter(Boolean),
              linked_aim_ids: (p.aims || []).map((a: Record<string, string>) => a.id),
            }))}>ADD REQUIREMENT</button>
          </section>

          <section className="block" id="basket" tabIndex={-1}>
            <h2>08 Dataset Basket</h2>
            {(p.basket || []).map((b: Record<string, string>) => <p key={b.id}>• {b.dataset_id} — {b.rationale} [{b.priority}]</p>)}
            <Field label="Add dataset ID (e.g. inq-0001)" value={form.dsid || ""} onChange={(v) => set("dsid", v)} />
            <Field label="Rationale (why it belongs)" textarea value={form.rat || ""} onChange={(v) => set("rat", v)} />
            <button className="nb-btn" onClick={() => call(() => api.post(`/api/v1/projects/${id}/basket`, { dataset_id: form.dsid, rationale: form.rat }))}>ADD TO PROJECT BASKET</button>
            <p><Link href="/datasets">Discover datasets →</Link> · <Link href="/basket/report">BASKET DATA REPORT →</Link></p>
          </section>

          <section className="block" id="matrix" tabIndex={-1}>
            <h2>09 Aim × Dataset Matrix</h2>
            <MatrixEditor projectId={id} aims={p.aims || []} basket={p.basket || []} cells={p.matrices || []} />
          </section>

          <section className="block" id="analysis" tabIndex={-1}>
            <h2>10 Analysis Steps (ordered pipeline)</h2>
            {(p.steps || []).map((s: Record<string, unknown>) => (
              <p key={s.id as string}>• <span className="tag">[{String(s.order)}] {String(s.stage)}</span> {String(s.description)}</p>
            ))}
            {!((p.steps || []).length) && <p>No analysis steps yet — they are appended in order.</p>}
            <Select label="Stage" value={form.sstage || "cleaning"} options={["acquisition", "cleaning", "transformation", "joining", "derived", "analysis", "validation", "sensitivity", "output"]} onChange={(v) => set("sstage", v)} />
            <Field label="Step description" textarea value={form.sdesc || ""} onChange={(v) => set("sdesc", v)} />
            <button className="nb-btn" onClick={() => call(() => api.post(`/api/v1/projects/${id}/steps`, { stage: form.sstage || "cleaning", description: form.sdesc }))}>ADD STEP</button>
          </section>

          <section className="block" id="notes" tabIndex={-1}>
            <h2>11 Notes</h2>
            {(p.notes || []).slice(0, 5).map((n: Record<string, string>) => <p key={n.id}>• [{n.note_type}] {n.title}</p>)}
            <p><Link className="nb-btn secondary" href={`/projects/${id}/notes`}>OPEN NOTEBOOK</Link></p>
          </section>

          <section className="block" id="citations" tabIndex={-1}>
            <h2>12 Literature / Citations</h2>
            <CitList id={id} />
            <div className="grid">
              <Field label="Authors (Surname, Initial)" value={form.cau || ""} onChange={(v) => set("cau", v)} />
              <Field label="Year" value={form.cyr || ""} onChange={(v) => set("cyr", v)} />
            </div>
            <Field label="Title" value={form.cti || ""} onChange={(v) => set("cti", v)} />
            <Field label="URL" value={form.curl || ""} onChange={(v) => set("curl", v)} />
            <button className="nb-btn" onClick={() => call(() => api.post(`/api/v1/projects/${id}/citations`, { ctype: "literature", authors: form.cau, year: form.cyr, title: form.cti, url: form.curl }))}>ADD CITATION</button>
          </section>

          <section className="block" id="gaps" tabIndex={-1}>
            <h2>13 Data Gaps</h2>
            <p><Link className="nb-btn secondary" href={`/projects/${id}/gaps`}>OPEN GAP RADAR</Link> <Link className="nb-btn secondary" href={`/projects/${id}/candidates`}>CANDIDATE INBOX</Link></p>
          </section>

          <section className="block" id="contrib" tabIndex={-1}>
            <h2>13B Contributions</h2>
            {(p.contributions || []).map((k: Record<string, string>) => <p key={k.id}>• <span className="tag">[{k.kind}]</span> {k.statement}</p>)}
            {!((p.contributions || []).length) && <p>No contributions recorded yet.</p>}
            <Field label="Contribution statement" textarea value={form.contrib || ""} onChange={(v) => set("contrib", v)} />
            <Select label="Kind" value={form.contribkind || "empirical"} options={["empirical", "methodological", "theoretical", "policy", "replication"]} onChange={(v) => set("contribkind", v)} />
            <button className="nb-btn" onClick={() => call(() => api.post(`/api/v1/projects/${id}/contributions`, { statement: form.contrib, kind: form.contribkind || "empirical" }))}>ADD CONTRIBUTION</button>
          </section>

          <section className="block" id="abstract" tabIndex={-1}>
            <h2>14 Abstract Builder</h2>
            <p>Evidence-traced; results require researcher-entered Result objects — nothing is fabricated.</p>
            <p><Link className="nb-btn secondary" href={`/projects/${id}/abstract`}>OPEN ABSTRACT BUILDER</Link></p>
          </section>

          <section className="block" id="report" tabIndex={-1}>
            <h2>15 Research Data Plan</h2>
            <p><Link className="nb-btn secondary" href={`/projects/${id}/report`}>OPEN REPORT</Link></p>
          </section>

          <section className="block" id="export" tabIndex={-1}>
            <h2>16 Export</h2>
            <p>
              <a className="nb-btn" href={`${API}/api/v1/projects/${id}/export?format=markdown`} download>DOWNLOAD MARKDOWN</a>{" "}
              <a className="nb-btn secondary" href={`${API}/api/v1/projects/${id}/export?format=json`} download>DOWNLOAD JSON</a>
            </p>
          </section>

          {msg && <p role="status">{msg}</p>}
          <Copilot projectId={id} />
        </div>
      </div>
    </div>
  );
}

function Copilot({ projectId }: { projectId: string }) {
  const status = useFetch(() => api.aiStatus(), []);
  const [q, setQ] = useState("");
  const [thread, setThread] = useState<{ tool: string; text: string }[]>([]);
  const enabled = (status.data as Record<string, unknown> | null)?.enabled === true;
  async function ask() {
    if (!q.trim()) return;
    try {
      const r = await api.aiChat({ message: q, project_id: projectId }) as Record<string, unknown>;
      setThread((t) => [{ tool: String(r.tool), text: JSON.stringify(r.result, null, 2).slice(0, 1200) }, ...t].slice(0, 6));
      setQ("");
    } catch (e) { setThread((t) => [{ tool: "error", text: String(e) }, ...t]); }
  }
  return (
    <section className="block" id="copilot" tabIndex={-1}>
      <h2>17 AI Copilot (optional)</h2>
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src="/img/brand/mascot.png" alt="" aria-hidden="true" width={48} height={48} style={{ border: "3px solid var(--nb-ink)", borderRadius: 8 }} />
        <p style={{ margin: 0 }}>
          {enabled
            ? "LLM layer active — it structures tool output only and cannot invent sources."
            : "No LLM provider configured. Answers come from deterministic tools over your project + the seed catalogue — INQETRA stays fully usable and never invents."}
        </p>
      </div>
      <label className="f">Ask about this project (gaps, compatibility, acquisition, methods…)
        <input value={q} onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter") ask(); }}
          placeholder="e.g. what data gaps remain?" />
      </label>
      <button className="nb-btn secondary" onClick={ask}>ASK COPILOT</button>
      {thread.map((t, i) => (
        <div key={i} className="nb-card"><span className="tag">[tool: {t.tool}]</span><pre style={{ whiteSpace: "pre-wrap", margin: "8px 0 0" }}>{t.text}</pre></div>
      ))}
    </section>
  );
}

function MethodologyForm({ projectId, meth, call }: { projectId: string; meth: Record<string, string> | null; call: (fn: () => Promise<unknown>, ok?: string) => Promise<void> }) {
  const [mf, setMf] = useState<Record<string, string>>({});
  const v = (k: string) => mf[k] ?? (meth?.[k] ?? "");
  return (
    <div className="nb-card">
      <h3>Methodology design</h3>
      <Field label="Design (e.g. Convergent mixed methods)" value={v("design")} onChange={(x) => setMf((s) => ({ ...s, design: x }))} />
      <Field label="Description" textarea value={v("description")} onChange={(x) => setMf((s) => ({ ...s, description: x }))} />
      <Field label="Ethics" textarea value={v("ethics")} onChange={(x) => setMf((s) => ({ ...s, ethics: x }))} />
      <Field label="Limitations" textarea value={v("limitations")} onChange={(x) => setMf((s) => ({ ...s, limitations: x }))} />
      <button className="nb-btn" onClick={() => call(() => api.post(`/api/v1/projects/${projectId}/methodology`, { design: v("design"), description: v("description"), ethics: v("ethics"), limitations: v("limitations") }))}>SAVE METHODOLOGY</button>
    </div>
  );
}

function EdgeForm({ projectId, nodes, call }: { projectId: string; nodes: Record<string, string>[]; call: (fn: () => Promise<unknown>, ok?: string) => Promise<void> }) {
  const [fromId, setFromId] = useState("");
  const [toId, setToId] = useState("");
  const [rel, setRel] = useState("influences");
  if (!nodes.length) return <p>Add nodes first, then connect them.</p>;
  return (
    <div className="grid">
      <Select label="From" value={fromId} options={["", ...nodes.map((n) => n.id)]} onChange={setFromId} />
      <Select label="To" value={toId} options={["", ...nodes.map((n) => n.id)]} onChange={setToId} />
      <Select label="Relation" value={rel} options={["influences", "moderates", "mediates", "measures", "confounds"]} onChange={setRel} />
      <button className="nb-btn" disabled={!fromId || !toId || fromId === toId}
        onClick={() => call(() => api.post(`/api/v1/projects/${projectId}/edges`, { from_id: fromId, to_id: toId, relation: rel }))}>
        CONNECT NODES
      </button>
      <p>{nodes.filter((n) => [fromId, toId].includes(n.id)).map((n) => n.label).join(" → ") || "Selected labels appear here."}</p>
    </div>
  );
}

function ConceptBoard({ projectId, nodes, edges, onMsg }: {
  projectId: string; nodes: Record<string, unknown>[]; edges: Record<string, unknown>[]; onMsg: (s: string) => void;
}) {
  const board = useRef<HTMLDivElement>(null);
  const drag = useRef<string | null>(null);
  if (!nodes.length) return <p>No nodes yet — add the first concept below.</p>;
  const labelOf = (nid: unknown) => nodes.find((n) => n.id === nid)?.label || String(nid);
  async function drop(e: React.PointerEvent) {
    const cid = drag.current;
    drag.current = null;
    if (!cid || !board.current) return;
    const r = board.current.getBoundingClientRect();
    const x = Math.max(0, Math.min(600, Math.round(e.clientX - r.left - 60)));
    const y = Math.max(0, Math.min(360, Math.round(e.clientY - r.top - 20)));
    try {
      await api.patch(`/api/v1/projects/${projectId}/concepts/${cid}`, { x, y });
      onMsg(`Moved node to (${x}, ${y}).`);
      window.location.reload();
    } catch (err) { onMsg(String(err)); }
  }
  return (
    <div ref={board} className="nb-card concept-board" role="application" aria-label="Concept map board"
      style={{ position: "relative", height: 400, touchAction: "none" }}
      onPointerMove={(e) => { if (drag.current) e.preventDefault(); }}
      onPointerUp={drop}>
      {edges.map((e) => {
        const a = nodes.find((n) => n.id === e.from_id);
        const b = nodes.find((n) => n.id === e.to_id);
        if (!a || !b) return null;
        const x1 = (Number(a.x) || 0) + 60, y1 = (Number(a.y) || 0) + 20;
        const x2 = (Number(b.x) || 0) + 60, y2 = (Number(b.y) || 0) + 20;
        return (
          <svg key={String(e.id)} width="600" height="400" style={{ position: "absolute", inset: 0, pointerEvents: "none" }} aria-hidden="true">
            <line x1={x1} y1={y1} x2={x2} y2={y2} stroke="var(--nb-ink)" strokeWidth="2" strokeDasharray="5 4" />
            <text x={(x1 + x2) / 2} y={(y1 + y2) / 2 - 4} fontSize="11" textAnchor="middle" fill="var(--nb-ink)">{String(e.relation)}</text>
          </svg>
        );
      })}
      {nodes.map((n) => (
        <button key={String(n.id)}
          className="concept-node"
          data-kind={String(n.kind)}
          style={{ position: "absolute", left: Number(n.x) || 0, top: Number(n.y) || 0, cursor: "grab" }}
          onPointerDown={() => { drag.current = String(n.id); }}
          onPointerUp={drop}
          aria-label={`Node ${String(n.label)} (${String(n.kind)}). Press and drag to move.`}>
          <strong>{String(n.label)}</strong><br /><small>{String(n.kind)}</small>
        </button>
      ))}
      <p style={{ position: "absolute", bottom: 8, right: 12, margin: 0, fontSize: 12 }}>
        {edges.length} edge{edges.length === 1 ? "" : "s"} · drag a node then release to store its position
      </p>
    </div>
  );
}

function MatrixEditor({ projectId, aims, basket, cells }: { projectId: string; aims: Record<string, string>[]; basket: Record<string, string>[]; cells: Record<string, string>[] }) {
  const rels = ["", "Primary", "Supporting", "Validation", "Context", "Not used"];
  async function cycle(row: string, col: string, current: string) {
    const next = rels[(rels.indexOf(current) + 1) % rels.length];
    await api.post(`/api/v1/projects/${projectId}/matrices/aim-dataset`, { row_id: row, col_id: col, relationship_type: next || "Not used", rationale: "Set in studio matrix" });
    window.location.reload();
  }
  if (!aims.length || !basket.length) return <p>Add at least one aim and one basket dataset to use the matrix.</p>;
  const val = (r: string, c: string) => cells.find((x) => x.row_id === r && x.col_id === c)?.relationship_type || "";
  return (
    <div className="matrix" role="grid" aria-label="Aim by dataset matrix">
      <div style={{ display: "contents" }} role="row">
        <span role="columnheader" style={{ padding: 8, fontWeight: 800 }}>Dataset ↓ · Aim →</span>
        {aims.map((a) => <span key={a.id} role="columnheader" style={{ padding: 8, fontWeight: 800 }}>{a.title}</span>)}
      </div>
      {basket.map((b) => (
        <div key={b.id} style={{ display: "contents" }} role="row">
          <span role="rowheader" style={{ padding: 8 }}>{b.dataset_id}</span>
          {aims.map((a) => (
            <button key={a.id} role="gridcell" className="cell" data-rel={val(b.dataset_id, a.id)}
              aria-label={`${b.dataset_id} by ${a.title}: ${val(b.dataset_id, a.id) || "unset"}. Activate to change.`}
              onClick={() => cycle(b.dataset_id, a.id, val(b.dataset_id, a.id))}>
              {val(b.dataset_id, a.id) || "—"}
            </button>
          ))}
        </div>
      ))}
      <p>Keyboard: Tab to a cell, Enter to cycle relationship. Every cell stores rationale + timestamp.</p>
    </div>
  );
}

function CitList({ id }: { id: string }) {
  const c = useFetch(() => api.get(`/api/v1/projects/${id}/citations`), [id]);
  if (c.loading) return <p>Loading citations…</p>;
  const items = (c.data?.items || []) as Record<string, string>[];
  return (
    <ul>
      {items.map((x, i) => (
        <li key={x.citation_id || x.dataset_id || i}>
          <strong>{x.harvard}</strong>
          <details><summary>All formats</summary>
            <p>APA: {x.apa}</p>
            <pre style={{ whiteSpace: "pre-wrap" }}>{x.bibtex}</pre>
            <pre style={{ whiteSpace: "pre-wrap" }}>{x.ris}</pre>
          </details>
          {x.citation_id
            ? <button className="nb-btn secondary" onClick={async () => { await api.del(`/api/v1/projects/${id}/citations/${x.citation_id}`); window.location.reload(); }}>REMOVE</button>
            : null}
        </li>
      ))}
    </ul>
  );
}
