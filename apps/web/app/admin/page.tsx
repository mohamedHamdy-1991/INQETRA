"use client";
import { useState } from "react";
import { useFetch } from "../../hooks/hooks";
import { api } from "../../lib/api";

export default function Admin() {
  const audit = useFetch(() => api.get("/api/v1/admin/audit"), []);
  const health = useFetch(() => api.health(), []);
  const [out, setOut] = useState("");
  return (
    <div className="grid">
      <h1>ADMIN</h1>
      {health.data && <p role="status">Seed {health.data.record_count} · unreachable {health.data.unreachable_record_count} · checked {health.data.checked_at_utc}</p>}
      <RulesEditor />
      <SubmissionsModeration />
      <StagingQueue />
      <SourceRuns />
      <ResolverRunner />
      <div className="nb-card">
        <h2>On-demand link check (SSRF-guarded, first N)</h2>
        <button className="nb-btn" style={{ background: "var(--nb-orange)" }} onClick={async () => {
          const r = await api.post("/api/v1/admin/link-check", { limit: 5 });
          setOut(JSON.stringify(r, null, 2));
        }}>RUN CHECK (5)</button>
        {out && <pre style={{ whiteSpace: "pre-wrap" }}>{out}</pre>}
      </div>
      <div className="nb-card">
        <h2>Export job + failure state</h2>
        <button className="nb-btn secondary" onClick={async () => {
          const ok = await api.post("/api/v1/jobs/exports", { project_id: "demo" });
          const fail = await api.post("/api/v1/jobs/exports", { project_id: "demo", simulate: "fail" });
          setOut(JSON.stringify({ ok: ok.status, fail: fail.status, note: fail.detail }, null, 2));
        }}>RUN JOB OK + FAIL SIMULATION</button>
      </div>
      <div className="nb-card"><h2>Audit log (latest)</h2><pre style={{ whiteSpace: "pre-wrap" }}>{JSON.stringify(audit.data, null, 2)?.slice(0, 2000)}</pre></div>
    </div>
  );
}

function RulesEditor() {
  const rules = useFetch(() => api.rules(), []);
  const [res, setRes] = useState<Record<string, unknown> | null>(null);
  const [msg, setMsg] = useState("");
  const items = (rules.data?.items || []) as Record<string, unknown>[];
  async function toggle(rule: string, active: boolean) {
    await api.patchRule(rule, { active });
    setMsg(`${rule} ${active ? "activated" : "deactivated"}.`);
    rules.reload();
  }
  async function severity(rule: string, s: string) {
    await api.patchRule(rule, { severity: s });
    setMsg(`${rule} severity → ${s}.`);
    rules.reload();
  }
  return (
    <div className="nb-card">
      <h2>Compatibility rules</h2>
      <p>Toggle rules or change severity, then run the fixed fixture to see the scoped engine result. Rules shape advice only — never a validity verdict.</p>
      {items.map((r) => (
        <p key={String(r.rule)}>
          <strong>{String(r.rule)}</strong> · severity{" "}
          <select value={String(r.severity)} onChange={(e) => severity(String(r.rule), e.target.value)} aria-label={`Severity for ${String(r.rule)}`}>
            {["info", "warn", "block"].map((s) => <option key={s} value={s}>{s}</option>)}
          </select>{" "}
          <button className="nb-btn secondary" onClick={() => toggle(String(r.rule), !r.active)}>{r.active ? "ACTIVE — DEACTIVATE" : "INACTIVE — ACTIVATE"}</button>
        </p>
      ))}
      <button className="nb-btn" onClick={async () => { setRes(await api.testRules()); }}>TEST FIXTURES</button>
      {msg && <p role="status">{msg}</p>}
      {res && <pre style={{ whiteSpace: "pre-wrap" }}>{JSON.stringify(res, null, 2)}</pre>}
    </div>
  );
}

function SubmissionsModeration() {
  const subs = useFetch(() => api.submissions(), []);
  const [notes, setNotes] = useState<Record<string, string>>({});
  const [msg, setMsg] = useState("");
  const items = (subs.data?.items || []) as Record<string, string>[];
  async function moderate(id: string, decision: "accepted" | "rejected") {
    const r = await api.moderate(id, { decision, moderator_notes: notes[id] || "" }) as Record<string, unknown>;
    setMsg(`${decision}: ${String(r.title)} — published_to_catalogue=${String(r.published_to_catalogue)}. ${String(r.note)}`);
    subs.reload();
  }
  return (
    <div className="nb-card">
      <h2>Community submissions ({items.length})</h2>
      {items.length === 0 && <p>No submissions yet.</p>}
      {items.map((s) => (
        <div key={s.id} style={{ borderBottom: "2px solid var(--nb-ink)", paddingBottom: 8, marginBottom: 8 }}>
          <p><strong>{s.title}</strong> — <a href={s.url} rel="nofollow noopener">{s.url}</a> <span className="tag">[{s.status}]</span> · {s.publisher}</p>
          <input placeholder="Moderator notes" value={notes[s.id] || ""} onChange={(e) => setNotes((n) => ({ ...n, [s.id]: e.target.value }))} />
          {" "}
          <button className="nb-btn secondary" onClick={() => moderate(s.id, "accepted")}>ACCEPT (→ staged candidate)</button>{" "}
          <button className="nb-btn secondary" onClick={() => moderate(s.id, "rejected")}>REJECT</button>
        </div>
      ))}
      {msg && <p role="status">{msg}</p>}
      <p className="warn">Moderation never publishes to the catalogue — accepted items become staging candidates requiring full provenance + link-health review.</p>
    </div>
  );
}

