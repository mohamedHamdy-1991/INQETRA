"use client";
import Link from "next/link";
import { Badges } from "../../../components/chrome";
import { Reveal } from "../../../components/reveal";
import { ThumbImg } from "../../../components/thumb";
import { useBasket, useFetch } from "../../../hooks/hooks";
import { api } from "../../../lib/api";

export default function AllData() {
  const all = useFetch(() => api.datasets({ limit: 200, offset: 0 }).then(async (first) => {
    const pages = [first];
    for (let off = 200; off < first.total; off += 200) {
      pages.push(await api.datasets({ limit: 200, offset: off }));
    }
    return { total: first.total, items: pages.flatMap((p) => p.items) };
  }), []);
  const basket = useBasket();
  if (all.loading) return <div className="grid">{[0, 1, 2].map((i) => <div className="skel" key={i} role="status" aria-label="Loading catalogue" />)}</div>;
  if (all.error) return <p className="warn" role="alert">Catalogue error: {all.error}</p>;
  const groups = new Map<string, Record<string, string>[]>();
  for (const d of (all.data?.items ?? []) as Record<string, string>[]) {
    const k = d.domain || "Unclassified";
    if (!groups.has(k)) groups.set(k, []);
    groups.get(k)!.push(d);
  }
  const names = [...groups.keys()].sort();
  return (
    <div className="grid">
      <h1>ALL DATA — DIVIDED BY DOMAIN</h1>
      <p role="status"><strong>{all.data?.total ?? 0}</strong> datasets in {names.length} domains. Landing-page reachability ≠ permission or fitness.</p>
      <nav aria-label="Domains" className="filters">
        {names.map((n) => <a key={n} className="nb-btn secondary" href={`#dom-${encodeURIComponent(n)}`}>{n} ({groups.get(n)!.length})</a>)}
      </nav>
      {names.map((n) => (
        <section key={n} id={`dom-${encodeURIComponent(n)}`} aria-label={n}>
          <h2>{n} ({groups.get(n)!.length})</h2>
          <div className="grid cards">
            {groups.get(n)!.map((d, i) => (
              <Reveal as="article" key={d.id} delay={Math.min(i * 0.03, 0.3)} cls="nb-card pop-in">
                <ThumbImg id={d.id} title={d.title} domain={d.domain} />
                <h3><Link href={`/datasets/${d.id}`}>{d.title}</Link></h3>
                <Badges item={d} />
                <p>{d.coverage} · {d.temporal_resolution}</p>
                <p>
                  {basket.has(d.id)
                    ? <button className="nb-btn secondary" onClick={() => basket.remove(d.id)}>✓ IN BASKET — REMOVE</button>
                    : <button className="nb-btn secondary" onClick={() => basket.add(d.id, d.title)}>ADD TO BASKET</button>}{" "}
                  <Link className="nb-btn" href={`/datasets/${d.id}`}>VIEW</Link>
                </p>
              </Reveal>
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}
