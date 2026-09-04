"use client";
import Link from "next/link";
import { useState } from "react";
import { api } from "../../lib/api";
import { useFetch } from "../../hooks/hooks";

export default function Paths() {
  const paths = useFetch(() => api.get("/api/v1/paths"), []);
  const projects = useFetch(() => api.projects(), []);
  const [slug, setSlug] = useState("");
  const detail = useFetch(() => (slug ? api.get(`/api/v1/paths/${slug}`) : Promise.resolve(null)), [slug]);
  const [pid, setPid] = useState("");
  const [msg, setMsg] = useState("");

  async function useForProject() {
    if (!pid || !slug) { setMsg("Choose a path and a project first."); return; }
    try {
      await api.patchProject(pid, { export_path: slug });
      const p = ((projects.data?.items || []) as Record<string, string>[]).find(x => x.id === pid);
      setMsg(`Path "${detail.data?.title}" set for "${p?.title}". The studio, abstract builder and exports now follow it.`);
    } catch (e) { setMsg(String(e)); }
  }

  return (
    <div className="grid">
      <h1>DOCUMENT PATHS</h1>
      <p>Every path carries its own section skeleton, word targets, the studio tools that matter, and suggested ways of working. Pick one per project — the abstract builder and exports follow it.</p>
      <div className="grid cards">
        {((paths.data?.items || []) as Record<string, unknown>[]).map((p) => (
          <button key={String(p.slug)} className={"path-card nb-card" + (slug === p.slug ? " path-active" : "")}
            onClick={() => setSlug(String(p.slug))}>
            <h3>{String(p.title)}</h3>
            <p>{String(p.tagline)}</p>
            <p className="prov">{String(p.audience)} · {String(p.word_target)} · {String(p.sections)} sections</p>
          </button>
        ))}
      </div>

      {detail.data && (
        <>
          <section className="nb-card pop-in">
            <h2>{detail.data.title} — section skeleton</h2>
            <table className="data">
              <thead><tr><th>Section</th><th>Words</th><th>What goes in it</th><th>Suggested opening</th></tr></thead>
              <tbody>
                {(detail.data.sections as Record<string, string>[]).map((s) => (
                  <tr key={s.heading}>
                    <td><strong>{s.heading}</strong></td>
                    <td>{s.words}</td>
                    <td>{s.guidance}</td>
                    <td><em>“{s.starters[0]}”</em></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
          <section className="nb-card">
            <h2>Tools this path leans on</h2>
            <div className="badges">
              {(detail.data.tools as string[]).map((t) => <span key={t} className="nb-chip violet">{t}</span>)}
            </div>
            <h2 style={{ marginTop: 16 }}>Suggested ways of working</h2>
            <ul>{(detail.data.suggested_working as string[]).map((w, i) => <li key={i}>{w}</li>)}</ul>
          </section>
          <section className="nb-card">
            <h2>Apply this path to a project</h2>
            <label className="f">Project
              <select value={pid} onChange={(e) => setPid(e.target.value)}>
                <option value="">— select a project —</option>
                {((projects.data?.items || []) as Record<string, string>[]).map((p) => <option key={p.id} value={p.id}>{p.title}</option>)}
              </select>
            </label>
            <button className="nb-btn orange" style={{ background: "var(--nb-orange)" }} onClick={useForProject}>SET PATH FOR PROJECT →</button>
            {msg && <p role="status">{msg}</p>}
            <p><Link className="nb-btn secondary" href="/projects/new">…or start a new project on this path via the wizard</Link></p>
          </section>
        </>
      )}
    </div>
  );
}
