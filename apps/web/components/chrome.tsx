"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { useBasket, useFetch } from "../hooks/hooks";
import { api } from "../lib/api";

const NAV: [string, string][] = [
  ["/", "HOME"], ["/datasets", "EXPLORE DATA"], ["/datasets/all", "ALL DATA (A–Z)"],
  ["/map", "DATA MAP"], ["/compare", "COMPARE"], ["/kits", "KITS"],
  ["/sources", "SOURCES"], ["/publishers", "PUBLISHERS"], ["/paths", "PATHS"], ["/projects", "MY PROJECTS"],
  ["/basket", "BASKET"], ["/methodology", "METHODOLOGY"],
  ["/about", "ABOUT & DATA METHOD"], ["/developers", "API"], ["/admin", "ADMIN"],
];

export function Shell({ children }: { children: React.ReactNode }) {
  const path = usePathname();
  const basket = useBasket();
  const [drawer, setDrawer] = useState(false);
  const [menu, setMenu] = useState(false);
  return (
    <>
      <a className="skip" href="#main">Skip to content</a>
      <div className="shell">
        <aside className="rail" aria-label="Primary">
          <Link className="brand" href="/" aria-label="INQETRA home">
            <img src="/logo.png" alt="INQETRA mark" width={36} height={36} />
            <span>INQETRA<small>RESEARCH DATA NAVIGATOR</small></span>
          </Link>
          <nav>
            <ul>
              {NAV.map(([href, label]) => (
                <li key={href}>
                  <Link href={href} aria-current={path === href ? "page" : undefined}
                    className={path === href ? "active" : ""}>
                    {label}{href === "/basket" ? ` (${basket.count})` : ""}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>
          <p className="railnote">Official links + provenance first. Reachability ≠ permission or fitness.</p>
        </aside>
        <div className="main">
          <header className="topbar">
            <button className="nb-btn secondary menubtn" aria-expanded={menu} aria-controls="mobilenav-panel"
              onClick={() => setMenu((v) => !v)}>
              {menu ? "✕ CLOSE" : "☰ MENU"}
            </button>
            <form className="gsearch" action="/datasets" role="search">
              <label className="sr" htmlFor="gq">Search datasets</label>
              <input id="gq" name="q" placeholder="Search datasets, variables, places, methods…" autoComplete="off" />
              <button className="nb-btn secondary" type="submit">SEARCH</button>
            </form>
            <div className="topactions">
              <Link className="nb-btn secondary" href="/projects">MY PROJECTS</Link>
              <button className="nb-btn" onClick={() => setDrawer(true)} aria-haspopup="dialog">
                BASKET ({basket.count})
              </button>
            </div>
          </header>
          {menu && (
            <nav id="mobilenav-panel" className="mobilenav-panel" aria-label="All pages">
              <ul>
                {NAV.map(([href, label]) => (
                  <li key={href}>
                    <Link href={href} aria-current={path === href ? "page" : undefined}
                      className={path === href ? "active" : ""}
                      onClick={() => setMenu(false)}>
                      {label}{href === "/basket" ? ` (${basket.count})` : ""}
                    </Link>
                  </li>
                ))}
              </ul>
            </nav>
          )}
          <main id="main" tabIndex={-1}>{children}</main>
          <footer className="foot">
            <span>INQETRA · Turn research questions into executable data plans.</span>
            <span>WCAG 2.2 AA target · Keyboard: Tab / Shift+Tab / Enter · Reduced motion respected.</span>
          </footer>
        </div>
      </div>
      {drawer && <BasketDrawer onClose={() => setDrawer(false)} />}
      <nav className="mobilenav" aria-label="Quick pages">
        <Link href="/">HOME</Link><Link href="/datasets">DATA</Link>
        <Link href="/projects">PROJECTS</Link><Link href="/basket">BASKET ({basket.count})</Link>
      </nav>
    </>
  );
}

export function BasketDrawer({ onClose }: { onClose: () => void }) {
  const basket = useBasket();
  const projects = useFetch(() => api.projects(), []);
  const [pid, setPid] = useState("");
  const [msg, setMsg] = useState("");
  async function saveToProject() {
    if (!pid) { setMsg("Choose a project first (or create one in MY PROJECTS)."); return; }
    try {
      for (const it of basket.items) {
        await api.post(`/api/v1/projects/${pid}/basket`, { dataset_id: it.id, rationale: "Saved from basket drawer" }).catch(() => null);
      }
      setMsg(`Saved ${basket.items.length} item(s) to project. Open the studio to assign them to aims.`);
    } catch (e) { setMsg(String(e)); }
  }
  return (
    <div role="dialog" aria-modal="true" aria-label="Basket" className="drawer-wrap" onClick={onClose}>
      <div className="drawer drawer-slide" onClick={(e) => e.stopPropagation()}>
        <h2>BASKET ({basket.count})</h2>
        {basket.items.length === 0 && <p>No datasets yet. Use ADD TO BASKET on any dataset card.</p>}
        <ul>{basket.items.map((i) => (
          <li key={i.id}><Link href={`/datasets/${i.id}`}>{i.title}</Link>{" "}
            <button className="nb-btn secondary" onClick={() => basket.remove(i.id)} aria-label={`Remove ${i.title}`}>×</button></li>
        ))}</ul>
        <label className="f">Save to project
          <select value={pid} onChange={(e) => setPid(e.target.value)}>
            <option value="">— choose —</option>
            {(projects.data?.items || []).map((p: Record<string, string>) => <option key={p.id} value={p.id}>{p.title}</option>)}
          </select>
        </label>
        <p>
          <button className="nb-btn" onClick={saveToProject}>SAVE TO PROJECT</button>{" "}
          <Link className="nb-btn secondary" href="/basket" onClick={onClose}>OPEN BASKET PAGE</Link>{" "}
          <button className="nb-btn secondary" onClick={onClose}>CLOSE</button>
        </p>
        {msg && <p role="status">{msg}</p>}
      </div>
    </div>
  );
}

export function Badges({ item }: { item: Record<string, string> }) {
  return (
    <div className="badges" aria-label="Authority, access and licence">
      <span className="nb-chip">{item.authority_level || "Unknown"}</span>
      <span className="nb-chip cyan">{item.access_type || "Unknown"}</span>
      <span className="nb-chip violet">{item.link_type || ""}</span>
      <span className="nb-chip green">{item.verification_state || ""}</span>
    </div>
  );
}

export function Provenance({ item }: { item: Record<string, string> }) {
  return (
    <p className="prov">
      Source: {item.publisher} · <a href={item.landing_url} target="_blank" rel="noreferrer">Official landing page</a> ·
      reviewed {item.last_catalogue_review} · Licence: {item.licence || "Unknown — read the source before reuse."}
    </p>
  );
}

export function Empty({ title, hint }: { title: string; hint: string }) {
  return <div className="nb-card" role="status"><h3>{title}</h3><p>{hint}</p></div>;
}
