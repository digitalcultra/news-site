/* Digital Cultra News infographic templates. Data-driven from a story object:
 {headline, demo, bg, sources:[{name,lean,url,ts,headline}], timeline:[{ts,label,source}],
  numbers:[{value,label,source}], claims:{confirmed:[{text,source}],unverified:[],disputed:[]}, docs:[{title,url}]}
 Sections with no data return '' (never invent facts). */
(function(g){
const LE=['left','center','right','independent','international','primary'],LN={left:'Left',center:'Center',right:'Right',independent:'Independent',international:'Intl',primary:'Primary doc'};
const COL={left:'#3b82f6',center:'#a78bfa',right:'#e23b3b',independent:'#22c55e',international:'#14b8a6',primary:'#e6edf3'};
const E=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
let BASE='';const I=n=>`<img src="${BASE}assets/icons/${n}.svg" alt="">`;
const T=ts=>new Date(ts*1e3).toLocaleString('en-US',{timeZone:'America/Chicago',month:'short',day:'numeric',hour:'numeric',minute:'2-digit'})+' CT';
const box=(s,ic,h,body,bg)=>`<div class="igc" data-card="${h}" style="--bg:url(${BASE}assets/fffuel/${bg||s.bg||'lllook'}.svg)"><div class="igh">${I(ic)} ${E(h)}</div>${body}</div>`;
function counts(s){const c={};const seen=new Set();for(const x of s.sources||[]){if(seen.has(x.name))continue;seen.add(x.name);c[x.lean]=(c[x.lean]||0)+1}return c}
const F={
 coverage(s){const c=counts(s),t=Object.values(c).reduce((a,b)=>a+b,0);if(!t)return'';
  return box(s,'news','Who covered it',`<div class="cbar">${LE.filter(l=>c[l]).map(l=>`<i class="k-${l}" style="width:${c[l]/t*100}%"></i>`).join('')}</div>
  <div class="cgrid">${LE.map(l=>`<div class="${c[l]?'':'z'}"><span class="sw k-${l}"></span>${LN[l]}<b>${c[l]||0}</b></div>`).join('')}</div>
  <div class="note">${t} outlet${t>1?'s':''}. Leaning labels describe outlets, not this story.</div>`,'cccoil')},
 timeline(s){const t=(s.timeline||[]).slice().sort((a,b)=>a.ts-b.ts);if(!t.length)return'';
  return box(s,'alert','Timeline',`<ol class="tl">${t.map(e=>`<li><time>${T(e.ts)}${e.source?' · '+E(e.source):''}</time>${E(e.label)}</li>`).join('')}</ol>`,'vvvortex')},
 numbers(s){const n=s.numbers||[];if(!n.length)return'';
  return box(s,'money','Key numbers',`<div class="nums">${n.map(x=>`<div class="num"><b>${E(x.value)}</b><span>${E(x.label)}</span>${x.source?`<div class="igs">${E(x.source)}</div>`:''}</div>`).join('')}</div>`,'ffflurry')},
 claims(s){const c=s.claims||{},k=[['confirmed','c','confirmed','Confirmed'],['unverified','u','unverified','Unverified'],['disputed','x','alert','Disputed']];
  if(!k.some(([a])=>(c[a]||[]).length))return'';
  return box(s,'confirmed',"What's confirmed",`<div class="cl">${k.filter(([a])=>(c[a]||[]).length).map(([a,cl,ic,lb])=>`<h4 class="${cl}">${I(ic)} ${lb}</h4><ul>${c[a].map(x=>`<li>${E(x.text)}${x.source?` <span class="igs">(${E(x.source)})</span>`:''}</li>`).join('')}</ul>`).join('')}</div>`,'lllook')},
 title(s){return box(s,'underreported','Digital Cultra News',`<div class="title"><div class="big">What they <em>didn't</em> tell you</div><div class="hl">${E(s.headline)}</div>${s.demo?'<div class="demo">DEMO · headlines & sources only</div>':''}</div>`,'ggglitch')},
 receipts(s){const r=[];const seen=new Set();for(const x of s.sources||[]){const k=x.name+x.url;if(!seen.has(k)){seen.add(k);r.push(x)}}for(const d of s.docs||[])if(!r.some(x=>x.url==d.url))r.push({name:'Primary doc',lean:'primary',url:d.url,headline:d.title});if(!r.length)return'';
  return box(s,'primary','Receipts',`<ul class="rc">${r.map(x=>`<li><span class="tag" style="background:${COL[x.lean]||'#a1a9b3'}">${LN[x.lean]||E(x.lean)}</span><span><b>${E(x.name)}</b>${x.ts?' · <span class="igs">'+T(x.ts)+'</span>':''}<br>${x.url?`<a href="${E(x.url)}" target="_blank" rel="noopener">${E(x.headline||x.url)} ↗</a>`:E(x.headline)}</span></li>`).join('')}</ul>`,'dddoodle')}
};
const ORDER=['title','coverage','timeline','numbers','claims','receipts'];
function fromCluster(c,bg){const its=c.items||[];return{headline:c.title,bg,
 sources:its.map(i=>({name:i.s,lean:i.lean,url:i.u,ts:i.ts,headline:i.t})),
 timeline:its.slice().sort((a,b)=>a.ts-b.ts).map(i=>({ts:i.ts,label:i.t,source:i.s})),
 docs:its.filter(i=>i.lean=='primary').map(i=>({title:i.t,url:i.u})),numbers:[],claims:{}}}
function panel(s,opts={}){const o=opts.order||ORDER;return `<div class="ig">${o.map(k=>F[k](s)).join('')}</div>`}
g.DCNInfo={...F,ORDER,panel,fromCluster,setBase:b=>BASE=b};
})(window);
