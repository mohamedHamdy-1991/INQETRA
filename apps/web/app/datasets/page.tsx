"use client";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import { Badges, Empty, Provenance } from "../../components/chrome";
import { useBasket, useFetch } from "../../hooks/hooks";
import { CAVEAT, api } from "../../lib/api";

const DOMAINS = ["", "climate", "weather", "climate change", "environment", "air quality", "flooding", "buildings", "housing", "building performance", "energy/carbon", "planning", "geospatial"];

function Inner() {
  const sp = useSearchParams();
  const [q, setQ] = useState(sp.get("q") || sp.get("publisher") || "");
  const [domain, setDomain] = useState("");
  const [access, setAccess] = useState("");
  const [licence, setLicence] = useState("");
  const [openOnly, setOpenOnly] = useState(false);
  const [offset, setOffset] = useState(0);
  const basket = useBasket();
  const res = useFetch(() => api.datasets({ q, domain, access, licence, open_only: openOnly, limit: 24, offset }), [q, domain, access, licence, openOnly, offset]);

  return (
    <div className="grid">
      <h1>EXPLORE DATA</h1>
      <form className="filters" role="search" onSubmit={(e) => { e.preventDefault(); setOffset(0); }}>
        <label>Query<input value={q} onChange={(e) => setQ(e.target.value)} placeholder="e.g. HadUK-Grid, EPC, flood" aria-label="Query" /></label>
        <label>Domain<select value={domain} onChange={(e) => setDomain(e.target.value)} aria-label="Domain">{DOMAINS.map((d) => <option key={d} value={d}>{d || "All domains"}</option>)}</select></label>
        <label>Access<input value={access} onChange={(e) => setAccess(e.target.value)} placeholder="Open…" aria-label="Access" /></label>
        <label>Licence<input value={licence} onChange={(e) => setLicence(e.target.value)} placeholder="OGL…" aria-label="Licence" /></label>
        <label>Open only<input type="checkbox" checked={openOnly} onChange={(e) => setOpenOnly(e.target.checked)} aria-label="Open only" /></label>
        <button className="nb-btn" type="submit">APPLY</button>
      </form>
      {res.loading && <p role="status">Loading catalogue…</p>}
      {res.error && <p className="warn" role="alert">Catalogue error: {res.error}. The public catalogue stays available during worker outages.</p>}
      {res.data && <p role="status"><strong>{res.data.total}</strong> datasets · Search relevance — not dataset quality. {CAVEAT}</p>}
      <div className="grid cards">
        {(res.data?.items || []).map((d: Record<string, string>) => (
          <article className="nb-card" key={d.id}>
            <h3><Link href={`/datasets/${d.id}`}>{d.title}</Link></h3>
            <Badges item={d} />
            <p>{d.subdomain} · {d.coverage} · {d.temporal_resolution}</p>
            <Provenance item={d} />
            <p>
              <button className="nb-btn secondary" onClick={() => basket.add(d.id)} aria-label={`Add ${d.title} to basket`}>ADD TO BASKET</button>{" "}
              <Link className="nb-btn secondary" href={`/compare?ids=${d.id}`}>COMPARE</Link>{" "}
              <Link className="nb-btn" href={`/datasets/${d.id}`}>VIEW</Link>
            </p>
          </article>
        ))}
      </div>
      {!res.loading && res.data?.items.length === 0 && <Empty title="No datasets match" hint="Loosen filters or try a publisher name (e.g. Met Office, ONS, Environment Agency)." />}
      <p>
        <button className="nb-btn secondary" disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - 24))}>← PREV</button>{" "}
        <button className="nb-btn secondary" disabled={!res.data || offset + 24 >= res.data.total} onClick={() => setOffset(offset + 24)}>NEXT →</button>
      </p>
    </div>
  );
}

export default function Page() {
  return <Suspense fallback={<p>Loading…</p>}><Inner /></Suspense>;
}
