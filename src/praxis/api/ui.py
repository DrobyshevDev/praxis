"""Веб-UI Praxis — одностраничное приложение (self-contained) поверх /v1/ask."""

from __future__ import annotations

INDEX_HTML = """<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Praxis — юридический ассистент по праву РФ</title>
<style>
:root{
  --bg:#fbfbfa; --surface:#ffffff; --fg:#181b20; --muted:#6b7280; --faint:#9aa1ab;
  --border:#e8e6e3; --line:#f0eeec; --accent:#2649c9; --accent-fg:#fff;
  --good:#0f7a52; --good-bg:#e7f4ee; --warn:#b7791f; --bad:#c33; --bad-bg:#fbeaea;
  --shadow:0 1px 2px rgba(20,20,30,.04),0 8px 24px rgba(20,20,30,.06);
  --serif:"Iowan Old Style",Georgia,"Times New Roman",serif;
  --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
}
:root[data-theme=dark],
@media (prefers-color-scheme: dark){:root:not([data-theme=light]){
  --bg:#0e1013; --surface:#161a20; --fg:#e9ebef; --muted:#9aa1ab; --faint:#6b7280;
  --border:#252b33; --line:#1e232a; --accent:#6d8bff; --accent-fg:#0b0d10;
  --good:#4cc38a; --good-bg:#122a20; --warn:#e0a458; --bad:#e5766f; --bad-bg:#2a1616;
  --shadow:0 1px 2px rgba(0,0,0,.3),0 10px 30px rgba(0,0,0,.35);
}}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--fg);font-family:var(--sans);
  font-size:16px;line-height:1.6;-webkit-font-smoothing:antialiased}
a{color:var(--accent);text-decoration:none}
.nav{position:sticky;top:0;z-index:10;backdrop-filter:saturate(1.2) blur(8px);
  background:color-mix(in srgb,var(--bg) 82%,transparent);border-bottom:1px solid var(--line)}
.nav .in{max-width:860px;margin:0 auto;padding:12px 20px;display:flex;align-items:center;gap:12px}
.brand{display:flex;align-items:center;gap:10px;font-family:var(--serif);font-size:20px;font-weight:600;
  letter-spacing:.2px}
.logo{width:28px;height:28px;border-radius:8px;background:var(--accent);color:var(--accent-fg);
  display:grid;place-items:center;font-family:var(--serif);font-weight:700;font-size:18px;flex:none}
.nav .sp{flex:1}
.nav a.lnk{color:var(--muted);font-size:14px;padding:6px 10px;border-radius:8px}
.nav a.lnk:hover{color:var(--fg);background:var(--line)}
.wrap{max-width:860px;margin:0 auto;padding:0 20px}
.hero{padding:56px 0 8px;text-align:center}
.hero h1{font-family:var(--serif);font-weight:600;font-size:40px;line-height:1.12;margin:0 0 14px;
  letter-spacing:-.5px}
.hero p{color:var(--muted);font-size:17px;max-width:560px;margin:0 auto 26px}
.search{display:flex;gap:8px;background:var(--surface);border:1px solid var(--border);
  border-radius:14px;padding:8px;box-shadow:var(--shadow);transition:border-color .15s}
.search:focus-within{border-color:var(--accent)}
.search .ic{width:22px;align-self:center;margin-left:8px;color:var(--faint);flex:none}
#q{flex:1;border:0;background:transparent;color:var(--fg);font-size:17px;padding:12px 4px;outline:none}
#b{border:0;border-radius:10px;background:var(--accent);color:var(--accent-fg);font-size:16px;
  font-weight:600;padding:0 22px;cursor:pointer;transition:opacity .15s}
#b:hover{opacity:.9} #b:disabled{opacity:.55;cursor:default}
.disc{color:var(--faint);font-size:12.5px;margin:12px 0 0}
.label{font-size:12px;color:var(--faint);text-transform:uppercase;letter-spacing:.06em;
  font-weight:600;margin:26px 0 10px}
.chips{display:flex;flex-wrap:wrap;gap:8px;justify-content:center}
.chip{font-size:14px;color:var(--fg);background:var(--surface);border:1px solid var(--border);
  border-radius:999px;padding:7px 14px;cursor:pointer;transition:all .15s;max-width:100%;
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.chip:hover{border-color:var(--accent);color:var(--accent)}
.corpus{display:flex;flex-wrap:wrap;gap:7px;justify-content:center;align-items:center;
  color:var(--muted);font-size:13px;margin-top:22px}
.badge{font-size:11px;font-weight:700;color:#fff;border-radius:6px;padding:2px 8px;
  letter-spacing:.02em;white-space:nowrap}
.out{margin:26px 0 40px}
.card{background:var(--surface);border:1px solid var(--border);border-radius:14px;
  box-shadow:var(--shadow);padding:22px 24px;margin-bottom:16px}
.meter{display:flex;align-items:center;gap:12px;margin-bottom:6px}
.meter .lab{font-size:13px;color:var(--muted);white-space:nowrap}
.meter .track{flex:1;height:8px;border-radius:99px;background:var(--line);overflow:hidden}
.meter .track>i{display:block;height:100%;border-radius:99px;transition:width .5s ease}
.meter .pct{font-size:14px;font-weight:700;font-variant-numeric:tabular-nums;min-width:42px;text-align:right}
.answer{white-space:pre-wrap;font-size:16px;line-height:1.7;margin-top:14px}
.sec-h{font-family:var(--serif);font-size:17px;font-weight:600;margin:26px 0 12px;
  display:flex;align-items:center;gap:8px}
.sec-h .n{color:var(--faint);font-weight:400;font-size:14px;font-family:var(--sans)}
.cite{border:1px solid var(--border);border-radius:12px;padding:14px 16px;margin-bottom:10px;
  background:var(--surface);transition:border-color .15s}
.cite:hover{border-color:color-mix(in srgb,var(--accent) 40%,var(--border))}
.cite .head{display:flex;align-items:center;gap:9px;flex-wrap:wrap}
.cite .num{font-weight:650;font-size:15px}
.cite .reqs{color:var(--faint);font-size:12px;white-space:nowrap}
.cite .title{color:var(--muted);font-size:14px}
.verdict{font-size:11.5px;font-weight:700;border-radius:6px;padding:2px 8px}
.v-ok{color:var(--good);background:var(--good-bg)} .v-no{color:var(--bad);background:var(--bad-bg)}
.v-q{color:var(--muted);background:var(--line)}
.cite .txt{color:var(--fg);font-size:14.5px;line-height:1.65;margin-top:9px}
.acts{margin-left:auto;display:flex;gap:8px;align-items:center}
.copy{font-size:12px;color:var(--faint);background:transparent;border:1px solid var(--border);
  border-radius:8px;padding:3px 10px;cursor:pointer;transition:all .15s}
.copy:hover{color:var(--fg);border-color:var(--accent)}
.verify{font-size:12px;color:var(--muted);border:1px solid var(--border);border-radius:8px;
  padding:3px 10px;white-space:nowrap;transition:all .15s}
.verify:hover{color:var(--accent);border-color:var(--accent)}
.srcnote{color:var(--faint);font-size:12.5px;margin-top:16px;padding-top:12px;
  border-top:1px solid var(--line)}
.docbtns{display:flex;gap:8px;flex-wrap:wrap}
.mkclaim{font-size:14px;font-weight:600;color:var(--accent);background:transparent;
  border:1px solid var(--accent);border-radius:10px;padding:9px 16px;cursor:pointer;transition:all .15s}
.mkclaim:hover{background:var(--accent);color:var(--accent-fg)}
.mkclaim:disabled{opacity:.55;cursor:default}
.claimdoc{white-space:pre-wrap;font-size:14px;line-height:1.7;background:var(--line);
  border-radius:10px;padding:16px 18px;margin-top:12px}
.claimnote{color:var(--muted);font-size:13px;margin-top:10px}
mark{background:color-mix(in srgb,var(--accent) 22%,transparent);color:inherit;border-radius:3px;
  padding:0 2px;box-decoration-break:clone}
.case{border-left:3px solid var(--accent);background:var(--line);border-radius:0 10px 10px 0;
  padding:12px 15px;margin-bottom:10px}
.case .c-h{font-weight:650;font-size:14.5px}
.case .c-t{color:var(--muted);font-size:13.5px;margin-top:4px}
.warn{color:var(--warn);background:var(--good-bg);border:1px solid color-mix(in srgb,var(--warn) 30%,transparent);
  border-radius:10px;padding:12px 15px;font-size:14px;margin-top:14px}
.warn{background:color-mix(in srgb,var(--warn) 12%,var(--surface))}
details{margin-top:16px} details>summary{cursor:pointer;color:var(--muted);font-size:13.5px;
  list-style:none;user-select:none}
details>summary::-webkit-details-marker{display:none}
details>summary::before{content:"▸ ";color:var(--faint)}
details[open]>summary::before{content:"▾ "}
details pre{white-space:pre-wrap;color:var(--muted);font-size:13px;line-height:1.7;
  margin-top:10px;padding-left:14px;border-left:2px solid var(--line)}
.skel{color:var(--muted);font-size:14px;display:flex;align-items:center;gap:10px}
.spin{width:15px;height:15px;border:2px solid var(--line);border-top-color:var(--accent);
  border-radius:50%;animation:s .7s linear infinite}
@keyframes s{to{transform:rotate(360deg)}}
.calc{margin:20px 0 0}
.calc>summary{cursor:pointer;color:var(--muted);font-size:14px;font-weight:600;list-style:none;
  user-select:none;padding:10px 0;text-align:center}
.calc>summary::-webkit-details-marker{display:none}
.calc>summary::before{content:"🧮 "}
.calcgrid{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:6px}
.calccard{background:var(--surface);border:1px solid var(--border);border-radius:14px;
  box-shadow:var(--shadow);padding:16px 18px}
.calct{font-family:var(--serif);font-size:16px;font-weight:600;margin-bottom:12px}
.calcrow{display:flex;gap:8px;margin-bottom:8px;align-items:center;flex-wrap:wrap}
.calccard input[type=number],.calccard select{flex:1;min-width:0;border:1px solid var(--border);
  background:var(--bg);color:var(--fg);border-radius:9px;padding:9px 11px;font-size:14px;outline:none}
.calccard input:focus,.calccard select:focus{border-color:var(--accent)}
.calccard .chk{flex:1;display:flex;align-items:center;gap:7px;font-size:13.5px;color:var(--muted);cursor:pointer}
.calccard button{border:0;border-radius:9px;background:var(--accent);color:var(--accent-fg);
  font-size:14px;font-weight:600;padding:9px 16px;cursor:pointer;transition:opacity .15s;white-space:nowrap}
.calccard button:hover{opacity:.9}
.calcout{margin-top:8px;min-height:1px}
.calc-amt{font-size:22px;font-weight:700;font-variant-numeric:tabular-nums}
.calc-bd{color:var(--muted);font-size:13px;margin-top:3px}
.calc-basis{font-size:12.5px;margin-top:8px;padding-top:8px;border-top:1px solid var(--line);color:var(--faint)}
.calc-basis a{color:var(--muted)}
.calc-err{color:var(--bad);font-size:13.5px}
@media(max-width:620px){.calcgrid{grid-template-columns:1fr}}
.contract{margin:12px 0 0}
.contract>summary{cursor:pointer;color:var(--muted);font-size:14px;font-weight:600;list-style:none;
  user-select:none;padding:10px 0;text-align:center}
.contract>summary::-webkit-details-marker{display:none}
.contract>summary::before{content:"📄 "}
.contract textarea{width:100%;min-height:140px;border:1px solid var(--border);background:var(--surface);
  color:var(--fg);border-radius:12px;padding:12px 14px;font-size:14px;line-height:1.5;outline:none;
  resize:vertical;font-family:var(--sans)}
.contract textarea:focus{border-color:var(--accent)}
.crow{display:flex;gap:10px;margin-top:8px;align-items:center;justify-content:space-between;flex-wrap:wrap}
.crow button{border:0;border-radius:9px;background:var(--accent);color:var(--accent-fg);font-size:14px;
  font-weight:600;padding:9px 18px;cursor:pointer;transition:opacity .15s}
.crow button:hover{opacity:.9}
.chk-sum{font-size:13.5px;color:var(--muted);margin:14px 0 4px;font-weight:600}
.chk-item{display:flex;gap:10px;align-items:flex-start;padding:10px 0;border-bottom:1px solid var(--line)}
.chk-ic{flex:none;width:20px;text-align:center;font-size:15px;font-weight:700}
.chk-ok .chk-ic{color:var(--good)} .chk-miss .chk-ic{color:var(--warn)} .chk-warn .chk-ic{color:var(--bad)}
.chk-label{font-weight:600;font-size:14.5px}
.chk-note{color:var(--muted);font-size:13.5px;margin-top:2px}
.chk-cite{font-size:12.5px;margin-top:3px;color:var(--faint)}
.chk-cite a{color:var(--muted)}
.foot{border-top:1px solid var(--line);margin-top:20px;padding:26px 0 60px;color:var(--faint);
  font-size:13px;text-align:center}
.foot a{color:var(--muted)} .foot .leg{margin-top:8px;font-size:12px}
@media(max-width:620px){.hero{padding:34px 0 4px}.hero h1{font-size:30px}.search{flex-direction:column}
  #b{padding:12px}.hero p{font-size:15px}}
</style>
</head>
<body>
<div class="nav"><div class="in">
  <div class="brand"><span class="logo">§</span>Praxis</div>
  <span class="sp"></span>
  <a class="lnk" href="/docs" target="_blank">API</a>
  <a class="lnk" href="https://github.com/DrobyshevDev/praxis" target="_blank">GitHub</a>
</div></div>

<div class="wrap">
  <div class="hero">
    <h1>Ответы по праву РФ<br>со ссылками на закон</h1>
    <p>Задайте вопрос простыми словами. Praxis найдёт применимые нормы, проверит каждую ссылку и покажет судебную практику.</p>
    <div class="search">
      <svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.2-3.2"/></svg>
      <input id="q" placeholder="Например: что грозит за мошенничество?" autocomplete="off">
      <button id="b" type="button">Спросить</button>
    </div>
    <div class="disc">Не является юридической консультацией.</div>
    <div class="corpus" id="corpus"></div>
  </div>

  <div id="starter">
    <div class="label" style="text-align:center">Примеры вопросов</div>
    <div class="chips" id="examples"></div>
  </div>
  <div id="histbox" style="display:none">
    <div class="label">Недавние</div>
    <div class="chips" id="hist" style="justify-content:flex-start"></div>
  </div>

  <details class="calc" id="calc">
    <summary>Калькуляторы: неустойка и госпошлина</summary>
    <div class="calcgrid">
      <div class="calccard">
        <div class="calct">Неустойка потребителю</div>
        <div class="calcrow">
          <input id="npPrice" type="number" min="0" placeholder="цена, ₽">
          <input id="npDays" type="number" min="0" placeholder="дней просрочки">
        </div>
        <div class="calcrow">
          <select id="npKind">
            <option value="товар">товар — 1%/день</option>
            <option value="услуга">услуга/работа — 3%/день</option>
          </select>
          <button id="npBtn" type="button">Рассчитать</button>
        </div>
        <div class="calcout" id="npOut"></div>
      </div>
      <div class="calccard">
        <div class="calct">Госпошлина в суд</div>
        <div class="calcrow">
          <input id="feeAmt" type="number" min="0" placeholder="цена иска, ₽">
        </div>
        <div class="calcrow">
          <label class="chk"><input id="feeCons" type="checkbox">иск о защите прав потребителя</label>
          <button id="feeBtn" type="button">Рассчитать</button>
        </div>
        <div class="calcout" id="feeOut"></div>
      </div>
      <div class="calccard">
        <div class="calct">Проценты по ст. 395 ГК</div>
        <div class="calcrow">
          <input id="inPrin" type="number" min="0" placeholder="сумма долга, ₽">
          <input id="inRate" type="number" min="0" step="0.01" placeholder="ставка ЦБ, %">
        </div>
        <div class="calcrow">
          <input id="inDays" type="number" min="0" placeholder="дней просрочки">
          <button id="inBtn" type="button">Рассчитать</button>
        </div>
        <div class="calcout" id="inOut"></div>
      </div>
    </div>
  </details>

  <details class="contract" id="contract">
    <summary>Проверка договора по чек-листу</summary>
    <textarea id="ctText" placeholder="Вставьте текст договора — Praxis проверит существенные условия и рискованные пункты по нормам…"></textarea>
    <div class="crow">
      <span class="disc" style="margin:0">Прозрачная проверка по нормам — ориентир, не заменяет юриста.</span>
      <button id="ctBtn" type="button">Проверить</button>
    </div>
    <div id="ctOut"></div>
  </details>

  <div class="out" id="out"></div>
</div>

<div class="foot"><div class="wrap">
  Praxis · юридический ассистент по праву РФ ·
  <a href="https://github.com/DrobyshevDev/praxis" target="_blank">исходный код</a>
  <div class="leg">Проверка цитат: ✓ норма подтверждает тезис · ? релевантна · ✗ противоречит. Не заменяет юриста.</div>
</div></div>

<script>
const q=document.getElementById('q'),b=document.getElementById('b'),out=document.getElementById('out'),
  hist=document.getElementById('hist'),histbox=document.getElementById('histbox'),
  examples=document.getElementById('examples'),corpus=document.getElementById('corpus');
const VMAP={"подтверждает":["v-ok","✓ подтверждает"],"не относится":["v-q","? релевантна"],
  "противоречит":["v-no","✗ противоречит"]};
const COLORS={"ГК РФ":"#2649c9","УК РФ":"#c0392b","НК РФ":"#0f7a52","ТК РФ":"#c26a1b",
  "КоАП РФ":"#7c4dbd","ЖК РФ":"#0e8a8a","ЗоЗПП":"#c2185b"};
const EXAMPLES=["что грозит за мошенничество","можно ли расторгнуть договор через суд",
  "как уволить сотрудника за прогул","за какое нарушение ПДД лишают прав",
  "что такое злоупотребление правом","в каком размере возмещаются убытки"];
function color(c){if(COLORS[c])return COLORS[c];let h=0;for(const x of c||"")h=(h*31+x.charCodeAt(0))%360;return`hsl(${h},45%,45%)`;}
function confColor(p){return p>=66?'var(--good)':p>=33?'var(--warn)':'var(--bad)';}
function esc(s){const d=document.createElement('div');d.textContent=s;return d.innerHTML;}
function hl(t,s){if(!s||s.length!==2)return esc(t);const[a,e]=s;if(a<0||e>t.length||a>=e)return esc(t);
  return esc(t.slice(0,a))+'<mark>'+esc(t.slice(a,e))+'</mark>'+esc(t.slice(e));}

async function ask(){
  const question=q.value.trim();if(!question)return;
  b.disabled=true;document.getElementById('starter').style.display='none';
  out.innerHTML='<div class="card"><div class="skel"><span class="spin"></span>Ищу в законе и проверяю ссылки…</div></div>';
  out.scrollIntoView({behavior:'smooth',block:'start'});
  try{const r=await fetch('/v1/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question})});
    render(await r.json());saveHist(question);renderHist();}
  catch(e){out.innerHTML='<div class="card"><div class="warn">Не удалось получить ответ. Проверьте, что сервер запущен.</div></div>';}
  b.disabled=false;
}
b.onclick=ask;q.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();ask();}});

function render(a){
  const pct=Math.round((a.confidence||0)*100);const cites=[];
  let h='<div class="card">';
  h+=`<div class="meter"><span class="lab">Уверенность</span><span class="track"><i style="width:${pct}%;background:${confColor(pct)}"></i></span><span class="pct">${pct}%</span></div>`;
  h+=`<div class="answer">${esc(a.text)}</div>`;
  if(a.citations&&a.citations.length){
    h+=`<div class="sec-h">Применимые нормы <span class="n">${a.citations.length}</span></div>`;
    for(const c of a.citations){
      const v=VMAP[c.verdict];const i=cites.length;
      cites.push(c.citation+' — '+c.article_title+'\\n'+c.text);
      h+='<div class="cite"><div class="head">';
      h+=`<span class="badge" style="background:${color(c.code)}">${esc(c.code||'')}</span>`;
      h+=`<span class="num">${esc(c.citation)}</span>`;
      if(c.act_ref)h+=`<span class="reqs">· ${esc(c.act_ref)}</span>`;
      if(v)h+=`<span class="verdict ${v[0]}">${v[1]}</span>`;
      h+='<span class="acts">';
      if(c.source_url)h+=`<a class="verify" href="${esc(c.source_url)}" target="_blank" rel="noopener" title="Открыть действующую редакцию статьи">сверить ↗</a>`;
      h+=`<button class="copy" data-c="${i}">копировать</button></span></div>`;
      h+=`<div class="title">${esc(c.article_title)}</div>`;
      h+=`<div class="txt">${hl(c.text,c.span)}</div></div>`;
    }
    h+='<div class="srcnote">Тексты норм — из корпуса (транскрипция, Викитека) и могут отставать от действующей редакции. «Сверить» открывает текущий текст статьи на zakonrf.info.</div>';
  }
  if(a.claim_applicable){
    h+=`<div class="sec-h">Документы <span class="n">на основе найденных норм</span></div>`;
    h+='<div class="docbtns"><button class="mkclaim" id="mkclaim">Составить претензию</button>';
    h+='<button class="mkclaim" id="mklaw">Исковое заявление</button></div>';
    h+='<div id="claimbox"></div>';
  }
  if(a.related_cases&&a.related_cases.length){
    h+=`<div class="sec-h">Судебная практика <span class="n">по этим нормам</span></div>`;
    for(const c of a.related_cases)
      h+=`<div class="case"><div class="c-h">${esc(c.citation)}</div><div class="c-t">${esc(c.summary)}</div></div>`;
  }
  if(a.unverified_claims&&a.unverified_claims.length)
    h+='<div class="warn">⚠ Утверждения без опоры на норму (не считать фактом): '+a.unverified_claims.map(esc).join('; ')+'</div>';
  if(a.steps&&a.steps.length)
    h+='<details><summary>Ход рассуждения</summary><pre>'+a.steps.map(esc).join('\\n')+'</pre></details>';
  h+='</div>';
  out.innerHTML=h;
  out.querySelectorAll('.copy').forEach(el=>el.onclick=()=>{navigator.clipboard.writeText(cites[+el.dataset.c]);
    el.textContent='скопировано';setTimeout(()=>el.textContent='копировать',1200);});
  const mk=document.getElementById('mkclaim'),ml=document.getElementById('mklaw');
  if(mk)mk.onclick=()=>makeDoc('/v1/claim',a.question,mk,'претензию');
  if(ml)ml.onclick=()=>makeDoc('/v1/lawsuit',a.question,ml,'исковое заявление');
}

async function makeDoc(path,question,btn,label){
  btn.disabled=true;const box=document.getElementById('claimbox');
  box.innerHTML='<div class="skel" style="margin-top:12px"><span class="spin"></span>Собираю '+label+'…</div>';
  try{
    const r=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question})});
    const c=await r.json();
    if(!c.applicable){box.innerHTML='<div class="claimnote">'+esc(c.note||'Документ неприменим.')+'</div>';btn.disabled=false;return;}
    let hh='<div class="claimdoc">'+esc(c.text)+'</div>';
    hh+='<div style="margin-top:10px"><button class="copy" id="claimcopy">копировать текст</button></div>';
    hh+='<div class="claimnote">⚠ '+esc(c.disclaimer)+'</div>';
    box.innerHTML=hh;
    document.getElementById('claimcopy').onclick=()=>{navigator.clipboard.writeText(c.text);
      const b=document.getElementById('claimcopy');b.textContent='скопировано';setTimeout(()=>b.textContent='копировать текст',1200);};
  }catch(e){box.innerHTML='<div class="warn">Не удалось собрать документ.</div>';}
  btn.disabled=false;
}

function saveHist(x){let h=JSON.parse(localStorage.getItem('praxis_hist')||'[]');
  h=[x,...h.filter(y=>y!==x)].slice(0,7);localStorage.setItem('praxis_hist',JSON.stringify(h));}
function renderHist(){const h=JSON.parse(localStorage.getItem('praxis_hist')||'[]');
  histbox.style.display=h.length?'block':'none';
  hist.innerHTML=h.map(x=>`<span class="chip" title="${esc(x)}">${esc(x)}</span>`).join('');
  hist.querySelectorAll('.chip').forEach((el,i)=>el.onclick=()=>{q.value=h[i];ask();});}

examples.innerHTML=EXAMPLES.map(x=>`<span class="chip">${esc(x)}</span>`).join('');
examples.querySelectorAll('.chip').forEach((el,i)=>el.onclick=()=>{q.value=EXAMPLES[i];ask();});
renderHist();

// --- Калькуляторы ---
function rub(x){return (Math.round(x*100)/100).toLocaleString('ru')+' ₽';}
function basisHtml(b){let s=esc(b.citation);
  if(b.source_url)s=`<a href="${esc(b.source_url)}" target="_blank" rel="noopener">${s} ↗</a>`;
  return `<div class="calc-basis">Основание: ${s}. ${esc(b.note||'')}</div>`;}
async function calcPost(path,body,outEl){
  outEl.innerHTML='<div class="calc-bd">…</div>';
  try{const r=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
    if(!r.ok){const e=await r.json().catch(()=>({}));outEl.innerHTML='<div class="calc-err">'+esc(e.detail||'Проверьте ввод')+'</div>';return null;}
    return await r.json();
  }catch(e){outEl.innerHTML='<div class="calc-err">Не удалось рассчитать.</div>';return null;}
}
document.getElementById('npBtn').onclick=async()=>{
  const price=parseFloat(document.getElementById('npPrice').value),days=parseInt(document.getElementById('npDays').value),
    out=document.getElementById('npOut');
  if(!(price>0)||!(days>=0)){out.innerHTML='<div class="calc-err">Введите цену и число дней.</div>';return;}
  const d=await calcPost('/v1/penalty',{price,days,kind:document.getElementById('npKind').value},out);
  if(!d)return;
  out.innerHTML=`<div class="calc-amt">${rub(d.amount)}</div><div class="calc-bd">${esc(d.breakdown)}${d.capped?' · достигнут потолок':''}</div>`+basisHtml(d.basis);
};
document.getElementById('feeBtn').onclick=async()=>{
  const amount=parseFloat(document.getElementById('feeAmt').value),out=document.getElementById('feeOut');
  if(!(amount>=0)){out.innerHTML='<div class="calc-err">Введите цену иска.</div>';return;}
  const d=await calcPost('/v1/fee',{amount,consumer:document.getElementById('feeCons').checked},out);
  if(!d)return;
  const head=d.exempt?'0 ₽ — освобождён':rub(d.fee);
  out.innerHTML=`<div class="calc-amt">${esc(head)}</div><div class="calc-bd">${esc(d.breakdown)}</div>`+basisHtml(d.basis);
};
document.getElementById('inBtn').onclick=async()=>{
  const principal=parseFloat(document.getElementById('inPrin').value),
    rate_pct=parseFloat(document.getElementById('inRate').value),
    days=parseInt(document.getElementById('inDays').value),out=document.getElementById('inOut');
  if(!(principal>0)||!(rate_pct>=0)||!(days>=0)){out.innerHTML='<div class="calc-err">Введите сумму, ставку и дни.</div>';return;}
  const d=await calcPost('/v1/interest',{principal,rate_pct,days},out);
  if(!d)return;
  out.innerHTML=`<div class="calc-amt">${rub(d.amount)}</div><div class="calc-bd">${esc(d.breakdown)}</div>`+basisHtml(d.basis);
};

// --- Чек-лист договора ---
const CHK_IC={ok:'✓',missing:'—',warning:'⚠'},CHK_CL={ok:'chk-ok',missing:'chk-miss',warning:'chk-warn'};
document.getElementById('ctBtn').onclick=async()=>{
  const text=document.getElementById('ctText').value.trim(),out=document.getElementById('ctOut');
  if(text.length<40){out.innerHTML='<div class="calc-err" style="margin-top:10px">Вставьте текст договора (не короче 40 символов).</div>';return;}
  out.innerHTML='<div class="skel" style="margin-top:14px"><span class="spin"></span>Проверяю по чек-листу…</div>';
  try{
    const r=await fetch('/v1/contract',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text})});
    const d=await r.json();
    if(!d.ok){out.innerHTML='<div class="calc-err" style="margin-top:10px">'+esc(d.note)+'</div>';return;}
    let h='<div class="chk-sum">'+esc(d.summary)+'</div>';
    for(const c of d.checks){
      let cite=esc(c.citation);
      if(c.source_url)cite=`<a href="${esc(c.source_url)}" target="_blank" rel="noopener">${cite} ↗</a>`;
      h+=`<div class="chk-item ${CHK_CL[c.status]}"><div class="chk-ic">${CHK_IC[c.status]}</div><div class="chk-body">`+
        `<div class="chk-label">${esc(c.label)}</div><div class="chk-note">${esc(c.note)}</div>`+
        `<div class="chk-cite">Норма: ${cite}</div></div></div>`;
    }
    h+='<div class="claimnote">⚠ '+esc(d.disclaimer)+'</div>';
    out.innerHTML=h;
  }catch(e){out.innerHTML='<div class="warn" style="margin-top:10px">Не удалось проверить договор.</div>';}
};
fetch('/v1/stats').then(r=>r.json()).then(s=>{
  corpus.innerHTML=`<span>${s.provisions.toLocaleString('ru')} норм · ${s.acts} кодексов</span>`+
    s.codes.map(c=>`<span class="badge" style="background:${color(c)}">${esc(c)}</span>`).join('');
}).catch(()=>{});
</script>
</body>
</html>"""
