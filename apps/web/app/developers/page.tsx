"use client";
import { useFetch } from "../../hooks/hooks";
import { api } from "../../lib/api";

export default function Developers() {
  const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const tax = useFetch(() => api.taxonomy(), []);
  return (
    <div className="grid">
      <h1>DEVELOPER API</h1>
      <p><a className="nb-btn" href={`${API}/docs`} target="_blank" rel="noreferrer">OPENAPI / DOCS</a> <a className="nb-btn secondary" href={`${API}/api/v1/openapi.json`} target="_blank" rel="noreferrer">OPENAPI JSON</a></p>
      <div className="nb-card"><h2>Catalogue</h2><pre>GET /api/v1/datasets?q=&amp;domain=&amp;geography=&amp;access=&amp;licence=&amp;publisher=&amp;open_only=&amp;limit=&amp;offset={"{}"}</pre><pre>GET /api/v1/datasets/{"{id}"} · POST /api/v1/datasets/compare · GET /api/v1/datasets/views/csv|json|markdown</pre></div>
      <div className="nb-card"><h2>Projects</h2><pre>POST /api/v1/projects · GET/PATCH /api/v1/projects/{"{id}"} · questions/aims/hypotheses/methods/requirements/notes/results/basket · matrices/rq-aim|aim-method|aim-dataset</pre></div>
      <div className="nb-card"><h2>Evaluation + reports</h2><pre>POST /api/v1/projects/{"{id}"}/evaluate · GET compatibility|gaps · POST requirements/{"{rid}"}/find-data · candidates/{"{cid}"}/resolve|reject|curate · abstract/draft · report-model · export?format=markdown|json</pre></div>
      {tax.data && <div className="nb-card"><h2>Taxonomy</h2><p>{tax.data.domains.length} domains · {tax.data.research_roles.length} roles</p></div>}
    </div>
  );
}
