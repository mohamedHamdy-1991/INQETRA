"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { api } from "../../../../lib/api";
import { useFetch } from "../../../../hooks/hooks";

export default function Abstract({ params }: { params: { id: string } }) {
  const id = params.id;
  const proj = useFetch(() => api.project(id), [id]);
  const t = useFetch(() => api.get(`/api/v1/projects/${id}/abstract/traces`), [id]);
  const [mode, setMode] = useState("proposal");
  const [limit, setLimit] = useState(250);
  const [draft, setDraft] = useState<Record<string, unknown> | null>(null);
  const [msg, setMsg] = useState("");
  const [editing, setEditing] = useState(false);
  const [text, setText] = useState("");
  const [add, setAdd] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);

  const pathSlug = (proj.data as Record<string, string> | null)?.export_path || "";
  const path = useFetch(() => (pathSlug ? api.get(`/api/v1/paths/${pathSlug}`) : Promise.resolve(null)), [pathSlug]);

  useEffect(() => { if (draft) { setText(String((draft as Record<string, unknown>).text ?? "")); setEditing(false); } }, [draft]);

  async function saveEdit() {
    if (!draft) return;
    setSaving(true);
    try {
      const updated = await api.patch(`/api/v1/projects/${id}/abstract/${(draft as Record<string, string>).id}`, { text });
      setDraft({ ...draft, ...updated });
      setMsg("Your edits are saved.");
      t.reload();
    } catch (e) { setMsg(String(e)); }
    setSaving(false);
  }

  async function quickAdd(kind: "questions" | "aims" | "methods") {
    const v = (add[kind] || "").trim();
    if (!v) return;
    try {
      if (kind === "questions") await api.post(`/api/v1/projects/${id}/questions`, { text: v });
      if (kind === "aims") await api.post(`/api/v1/projects/${id}/aims`, { title: v, statement: v });
      if (kind === "methods") await api.post(`/api/v1/projects/${id}/methods`, { name: v, purpose: "Added from abstract builder" });
      setAdd((a) => ({ ...a, [kind]: "" }));
      setMsg(`Added: ${v}. Re-draft to include it.`);
      proj.reload();
    } catch (e) { setMsg(String(e)); }
  }

  return (
    <div className="grid">
      <h1>ABSTRACT BUILDER</h1>
      <p>Sentences draw from project objects only. Results require researcher-entered Result objects. Every draft is editable — your words, saved verbatim.</p>

      {pathSlug && path.data && (
        <section className="nb-card" style={{ background: "var(--nb-cyan)" }}>
          <h2>YOUR PATH: {path.data.title}</h2>
          <p>Abstract target {((path.data.sections as Record<string, string>[])[0] || {}).words} words. Full skeleton in <Link href="/paths">PATHS</Link>.</p>
          <div className="grid cards">
            {(path.data.sections as Record<string, string>[]).slice(0, 4).map((s) => (
              <div key={s.heading} className="nb-card" style={{ background: "var(--nb-surface)" }}>
                <h3>{s.heading} <small style={{ fontWeight: 700 }}>({s.words} words)</small></h3>
                <p>{s.guidance}</p>
                <p><em>“{s.starters[0]}”</em></p>
              </div>
            ))}
          </div>
        </section>
      )}

      <div className="nb-card">
        <h2>1 · Generate a draft (or start blank)</h2>
        <div className="grid" style={{ gridTemplateColumns: "1fr 1fr", gap: 12 }}>
          <label className="f">Mode<select value={mode} onChange={(e) => setMode(e.target.value)}>{["proposal", "thesis", "journal", "conference", "grant", "extended", "plain"].map((m) => <option key={m}>{m}</option>)}</select></label>
          <label className="f">Word limit<input type="number" value={limit} onChange={(e) => setLimit(Number(e.target.value))} min={50} max={1000} /></label>
        </div>
        <button className="nb-btn" onClick={async () => { try { setDraft(await api.post(`/api/v1/projects/${id}/abstract/draft`, { mode, word_limit: limit })); } catch (e) { setMsg(String(e)); } }}>DRAFT ABSTRACT</button>{" "}
        <button className="nb-btn secondary" onClick={async () => { try { setDraft(await api.post(`/api/v1/projects/${id}/abstract/blank`, {})); setMsg("Blank page created — write what you want."); } catch (e) { setMsg(String(e)); } }}>START FROM BLANK PAGE</button>
      </div>

      {draft && (
        <section className="nb-card" style={{ background: "var(--nb-yellow)" }}>
          <h2>2 · Your abstract — edit freely</h2>
          {editing ? (
            <>
              <label className="f">Abstract text<textarea rows={12} value={text} onChange={(e) => setText(e.target.value)} style={{ background: "#fff" }} /></label>
              <button className="nb-btn" disabled={saving} onClick={saveEdit}>{saving ? "SAVING…" : "SAVE MY ABSTRACT"}</button>{" "}
              <button className="nb-btn secondary" onClick={() => { setText(String((draft as Record<string, unknown>).text ?? "")); setEditing(false); }}>DISCARD EDITS</button>
            </>
          ) : (
            <>
              <p style={{ fontSize: 17, lineHeight: 1.7, whiteSpace: "pre-wrap" }}>{String((draft as Record<string, unknown>).text) || <em>(empty — write your abstract here)</em>}</p>
              <button className="nb-btn" onClick={() => setEditing(true)}>EDIT THIS TEXT</button>
              <p><small>{String(text || (draft as Record<string, unknown>).text || "").split(/\s+/).filter(Boolean).length} words · target {String((draft as Record<string, unknown>).word_limit)}</small></p>
            </>
          )}
          <details>
            <summary><strong>Evidence trace</strong></summary>
            <ul>{((draft as Record<string, unknown>).traces as { text: string; sources: string[] }[] | undefined)?.map((tr, i) => <li key={i}>{tr.text} <em>← {tr.sources.join(", ")}</em></li>)}</ul>
          </details>
        </section>
      )}

      <section className="nb-card">
        <h2>3 · Missing something? Add it here</h2>
        <p>Added items enter the project graph; generate a new draft to weave them in.</p>
        {([["questions", "Research question"], ["aims", "Aim"], ["methods", "Method"]] as const).map(([kind, label]) => (
          <div key={kind} style={{ display: "flex", gap: 8, alignItems: "end", flexWrap: "wrap", marginBottom: 8 }}>
            <label className="f" style={{ flex: 1, minWidth: 220 }}>{label}
              <input value={add[kind] || ""} placeholder={`New ${label.toLowerCase()}…`} onChange={(e) => setAdd((a) => ({ ...a, [kind]: e.target.value }))} />
            </label>
            <button className="nb-btn secondary" onClick={() => quickAdd(kind)}>+ ADD {label.toUpperCase()}</button>
          </div>
        ))}
        <p>Project currently has: {(proj.data?.questions || []).length} question(s) · {(proj.data?.aims || []).length} aim(s) · {(proj.data?.methods || []).length} method(s). <Link href={`/projects/${id}/studio`}>Open studio →</Link></p>
      </section>

      {msg && <p role="status">{msg}</p>}

      <h2>History</h2>
      {(t.data?.items || []).map((d: Record<string, string>) => (
        <div className="nb-card" key={d.id}>
          <h3>{d.mode} · {d.word_limit} words</h3>
          <p style={{ whiteSpace: "pre-wrap" }}>{(d.text || "").slice(0, 400)}{(d.text || "").length > 400 ? "…" : ""}</p>
          <button className="nb-btn secondary" onClick={async () => { try { const full = await api.get(`/api/v1/projects/${id}/abstract/drafts/${d.id}`); setDraft(full as Record<string, unknown>); window.scrollTo({ top: 0, behavior: "smooth" }); } catch (e) { setMsg(String(e)); } }}>OPEN IN EDITOR</button>
        </div>
      ))}
    </div>
  );
}
