"use client";
import Link from "next/link";
import { useFetch } from "../../../../../hooks/hooks";
import { api } from "../../../../../lib/api";

const STATUS_COLOR: Record<string, string> = {
  COVERED: "var(--nb-green)", PARTIAL: "var(--nb-yellow)", MISSING: "var(--nb-pink)",
  INCOMPATIBLE: "var(--nb-orange)", RESTRICTED: "var(--nb-violet)", UNKNOWN: "var(--nb-muted)",
};

export default function ReportPrint({ params }: { params: { id: string } }) {
  const id = params.id;
  const r = useFetch(() => api.get(`/api/v1/projects/${id}/report-model`), [id]);
  const gaps = useFetch(() => api.get(`/api/v1/projects/${id}/gaps`), [id]);
  const cites = useFetch(() => api.get(`/api/v1/projects/${id}/citations`), [id]);
  const proj = useFetch(() => api.project(id), [id]);
  const pathSlug = (proj.data as Record<string, string> | null)?.export_path || "";
  const path = useFetch(() => (pathSlug ? api.get(`/api/v1/paths/${pathSlug}`) : Promise.resolve(null)), [pathSlug]);

  if (r.loading) return <p role="status">Preparing the report…</p>;
  if (r.error || !r.data) return <p className="warn">{String(r.error)}</p>;
  const m = r.data as Record<string, unknown>;
  const p = m.project as Record<string, string>;
  const today = new Date().toISOString().slice(0, 10);

  return (
    <div className="print-doc">
      <div className="no-print" style={{ position: "fixed", top: 12, right: 12, zIndex: 50, display: "flex", gap: 8 }}>
        <button className="nb-btn orange" style={{ background: "var(--nb-orange)" }} onClick={() => window.print()}>SAVE AS PDF →</button>
        <Link className="nb-btn secondary" href={`/projects/${id}/report`}>← BACK</Link>
      </div>

      {/* cover */}
      <header className="pr-cover">
        <div className="pr-cover-brand">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/logo.png" alt="" width={64} height={64} />
          <div><strong>INQETRA</strong><small>RESEARCH DATA PLAN</small></div>
        </div>
        <h1>{p.title}</h1>
        {p.geography ? <p className="pr-sub">{p.geography}{p.start_date ? ` · ${p.start_date} → ${p.end_date}` : ""}</p> : null}
        <div className="pr-badges">
          {pathSlug && path.data ? <span className="pr-badge" style={{ background: "var(--nb-violet)", color: "#fff" }}>{(path.data as Record<string, string>).title} PATH</span> : <span className="pr-badge" style={{ background: "var(--nb-yellow)" }}>RESEARCH DATA PLAN</span>}
          <span className="pr-badge" style={{ background: "var(--nb-green)" }}>{(m.inventory as unknown[]).length} DATASETS</span>
          <span className="pr-badge" style={{ background: "var(--nb-cyan)" }}>{(m.questions as unknown[]).length} QUESTIONS · {(m.aims as unknown[]).length} AIMS</span>
        </div>
        <p className="pr-date">Generated {today} · INQETRA studio export</p>
      </header>

      {/* problem + gap */}
      <section className="pr-sec">
        <h2>Research problem & gap</h2>
        <p>{p.problem || "Not yet stated."}</p>
        <p className="pr-gap"><strong>Gap:</strong> {p.gap || "Not yet stated."}</p>
      </section>

      {/* questions + aims */}
      <section className="pr-sec pr-2col">
        <div>
          <h2>Research questions</h2>
          <ol>{(m.questions as Record<string, string>[]).map((q) => <li key={q.id}>{q.text}</li>)}</ol>
        </div>
        <div>
          <h2>Aims</h2>
          <ul>{(m.aims as Record<string, string>[]).map((a) => <li key={a.id}><strong>{a.title}</strong> — {a.statement}</li>)}</ul>
        </div>
      </section>

      {/* methods + path skeleton */}
      <section className="pr-sec pr-2col">
        <div>
          <h2>Methods</h2>
          <ul>{(m.methods as Record<string, string>[]).map((x) => <li key={x.id}>{x.name} — {x.purpose}</li>)}</ul>
        </div>
        {path.data ? (
          <div>
            <h2>{(path.data as Record<string, string>).title} skeleton</h2>
            <ol>{((path.data as Record<string, unknown>).sections as Record<string, string>[]).map((s) => <li key={s.heading}>{s.heading} <small>({s.words})</small></li>)}</ol>
          </div>
        ) : null}
      </section>

      {/* dataset inventory */}
      <section className="pr-sec">
        <h2>Evidence base — {(m.inventory as unknown[]).length} dataset(s)</h2>
        <table className="pr-table">
          <thead><tr><th>Dataset</th><th>Publisher</th><th>Access</th><th>Licence</th><th>Link / verification</th></tr></thead>
          <tbody>
            {(m.inventory as Record<string, Record<string, string>>[]).map(({ basket, dataset }) => (
              <tr key={basket.id}>
                <td><strong>{dataset.id}</strong><br />{dataset.title}<br /><span className="pr-art"><img src={dataset.domain ? `/img/domains/domain-${dataset.domain.toLowerCase().replace(/&/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "")}.png` : "/logo.png"} alt="" width={96} height={54} /></span></td>
                <td>{dataset.publisher}</td>
                <td>{dataset.access_type}</td>
                <td>{dataset.licence}</td>
                <td><span className="pr-tag">{dataset.link_type}</span> <span className="pr-tag">{dataset.verification_state}</span><br /><span className="pr-url">{dataset.landing_url}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      {/* gaps */}
      <section className="pr-sec">
        <h2>Coverage & gaps</h2>
        <ul className="pr-gaps">
          {((gaps.data as Record<string, unknown>)?.requirements as Record<string, string>[] | undefined)?.map((g) => (
            <li key={g.requirement_id}>
              <span className="pr-status" style={{ background: STATUS_COLOR[g.status] || "var(--nb-muted)" }}>{g.status}</span>
              <strong>{g.requirement_title}</strong> — {g.explanation}
            </li>
          ))}
        </ul>
      </section>

      {/* citations */}
      <section className="pr-sec">
        <h2>Dataset citations (Harvard)</h2>
        <ol className="pr-cites">
          {((cites.data as Record<string, unknown>)?.items as Record<string, string>[] | undefined)?.map((c, i) => <li key={i}>{c.harvard}</li>)}
        </ol>
      </section>

      <footer className="pr-foot">
        <span>{m.provenance as string}</span>
        <span>INQETRA · {today}</span>
      </footer>
    </div>
  );
}