function StagingQueue() {
  const st = useFetch(() => api.staging(), []);
  const items = (st.data?.items || []) as Record<string, unknown>[];
  return (
    <div className="nb-card">
      <h2>Staging queue ({items.length})</h2>
      <p>Raw harvester/resolver output awaiting curation. Nothing here is a catalogue record.</p>
      {items.length === 0 ? <p>Queue empty.</p> : (
        <div className="matrix" role="table" aria-label="Staging candidates">
          <div style={{ display: "contents" }} role="row">
            {["Title", "URL", "Publisher", "Licence state", "Provenance"].map((h) => (
              <span key={h} role="columnheader" style={{ padding: 8, fontWeight: 800 }}>{h}</span>
            ))}
          </div>
          {items.slice(0, 25).map((c) => (
            <div key={String(c.id)} style={{ display: "contents" }} role="row">
              <span role="cell" style={{ padding: 8 }}>{String(c.title)}</span>
              <span role="cell" style={{ padding: 8 }}><a href={String(c.url)} rel="nofollow noopener">{String(c.url).slice(0, 48)}…</a></span>
              <span role="cell" style={{ padding: 8 }}>{String(c.publisher || "—")}</span>
              <span role="cell" style={{ padding: 8 }}>{String(c.licence_state)}</span>
              <span role="cell" style={{ padding: 8 }}><code>{JSON.stringify(c.provenance).slice(0, 60)}…</code></span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function SourceRuns() {
  const sources = useFetch(() => api.sources(), []);
  const [msg, setMsg] = useState("");
  const [runs, setRuns] = useState<Record<string, Record<string, unknown>[]>>({});
  const items = (sources.data?.items || []) as Record<string, unknown>[];
  async function run(sid: string) {
    try {
      const r = await api.post(`/api/v1/sources/${sid}/run`, { limit: 10 }) as Record<string, unknown>;
      setMsg(`Run ${String(r.status)}: +${String(r.added)} ~${String(r.changed)} (metadata-only, staged).`);
      const log = await api.get(`/api/v1/sources/${sid}/runs`) as { items: Record<string, unknown>[] };
      setRuns((m) => ({ ...m, [sid]: log.items || [] }));
    } catch (e) { setMsg(String(e)); }
  }
  async function log(sid: string) {
    const l = await api.get(`/api/v1/sources/${sid}/runs`) as { items: Record<string, unknown>[] };
    setRuns((m) => ({ ...m, [sid]: l.items || [] }));
  }
  return (
    <div className="nb-card">
      <h2>Source registry ({items.length})</h2>
      {items.map((s) => (
        <div key={String(s.id)} style={{ borderBottom: "2px solid var(--nb-ink)", paddingBottom: 8, marginBottom: 8 }}>
          <p><strong>{String(s.name)}</strong> · {String(s.adapter)} · {String(s.trust_level)} · {s.active ? "active" : "inactive"}{s.kill_switch ? " · KILL SWITCH ON" : ""}</p>
          <p><code>{String(s.base_url)}</code></p>
          <button className="nb-btn secondary" onClick={() => run(String(s.id))}>RUN (metadata-only, staged)</button>{" "}
          <button className="nb-btn secondary" onClick={() => log(String(s.id))}>RUNS LOG</button>
          {runs[String(s.id)] && (
            <ul>{runs[String(s.id)].slice(0, 5).map((r) => (
              <li key={String(r.id)}>[{String(r.status)}] {String(r.detail || "")} (+{String(r.added)} ~{String(r.changed)})</li>
            ))}</ul>
          )}
        </div>
      ))}
      {msg && <p role="status">{msg}</p>}
      <p className="warn">Harvest fetches metadata only and writes staging candidates. The catalogue is never mutated by a run.</p>
    </div>
  );
}

function ResolverRunner() {
  const [rid, setRid] = useState("");
  const [res, setRes] = useState<Record<string, unknown> | null>(null);
  return (
    <div className="nb-card">
      <h2>Resolver (collection / search records)</h2>
      <p>Resolve an official_collection or search record to a current item. Exactly one portal match stages a candidate; 0 or &gt;1 stays unresolved. Never auto-publishes.</p>
      <label className="f">Dataset ID (e.g. inq-0016)<input value={rid} onChange={(e) => setRid(e.target.value)} /></label>
      <button className="nb-btn" disabled={!rid} onClick={async () => { try { setRes(await api.post("/api/v1/resolve", { dataset_id: rid }) as Record<string, unknown>); } catch (e) { setRes({ error: String(e) }); } }}>RESOLVE</button>
      {res && <pre style={{ whiteSpace: "pre-wrap" }}>{JSON.stringify(res, null, 2)}</pre>}
    </div>
  );
}
