export default function About() {
  return (
    <div className="grid">
      <h1>ABOUT + DATA METHOD</h1>
      <div className="nb-card"><h2>What INQETRA is</h2><p>Research-design studio + UK dataset hub for climate, environment, buildings and the built environment. Problem → Gap → RQs → Aims → Methods → Requirements → Basket → Assignment → Compatibility → Gaps → Notes/Results → Abstract → Data Plan.</p></div>
      <div className="nb-card"><h2>Data method</h2><p>Seed metadata is staged, never silently upgraded. <em>link_type</em> and <em>verification_state</em> are preserved verbatim. Landing-page HTTP 200–399 proves reachability only — not download access, licence permission, scientific fitness or resolved metadata. Crawler output never publishes directly; candidates require provenance + link health + review.</p></div>
      <div className="nb-card"><h2>AI</h2><p>Optional and provider-neutral. Structures and drafts from project state; never invents datasets, licences, results, methods or citations. Every dataset claim needs dataset ID + field + source provenance.</p></div>
    </div>
  );
}
