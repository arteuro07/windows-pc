const HTML = `<!doctype html><meta name=viewport content="width=device-width,initial-scale=1">
<body style="font-family:sans-serif;max-width:420px;margin:24px auto;padding:0 16px">
<h2>Robot MT5 démo</h2>
<label>Mot de passe</label>
<input id=k type=password style="width:100%;padding:10px;margin:4px 0 12px">
<label>Durée (minutes)</label>
<input id=m value=120 style="width:100%;padding:10px;margin:4px 0 12px">
<label>Catégories</label>
<input id=c value="Forex,Metals,Crypto,Indices" style="width:100%;padding:10px;margin:4px 0 12px">
<label>Stratégies</label>
<input id=s value="booster,ema" style="width:100%;padding:10px;margin:4px 0 12px">
<button onclick="go()" style="width:100%;padding:14px;font-size:16px">Lancer le robot</button>
<p id=o></p>
<script>async function go(){o.textContent='...';const r=await fetch('/run',{method:'POST',headers:{'x-key':k.value},body:JSON.stringify({minutes:m.value,categories:c.value,strategies:s.value})});o.textContent=await r.text()}</script>`;
export default {
  async fetch(req, env) {
    const u = new URL(req.url);
    if (u.pathname === "/run" && req.method === "POST") {
      if (req.headers.get("x-key") !== env.PANEL_KEY) return new Response("Mot de passe incorrect", { status: 401 });
      const b = await req.json().catch(() => ({}));
      const r = await fetch("https://api.github.com/repos/arteuro07/windows-pc/actions/workflows/mt5.yml/dispatches", {
        method: "POST",
        headers: { Authorization: "Bearer " + env.GH_TOKEN, "User-Agent": "mt5-panel", Accept: "application/vnd.github+json" },
        body: JSON.stringify({ ref: "main", inputs: {
          minutes: String(b.minutes || 5),
          categories: String(b.categories || "Forex,Metals,Crypto,Indices"),
          strategies: String(b.strategies || "booster,ema"),
        } }),
      });
      return new Response(r.status === 204 ? "Robot lancé" : "Erreur " + r.status, { status: r.ok ? 200 : 500 });
    }
    return new Response(HTML, { headers: { "content-type": "text/html;charset=utf-8" } });
  },
};
