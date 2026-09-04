"use client";
import { useState } from "react";
import { useFetch } from "../../../hooks/hooks";
import { api } from "../../../lib/api";

const STEPS = ["Problem + Gap", "Questions", "Aims", "Methods", "Requirements", "Review + Create"];
const RQ_STARTERS = [
  "How does … influence … across …?",
  "Where do … and … intersect in …?",
  "Which … have the greatest … in …?",
  "How are … associated with … in …?",
];

export default function NewProject() {
  const [step, setStep] = useState(0);
  const [title, setTitle] = useState("");
  const [problem, setProblem] = useState("");
  const [gap, setGap] = useState("");
  const [geography, setGeography] = useState("United Kingdom");
  const [questions, setQuestions] = useState<string[]>([""]);
  const [aims, setAims] = useState<string[]>([""]);
  const [methods, setMethods] = useState<string[]>(["GIS"]);
  const [roles, setRoles] = useState<string[]>(["Climate / exposure", "Built environment"]);
  const [kit, setKit] = useState("");
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);
  const kits = useFetch(() => api.kits(), []);

  function applyKit(slug: string) {
    setKit(slug);
    const k = (kits.data?.items || []).find((x: Record<string, unknown>) => x.slug === slug) as Record<string, string[]> | undefined;
    if (!k) return;
    if (k.questions?.length) setQuestions(k.questions as string[]);
    if (k.aims?.length) setAims(k.aims as string[]);
    if (k.methods?.length) setMethods(k.methods as string[]);
    if (k.required_roles?.length) setRoles(k.required_roles as string[]);
    setMsg(`Template '${slug}' applied — edit freely before creating.`);
  }

  const setList = (fn: (v: string[]) => void, arr: string[], i: number, v: string) => {
    const n = [...arr]; n[i] = v; fn(n);
  };

  async function create() {
    if (!title.trim() || !problem.trim()) { setMsg("Title and problem statement are required."); setStep(0); return; }
    setBusy(true);
    try {
      const p = await api.createProject({ title, problem, gap, geography });
      for (const q of questions.filter(Boolean)) await api.post(`/api/v1/projects/${p.id}/questions`, { text: q });
      const aimIds: string[] = [];
      for (const a of aims.filter(Boolean)) {
        const r = await api.post(`/api/v1/projects/${p.id}/aims`, { title: a, statement: a });
        aimIds.push(r.id);
      }
      const mIds: string[] = [];
      for (const m of methods.filter(Boolean)) {
        const r = await api.post(`/api/v1/projects/${p.id}/methods`, { name: m, purpose: "Chosen in project wizard" });
        mIds.push(r.id);
      }
      for (const r of roles.filter(Boolean))
        await api.post(`/api/v1/projects/${p.id}/requirements`, { title: `${r} — evidence requirement`, research_role: r, geography, linked_aim_ids: aimIds, linked_method_ids: mIds });
      window.location.href = `/projects/${p.id}/studio`;
    } catch (e) { setMsg(String(e)); setBusy(false); }
  }

  return (
    <div className="grid">
      <h1>START A RESEARCH PROJECT</h1>
      <div className="wizard-steps" aria-label={`Step ${step + 1} of ${STEPS.length}: ${STEPS[step]}`}>
        {STEPS.map((s, i) => <span key={s} title={s} className={i < step ? "done" : i === step ? "now" : ""} />)}
      </div>
      <h2>{ STEPS[step]}</h2>

      {step === 0 && (
        <div className="nb-card pop-in">
          <label className="f">Project title<input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g. Overheating in Leeds terraces" /></label>
          <label className="f">Research problem (background + problem statement)<textarea rows={4} value={problem} onChange={(e) => setProblem(e.target.value)} placeholder="What is wrong, for whom, where? One paragraph." /></label>
          <label className="f">Knowledge gap<textarea rows={3} value={gap} onChange={(e) => setGap(e.target.value)} placeholder="What is missing from current evidence?" /></label>
          <label className="f">Study geography<input value={geography} onChange={(e) => setGeography(e.target.value)} /></label>
          <label className="f">Start from a kit template (optional)<select value={kit} onChange={(e) => applyKit(e.target.value)}>
            <option value="">— blank —</option>
            {(kits.data?.items || []).map((k: Record<string, string>) => <option key={k.slug} value={k.slug}>{k.title}</option>)}
          </select></label>
        </div>
      )}
      {step === 1 && (
        <div className="nb-card pop-in">
          <p>Starters: {RQ_STARTERS.map((s) => <button key={s} className="nb-chip" style={{ cursor: "pointer" }} onClick={() => setQuestions([...questions, s])}>{s}</button>)}</p>
          {questions.map((q, i) => <label className="f" key={i}>Question {i + 1}<textarea value={q} onChange={(e) => setList(setQuestions, questions, i, e.target.value)} /></label>)}
          <button className="nb-btn secondary" onClick={() => setQuestions([...questions, ""])}>+ ADD QUESTION</button>
        </div>
      )}
      {step === 2 && (
        <div className="nb-card pop-in">
          {aims.map((a, i) => <label className="f" key={i}>Aim {i + 1}<input value={a} onChange={(e) => setList(setAims, aims, i, e.target.value)} /></label>)}
          <button className="nb-btn secondary" onClick={() => setAims([...aims, ""])}>+ ADD AIM</button>
        </div>
      )}
      {step === 3 && (
        <div className="nb-card pop-in">
          {methods.map((m, i) => <label className="f" key={i}>Method {i + 1}<input value={m} onChange={(e) => setList(setMethods, methods, i, e.target.value)} placeholder="GIS, regression, simulation…" /></label>)}
          <button className="nb-btn secondary" onClick={() => setMethods([...methods, ""])}>+ ADD METHOD</button>
        </div>
      )}
      {step === 4 && (
        <div className="nb-card pop-in">
          <p>Requirements first: what evidence must each aim have — before choosing datasets.</p>
          {roles.map((r, i) => <label className="f" key={i}>Required role {i + 1}<input value={r} onChange={(e) => setList(setRoles, roles, i, e.target.value)} /></label>)}
          <button className="nb-btn secondary" onClick={() => setRoles([...roles, ""])}>+ ADD ROLE</button>
        </div>
      )}
      {step === 5 && (
        <div className="nb-card pop-in">
          <h3>Review</h3>
          <p><strong>{title || "(untitled)"}</strong> · {geography}</p>
          <p>{questions.filter(Boolean).length} question(s) · {aims.filter(Boolean).length} aim(s) · {methods.filter(Boolean).length} method(s) · {roles.filter(Boolean).length} requirement(s)</p>
          <button className="nb-btn" disabled={busy} onClick={create}>{busy ? "CREATING…" : "CREATE PROJECT → OPEN STUDIO"}</button>
        </div>
      )}
      <p>
        {step > 0 && <button className="nb-btn secondary" onClick={() => setStep(step - 1)}>← BACK</button>}{" "}
        {step < 5 && <button className="nb-btn" onClick={() => setStep(step + 1)}>NEXT →</button>}
      </p>
      {msg && <p role="status">{msg}</p>}
    </div>
  );
}
