// Isoloir keeps working without network once visited (metro, tunnels).
// Pages: network first, so they are always fresh when online; the saved copy is used offline.
// Built files, fonts and pictures: served from the saved copy. Nothing is ever sent anywhere.
const CACHE = "isoloir-v1";
const PAGES = ["/", "/quiz", "/resultats", "/methode"];

// "/quiz/", "/quiz?suite=1" and "/quiz" are the same page
const pageKey = (url) => {
  const u = new URL(url, self.location.origin);
  const path = u.pathname.replace(/\/index\.html$/, "/").replace(/(.)\/$/, "$1");
  return new URL(path, self.location.origin).href;
};

// a redirected response cannot be replayed for a navigation: keep only its body and headers
const plain = async (res) =>
  res.redirected ? new Response(await res.blob(), { status: res.status, headers: res.headers }) : res;

// built files and pictures linked from a page, fonts linked from a stylesheet,
// and the candidate portraits listed in the results page's data
const assetsOf = (text) => [...text.matchAll(/(?:src|href)="(\/(?:_astro|img)\/[^"]+)"|url\((\/_astro\/[^)]+\.woff2)\)|"(\/photos\/[^"]+\.jpg)"/g)]
  .map((m) => m[1] || m[2] || m[3]);

self.addEventListener("install", (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE);
    const assets = new Set();
    for (const page of PAGES) {
      try {
        const res = await fetch(page, { cache: "no-cache" });
        if (!res.ok) continue;
        assetsOf(await res.clone().text()).forEach((a) => assets.add(a));
        await cache.put(pageKey(page), await plain(res));
      } catch {}
    }
    // fonts are referenced from the stylesheets, not the pages
    for (const css of [...assets].filter((a) => a.endsWith(".css"))) {
      try { assetsOf(await (await fetch(css)).text()).forEach((a) => assets.add(a)); } catch {}
    }
    await Promise.all([...assets].map((a) => cache.add(a).catch(() => {})));
    await self.skipWaiting();
  })());
});

self.addEventListener("activate", (event) => {
  event.waitUntil((async () => {
    for (const key of await caches.keys()) if (key !== CACHE) await caches.delete(key);
    await self.clients.claim();
  })());
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET" || new URL(req.url).origin !== self.location.origin) return;

  if (req.mode === "navigate") {
    event.respondWith((async () => {
      const cache = await caches.open(CACHE);
      try {
        const res = await fetch(req);
        if (res.ok) cache.put(pageKey(req.url), await plain(res.clone()));
        return res;
      } catch {
        return (await cache.match(pageKey(req.url))) || (await cache.match(pageKey("/"))) || Response.error();
      }
    })());
    return;
  }

  // /_astro/ names change with their content, so a saved copy never goes stale;
  // pictures keep their names, so the saved copy is shown and refreshed in the background
  const hashed = new URL(req.url).pathname.startsWith("/_astro/");
  event.respondWith((async () => {
    const cache = await caches.open(CACHE);
    const hit = await cache.match(req, { ignoreSearch: true });
    const refresh = fetch(req).then((res) => {
      if (res.ok && res.type === "basic") cache.put(req, res.clone());
      return res;
    });
    if (hit) {
      if (!hashed) event.waitUntil(refresh.catch(() => {}));
      return hit;
    }
    return refresh;
  })());
});
