import re, sys, os
p = "worker.js"
if not os.path.exists(p):
    print("ECHEC : worker.js introuvable."); sys.exit(1)
s = open(p, encoding="utf-8").read()
if "/*v2*/" in s:
    print("Design deja applique."); sys.exit(0)
if s.count("<style>") != 1 or s.count("</style>") != 1:
    print("ECHEC : bloc de style introuvable. Rien modifie. Envoie-moi ce message."); sys.exit(1)
CSS = r'''/*v2*/
:root{--bg:#06080a;--bg2:#0a0d10;--panel:#0e1215;--panel2:#141a1e;--line:#1d252a;--line2:#2a343a;--ink:#eef0ea;--mut:#7f8a92;--gold:#e3b559;--gold2:#c4912f;--up:#3ddc97;--down:#ff6b5e;--mono:ui-monospace,SFMono-Regular,"JetBrains Mono",Menlo,Consolas,monospace;--r:16px;color-scheme:dark}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
[hidden]{display:none!important}
html{background:var(--bg)}
body{margin:0;color:var(--ink);font:15px/1.5 -apple-system,BlinkMacSystemFont,"Inter","Segoe UI",Roboto,system-ui,sans-serif;-webkit-font-smoothing:antialiased;
 background:radial-gradient(120% 60% at 50% -10%,#1d1709 0%,rgba(29,23,9,0) 60%),radial-gradient(80% 40% at 100% 30%,#0b1a14 0%,rgba(11,26,20,0) 70%),var(--bg);
 background-attachment:fixed;
 padding:max(16px,env(safe-area-inset-top)) max(16px,env(safe-area-inset-right)) 56px max(16px,env(safe-area-inset-left))}
.wrap{max-width:560px;margin:0 auto;display:flex;flex-direction:column;gap:16px;min-width:0}
.wrap>.wrap{animation:rise .5s ease both}
@keyframes rise{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}

/* en-tete */
.top{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:6px 2px 2px}
.brand{font-weight:800;letter-spacing:.32em;font-size:13px;color:var(--ink);display:flex;align-items:center;gap:10px}
.brand::before{content:"";width:26px;height:26px;border-radius:8px;box-shadow:0 0 20px #e3b55955;background:url("data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 26 26%27%3E%3Cdefs%3E%3ClinearGradient id=%27g%27 x1=%270%27 y1=%270%27 x2=%271%27 y2=%271%27%3E%3Cstop offset=%270%27 stop-color=%27%23f0c76a%27/%3E%3Cstop offset=%271%27 stop-color=%27%23c4912f%27/%3E%3C/linearGradient%3E%3C/defs%3E%3Crect width=%2726%27 height=%2726%27 rx=%278%27 fill=%27url(%23g)%27/%3E%3Cpath d=%27M5.5 18 L10 12.5 L13.5 15.5 L20.5 7.5%27 fill=%27none%27 stroke=%27%231a1204%27 stroke-width=%272.4%27 stroke-linecap=%27round%27 stroke-linejoin=%27round%27/%3E%3Ccircle cx=%2720.5%27 cy=%277.5%27 r=%272%27 fill=%27%231a1204%27/%3E%3C/svg%3E") center/100% 100% no-repeat}
.sub{color:var(--mut);font-size:12.5px;margin-top:2px;letter-spacing:.01em}
.pill{display:flex;align-items:center;gap:8px;border:1px solid var(--line2);background:#0c1013cc;border-radius:999px;padding:7px 13px;font-size:11px;font-weight:700;letter-spacing:.14em;white-space:nowrap;color:var(--mut)}
.pill i{width:8px;height:8px;border-radius:50%;background:var(--mut)}
.pill.run{color:var(--up);border-color:#1f5a40;background:#0b1a14cc}
.pill.run i{background:var(--up);box-shadow:0 0 0 0 #3ddc9788;animation:ping 1.8s ease-out infinite}
.pill.boot{color:var(--gold);border-color:#5a4720;background:#1a1409cc}
.pill.boot i{background:var(--gold);animation:blink 1.2s ease-in-out infinite}
@keyframes ping{0%{box-shadow:0 0 0 0 #3ddc9799}80%,100%{box-shadow:0 0 0 9px #3ddc9700}}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}
@media (prefers-reduced-motion:reduce){.pill i,.wrap>.wrap{animation:none!important}}

/* cartes */
.card{position:relative;background:linear-gradient(180deg,#11171a 0%,#0d1114 100%);border:1px solid var(--line);border-radius:var(--r);padding:18px;min-width:0;box-shadow:0 1px 0 #ffffff08 inset,0 18px 40px -24px #000}
.lbl{font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--mut);font-weight:700}
h2{margin:6px 0 10px;font-size:10.5px;letter-spacing:.18em;text-transform:uppercase;color:var(--mut);font-weight:700;display:flex;align-items:center;gap:10px}
h2::before{content:"";width:3px;height:12px;border-radius:2px;background:linear-gradient(var(--gold),var(--gold2))}
section>h2{padding-left:2px}

/* equite */
.card:first-child{border-color:#2c2614;background:radial-gradient(120% 90% at 0% 0%,#1b1609 0%,rgba(27,22,9,0) 55%),linear-gradient(180deg,#11171a,#0d1114)}
.big{font:700 42px/1.1 var(--mono);letter-spacing:-.03em;margin-top:6px;font-variant-numeric:tabular-nums;background:linear-gradient(180deg,#fff 0%,#e9d8ad 100%);-webkit-background-clip:text;background-clip:text;color:transparent}
.pnl{display:flex;width:fit-content;max-width:100%;align-items:center;gap:6px;font:600 13px var(--mono);margin-top:10px;min-height:28px;padding:4px 11px;border-radius:999px;background:#ffffff0a;color:var(--mut);font-variant-numeric:tabular-nums}
.pnl.up{background:#3ddc9718;color:var(--up)}
.pnl.down{background:#ff6b5e18;color:var(--down)}
.pnl:empty{display:none}
.kpis{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:0;margin-top:18px;padding-top:16px;border-top:1px solid var(--line)}
.kpis>div{padding:0 12px;border-left:1px solid var(--line)}
.kpis>div:first-child{padding-left:0;border-left:0}
.kpis b{display:block;font:600 17px var(--mono);margin-top:4px;font-variant-numeric:tabular-nums}
.up{color:var(--up)}.down{color:var(--down)}.mut{color:var(--mut)}

/* graphique */
svg{width:100%;height:auto;display:block;margin-top:10px}
.grid{stroke:var(--line2);stroke-dasharray:2 5;stroke-width:1}
.ln{fill:none;stroke-width:2.2;stroke-linejoin:round;stroke-linecap:round}
.ln.u{stroke:var(--up);filter:drop-shadow(0 0 5px #3ddc9766)}
.ln.d{stroke:var(--down);filter:drop-shadow(0 0 5px #ff6b5e66)}
.area.u{fill:var(--up);opacity:.16}.area.d{fill:var(--down);opacity:.16}
.dot.u{fill:var(--up);filter:drop-shadow(0 0 6px var(--up))}.dot.d{fill:var(--down);filter:drop-shadow(0 0 6px var(--down))}
.ax{fill:var(--mut);font:10px var(--mono)}
.cap{font-size:11.5px;color:var(--mut);margin-top:8px}

/* positions et trades */
section:not(.card)>div[id]{display:flex;flex-direction:column;gap:8px}
.row{display:grid;grid-template-columns:minmax(0,1fr) auto auto;gap:12px;align-items:center;padding:12px 14px;border:1px solid var(--line);border-left:3px solid var(--line2);border-radius:12px;background:linear-gradient(180deg,#0f1417,#0c1013)}
.row:has(.tag.buy){border-left-color:var(--up)}
.row:has(.tag.sell){border-left-color:var(--down)}
.row b{font-weight:700;letter-spacing:.01em}
.row .mut{font-size:12.5px!important}
.row .pl{font:700 14px var(--mono);text-align:right;min-width:68px;font-variant-numeric:tabular-nums}
.tag{display:inline-block;font:700 9.5px var(--mono);letter-spacing:.1em;padding:3px 7px;border-radius:5px;margin-left:8px;vertical-align:1px}
.tag.buy{color:var(--up);background:#3ddc9718}.tag.sell{color:var(--down);background:#ff6b5e18}
.empty{color:var(--mut);font-size:13.5px;padding:14px;border:1px dashed var(--line2);border-radius:12px;text-align:center}

/* statistiques */
.stats{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-top:12px}
.stats>div{background:#ffffff05;border:1px solid var(--line);border-radius:12px;padding:12px 14px}
.stats b{display:block;font:700 18px var(--mono);margin-top:4px;font-variant-numeric:tabular-nums}
#s_bw{font-size:15px;white-space:nowrap}
table{width:100%;border-collapse:collapse;margin-top:16px;font-size:13px}
th{font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--mut);text-align:right;padding:6px 0;font-weight:700}
th:first-child,td:first-child{text-align:left}
td{padding:10px 0;border-top:1px solid var(--line);text-align:right;font-family:var(--mono);font-variant-numeric:tabular-nums}

/* lancement */
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0 18px}
.chip{font:600 13px -apple-system,BlinkMacSystemFont,"Inter",system-ui,sans-serif;color:var(--mut);background:#ffffff06;border:1px solid var(--line2);border-radius:999px;padding:9px 15px;cursor:pointer;min-height:40px;transition:all .15s}
.chip.on{color:#1a1204;background:linear-gradient(135deg,#f0c76a,#c8932f);border-color:#f0c76a;box-shadow:0 6px 18px -8px #e3b559aa}
.chip:active{transform:scale(.97)}
.chip:focus-visible,.btn:focus-visible,input:focus-visible{outline:2px solid var(--gold);outline-offset:2px}
.btn{width:100%;font:700 15px -apple-system,BlinkMacSystemFont,"Inter",system-ui,sans-serif;letter-spacing:.02em;border-radius:12px;padding:15px;border:1px solid #f0c76a;background:linear-gradient(135deg,#f0c76a,#c8932f);color:#1a1204;cursor:pointer;min-height:50px;box-shadow:0 10px 24px -12px #e3b559cc;transition:transform .12s,opacity .12s}
.btn:active{transform:scale(.985)}
.btn.stop{background:#ff6b5e0f;color:var(--down);border-color:#ff6b5e66;margin-top:10px;box-shadow:none}
.btn[disabled]{opacity:.5}
#dl{background:#ffffff06!important;color:var(--gold)!important;border-color:var(--line2)!important;box-shadow:none;font-weight:600}
.msg{min-height:22px;margin-top:12px;font-size:13.5px}
input[type=password]{width:100%;font:16px var(--mono);padding:14px;background:#0a0d10;color:var(--ink);border:1px solid var(--line2);border-radius:12px;margin:12px 0 14px}

/* journal */
pre{margin:0;font:11.5px/1.65 var(--mono);color:#9fd8b8;white-space:pre-wrap;word-break:break-word;max-height:260px;overflow:auto;background:#07090b;border:1px solid var(--line);border-radius:12px;padding:14px;box-shadow:0 1px 0 #ffffff06 inset}
pre::-webkit-scrollbar{width:6px}pre::-webkit-scrollbar-thumb{background:var(--line2);border-radius:3px}
.foot{font-size:12px;color:var(--mut);text-align:center;padding-top:4px}
.foot a{color:var(--gold);text-decoration:none;border-bottom:1px solid #e3b55955}
#lock{margin-top:12vh;text-align:center}
#lock .lbl{font-size:11px}
'''
new = "<style>\n" + CSS + "</style>"
s = re.sub(r"<style>.*?</style>", lambda m: new, s, count=1, flags=re.S)
open(p, "w", encoding="utf-8").write(s)
print("Nouveau design applique.")
