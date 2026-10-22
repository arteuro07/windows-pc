const PAGE = String.raw`<!doctype html>
<html lang="fr"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#04070b">
<meta name="color-scheme" content="dark">
<title>ART_EURO Robot MT5</title>
<style>
/*v3-hud*/
:root{--bg:#04070b;--panel:rgba(10,18,26,.82);--line:rgba(53,224,255,.16);--line2:rgba(53,224,255,.34);--ink:#e6f1f5;--mut:#6f8794;--up:#19f0a0;--down:#ff4d6d;--gold:#ffd23f;--cy:#35e0ff;--mono:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
[hidden]{display:none!important}
html{background:var(--bg)}
body{margin:0;color:var(--ink);font:14px/1.5 var(--mono);-webkit-font-smoothing:antialiased;min-height:100vh;
  background:radial-gradient(1200px 600px at 50% -10%,rgba(53,224,255,.10),transparent 60%),radial-gradient(800px 500px at 100% 100%,rgba(25,240,160,.06),transparent 60%),var(--bg);padding-bottom:46px}
.scan{position:fixed;inset:0;pointer-events:none;z-index:50;background:repeating-linear-gradient(to bottom,rgba(255,255,255,.025) 0,rgba(255,255,255,.025) 1px,transparent 1px,transparent 3px);mix-blend-mode:overlay}
.wrap{max-width:560px;margin:0 auto;padding:14px 16px;padding-left:max(16px,env(safe-area-inset-left));padding-right:max(16px,env(safe-area-inset-right))}
.wrap .wrap{padding:0}
.up{color:var(--up)}.down{color:var(--down)}.mut{color:var(--mut)}
.top{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:14px}
.logo{display:flex;align-items:center;gap:10px}
.mark{width:34px;height:34px;border:1px solid var(--line2);border-radius:9px;display:grid;place-items:center;background:rgba(53,224,255,.07);color:var(--cy);font-weight:800;font-size:13px;letter-spacing:.5px}
.brand{font-weight:800;letter-spacing:2px;font-size:15px}
.brand span{color:var(--cy)}
.sub{font-size:11px;color:var(--mut);margin-top:1px}
.right{display:flex;flex-direction:column;align-items:flex-end;gap:5px}
.clock{font-size:12px;color:var(--cy);letter-spacing:1px;white-space:nowrap}
.pill{white-space:nowrap;display:inline-flex;align-items:center;gap:7px;font-size:11px;font-weight:700;letter-spacing:1.5px;padding:4px 10px;border-radius:999px;border:1px solid var(--line2)}
.pill i{width:7px;height:7px;border-radius:50%;background:var(--mut)}
.pill.run{color:var(--up);border-color:rgba(25,240,160,.45)}.pill.run i{background:var(--up);box-shadow:0 0 10px var(--up);animation:pulse 1.4s infinite}
.pill.boot{color:var(--gold);border-color:rgba(255,210,63,.45)}.pill.boot i{background:var(--gold);animation:pulse 1s infinite}
.pill.off{color:var(--mut)}
@keyframes pulse{50%{opacity:.35}}
.card{position:relative;background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:16px;margin-bottom:12px;backdrop-filter:blur(6px)}
.card:before,.card:after{content:"";position:absolute;width:14px;height:14px;border:2px solid var(--cy);opacity:.8}
.card:before{top:-1px;left:-1px;border-right:0;border-bottom:0;border-radius:14px 0 0 0}
.card:after{bottom:-1px;right:-1px;border-left:0;border-top:0;border-radius:0 0 14px 0}
.lbl{font-size:10px;letter-spacing:2px;color:var(--mut);text-transform:uppercase}
h2{font-size:10px;letter-spacing:2px;color:var(--mut);text-transform:uppercase;margin:18px 2px 8px;font-weight:600}
h2:before{content:"▍";color:var(--cy);margin-right:6px}
.hero{text-align:left}
.pbig{font-size:clamp(40px,13vw,64px);font-weight:800;line-height:1.05;letter-spacing:-1px;margin:6px 0 2px;text-shadow:0 0 24px currentColor;font-variant-numeric:tabular-nums}
.pnl{font-size:12px;color:var(--mut)}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:14px;padding-top:12px;border-top:1px dashed var(--line)}
.kpis b{display:block;font-size:15px;margin-top:3px;font-variant-numeric:tabular-nums}
.sphwrap{position:relative;padding:0;overflow:hidden}
#sph{display:block;width:100%;height:230px}
.sl{position:absolute;top:12px;left:14px}.sr{position:absolute;top:12px;right:14px;text-align:right}
.sl b,.sr b{display:block;font-size:13px}
.sb{position:absolute;bottom:10px;left:0;right:0;text-align:center;font-size:10px;letter-spacing:2px;color:var(--mut)}
.phase{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin-top:12px;position:relative}
.node{border:1px solid var(--line);border-radius:10px;padding:10px 4px;text-align:center;opacity:.5;transition:.3s}
.node em{display:block;font-style:normal;font-size:18px;margin-bottom:2px}
.node b{display:block;font-size:10px;letter-spacing:1px}
.node small{display:block;font-size:10px;color:var(--mut)}
.node.on{opacity:1;border-color:var(--up);box-shadow:0 0 16px rgba(25,240,160,.35),inset 0 0 12px rgba(25,240,160,.12)}
.node.on b{color:var(--up)}
.pmsg{font-size:11px;color:var(--mut);margin-top:10px;text-align:center}
svg#ch{display:block;width:100%;height:auto;margin-top:8px}
.grid{stroke:var(--line2);stroke-dasharray:3 4;stroke-width:1}
.ln{fill:none;stroke-width:2;stroke-linejoin:round;filter:drop-shadow(0 0 4px currentColor)}
.ln.u{stroke:var(--up);color:var(--up)}.ln.d{stroke:var(--down);color:var(--down)}
.area.u{fill:rgba(25,240,160,.12)}.area.d{fill:rgba(255,77,109,.12)}
.dot.u{fill:var(--up)}.dot.d{fill:var(--down)}
.ax{fill:var(--mut);font:9px var(--mono)}
.cap{font-size:11px;color:var(--mut);margin-top:8px}
.row{display:grid;grid-template-columns:auto 1fr auto;gap:10px;align-items:center;padding:10px 12px;border:1px solid var(--line);border-radius:10px;margin-bottom:6px;background:var(--panel)}
.row .pl{font-weight:700;font-variant-numeric:tabular-nums}
.tag{display:inline-block;font-size:10px;font-weight:700;letter-spacing:1px;padding:1px 7px;border-radius:5px;margin-left:8px}
.tag.buy{color:var(--up);background:rgba(25,240,160,.12)}.tag.sell{color:var(--down);background:rgba(255,77,109,.12)}
.empty{font-size:12px;color:var(--mut);padding:12px;border:1px dashed var(--line);border-radius:10px;text-align:center}
.stats{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}
.stats b{display:block;font-size:17px;margin-top:2px}
table{width:100%;border-collapse:collapse;margin-top:14px;font-size:12px}
th{font-weight:600;color:var(--mut);font-size:10px;letter-spacing:1px;text-transform:uppercase;text-align:right;padding:6px 4px;border-bottom:1px solid var(--line)}
td{text-align:right;padding:8px 4px;border-bottom:1px solid var(--line)}
th:first-child,td:first-child{text-align:left}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0 14px}
.chip{font:600 12px var(--mono);color:var(--mut);background:transparent;border:1px solid var(--line2);border-radius:999px;padding:8px 14px;cursor:pointer}
.chip.on{color:#04070b;background:var(--cy);border-color:var(--cy);box-shadow:0 0 14px rgba(53,224,255,.4)}
input{width:100%;font:15px var(--mono);color:var(--ink);background:rgba(0,0,0,.35);border:1px solid var(--line2);border-radius:10px;padding:13px;margin:12px 0}
.btn{width:100%;font:700 13px var(--mono);letter-spacing:2px;text-transform:uppercase;color:#04070b;background:var(--up);border:0;border-radius:10px;padding:14px;cursor:pointer;box-shadow:0 0 20px rgba(25,240,160,.3)}
.btn:disabled{opacity:.5}
.btn.stop{background:transparent;color:var(--down);border:1px solid var(--down);box-shadow:none;margin-top:10px}
.btn.ghost{background:transparent;color:var(--cy);border:1px solid var(--line2);box-shadow:none}
.msg{font-size:12px;min-height:18px;margin-top:10px}
pre#log{margin:0;max-height:240px;overflow:auto;font:11px/1.55 var(--mono);color:#9fe9c8;background:rgba(0,0,0,.45);border:1px solid var(--line);border-radius:10px;padding:12px;white-space:pre-wrap;word-break:break-word}
.foot{font-size:11px;color:var(--mut);text-align:center;margin:18px 0 8px}
.foot a{color:var(--cy)}
.ticker{position:fixed;left:0;right:0;bottom:0;z-index:40;height:34px;overflow:hidden;background:rgba(4,7,11,.92);border-top:1px solid var(--line2);display:flex;align-items:center}
.ticker div{white-space:nowrap;font-size:11px;color:var(--up);padding-left:100%;animation:mq 40s linear infinite}
@keyframes mq{to{transform:translateX(-100%)}}
@media (prefers-reduced-motion:reduce){.scan{display:none}.ticker div{animation:none;padding-left:12px}.pill i{animation:none!important}}
</style></head><body>
<div class="scan"></div>
<div class="wrap">
  <header class="top">
    <div class="logo"><div class="mark">AE</div><div><div class="brand">ART<span>_</span>EURO</div><div class="sub" id="sub">Cassure Or · compte démo</div></div></div>
    <div class="right"><div class="clock" id="clock">--:--:-- UTC</div><div class="pill off" id="pill"><i></i><span id="pt">HORS LIGNE</span></div></div>
  </header>

  <section class="card" id="lock" hidden>
    <div class="lbl">Accès sécurisé</div>
    <input type="password" id="key" placeholder="Mot de passe du panneau" autocomplete="current-password">
    <button class="btn" id="enter" type="button">Entrer</button>
    <div class="msg down" id="lockmsg"></div>
  </section>

  <div class="wrap" id="main" hidden>
    <section class="card hero">
      <div class="lbl">Résultat de la session</div>
      <div class="pbig" id="pbig">—</div>
      <div class="pnl" id="pnl"></div>
      <div class="kpis">
        <div><div class="lbl">Équité</div><b id="eq">—</b></div>
        <div><div class="lbl">Solde</div><b id="bal">—</b></div>
        <div><div class="lbl">Actifs</div><b id="opn">—</b></div>
        <div><div class="lbl">Positions</div><b id="pos">—</b></div>
      </div>
    </section>

    <section class="card sphwrap">
      <canvas id="sph" aria-label="Visualisation animée de l'activité du robot"></canvas>
      <div class="sl"><div class="lbl">Cible</div><b>XAUUSD</b></div>
      <div class="sr"><div class="lbl">Sortie</div><b>18h</b></div>
      <div class="sb" id="sphcap">NEURAL SHELL · CASSURE OR</div>
    </section>

    <section class="card">
      <div class="lbl">Stratégie · Cassure Or</div>
      <div class="phase" id="phase">
        <div class="node" id="n_range"><em>◎</em><b>RANGE</b><small>00h–07h</small></div>
        <div class="node" id="n_ord"><em>⇅</em><b>ORDRES</b><small>07h</small></div>
        <div class="node" id="n_pos"><em>⚡</em><b>POSITION</b><small>1 / jour</small></div>
        <div class="node" id="n_cl"><em>■</em><b>CLÔTURE</b><small>18h</small></div>
      </div>
      <div class="pmsg" id="pmsg"></div>
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
      <button class="btn ghost" id="dl" type="button" style="margin-top:16px">Télécharger le relevé CSV</button>
    </section>

    <section class="card">
      <div class="lbl">Lancer le robot</div>
      <div class="cap">Durée de la session</div>
      <div class="chips" id="c_min"></div>
      <button class="btn" id="go" type="button">Lancer la session</button>
      <button class="btn stop" id="stop" type="button" hidden>Arrêter la session en cours</button>
      <div class="msg" id="msg"></div>
    </section>

    <section><h2>Journal du robot</h2><pre id="log">En attente de données…</pre></section>
    <div class="foot" id="foot"></div>
  </div>
</div>
<div class="ticker" aria-hidden="true"><div id="tick">ART_EURO · CASSURE OR · en attente de données</div></div>
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
var sel={min:240};
var timer=null,activeId=null,POS=0,PNL=0,LIVE=false;

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
function chipsBuild(id,items,key){
  var box=$(id);box.innerHTML='';
  items.forEach(function(it){
    var b=document.createElement('button');b.type='button';b.setAttribute('data-v',it[0]);b.textContent=it[1];
    b.className='chip'+(sel[key]===it[0]?' on':'');
    b.addEventListener('click',function(){
      sel[key]=it[0];
      Array.prototype.forEach.call(box.children,function(c){c.className='chip'+(String(sel[key])===c.getAttribute('data-v')?' on':'')});
    });
    box.appendChild(b);
  });
}
chipsBuild('c_min',[[60,'1 h'],[120,'2 h'],[240,'4 h'],[350,'≈ 6 h']],'min');

/* heure serveur MT5 = New York + 7 h (comme le robot) */
function srv(){
  var ny=new Date(new Date().toLocaleString('en-US',{timeZone:'America/New_York'}));
  return new Date(ny.getTime()+7*3600000);
}
function two(n){return (n<10?'0':'')+n}
function phase(){
  var d=srv(),h=d.getHours(),wk=d.getDay(),ids=['n_range','n_ord','n_pos','n_cl'],on=-1,msg='';
  if(wk===0||wk===6){msg='Week-end : marché fermé, le robot attend lundi.'}
  else if(h<7){on=0;msg='Le robot mesure le range de nuit (haut / bas).'}
  else if(h>=18){on=3;msg='Tout est fermé pour aujourd’hui.'}
  else if(POS>0){on=2;msg='Position ouverte : stop à 1 %, fermeture à 18h.'}
  else{on=1;msg='Ordres stop armés au-dessus et sous le range.'}
  ids.forEach(function(id,i){$(id).className='node'+(i===on?' on':'')});
  $('pmsg').textContent=msg+'  ·  heure serveur '+two(h)+':'+two(d.getMinutes());
}
function clock(){
  var d=new Date();$('clock').textContent=two(d.getUTCHours())+':'+two(d.getUTCMinutes())+':'+two(d.getUTCSeconds())+' UTC';
}

/* sphère de particules */
var cv=$('sph'),cx=cv.getContext('2d'),pts=[],N=520,ang=0,raf=0,W=0,H=0,dpr=1;
(function(){var g=Math.PI*(3-Math.sqrt(5));for(var i=0;i<N;i++){var y=1-(i/(N-1))*2,r=Math.sqrt(1-y*y),t=g*i;pts.push({x:Math.cos(t)*r,y:y,z:Math.sin(t)*r,k:Math.random(),s:Math.random()*6.28})}})();
function size(){dpr=Math.min(2,window.devicePixelRatio||1);W=cv.clientWidth;H=cv.clientHeight;cv.width=Math.round(W*dpr);cv.height=Math.round(H*dpr);cx.setTransform(dpr,0,0,dpr,0,0)}
function draw(ts){
  raf=0;if(document.hidden||$('main').hidden)return;
  if(!W)size();
  cx.clearRect(0,0,W,H);
  var R=Math.min(W,H)*0.36,mx=W/2,my=H/2+4,gain=PNL>=0?0.7:0.3,sp=LIVE?0.012:0.004;
  ang+=sp;var ca=Math.cos(ang),sa=Math.sin(ang),bre=1+0.03*Math.sin(ts/700);
  var g=cx.createRadialGradient(mx,my,R*0.2,mx,my,R*1.5);g.addColorStop(0,PNL>=0?'rgba(25,240,160,.10)':'rgba(255,77,109,.10)');g.addColorStop(1,'rgba(0,0,0,0)');
  cx.fillStyle=g;cx.fillRect(0,0,W,H);
  var arr=[];
  for(var i=0;i<N;i++){
    var p=pts[i],x=p.x*ca+p.z*sa,z=-p.x*sa+p.z*ca,y=p.y,tw=0.5+0.5*Math.sin(ts/500+p.s);
    arr.push([x,y,z,p.k,tw]);
  }
  arr.sort(function(a,b){return a[2]-b[2]});
  for(var j=0;j<N;j++){
    var q=arr[j],sc=0.6+0.4*(q[2]+1)/2,px=mx+q[0]*R*bre*1.25,py=my+q[1]*R*bre,a=(0.25+0.6*(q[2]+1)/2)*(0.6+0.4*q[4]);
    var up=q[3]<gain;
    cx.fillStyle=up?'rgba(25,240,160,'+a.toFixed(2)+')':'rgba(255,77,109,'+a.toFixed(2)+')';
    cx.beginPath();cx.arc(px,py,1.1+1.6*sc,0,6.283);cx.fill();
  }
  cx.strokeStyle='rgba(53,224,255,.22)';cx.lineWidth=1;cx.beginPath();cx.ellipse(mx,my,R*1.28*bre,R*0.32,0,0,6.283);cx.stroke();
  cx.beginPath();cx.ellipse(mx,my,R*bre,R*bre,0,0,6.283);cx.stroke();
  raf=requestAnimationFrame(draw);
}
function startSph(){if(!raf&&!(window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches&&0))raf=requestAnimationFrame(draw)}
window.addEventListener('resize',function(){W=0});
document.addEventListener('visibilitychange',function(){if(!document.hidden)startSph()});

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
  return '<div class="row"><div><b>'+esc(sym)+'</b><span class="tag '+(side==='BUY'?'buy':'sell')+'">'+esc(side)+'</span></div><div class="mut" style="font-size:12px">'+esc(mid)+'</div><div class="pl '+cl(pl)+'">'+sg(pl)+'</div></div>';
}
function stratName(s){return s==='booster'?'Booster':(s==='ema'?'EMA 9/21':(s==='fvg'?'FVG Or':(s==='brk'?'Cassure Or':s)))}

function render(st,runs){
  LAST=st;
  var run=runs&&runs.length?runs[0]:null;
  var live=run&&(run.status==='in_progress'||run.status==='queued'||run.status==='waiting'||run.status==='requested'||run.status==='pending');
  activeId=live?run.id:null;LIVE=!!live;
  var mine=run&&st&&String(st.run_id)===String(run.id);
  var age=st&&st.updated?(st.now-st.updated):null;
  var fresh=live&&mine&&age!==null&&age<180000;
  var pill=$('pill');
  if(fresh){pill.className='pill run';$('pt').textContent='EN COURS'}
  else if(live){pill.className='pill boot';$('pt').textContent='DÉMARRAGE'}
  else{pill.className='pill off';$('pt').textContent='ARRÊTÉ'}
  var sub='Cassure Or · compte démo';
  if(live&&!fresh)sub='Windows s’installe, premières mesures dans 3 à 5 min';
  else if(st&&st.updated)sub='Session '+(live?'en cours':'terminée')+' · mesure il y a '+ago(age);
  $('sub').textContent=sub;

  if(!st||!st.updated){
    PNL=0;POS=0;
    $('pbig').textContent='—';$('pbig').className='pbig';$('pnl').textContent='Aucune donnée. Lance une session ci-dessous.';
    $('eq').textContent='—';$('bal').textContent='—';$('opn').textContent='—';$('pos').textContent='—';
    chart([],0);$('plist').innerHTML='<div class="empty">Aucune position ouverte.</div>';
    $('dlist').innerHTML='<div class="empty">Aucun trade fermé.</div>';
  }else{
    var pnl=st.equity-st.start_eq;PNL=pnl;
    $('pbig').textContent=sg(pnl);$('pbig').className='pbig '+(pnl>0?'up':(pnl<0?'down':''));
    $('pnl').textContent=sg(st.start_eq?pnl/st.start_eq*100:0)+' % depuis le départ ('+f2(st.start_eq)+')';
    $('eq').textContent=f2(st.equity);
    $('bal').textContent=f2(st.balance);
    $('opn').textContent=st.opened+'/'+st.total;
    var ps=st.positions||[];POS=ps.length;
    $('pos').textContent=ps.length;
    chart(st.history,st.start_eq);
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
    if(st.log&&st.log.length)$('tick').textContent='ART_EURO · CASSURE OR  ///  '+st.log.slice(-6).join('   ///   ');
  }
  $('sphcap').textContent=(live?'EN DIRECT':'VEILLE')+' · '+(PNL>=0?'BIAIS HAUSSIER':'BIAIS BAISSIER');
  phase();startSph();
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
  $('go').disabled=true;m.className='msg mut';m.textContent='Envoi…';
  api('/api/run',{minutes:sel.min}).then(function(j){
    m.className='msg '+(j.ok?'up':'down');m.textContent=j.ok?'Session lancée. Windows démarre, compte 3 à 5 minutes.':(j.error||'Échec du lancement.');
    setTimeout(function(){refresh().catch(function(){})},5000);
  }).catch(function(){m.className='msg down';m.textContent='Connexion impossible.'}).then(function(){$('go').disabled=false});
});
$('stop').addEventListener('click',function(){
  if(!activeId)return;var m=$('msg');m.className='msg mut';m.textContent='Arrêt demandé…';
  api('/api/cancel',{id:activeId}).then(function(j){m.className='msg '+(j.ok?'up':'down');m.textContent=j.ok?'Arrêt envoyé.':(j.error||'Échec de l’arrêt.');setTimeout(function(){refresh().catch(function(){})},4000)}).catch(function(){m.className='msg down';m.textContent='Connexion impossible.'});
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
setInterval(clock,1000);clock();phase();
if(KEY){refresh().catch(function(){})}else{lock('')}
})();
</script></body></html>
`;

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
          inputs: { minutes: String(minutes) },
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
