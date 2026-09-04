"use client";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { useBasket, useFetch } from "../../../hooks/hooks";
import { api } from "../../../lib/api";

type Ev = { dataset_id: string; requirement_id: string | null; overall: string };
type GapRow = { requirement_id: string; requirement_title: string; status: string; explanation: string };

export default function BasketReport() {
  const basket = useBasket();
  const projects = useFetch(() => api.projects(), []);
  const [pid, setPid] = useState("");
  useEffect(() => {
    const q = new URLSearchParams(window.location.search).get("project");
    if (q) setPid(q);
  }, []);
  const proj = useFetch(
    () => (pid ? api.project(pid) : Promise.resolve(null)),
    [pid],
  );
  const info = useFetch(
    () => (basket.ids.length ? api.info(basket.ids) : Promise.resolve({ items: [] })),
    [basket.ids.join(",")],
  );
  const [ev, setEv] = useState<Ev[]>([]);
  const [gaps, setGaps] = useState<GapRow[]>([]);
  const [disclaimer, setDisclaimer] = useState("");
  const [msg, setMsg] = useState("");

  async function runEvaluate() {
    if (!pid) { setMsg("Choose a project first."); return; }
    try {
      // bring browser-basket items into the project basket first (save-to-project)
      const proj = await api.project(pid) as { basket: { dataset_id: string }[] };
      const already = new Set((proj.basket || []).map((b) => b.dataset_id));
      let saved = 0;
      for (const item of basket.items) {
        if (!already.has(item.id)) {
          await api.post(`/api/v1/projects/${pid}/basket`, { dataset_id: item.id, rationale: "Saved from basket data report" }).catch(() => null);
          saved += 1;
        }
      }
      const e = await api.post(`/api/v1/projects/${pid}/evaluate`, {}) as { evaluations: Ev[]; disclaimer: string };
      setEv(e.evaluations || []);
      setDisclaimer(e.disclaimer || "");
      const g = await api.get(`/api/v1/projects/${pid}/gaps`) as { requirements: GapRow[] };
      setGaps(g.requirements || []);
      setMsg(`${saved} basket item(s) saved to project. Evaluated ${e.evaluations.length} basket × requirement combinations.`);
    } catch (err) { setMsg(String(err)); }
  }

  const reqs = useMemo(() => (proj.data?.requirements || []) as Record<string, string>[], [proj.data]);
  const statusFor = (datasetId: string, requirementId: string) =>
    ev.find((e) => e.dataset_id === datasetId && String(e.requirement_id) === String(requirementId))?.overall || "";
  const gapFor = (requirementId: string) => gaps.find((g) => g.requirement_id === requirementId);

  return (
    <div className="grid">
      <h1>BASKET DATA REPORT</h1>
      <p>Coverage of your basket against a project's dataset requirements — mechanically evaluated, never a fitness verdict. {disclaimer}</p>

      <div className="nb-card">
        <h2>1 · Choose project</h2>
        <label className="f">Project
          <select value={pid} onChange={(e) => setPid(e.target.value)}>
            <option value="">— select a project —</option>
            {((projects.data?.items || []) as Record<string, string>[]).map((p) => (
              <option key={p.id} value={p.id}>{p.title}</option>
            ))}
          </select>
        </label>
      </div>

      <div className="nb-card">
        <h2>2 · Browser basket ({basket.count})</h2>
        {basket.count === 0 ? (
          <div>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="/img/empty/empty-basket.png" alt="An empty basket" width={450} height={300} style={{ maxWidth: "100%", height: "auto" }} />
            <p>The basket is empty. <Link href="/datasets">Explore datasets</Link> and ADD TO BASKET — items stay in this browser until you assign them in the Studio.</p>
          </div>
        ) : (
          <ul>
            {basket.items.map((i) => (
              <li key={i.id}><Link href={`/datasets/${i.id}`}>{i.title !== i.id ? `${i.title} (${i.id})` : i.id}</Link></li>
            ))}
          </ul>
        )}
        <p><button className="nb-btn secondary" onClick={() => basket.clear()}>CLEAR BASKET</button></p>
      </div>

      <div className="nb-card">
        <h2>3 · Evaluate coverage</h2>
        <button className="nb-btn" onClick={runEvaluate} disabled={!pid}>RUN COMPATIBILITY EVALUATION →</button>
        {msg && <p role="status">{msg}</p>}
        {pid && proj.data && (
          <p>Project <strong>{(proj.data as Record<string, string>).title}</strong>: {reqs.length} requirement(s), {(proj.data as Record<string, unknown>).basket ? ((proj.data as Record<string, unknown>).basket as unknown[]).length : 0} project-basket item(s).</p>
        )}
        {ev.length > 0 && (
          <div className="matrix" role="table" aria-label="Basket by requirement coverage">
            <div style={{ display: "contents" }} role="row">
              <span role="columnheader" style={{ padding: 8, fontWeight: 800 }}>Dataset ↓ · Requirement →</span>
              {reqs.map((r) => <span key={r.id} role="columnheader" style={{ padding: 8, fontWeight: 800 }}>{r.title}</span>)}
            </div>
            {basket.items.map((i) => (
              <div key={i.id} style={{ display: "contents" }} role="row">
                <span role="rowheader" style={{ padding: 8 }}>{i.title !== i.id ? `${i.title} (${i.id})` : i.id}</span>
                {reqs.map((r) => {
                  const s = statusFor(i.id, r.id);
                  return (
                    <span key={r.id} role="cell" className="cell" data-rel={s || "—"} style={{ padding: 8 }}>
                      {s || "—"}
                    </span>
                  );
                })}
              </div>
            ))}
          </div>
        )}
        {gaps.length > 0 && (
          <div>
            <h3>Requirement statuses</h3>
            <ul>
              {gaps.map((g) => (
                <li key={g.requirement_id}><strong>{g.requirement_title}</strong>: <span className="tag">[{g.status}]</span> {g.explanation}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <div className="nb-card">
        <h2>4 · Access / licence readiness (source-declared)</h2>
        {(info.data?.items || []).length === 0 ? <p>No basket items to inspect.</p> : (
          <div className="matrix" role="table" aria-label="Access and licence readiness">
            <div style={{ display: "contents" }} role="row">
              {["Dataset", "Publisher", "Access", "Licence", "Link type", "Verification"].map((h) => (
                <span key={h} role="columnheader" style={{ padding: 8, fontWeight: 800 }}>{h}</span>
              ))}
            </div>
            {((info.data?.items || []) as Record<string, string>[]).map((d) => (
              <div key={d.id} style={{ display: "contents" }} role="row">
                <span role="cell" style={{ padding: 8 }}><Link href={`/datasets/${d.id}`}>{d.id}</Link></span>
                <span role="cell" style={{ padding: 8 }}>{d.publisher}</span>
                <span role="cell" style={{ padding: 8 }}>{d.access_type}</span>
                <span role="cell" style={{ padding: 8 }}>{d.licence}</span>
                <span role="cell" style={{ padding: 8 }}>{d.link_type}</span>
                <span role="cell" style={{ padding: 8 }}>{d.verification_state}</span>
              </div>
            ))}
          </div>
        )}
        <p className="warn">Declared access/licence strings only — open each landing page and confirm entitlement before reuse. Reachability ≠ permission.</p>
      </div>

      {pid && (
        <div className="nb-card pop-in">
          <h2>5 · Generate the plan</h2>
          <p><Link className="nb-btn orange" href={`/projects/${pid}/report`} style={{ background: "var(--nb-orange)" }}>GENERATE DATA PLAN →</Link>{" "}
            <Link className="nb-btn secondary" href={`/projects/${pid}/studio`}>OPEN STUDIO</Link></p>
        </div>
      )}
    </div>
  );
}
