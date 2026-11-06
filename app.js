const $=s=>document.querySelector(s),ST="AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC".split(" ");
// Pluggable profile store: swap LocalStore for a Supabase-backed one (see README).
const Store={get:()=>JSON.parse(localStorage.getItem('dcn_profile')||'null'),set:p=>localStorage.setItem('dcn_profile',JSON.stringify(p)),clear:()=>localStorage.removeItem('dcn_profile')};
const TOPICS={All:null,Politics:/congress|senate|house|trump|vote|election|bill|governor|democrat|republican|campaign/i,Courts:/court|judge|lawsuit|indict|ruling|sentenc|trial|charged|doj/i,Crime:/shoot|police|killed|murder|arrest|robbery|crash|fire/i,Economy:/econom|market|stock|inflation|jobs|tax|tariff|bank|fed\b|sec\b/i,World:/ukrain|russia|china|israel|gaza|iran|war|nato|un\b/i,Health:/health|covid|vaccin|hospital|drug|disease|fda|cdc/i,Tech:/\bai\b|tech|meta|google|apple|cyber|musk/i,Weather:/storm|tornado|flood|hurricane|weather|wildfire|quake/i};
const TI={Politics:'politics',Courts:'politics',Crime:'crime',Economy:'money',World:'world',Health:'health',Tech:'tech',Weather:'weather'};let D=null,topic='All',q='';const esc=s=>s.replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const ago=t=>{const m=(Date.now()/1e3-t)/60;return m<60?Math.max(1,m|0)+'m ago':m<1440?(m/60|0)+'h ago':(m/1440|0)+'d ago'};
const LE=['left','center','right','independent','international','primary'];
function status(s){const c=s.status[0]=='S'?'s':s.status[0]=='M'?'m':'p';return `<span class="st ${c}">${IC({s:'unverified',m:'confirmed',p:'primary'}[c],14)} ${s.status}</span>`}
const BGT=[[/war|attack|strike|missile|troops|military|gaza|ukrain|israel|iran|bomb|conflict/i,'ccchaos','conflict'],[/storm|tornado|flood|hurricane|weather|wildfire|quake|heat|snow/i,'cccloud','weather'],[/congress|senate|house|trump|vote|election|bill|governor|democrat|republican|campaign|court|judge/i,'cccoil','politics'],[/shoot|police|killed|murder|arrest|robbery|crash|charged/i,'ggglitch','crime'],[/econom|market|stock|inflation|jobs|tax|tariff|bank/i,'ffflurry','money'],[/health|covid|vaccin|hospital|drug|disease|fda|cdc/i,'cccloud','health'],[/\bai\b|tech|google|apple|cyber|musk/i,'vvvortex','tech']];
function theme(s){const sc=s.scopes.map(x=>x.split(':')[0]);if(s.score>=2)return['ggglitch','underreported'];for(const[r,b,i]of BGT)if(r.test(s.title))return[b,i];if(sc.includes('primary'))return['lllook','primary'];if(sc.includes('world')&&!sc.includes('national'))return['vvvortex','world'];if(sc.some(x=>x=='local'))return['dddoodle','local'];return['ffflurry','national']}
function bar(s){const t=Object.values(s.leans).reduce((a,b)=>a+b,0);return `<div class="bar">${LE.filter(l=>s.leans[l]).map(l=>`<div class="l-${l}" style="width:${s.leans[l]/t*100}%"></div>`).join('')}</div>`}
function lcr(s){const g=l=>s.leans[l]||0;return `L${g('left')}/C${g('center')}/R${g('right')}`+(g('independent')?` · Ind ${g('independent')}`:'')+(g('international')?` · Intl ${g('international')}`:'')+(g('primary')?` · Doc ${g('primary')}`:'')}
function card(s,i){const[b,ic]=theme(s);return `<div class="card story" data-i="${i}"><a class="thumb" href="#story-${i}" style="background-image:url(assets/fffuel/${b}.svg)">${IC(ic,26)}</a><div class="cbody">${status(s)}<h3>${esc(s.title)}</h3>${bar(s)}<div class="meta">Covered by ${s.n} source${s.n>1?'s':''} (${lcr(s)}) · ${esc(s.items[0].s)}${s.n>1?' +'+(s.n-1):''} · ${ago(s.last)}</div>${s.why.length?`<div class="why">${s.why.join(' · ')}</div>`:''}</div></div>`}
function match(s){return(!TOPICS[topic]||TOPICS[topic].test(s.title))&&(!q||s.items.some(i=>i.t.toLowerCase().includes(q)))}
function render(){if(!D)return;const S=D.stories.map((s,i)=>(s.i=i,s)).filter(match);const sc=s=>s.scopes.map(x=>x.split(':')[0]);
 const put=(id,arr,n=12)=>{$(id).innerHTML=arr.slice(0,n).map(s=>card(s,s.i)).join('')||'<p class="muted tiny">No matching stories.</p>'};
 const hot=a=>a.sort((x,y)=>y.n-x.n||y.last-x.last);
 put('#under',S.filter(s=>s.score>=2).sort((a,b)=>b.score-a.score||b.last-a.last),15);
 const loc=s=>s.items.filter(i=>i.scope.startsWith('local')).length*2>=s.items.length;put('#local',hot(S.filter(loc)));put('#national',hot(S.filter(s=>!loc(s)&&sc(s).includes('national'))));
 put('#world',hot(S.filter(s=>sc(s).includes('world')&&!sc(s).includes('national'))));put('#primary',S.filter(s=>sc(s).includes('primary')).sort((a,b)=>b.last-a.last),8);}
