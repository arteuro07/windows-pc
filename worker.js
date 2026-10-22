const PAGE = String.raw`<!doctype html>
<html lang="fr"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#0b0c0b">
<title>ART_EURO Robot MT5</title>
<style>
/*v2*/
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

/* ART_EURO UI refresh: responsive desktop dashboard + mobile polish */
:root{--r:18px}
.wrap{max-width:1180px;gap:20px}
.top{position:relative;padding:12px 4px 8px;min-height:58px}
.brand{font-size:14px;letter-spacing:.28em}
.pill{backdrop-filter:blur(12px)}
.card{padding:clamp(16px,2.2vw,24px);border-radius:18px;transition:border-color .18s,transform .18s}
.card:hover{border-color:#343d40}
#main{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));align-items:start;gap:20px}
#main>section:nth-of-type(1){grid-column:span 7}
#main>section:nth-of-type(2){grid-column:span 5}
#main>section:nth-of-type(3),#main>section:nth-of-type(4){grid-column:span 6;min-width:0}
#main>section:nth-of-type(5){grid-column:span 7;min-width:0}
#main>section:nth-of-type(6){grid-column:span 5;min-width:0}
#main>section:nth-of-type(7),#main>.foot{grid-column:1/-1;min-width:0}
#main>section:nth-of-type(1) .big{font-size:clamp(36px,4vw,52px)}
#main>section:nth-of-type(2) svg{max-height:190px}
#main>section:nth-of-type(5) table{border-collapse:separate;border-spacing:0}
#main>section:nth-of-type(5) th{padding:10px 8px}
#main>section:nth-of-type(5) td{padding:12px 8px}
#main>section:nth-of-type(5) th:first-child,#main>section:nth-of-type(5) td:first-child{padding-left:0}
#main>section:nth-of-type(6) .chips{gap:9px}
#main>section:nth-of-type(6) .chip{flex:0 0 auto}
.row{min-width:0;gap:10px}
.row>div{min-width:0}
.row>div:nth-child(2){overflow-wrap:anywhere}
.foot{padding:14px 0 4px}
@media(min-width:1100px){
  body{padding-left:28px;padding-right:28px}
  .top{margin-bottom:2px}
  #main{gap:22px}
  #main>section:nth-of-type(1),#main>section:nth-of-type(2){min-height:220px}
}
@media(max-width:760px){
  .wrap{max-width:560px;gap:16px}
  #main{display:flex;flex-direction:column;gap:16px}
  #main>section,#main>.foot{width:100%}
  .top{position:relative;padding:6px 2px 2px;min-height:0}
  .card{padding:17px;border-radius:16px}
}
@media(max-width:390px){
  body{padding-left:12px;padding-right:12px}
  .brand{letter-spacing:.2em}
  .pill{padding:6px 9px;font-size:10px}
  .kpis>div{padding:0 8px}
  .kpis b{font-size:14px}
  .row{grid-template-columns:minmax(0,1fr) auto;gap:7px;padding:11px}
  .row>div:nth-child(2){grid-column:1;grid-row:2}
  .row .pl{grid-column:2;grid-row:1/3;align-self:center;min-width:58px;font-size:12px}
  .stats>div{padding:10px}
  .stats b{font-size:16px}
  .chip{padding:8px 12px;min-height:38px;font-size:12px}
}
@media(prefers-reduced-motion:reduce){.card{transition:none}}

</style></head><body>
<div class="wrap">
  <header class="top">
    <div><div class="brand">ART_EURO</div><div class="sub" id="sub">Robot MT5 · compte démo</div></div>
    <div class="pill off" id="pill"><i></i><span id="pt">HORS LIGNE</span></div>
  </header>

  <section class="card" id="lock" hidden>
    <div class="lbl">Accès</div>
    <input type="password" id="key" placeholder="Mot de passe du panneau" autocomplete="current-password">
    <button class="btn" id="enter" type="button">Entrer</button>
    <div class="msg down" id="lockmsg"></div>
  </section>

  <div class="wrap" id="main" hidden>
    <section class="card">
      <div class="lbl">Équité</div>
      <div class="big" id="eq">—</div>
      <div class="pnl" id="pnl"></div>
      <div class="kpis">
        <div><div class="lbl">Solde</div><b id="bal">—</b></div>
        <div><div class="lbl">Ouverts</div><b id="opn">—</b></div>
        <div><div class="lbl">Positions</div><b id="pos">—</b></div>
      </div>
    </section>

    <section class="card">
      <div class="lbl">Courbe d'équité</div>
      <svg id="ch" viewBox="0 0 320 130" role="img" aria-label="Courbe d'équité de la session"></svg>
      <div class="cap" id="chcap"></div>
    </section>

    <section><h2>Positions ouvertes</h2><div id="plist"></div></section>
    <section><h2>Derniers trades fermés</h2><div id="dlist"></div></section>

    <section class="card">
      <div class="lbl">Statistiques de la session</div>
      <div class="stats" style="margin-top:12px">
        <div><div class="lbl">Trades fermés</div><b id="s_n">0</b></div>
        <div><div class="lbl">Gagnants</div><b id="s_w">—</b></div>
        <div><div class="lbl">Profit net</div><b id="s_t">—</b></div>
        <div><div class="lbl">Meilleur / pire</div><b id="s_bw">—</b></div>
      </div>
      <table><thead><tr><th>Stratégie</th><th>Trades</th><th>Gagnants</th><th>Net</th></tr></thead><tbody id="s_tab"></tbody></table>
      <button class="btn" id="dl" type="button" style="margin-top:16px;background:transparent;color:var(--gold)">Télécharger le relevé</button>
    </section>

    <section class="card">
      <div class="lbl">Lancer le robot</div>
      <div class="cap" style="margin-top:10px">Durée</div>
      <div class="chips" id="c_min"></div>
      <div class="cap">Catégories d'actifs</div>
      <div class="chips" id="c_cat"></div>
      <div class="cap">Stratégies</div>
      <div class="chips" id="c_str"></div>
      <button class="btn" id="go" type="button">Lancer la session</button>
      <button class="btn stop" id="stop" type="button" hidden>Arrêter la session en cours</button>
      <div class="msg" id="msg"></div>
    </section>

    <section><h2>Journal du robot</h2><pre id="log">En attente de données…</pre></section>
    <div class="foot" id="foot"></div>
  </div>
</div>
<script>
(function(){
var $=function(i){return document.getElementById(i)};
var KEY='';try{KEY=localStorage.getItem('k')||''}catch(e){}
var fmt=new Intl.NumberFormat('fr-FR',{minimumFractionDigits:2,maximumFractionDigits:2});
function f2(n){return fmt.format(n)}
function sg(n){return (n>0?'+':'')+f2(n)}
function cl(n){return n>0?'up':(n<0?'down':'')}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function tm(t){return new Date(t).toLocaleTimeString('fr-FR',{hour:'2-digit',minute:'2-digit'})}
function ago(ms){var s=Math.max(0,Math.round(ms/1000));if(s<90)return s+' s';var m=Math.round(s/60);if(m<90)return m+' min';return Math.round(m/60)+' h'}
var sel={min:120,cat:['Forex','Metals','Crypto','Indices'],str:['booster','ema']};
var timer=null,activeId=null;

function api(path,body){
  return fetch(path,{method:body?'POST':'GET',headers:{'x-key':KEY,'content-type':'application/json'},body:body?JSON.stringify(body):undefined})
  .then(function(r){
    if(r.status===401){lock('Mot de passe incorrect');throw new Error('401')}
    return r.text().then(function(t){var j;try{j=JSON.parse(t)}catch(e){j={error:t}}return j})
  });
}
function lock(msg){
  $('lock').hidden=false;$('main').hidden=true;$('lockmsg').textContent=msg||'';
  if(timer){clearInterval(timer);timer=null}
}
function chipsBuild(id,items,multi,key){
  var box=$(id);box.innerHTML='';
  items.forEach(function(it){
    var b=document.createElement('button');b.type='button';b.className='chip';b.textContent=it[1];b.setAttribute('data-v',it[0]);
    function on(){return multi?sel[key].indexOf(it[0])>=0:sel[key]===it[0]}
    function paint(){b.className='chip'+(on()?' on':'')}
    b.addEventListener('click',function(){
      if(multi){var i=sel[key].indexOf(it[0]);if(i>=0)sel[key].splice(i,1);else sel[key].push(it[0])}
      else sel[key]=it[0];
      Array.prototype.forEach.call(box.children,function(c){c.className='chip'+(multi?(sel[key].indexOf(c.getAttribute('data-v'))>=0?' on':''):(String(sel[key])===c.getAttribute('data-v')?' on':''))});
    });
    box.appendChild(b);
    b.className='chip'+(multi?(on()?' on':''):(String(sel[key])===String(it[0])?' on':''));
    b.setAttribute('data-v',it[0]);
  });
}
chipsBuild('c_min',[[30,'30 min'],[60,'1 h'],[120,'2 h'],[240,'4 h'],[350,'≈ 6 h']],false,'min');
chipsBuild('c_cat',[['Forex','Forex'],['Metals','Métaux'],['Crypto','Crypto'],['Indices','Indices'],['Stocks','Actions']],true,'cat');
chipsBuild('c_str',[['booster','Scalping Booster'],['ema','EMA 9/21'],['fvg','FVG Or'],['brk','Cassure Or']],true,'str');

function chart(h,start){
  var svg=$('ch');
  if(!h||h.length<2){svg.innerHTML='<text x="160" y="66" text-anchor="middle" class="ax">Le graphique apparaît après 2 mesures (1 par minute)</text>';$('chcap').textContent='';return}
  var W=320,H=130,L=8,R=8,T=12,B=22;
  var xs=h.map(function(p){return p[0]}),ys=h.map(function(p){return p[1]});
  var x0=xs[0],x1=xs[xs.length-1];if(x1===x0)x1=x0+1;
  var lo=Math.min.apply(null,ys.concat([start])),hi=Math.max.apply(null,ys.concat([start]));
  if(hi-lo<0.000001){hi+=1;lo-=1}
  var pad=(hi-lo)*0.15;lo-=pad;hi+=pad;
  function X(t){return L+(t-x0)/(x1-x0)*(W-L-R)}
  function Y(v){return T+(hi-v)/(hi-lo)*(H-T-B)}
  var d=h.map(function(p,i){return (i?'L':'M')+X(p[0]).toFixed(1)+' '+Y(p[1]).toFixed(1)}).join(' ');
  var last=h[h.length-1],k=last[1]>=start?'u':'d';
  var area=d+' L'+X(last[0]).toFixed(1)+' '+(H-B)+' L'+X(x0).toFixed(1)+' '+(H-B)+' Z';
  var ys0=Y(start).toFixed(1);
  svg.innerHTML='<line class="grid" x1="'+L+'" x2="'+(W-R)+'" y1="'+ys0+'" y2="'+ys0+'"/>'
   +'<path class="area '+k+'" d="'+area+'"/><path class="ln '+k+'" d="'+d+'"/>'
   +'<circle class="dot '+k+'" cx="'+X(last[0]).toFixed(1)+'" cy="'+Y(last[1]).toFixed(1)+'" r="3.5"/>'
   +'<text class="ax" x="'+L+'" y="'+(H-6)+'">'+tm(x0)+'</text>'
   +'<text class="ax" x="'+(W-R)+'" y="'+(H-6)+'" text-anchor="end">'+tm(x1)+'</text>';
  $('chcap').textContent='Pointillé : équité de départ ('+f2(start)+')';
}
function row(sym,side,mid,pl){
  return '<div class="row"><div><b>'+esc(sym)+'</b><span class="tag '+(side==='BUY'?'buy':'sell')+'">'+esc(side)+'</span></div><div class="mut" style="font-size:13px">'+esc(mid)+'</div><div class="pl '+cl(pl)+'">'+sg(pl)+'</div></div>';
}
function stratName(s){return s==='booster'?'Booster':(s==='ema'?'EMA 9/21':(s==='fvg'?'FVG Or':(s==='brk'?'Cassure Or':s)))}

function render(st,runs){
  LAST=st;
  var run=runs&&runs.length?runs[0]:null;
  var live=run&&(run.status==='in_progress'||run.status==='queued'||run.status==='waiting'||run.status==='requested'||run.status==='pending');
  activeId=live?run.id:null;
  var mine=run&&st&&String(st.run_id)===String(run.id);
  var age=st&&st.updated?(st.now-st.updated):null;
  var fresh=live&&mine&&age!==null&&age<180000;
  var pill=$('pill');
  if(fresh){pill.className='pill run';$('pt').textContent='EN COURS'}
  else if(live){pill.className='pill boot';$('pt').textContent='DÉMARRAGE'}
  else{pill.className='pill off';$('pt').textContent='ARRÊTÉ'}
  var sub='Robot MT5 · compte démo';
  if(live&&!fresh)sub='Windows s’installe, premières mesures dans 3 à 5 min';
  else if(st&&st.updated)sub='Session '+(live?'en cours':'terminée')+' · mesure il y a '+ago(age);
  $('sub').textContent=sub;

  if(!st||!st.updated){
    $('eq').textContent='—';$('pnl').textContent='Aucune donnée. Lance une session ci-dessous.';
    chart([],0);$('plist').innerHTML='<div class="empty">Aucune position ouverte.</div>';
    $('dlist').innerHTML='<div class="empty">Aucun trade fermé.</div>';
  }else{
    var pnl=st.equity-st.start_eq;
    $('eq').textContent=f2(st.equity);
    $('pnl').className='pnl '+cl(pnl);
    $('pnl').textContent=sg(pnl)+'  ('+sg(st.start_eq?pnl/st.start_eq*100:0)+' %) depuis le départ';
    $('bal').textContent=f2(st.balance);
    $('opn').textContent=st.opened+' / '+st.total;
    $('pos').textContent=(st.positions||[]).length;
    chart(st.history,st.start_eq);
    var ps=st.positions||[];
    $('plist').innerHTML=ps.length?ps.map(function(p){return row(p.symbol,p.side,stratName(p.strat)+' · '+p.volume,p.profit)}).join(''):'<div class="empty">Aucune position ouverte.</div>';
    var ds=Object.keys(st.deals||{}).map(function(k){return st.deals[k]}).sort(function(a,b){return b.seen-a.seen});
    $('dlist').innerHTML=ds.length?ds.slice(0,15).map(function(d){return row(d.symbol,d.side,stratName(d.strat)+' · '+tm(d.seen),d.profit)}).join(''):'<div class="empty">Aucun trade fermé pour l’instant.</div>';
    var n=ds.length,w=ds.filter(function(d){return d.profit>0}).length;
    var tot=ds.reduce(function(a,d){return a+d.profit},0);
    $('s_n').textContent=n;
    $('s_w').textContent=n?Math.round(w/n*100)+' %':'—';
    $('s_t').className=cl(tot);$('s_t').textContent=n?sg(tot):'—';
    var bw=n?Math.max.apply(null,ds.map(function(d){return d.profit})):0,wr=n?Math.min.apply(null,ds.map(function(d){return d.profit})):0;
    $('s_bw').innerHTML=n?'<span class="up">'+sg(bw)+'</span> / <span class="down">'+sg(wr)+'</span>':'—';
    var by={};ds.forEach(function(d){var o=by[d.strat]||(by[d.strat]={n:0,w:0,t:0});o.n++;if(d.profit>0)o.w++;o.t+=d.profit});
    var keys=Object.keys(by);
    $('s_tab').innerHTML=keys.length?keys.map(function(k){var o=by[k];return '<tr><td>'+esc(stratName(k))+'</td><td>'+o.n+'</td><td>'+Math.round(o.w/o.n*100)+' %</td><td class="'+cl(o.t)+'">'+sg(o.t)+'</td></tr>'}).join(''):'<tr><td colspan="4" class="mut" style="text-align:left">Pas encore de trade fermé.</td></tr>';
    $('log').textContent=(st.log&&st.log.length?st.log.slice(-25).join('\n'):'Journal vide.');
    var lg=$('log');lg.scrollTop=lg.scrollHeight;
  }
  $('stop').hidden=!live;
  var f=run?('Dernière session : '+(live?'en cours':(run.conclusion==='success'?'terminée':(run.conclusion==='cancelled'?'annulée':'échec')))+' · <a href="'+esc(run.url)+'" target="_blank" rel="noopener">GitHub</a>'):'Aucune session lancée pour l’instant.';
  $('foot').innerHTML=f;
}
function refresh(){
  return Promise.all([api('/api/state'),api('/api/runs')]).then(function(r){
    $('lock').hidden=true;$('main').hidden=false;render(r[0],r[1].runs||[]);
    if(!timer)timer=setInterval(function(){if(!document.hidden)refresh().catch(function(){})},15000);
  });
}
$('enter').addEventListener('click',function(){
  KEY=$('key').value;try{localStorage.setItem('k',KEY)}catch(e){}
  refresh().catch(function(e){if(String(e.message)!=='401')$('lockmsg').textContent='Connexion impossible, réessaie.'});
});
$('key').addEventListener('keydown',function(e){if(e.key==='Enter')$('enter').click()});
$('go').addEventListener('click',function(){
  var m=$('msg');
  if(!sel.cat.length||!sel.str.length){m.className='msg down';m.textContent='Choisis au moins une catégorie et une stratégie.';return}
  $('go').disabled=true;m.className='msg mut';m.textContent='Envoi…';
  api('/api/run',{minutes:sel.min,categories:sel.cat.join(','),strategies:sel.str.join(',')}).then(function(j){
    m.className='msg '+(j.ok?'up':'down');m.textContent=j.ok?'Session lancée. Windows démarre, compte 3 à 5 minutes.':(j.error||'Échec du lancement.');
    setTimeout(function(){refresh().catch(function(){})},5000);
  }).catch(function(){m.className='msg down';m.textContent='Connexion impossible.'}).then(function(){$('go').disabled=false});
});
$('stop').addEventListener('click',function(){
  if(!activeId)return;var m=$('msg');m.className='msg mut';m.textContent='Arrêt demandé…';
  api('/api/cancel',{id:activeId}).then(function(j){m.className='msg '+(j.ok?'up':'down');m.textContent=j.ok?'Arrêt envoyé.':(j.error||'Échec de l’arrêt.');setTimeout(function(){refresh().catch(function(){})},4000)});
});
var LAST=null;
function csvv(v){v=(v===undefined||v===null)?'':String(v);return /[;"\n]/.test(v)?'"'+v.replace(/"/g,'""')+'"':v}
function csvl(a){return a.map(csvv).join(';')}
function nb(n,d){return Number(n).toFixed(d===undefined?2:d).replace('.',',')}
function iso(t){return new Date(t).toISOString().slice(0,19).replace('T',' ')}
function releve(){
  var st=LAST,b=$('dl');
  if(!st||!st.updated){b.textContent='Aucune donnée à télécharger';setTimeout(function(){b.textContent='Télécharger le relevé'},2500);return}
  var L=[];
  L.push(csvl(['RELEVE ART_EURO ROBOT MT5 (compte demo)']));
  L.push(csvl(['Genere le (UTC)',iso(Date.now())]));
  L.push(csvl(['Session (numero GitHub)',st.run_id]));
  L.push(csvl(['Debut de session (UTC)',iso(st.started)]));
  L.push(csvl(['Derniere mesure (UTC)',iso(st.updated)]));
  L.push(csvl(['Strategies',st.strategies]));
  L.push(csvl(['Duree prevue (min)',st.minutes]));
  L.push(csvl(['Equite de depart',nb(st.start_eq)]));
  L.push(csvl(['Equite actuelle',nb(st.equity)]));
  L.push(csvl(['Resultat',nb(st.equity-st.start_eq)]));
  L.push(csvl(['Solde',nb(st.balance)]));
  L.push(csvl(['Marches ouverts',st.opened+' / '+st.total]));
  var ds=Object.keys(st.deals||{}).map(function(k){return st.deals[k]});
  function tt(d){return d.time?d.time*1000:d.seen}
  ds.sort(function(a,c){return tt(a)-tt(c)});
  L.push('');L.push(csvl(['STATISTIQUES PAR STRATEGIE']));
  L.push(csvl(['Strategie','Trades','Gagnants','Taux %','Net','Meilleur','Pire','Facteur de profit']));
  var by={},all=[];
  ds.forEach(function(d){(by[d.strat]||(by[d.strat]=[])).push(d.profit);all.push(d.profit)});
  function srow(name,a){
    var g=a.filter(function(x){return x>0}),lo=a.filter(function(x){return x<=0});
    var gs=g.reduce(function(s,x){return s+x},0),ls=-lo.reduce(function(s,x){return s+x},0);
    return csvl([name,a.length,g.length,a.length?nb(g.length/a.length*100,0):'',nb(a.reduce(function(s,x){return s+x},0)),nb(Math.max.apply(null,a)),nb(Math.min.apply(null,a)),ls>0?nb(gs/ls):'']);
  }
  Object.keys(by).forEach(function(k){L.push(srow(stratName(k),by[k]))});
  if(all.length)L.push(srow('TOTAL',all));
  else L.push(csvl(['Aucun trade ferme']));
  L.push('');L.push(csvl(['POSITIONS OUVERTES']));
  L.push(csvl(['Symbole','Sens','Strategie','Volume','Profit latent']));
  (st.positions||[]).forEach(function(p){L.push(csvl([p.symbol,p.side,stratName(p.strat),nb(p.volume),nb(p.profit)]))});
  L.push('');L.push(csvl(['TRADES FERMES (heure serveur MT5 si disponible, sinon ~UTC)']));
  L.push(csvl(['Heure fermeture','Symbole','Sens','Strategie','Volume','Prix sortie','Profit net']));
  ds.forEach(function(d){L.push(csvl([(d.time?'':'~')+iso(tt(d)),d.symbol,d.side,stratName(d.strat),d.volume===undefined?'':nb(d.volume),d.price===undefined?'':String(d.price).replace('.',','),nb(d.profit)]))});
  L.push('');L.push(csvl(['COURBE D EQUITE (UTC)']));
  L.push(csvl(['Heure','Equite']));
  (st.history||[]).forEach(function(p){L.push(csvl([iso(p[0]),nb(p[1])]))});
  L.push('');L.push(csvl(['JOURNAL DU ROBOT (dernieres lignes)']));
  (st.log||[]).forEach(function(x){L.push(csvl([x]))});
  var blob=new Blob(['\ufeff'+L.join('\r\n')],{type:'text/csv;charset=utf-8'});
  var a=document.createElement('a');
  a.href=URL.createObjectURL(blob);
  a.download='releve-'+iso(Date.now()).replace(/[: ]/g,'-').slice(0,16)+'.csv';
  document.body.appendChild(a);a.click();
  setTimeout(function(){URL.revokeObjectURL(a.href);a.remove()},1500);
}
$('dl').addEventListener('click',releve);
if(KEY){refresh().catch(function(){})}else{lock('')}
})();
</script></body></html>`;

