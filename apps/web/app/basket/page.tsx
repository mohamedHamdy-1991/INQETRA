"use client";
import Link from "next/link";
import { api } from "../../lib/api";
import { useBasket, useFetch } from "../../hooks/hooks";

export default function Basket() {
  const b = useBasket();
  const info = useFetch(
    () => (b.ids.length ? api.info(b.ids) : Promise.resolve({ items: [] })),
    [b.ids.join(",")],
  );
  return (
    <div className="grid">
      <h1>BASKET ({b.count})</h1>
      <p>Persistent selection (this browser) — assign items to a project aim inside the Studio for persistent database state.</p>
      {b.ids.length === 0 ? (
        <div className="nb-card">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/img/empty/empty-basket.png" alt="An empty woven basket" width={450} height={300} style={{ maxWidth: "100%", height: "auto" }} />
          <h2>Empty basket</h2>
          <p><Link href="/datasets">Explore datasets</Link> and ADD TO BASKET.</p>
        </div>
      ) : (
        <ul>
          {((info.data?.items || []) as Record<string, string>[]).map((d) => (
            <li key={d.id}>
              <Link href={`/datasets/${d.id}`}>{d.title}</Link> <small>({d.id} · {d.publisher})</small>{" "}
              <button className="nb-btn secondary" onClick={() => b.remove(d.id)}>REMOVE</button>
            </li>
          ))}
          {b.items.filter((i) => !(info.data?.items || []).some((d: Record<string, string>) => d.id === i.id))
            .map((i) => <li key={i.id}><Link href={`/datasets/${i.id}`}>{i.id}</Link> <button className="nb-btn secondary" onClick={() => b.remove(i.id)}>REMOVE</button></li>)}
        </ul>
      )}
      <p>
        <Link className="nb-btn orange" href="/basket/report" style={{ background: "var(--nb-orange)" }}>BASKET DATA REPORT →</Link>{" "}
        <Link className="nb-btn secondary" href={`/compare?ids=${b.ids.slice(0, 4).join(",")}`}>COMPARE SELECTION</Link>{" "}
        <button className="nb-btn secondary" onClick={b.clear}>CLEAR</button>
      </p>
    </div>
  );
}