function open(i){if(window.DCNMeter&&!DCNMeter.allow('m:'+D.stories[i].title))return;const s=D.stories[i],[b,ic]=theme(s);$('.sheet').style.setProperty('--sbg',`url(assets/fffuel/${b}.svg)`);$('#mbody').innerHTML=`<div class="skick">${IC(ic,22)} ${ic}</div>${status(s)}<h2>${esc(s.title)}</h2>${bar(s)}<div class="legend">${LE.map(l=>`<span><i class="l-${l}"></i>${l}</span>`).join('')}</div>
 <p class="meta">Covered by ${s.n} source(s) (${lcr(s)}). First seen ${ago(s.first)}, last ${ago(s.last)}.</p>${s.why.length?`<p class="why">Why it's flagged: ${s.why.join(' · ')}</p>`:''}
 <h3 class="sec">${IC('news',18)} Infographic</h3>${DCNInfo.panel(DCNInfo.fromCluster(s,b),{order:['coverage','timeline','numbers','claims','receipts']})}<h3 class="sec">Headlines as published</h3>${s.items.map(it=>`<a class="src" href="${esc(it.u)}" target="_blank" rel="noopener"><span class="st" style="background:#21262d">${it.lean}</span> <b>${esc(it.s)}</b> · <span class="meta">${ago(it.ts)}</span><br>${esc(it.t)} ↗</a>`).join('')}`;$('#modal').classList.remove('hidden')}
async function load(){const p=Store.get();$('#loc').innerHTML=IC('local',14)+' '+(p.city?p.city+', ':'')+p.state;$('#lname').textContent=(p.city||'')+' '+p.state;if(window.renderGear&&$('#gear'))renderGear($('#gear'),true,p.state);$('#stat').textContent='Loading feeds…';
 D=await (await fetch(`/api/news?state=${p.state}&city=${encodeURIComponent(p.city)}`)).json();$('#stat').textContent=`${D.feeds_ok}/${D.feeds_total} feeds loaded · ${D.stories.length} stories · updated ${new Date(D.generated*1e3).toLocaleTimeString()}`;render()}
function start(){const p=Store.get();$('#onb').classList.toggle('hidden',!!p);$('#app').classList.toggle('hidden',!p);$('#loc').classList.toggle('hidden',!p);if(p)load()}
$('#stt').innerHTML=ST.map(s=>`<option value="${s}" ${s=='IL'?'selected':''}>${s}</option>`).join('');
$('#f').onsubmit=e=>{e.preventDefault();Store.set({email:$('#em').value,country:$('#co').value,state:$('#stt').value,city:$('#ci').value.trim()});start()};
$('#loc').onclick=()=>{Store.clear();start()};$('#topics').innerHTML=Object.keys(TOPICS).map(t=>`<button class="chip ${t=='All'?'on':''}" data-t="${t}">${TI[t]?IC(TI[t],14)+' ':''}${t}</button>`).join('');
$('#topics').onclick=e=>{const bt=e.target.closest('button');if(!bt)return;e={target:bt};topic=e.target.dataset.t;[...$('#topics').children].forEach(b=>b.classList.toggle('on',b==e.target));render()};
$('#q').oninput=e=>{q=e.target.value.toLowerCase();render()};
document.body.onclick=e=>{const c=e.target.closest('.story');if(c){e.preventDefault();open(+c.dataset.i)}};
$('#x').onclick=()=>$('#modal').classList.add('hidden');$('#modal').onclick=e=>{if(e.target.id=='modal')$('#modal').classList.add('hidden')};

// Worldwide Buried-News Search (Enter + button + region chips). Local filter still runs live via #q.
let W=null, worldMode=false;
const WORLD_CHIPS=[['Ukraine','ukraine war'],['Sudan','sudan war shelter'],['Gaza','gaza israel'],['Myanmar','myanmar airstrike'],['Houthi','houthi red sea'],['Taiwan','taiwan china'],['Sahel','sahel conflict'],['Venezuela','venezuela crisis']];
$('#worldchips').innerHTML=WORLD_CHIPS.map(([lab,qv])=>`<button type="button" class="chip" data-wq="${qv}">${lab}</button>`).join('');
function clearWorld(){worldMode=false;W=null;$('#worldbox').classList.add('hidden');$('#world').innerHTML='';$('#worldmeta').textContent='';$('#stat').textContent=D?`${D.feeds_ok}/${D.feeds_total} feeds loaded · ${D.stories.length} stories · updated ${new Date(D.generated*1e3).toLocaleTimeString()}`:$('#stat').textContent}
async function worldSearch(raw){
  const query=(raw||$('#q').value||'').trim(); if(!query){clearWorld();return}
  worldMode=true; $('#worldbox').classList.remove('hidden'); $('#worldmeta').textContent='Searching worldwide feeds…'; $('#world').innerHTML='<p class="muted tiny">Loading buried matches…</p>';
  try{
    W=await (await fetch('/api/world-search?q='+encodeURIComponent(query))).json();
    const S=(W.stories||[]).map((s,i)=>(s.i='w'+i,s));
    const buried=S.filter(s=>s.score>=2), rest=S.filter(s=>s.score<2);
    const ordered=[...buried,...rest];
    $('#worldmeta').textContent=`Worldwide: “${W.query}” · ${W.feeds_ok||0} feeds · ${ordered.length} stories · buried/underreported first`;
    $('#world').innerHTML=ordered.length?ordered.slice(0,24).map((s,i)=>{s._wi=i;return card(s,'w'+i).replace('data-i="w'+i+'"','data-i="w'+i+'" data-world="1"')}).join(''):'<p class="muted tiny">No worldwide matches yet. Try a country, city, or conflict keyword.</p>';
    $('#stat').textContent=$('#worldmeta').textContent;
  }catch(err){ $('#worldmeta').textContent='Worldwide search failed. Try again.'; $('#world').innerHTML='';}
}
$('#worldbtn').onclick=()=>worldSearch();
$('#worldclear').onclick=()=>clearWorld();
$('#worldchips').onclick=e=>{const bt=e.target.closest('button[data-wq]'); if(!bt)return; $('#q').value=bt.dataset.wq; q=bt.dataset.wq.toLowerCase(); render(); worldSearch(bt.dataset.wq)};
$('#q').addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();worldSearch()}});
// Open world cards from W instead of D
const _open=open; open=function(i){
  if(typeof i==='string' && String(i).startsWith('w') && W){
    const idx=+String(i).slice(1); const s=W.stories[idx]; if(!s)return;
    if(window.DCNMeter&&!DCNMeter.allow('m:'+s.title))return;
    const[b,ic]=theme(s);$('.sheet').style.setProperty('--sbg',`url(assets/fffuel/${b}.svg)`);
    $('#mbody').innerHTML=`<div class="skick">${IC(ic,22)} ${ic}</div>${status(s)}<h2>${esc(s.title)}</h2>${bar(s)}<div class="legend">${LE.map(l=>`<span><i class="l-${l}"></i>${l}</span>`).join('')}</div>
 <p class="meta">Covered by ${s.n} source(s) (${lcr(s)}). First seen ${ago(s.first)}, last ${ago(s.last)}.</p>${s.why.length?`<p class="why">Why it's flagged: ${s.why.join(' · ')}</p>`:''}
 <h3 class="sec">${IC('news',18)} Infographic</h3>${DCNInfo.panel(DCNInfo.fromCluster(s,b),{order:['coverage','timeline','numbers','claims','receipts']})}<h3 class="sec">Headlines as published</h3>${s.items.map(it=>`<a class="src" href="${esc(it.u)}" target="_blank" rel="noopener"><span class="st" style="background:#21262d">${it.lean}</span> <b>${esc(it.s)}</b> · <span class="meta">${ago(it.ts)}</span><br>${esc(it.t)} ↗</a>`).join('')}`;
    $('#modal').classList.remove('hidden'); return;
  }
  return _open(i);
};
document.body.addEventListener('click',e=>{const c=e.target.closest('.story[data-world]'); if(!c)return; e.preventDefault(); e.stopPropagation(); open(c.dataset.i);}, true);

start();setInterval(()=>Store.get()&&load(),10*60e3);