const CATS = ["Forex", "Metals", "Crypto", "Indices", "Stocks"];
const STRS = ["booster", "ema", "fvg", "brk"];
const pick = (v, ok, d) => {
  const a = String(v || "").split(",").map((s) => s.trim()).filter((s) => ok.includes(s));
  return (a.length ? a : d).join(",");
};
const json = (o, status = 200) =>
  new Response(JSON.stringify(o), { status, headers: { "content-type": "application/json", "cache-control": "no-store" } });
const gh = (env, path, init = {}) =>
  fetch("https://api.github.com/repos/arteuro07/windows-pc/" + path, {
    ...init,
    headers: {
      Authorization: "Bearer " + env.GH_TOKEN,
      "User-Agent": "mt5-panel",
      Accept: "application/vnd.github+json",
      ...(init.headers || {}),
    },
  });

export default {
  async fetch(req, env) {
    const u = new URL(req.url);
    if (u.pathname === "/" && req.method === "GET") {
      return new Response(PAGE, { headers: { "content-type": "text/html;charset=utf-8", "cache-control": "no-store" } });
    }
    if (!u.pathname.startsWith("/api/")) return new Response("Introuvable", { status: 404 });
    if (!env.PANEL_KEY || req.headers.get("x-key") !== env.PANEL_KEY) return json({ error: "Mot de passe incorrect" }, 401);

    if (u.pathname === "/api/report" && req.method === "POST") {
      const b = await req.json().catch(() => null);
      if (!b || typeof b.equity !== "number") return json({ error: "Rapport invalide" }, 400);
      let s = null;
      try { s = JSON.parse((await env.STATE.get("s")) || "null"); } catch (e) { s = null; }
      const now = Date.now();
      if (!s || String(s.run_id) !== String(b.run_id)) {
        s = { run_id: String(b.run_id), start_eq: b.equity, started: now, history: [], log: [], deals: {} };
      }
      Object.assign(s, {
        updated: now, balance: b.balance, equity: b.equity, opened: b.opened, total: b.total,
        minutes: b.minutes, strategies: b.strategies, finished: !!b.finished,
        positions: Array.isArray(b.positions) ? b.positions.slice(0, 50) : [],
      });
      s.history.push([now, b.equity]);
      if (s.history.length > 600) s.history = s.history.slice(-600);
      for (const d of Array.isArray(b.deals) ? b.deals : []) {
        const k = String(d.ticket);
        if (!s.deals[k]) s.deals[k] = { ...d, seen: now };
      }
      const ks = Object.keys(s.deals);
      if (ks.length > 200) {
        ks.sort((a, c) => s.deals[a].seen - s.deals[c].seen).slice(0, ks.length - 200).forEach((k) => delete s.deals[k]);
      }
      s.log = s.log.concat(Array.isArray(b.log) ? b.log.map(String) : []).slice(-80);
      await env.STATE.put("s", JSON.stringify(s));
      return json({ ok: true });
    }

    if (u.pathname === "/api/state" && req.method === "GET") {
      let s = {};
      try { s = JSON.parse((await env.STATE.get("s")) || "{}"); } catch (e) { s = {}; }
      s.now = Date.now();
      return json(s);
    }

    if (u.pathname === "/api/runs" && req.method === "GET") {
      const r = await gh(env, "actions/workflows/mt5.yml/runs?per_page=3");
      if (!r.ok) return json({ runs: [], error: "GitHub " + r.status });
      const j = await r.json();
      return json({
        runs: (j.workflow_runs || []).map((x) => ({
          id: x.id, status: x.status, conclusion: x.conclusion, created: x.created_at, url: x.html_url,
        })),
      });
    }

    if (u.pathname === "/api/run" && req.method === "POST") {
      const b = await req.json().catch(() => ({}));
      const minutes = Math.min(350, Math.max(1, parseInt(b.minutes, 10) || 5));
      const r = await gh(env, "actions/workflows/mt5.yml/dispatches", {
        method: "POST",
        body: JSON.stringify({
          ref: "main",
          inputs: {
            minutes: String(minutes),
            categories: pick(b.categories, CATS, ["Forex", "Metals", "Crypto", "Indices"]),
            strategies: pick(b.strategies, STRS, ["booster", "ema"]),
          },
        }),
      });
      return r.status === 204 ? json({ ok: true }) : json({ ok: false, error: "GitHub a répondu " + r.status }, 502);
    }

    if (u.pathname === "/api/cancel" && req.method === "POST") {
      const b = await req.json().catch(() => ({}));
      if (!/^[0-9]+$/.test(String(b.id))) return json({ ok: false, error: "Identifiant invalide" }, 400);
      const r = await gh(env, "actions/runs/" + b.id + "/cancel", { method: "POST" });
      return r.status === 202 ? json({ ok: true }) : json({ ok: false, error: "GitHub a répondu " + r.status }, 502);
    }

    return json({ error: "Route inconnue" }, 404);
  },
};
