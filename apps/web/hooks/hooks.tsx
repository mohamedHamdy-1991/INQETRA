"use client";
import { useCallback, useEffect, useState } from "react";

export function useFetch<T>(fn: () => Promise<T>, deps: unknown[] = []) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string>("");
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    let live = true;
    setLoading(true);
    fn().then((d) => live && setData(d)).catch((e) => live && setError(String(e))).finally(() => live && setLoading(false));
    return () => { live = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
  return { data, error, loading, reload: () => setLoading(true) };
}

export type BasketItem = { id: string; title: string };

function readBasket(): BasketItem[] {
  try {
    const raw = JSON.parse(localStorage.getItem("inqetra-basket") || "[]");
    if (Array.isArray(raw) && raw.length && typeof raw[0] === "string")
      return (raw as string[]).map((id) => ({ id, title: id })); // migrate v1 shape
    return raw as BasketItem[];
  } catch { return []; }
}

export function useBasket() {
  const [items, setItems] = useState<BasketItem[]>([]);
  useEffect(() => {
    setItems(readBasket());
    const on = (e: Event) => { try { setItems((e as CustomEvent).detail); } catch { /* noop */ } };
    window.addEventListener("inqetra-basket", on);
    return () => window.removeEventListener("inqetra-basket", on);
  }, []);
  const save = useCallback((next: BasketItem[]) => {
    setItems(next);
    try {
      localStorage.setItem("inqetra-basket", JSON.stringify(next));
      window.dispatchEvent(new CustomEvent("inqetra-basket", { detail: next }));
    } catch { /* private mode */ }
  }, []);
  const ids = items.map((i) => i.id);
  return {
    items, ids,
    count: items.length,
    has: (id: string) => ids.includes(id),
    add: (id: string, title?: string) => { if (!ids.includes(id)) save([...items, { id, title: title || id }]); },
    remove: (id: string) => save(items.filter((x) => x.id !== id)),
    clear: () => save([]),
  };
}
