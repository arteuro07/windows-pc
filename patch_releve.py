import os, sys

def patch(path, edits, marker):
    if not os.path.exists(path):
        print(path, ": introuvable (ignore).")
        return None
    s = open(path, encoding="utf-8").read()
    if marker in s:
        print(path, ": deja applique.")
        return True
    for old, new in edits:
        if s.count(old) != 1:
            print("ECHEC dans", path, "-> bloc introuvable:", old.strip().splitlines()[0])
            print("Rien n'a ete modifie dans ce fichier. Envoie-moi ce message.")
            return False
        s = s.replace(old, new)
    open(path, "w", encoding="utf-8").write(s)
    print(path, ": OK")
    return True

JS = r'''var LAST=null;
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
'''

panel = [
    ('<tbody id="s_tab"></tbody></table>',
     '<tbody id="s_tab"></tbody></table>\n      <button class="btn" id="dl" type="button" style="margin-top:16px;background:transparent;color:var(--gold)">Télécharger le relevé</button>'),
    ("function render(st,runs){\n", "function render(st,runs){\n  LAST=st;\n"),
    ("if(KEY){refresh().catch(function(){})}else{lock('')}", JS + "if(KEY){refresh().catch(function(){})}else{lock('')}"),
]
rep = [
    ('"profit": round(d.profit + d.commission + d.swap, 2)})',
     '"profit": round(d.profit + d.commission + d.swap, 2),\n                              "time": d.time, "volume": d.volume, "price": d.price})'),
]
a = patch("worker.js", panel, "id=\"dl\"")
b = patch("report.py", rep, '"time": d.time')
if a is False or b is False:
    sys.exit(1)
print("Releve ajoute. Pousse sur GitHub pour deployer.")
