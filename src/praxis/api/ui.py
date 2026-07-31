"""Веб-UI (одна страница, self-contained) для /v1/ask."""

from __future__ import annotations

INDEX_HTML = """<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Praxis — юридический ассистент</title>
<style>
:root { color-scheme: light dark; --bg:#fff; --fg:#1a1a1a; --muted:#6b7280;
  --card:#f6f7f9; --border:#e3e5e8; --accent:#2d6cdf; --good:#12855a; --warn:#b7791f; }
@media (prefers-color-scheme: dark) { :root { --bg:#15171a; --fg:#e8eaed; --muted:#9aa0a6;
  --card:#1e2126; --border:#2c3036; --accent:#5b8def; --good:#3fbe86; --warn:#e0a458; } }
* { box-sizing:border-box; } body { margin:0; background:var(--bg); color:var(--fg);
  font:16px/1.55 -apple-system,Segoe UI,Roboto,sans-serif; }
.wrap { max-width:780px; margin:0 auto; padding:40px 20px 80px; }
h1 { font-size:24px; margin:0 0 2px; } .tag { color:var(--muted); margin-bottom:6px; font-size:14px; }
.stats { color:var(--muted); font-size:13px; margin-bottom:22px; display:flex; flex-wrap:wrap;
  gap:6px; align-items:center; }
form { display:flex; gap:8px; margin-bottom:8px; }
input { flex:1; padding:12px 14px; border:1px solid var(--border); border-radius:10px;
  background:var(--card); color:var(--fg); font-size:16px; }
button { padding:12px 18px; border:0; border-radius:10px; background:var(--accent);
  color:#fff; font-size:16px; font-weight:600; cursor:pointer; }
button:disabled { opacity:.6; cursor:default; }
.hint { color:var(--muted); font-size:13px; margin-bottom:14px; }
.chips { display:flex; flex-wrap:wrap; gap:6px; margin-bottom:20px; }
.chip { font-size:13px; color:var(--fg); background:var(--card); border:1px solid var(--border);
  border-radius:20px; padding:5px 12px; cursor:pointer; max-width:100%;
  overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.chip:hover { border-color:var(--accent); }
.chip.hq { color:var(--muted); }
.label { font-size:12px; color:var(--muted); margin:0 0 6px; text-transform:uppercase; letter-spacing:.04em; }
.answer { white-space:pre-wrap; background:var(--card); border:1px solid var(--border);
  border-radius:12px; padding:16px 18px; margin-top:16px; }
.conf { display:flex; align-items:center; gap:10px; margin:18px 0 4px; font-size:14px; color:var(--muted); }
.bar { flex:1; height:8px; border-radius:5px; background:var(--border); overflow:hidden; }
.bar > i { display:block; height:100%; background:var(--accent); }
.sources { margin-top:18px; } .src { border:1px solid var(--border); border-radius:10px;
  padding:12px 14px; margin-bottom:10px; background:var(--card); }
.src .cit { font-weight:600; display:flex; align-items:center; gap:8px; flex-wrap:wrap; }
.badge { font-size:11px; font-weight:700; color:#fff; border-radius:6px; padding:1px 7px; }
.src .mark { margin-right:2px; }
.mark.ok { color:var(--good); } .mark.q { color:var(--muted); } .mark.no { color:#c0392b; }
.src .txt { color:var(--fg); font-size:14px; margin-top:6px; }
.copy { margin-left:auto; font-size:11px; font-weight:400; color:var(--muted); background:none;
  border:1px solid var(--border); border-radius:6px; padding:1px 8px; cursor:pointer; }
.copy:hover { color:var(--fg); }
mark { background:rgba(45,108,223,.22); color:inherit; border-radius:3px; padding:0 2px; }
.warn { color:var(--warn); font-size:14px; margin-top:14px; }
details { margin-top:20px; color:var(--muted); font-size:13px; }
details pre { white-space:pre-wrap; }
.foot { margin-top:28px; color:var(--muted); font-size:12px; }
@media (max-width:600px) { .wrap { padding:24px 14px 60px; } form { flex-direction:column; }
  button { width:100%; } h1 { font-size:22px; } }
</style>
</head>
<body>
<div class="wrap">
  <h1>Praxis</h1>
  <div class="tag">Юридический ассистент по праву РФ · ответы с проверяемыми ссылками на нормы</div>
  <div class="stats" id="stats"></div>
  <form id="f">
    <input id="q" placeholder="Например: что грозит за мошенничество?" autocomplete="off">
    <button id="b" type="button">Спросить</button>
  </form>
  <div class="hint">Не является юридической консультацией.</div>
  <div id="starter">
    <div class="label">Примеры</div>
    <div class="chips" id="examples"></div>
  </div>
  <div id="histbox" style="display:none">
    <div class="label">История</div>
    <div class="chips" id="hist"></div>
  </div>
  <div id="out"></div>
  <div class="foot">Каждый ответ проходит проверку цитат: ✓ — норма подтверждает тезис, ? — релевантна, ✗ — противоречит.</div>
</div>
<script>
const q=document.getElementById('q'), b=document.getElementById('b'), out=document.getElementById('out'),
      hist=document.getElementById('hist'), histbox=document.getElementById('histbox'),
      examples=document.getElementById('examples'), statsEl=document.getElementById('stats');
const MARK={"подтверждает":["ok","✓"],"не относится":["q","?"],"противоречит":["no","✗"]};
const COLORS={"ГК РФ":"#2d6cdf","УК РФ":"#c0392b","НК РФ":"#12855a","ТК РФ":"#c26a1b",
  "КоАП РФ":"#7c4dbd","ЖК РФ":"#0e8a8a"};
const EXAMPLES=["что грозит за мошенничество","можно ли расторгнуть договор через суд",
  "как уволить сотрудника за прогул","за какое нарушение ПДД лишают прав",
  "что такое злоупотребление правом","в каком размере возмещаются убытки"];

function colorOf(code){ if(COLORS[code]) return COLORS[code];
  let h=0; for(const ch of code||"") h=(h*31+ch.charCodeAt(0))%360; return `hsl(${h},45%,45%)`; }

async function ask(){
  const question=q.value.trim(); if(!question) return;
  b.disabled=true; b.textContent='...'; out.innerHTML='<div class="conf">Ищу в законе…</div>';
  try{
    const r=await fetch('/v1/ask',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({question})});
    render(await r.json()); saveHist(question); renderHist();
  }catch(err){ out.innerHTML='<div class="warn">Ошибка запроса. Проверьте, что сервер запущен.</div>'; }
  b.disabled=false; b.textContent='Спросить';
}
b.addEventListener('click', ask);
q.addEventListener('keydown', e=>{ if(e.key==='Enter'){ e.preventDefault(); ask(); }});

function esc(s){const d=document.createElement('div');d.textContent=s;return d.innerHTML;}
function hl(text,span){ if(!span||span.length!==2) return esc(text);
  const [s,e]=span; if(s<0||e>text.length||s>=e) return esc(text);
  return esc(text.slice(0,s))+'<mark>'+esc(text.slice(s,e))+'</mark>'+esc(text.slice(e)); }
function saveHist(query){ let h=JSON.parse(localStorage.getItem('praxis_hist')||'[]');
  h=[query,...h.filter(x=>x!==query)].slice(0,8); localStorage.setItem('praxis_hist',JSON.stringify(h)); }
function renderHist(){ const h=JSON.parse(localStorage.getItem('praxis_hist')||'[]');
  histbox.style.display = h.length?'block':'none';
  hist.innerHTML=h.map(x=>`<span class="chip hq" title="${esc(x)}">${esc(x)}</span>`).join('');
  hist.querySelectorAll('.chip').forEach((el,i)=>el.onclick=()=>{q.value=h[i];ask();}); }
function copyCite(btn,txt){ navigator.clipboard.writeText(txt).then(()=>{
  btn.textContent='скопировано'; setTimeout(()=>btn.textContent='копировать',1200); }); }

function render(a){
  const pct=Math.round((a.confidence||0)*100);
  let h=`<div class="conf">Уверенность: ${pct}%<div class="bar"><i style="width:${pct}%"></i></div></div>`;
  h+=`<div class="answer">${esc(a.text)}</div>`;
  const cites=[];
  if(a.citations&&a.citations.length){
    h+='<div class="sources">';
    for(const c of a.citations){
      const m=MARK[c.verdict]||["q",""]; const i=cites.length;
      cites.push(c.citation+' — '+c.article_title+'\\n'+c.text);
      const badge=`<span class="badge" style="background:${colorOf(c.code)}">${esc(c.code||'')}</span>`;
      const mark=m[1]?`<span class="mark ${m[0]}">${m[1]}</span>`:'';
      h+=`<div class="src"><div class="cit">${badge}${mark}${esc(c.citation)}<button class="copy" data-c="${i}">копировать</button></div><div class="txt">${hl(c.text,c.span)}</div></div>`;
    }
    h+='</div>';
  }
  if(a.related_cases&&a.related_cases.length){
    h+='<div class="sources"><div class="label">Судебная практика по этим нормам</div>';
    for(const c of a.related_cases)
      h+=`<div class="src"><div class="cit">${esc(c.citation)}</div><div class="txt">${esc(c.summary)}</div></div>`;
    h+='</div>';
  }
  if(a.unverified_claims&&a.unverified_claims.length)
    h+='<div class="warn">⚠ Без опоры на норму (не считать фактом): '+a.unverified_claims.map(esc).join('; ')+'</div>';
  if(a.steps&&a.steps.length)
    h+='<details><summary>Ход рассуждения</summary><pre>'+a.steps.map(esc).join('\\n')+'</pre></details>';
  out.innerHTML=h;
  out.querySelectorAll('.copy').forEach(el=>el.onclick=()=>copyCite(el, cites[+el.dataset.c]));
}

examples.innerHTML=EXAMPLES.map(x=>`<span class="chip">${esc(x)}</span>`).join('');
examples.querySelectorAll('.chip').forEach((el,i)=>el.onclick=()=>{q.value=EXAMPLES[i];ask();});
renderHist();
fetch('/v1/stats').then(r=>r.json()).then(s=>{
  const badges=s.codes.map(c=>`<span class="badge" style="background:${colorOf(c)}">${esc(c)}</span>`).join(' ');
  statsEl.innerHTML=`Корпус: ${s.provisions.toLocaleString('ru')} норм в ${s.acts} кодексах &nbsp; ${badges}`;
}).catch(()=>{});
</script>
</body>
</html>"""
