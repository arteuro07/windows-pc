const HTML = `<!doctype html><meta name=viewport content="width=device-width,initial-scale=1">
<body style="font-family:sans-serif;max-width:420px;margin:24px auto;padding:0 16px">
<h2>Robot MT5 démo</h2>
<input id=k type=password placeholder="Mot de passe" style="width:100%;padding:10px;margin:6px 0">
<input id=m value=5 style="width:100%;padding:10px;margin:6px 0">
<button onclick="go()" style="width:100%;padding:14px;font-size:16px">Lancer</button>
<p id=o></p>
<script>async function go(){const r=await fetch('/run',{method:'POST',headers:{'x-key':k.value},body:JSON.stringify({minutes:m.value})});o.textContent=await r.text()}</script>`;
export default {
  async fetch(req, env) {
    const u = new URL(req.url);
    if (u.pathname === "/run" && req.method === "POST") {
      if (req.headers.get("x-key") !== env.PANEL_KEY) return new Response("Mot de passe incorrect", { status: 401 });
      const b = await req.json().catch(() => ({}));
      const r = await fetch("https://api.github.com/repos/arteuro07/windows-pc/actions/workflows/mt5.yml/dispatches", {
        method: "POST",
        headers: { Authorization: "Bearer " + env.GH_TOKEN, "User-Agent": "mt5-panel", Accept: "application/vnd.github+json" },
        body: JSON.stringify({ ref: "main", inputs: { minutes: String(b.minutes || 5) } }),
      });
      return new Response(r.status === 204 ? "Robot lancé" : "Erreur " + r.status, { status: r.ok ? 200 : 500 });
    }
    return new Response(HTML, { headers: { "content-type": "text/html;charset=utf-8" } });
  },
};
