"use client";
import Link from "next/link";
import { Badges } from "../../../components/chrome";
import { Reveal } from "../../../components/reveal";
import { ThumbImg } from "../../../components/thumb";
import { useBasket, useFetch } from "../../../hooks/hooks";
import { api } from "../../../lib/api";

export default function PublisherDetail({ params }: { params: { name: string } }) {
  const pub = decodeURIComponent(params.name);
  const r = useFetch(() => api.datasets({ publisher: pub, limit: 200, offset: 0 }), [pub]);
  const basket = useBasket();
  if (r.loading) return <p role="status">Loading publisher…</p>;
  if (r.error || !r.data) return <p className="warn">{String(r.error)}</p>;
  return (
    <div className="grid">
      <p><Link href="/publishers">← Publishers</Link></p>
      <h1>{pub}</h1>
      <p role="status">{r.data.total} datasets. Access/licence patterns are source-declared — public availability ≠ permission.</p>
      <div className="grid cards">
        {(r.data.items || []).map((d: Record<string, string>, i: number) => (
          <Reveal as="article" key={d.id} delay={Math.min(i * 0.02, 0.2)} cls="nb-card">
            <ThumbImg id={d.id} title={d.title} domain={d.domain} />
            <h3><Link href={`/datasets/${d.id}`}>{d.title}</Link></h3>
            <Badges item={d} />
            <p>
              {basket.has(d.id)
                ? <button className="nb-btn secondary" onClick={() => basket.remove(d.id)}>✓ IN BASKET</button>
                : <button className="nb-btn secondary" onClick={() => basket.add(d.id, d.title)}>ADD TO BASKET</button>}{" "}
              <Link className="nb-btn" href={`/datasets/${d.id}`}>VIEW</Link>
            </p>
          </Reveal>
        ))}
      </div>
    </div>
  );
}
