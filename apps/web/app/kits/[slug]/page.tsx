"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { Reveal } from "../../../components/reveal";
import { useFetch } from "../../../hooks/hooks";
import { api } from "../../../lib/api";

type List = string[];

export default function KitDetail({ params }: { params: { slug: string } }) {
  const slug = params.slug;
  const k = useFetch(() => api.kit(slug), [slug]);
  const [geo, setGeo] = useState("United Kingdom");
  const [msg, setMsg] = useState("");
  const [customising, setCustomising] = useState(false);
  const [title, setTitle] = useState("");
  const [questions, setQuestions] = useState<List>([]);
  const [aims, setAims] = useState<List>([]);
  const [methods, setMethods] = useState<List>([]);
  const [roles, setRoles] = useState<List>([]);
  const [customSlug, setCustomSlug] = useState("");

  useEffect(() => {
    if (!k.data) return;
    const d = k.data as Record<string, unknown>;
    setTitle(String(d.title ?? ""));
    setQuestions([...(d.questions as List ?? [])]);
    setAims([...(d.aims as List ?? [])]);
    setMethods([...(d.methods as List ?? [])]);
    setRoles([...(d.required_roles as List ?? [])]);
  }, [k.data]);

  if (k.loading) return <p role="status">Loading kit…</p>;
  if (k.error || !k.data) return <p className="warn" role="alert">{String(k.error)}</p>;
  const d = k.data as Record<string, unknown>;
  const isCustom = !!(d as Record<string, unknown>).custom;

  async function instantiate(target = slug) {
    try {
      const r = await api.instantiate(target, { geography: geo });
      window.location.href = `/projects/${r.project_id}/studio`;
    } catch (e) { setMsg(String(e)); }
  }

  async function saveAsMyKit() {
    try {
      const created = await api.post("/api/v1/kits", {
        slug: customSlug || undefined,
        title: title,
        version: "1.0",
        graph: { questions: questions.filter(Boolean), aims: aims.filter(Boolean), methods: methods.filter(Boolean), required_roles: roles.filter(Boolean), recommended_domains: d.recommended_domains, custom: true },
      }) as Record<string, string>;
      setMsg(`Saved as "${created.slug}". Opening it…`);
      window.location.href = `/kits/${created.slug}`;
    } catch (e) { setMsg(String(e)); }
  }

  async function removeCustom() {
    try {
      await api.del(`/api/v1/kits/${slug}`);
      window.location.href = "/kits";
    } catch (e) { setMsg(String(e)); }
  }

  const listEditor = (label: string, arr: List, setArr: (v: List) => void) => (
    <div className="nb-card" style={{ marginBottom: 12 }}>
      <h3>{label}</h3>
      {arr.map((q, i) => (
        <div key={i} style={{ display: "flex", gap: 6, marginBottom: 6 }}>
          <input value={q} onChange={(e) => { const n = [...arr]; n[i] = e.target.value; setArr(n); }} style={{ flex: 1, minHeight: 44, border: "var(--nb-border-2)", padding: "8px 10px", font: "inherit", background: "#fff" }} />
          <button className="nb-btn secondary" onClick={() => setArr(arr.filter((_, j) => j !== i))} aria-label={`Remove item ${i + 1} from ${label}`}>×</button>
        </div>
      ))}
      <button className="nb-btn secondary" onClick={() => setArr([...arr, ""])}>+ ADD {label.toUpperCase().replace(/S$/, "")}</button>
    </div>
  );

  return (
    <div className="grid">
      <p><Link href="/kits">← Kits</Link></p>
      {customising ? (
        <input value={title} onChange={(e) => setTitle(e.target.value)} aria-label="Kit title"
          style={{ font: "900 clamp(24px,3vw,40px)/1.1 var(--nb-font-display)", border: "none", background: "transparent", width: "100%" }} />
      ) : (
        <h1>{title || String(d.title)} {isCustom && <span className="nb-chip pink">MY KIT</span>}</h1>
      )}
      <p>A kit instantiates a research graph — questions, aims, methods, requirements — not just a dataset list.</p>

      <div className="nb-card" style={{ padding: 0, overflow: "hidden" }}>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src={`/img/kits/kit-${(String(d.slug).startsWith("my-") ? String(d.slug).split("-").slice(0, -1).join("-") : String(d.slug))}.png`} alt="Kit cover" width={800} height={450}
          style={{ width: "100%", height: "auto", display: "block", maxHeight: 360, objectFit: "cover" }}
          onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }} />
      </div>

      {!customising ? (
        <>
          <div className="grid cards">
            <Reveal cls="nb-card">{list("Suggested questions", d.questions as List)}</Reveal>
            <Reveal cls="nb-card">{list("Aim templates", d.aims as List)}</Reveal>
            <Reveal cls="nb-card">{list("Methods", d.methods as List)}</Reveal>
            <Reveal cls="nb-card">{list("Required roles", d.required_roles as List)}</Reveal>
          </div>
          {d.recommended_domains && list("Recommended domains", d.recommended_domains as List)}
          <div className="nb-card pop-in">
            <h2>Use this kit</h2>
            <label className="f">Study geography<input value={geo} onChange={(e) => setGeo(e.target.value)} /></label>
            <button className="nb-btn" onClick={() => instantiate()}>CREATE PROJECT FROM KIT →</button>{" "}
            <button className="nb-btn orange" style={{ background: "var(--nb-orange)" }} onClick={() => { setCustomising(true); setCustomSlug(`${slug}-my`); }}>CUSTOMISE THIS KIT</button>
            {isCustom && <button className="nb-btn secondary" onClick={removeCustom}>DELETE MY KIT</button>}
          </div>
        </>
      ) : (
        <>
          <div className="nb-card" style={{ background: "var(--nb-yellow)" }}>
            <h2>Customising — edit anything, then save as your own kit</h2>
            <p>Built-in kits stay untouched; your version gets its own page and can start projects.</p>
            <label className="f">Save as slug (lowercase, hyphens)<input value={customSlug} onChange={(e) => setCustomSlug(e.target.value)} placeholder="urban-heat-island-my" /></label>
            <button className="nb-btn" onClick={saveAsMyKit}>SAVE AS MY KIT →</button>{" "}
            <button className="nb-btn secondary" onClick={() => setCustomising(false)}>CANCEL</button>
            {msg && <p role="status">{msg}</p>}
          </div>
          {listEditor("Questions", questions, setQuestions)}
          {listEditor("Aims", aims, setAims)}
          {listEditor("Methods", methods, setMethods)}
          {listEditor("Required roles", roles, setRoles)}
        </>
      )}
    </div>
  );
}

function list(t: string, arr: List) {
  return (
    <div className="nb-card"><h2>{t}</h2><ul>{(arr || []).map((x, i) => <li key={i}>{x}</li>)}</ul></div>
  );
}
