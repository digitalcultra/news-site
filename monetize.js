// Monetization UI: pricing cards, prep gear, store promo, newsletter. Config lives in config.js.
(function(){
const C=window, $=s=>document.querySelector(s);
const css=`.mz-plans{display:grid;gap:12px}@media(min-width:700px){.mz-plans{grid-template-columns:1fr 1fr}}
.mz-plan{background:#161b22;border:1px solid #30363d;border-radius:14px;padding:18px;position:relative}
.mz-plan.pro{border-color:#e5484d;box-shadow:0 0 22px #e5484d33}.mz-plan h3{margin:0 0 4px;font-size:18px}
.mz-price{font-size:30px;font-weight:800;margin:6px 0}.mz-price small{font-size:13px;color:#8b949e;font-weight:500}
.mz-plan ul{list-style:none;padding:0;margin:12px 0}.mz-plan li{padding:6px 0;border-top:1px solid #21262d;font-size:14px}.mz-plan li:before{content:"✓ ";color:#3fb950;font-weight:700}
.mz-tag{position:absolute;top:-10px;right:14px;background:#e5484d;color:#fff;font-size:11px;font-weight:700;padding:3px 9px;border-radius:999px}
.mz-btn{display:block;text-align:center;background:#e5484d;color:#fff!important;text-decoration:none;font-weight:700;padding:11px;border-radius:9px;margin-top:8px}
.mz-btn.alt{background:#21262d;border:1px solid #30363d}.mz-gear{display:grid;gap:10px;grid-template-columns:repeat(auto-fill,minmax(160px,1fr))}
.mz-g{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:12px;display:flex;flex-direction:column}.mz-g .i{font-size:26px}.mz-g b{margin:4px 0}.mz-g p{font-size:12px;color:#8b949e;flex:1;margin:4px 0 8px}
.mz-g a{background:#f0b429;color:#000!important;text-decoration:none;font-weight:700;font-size:13px;text-align:center;padding:8px;border-radius:8px}
.mz-ftc{font-size:11px;color:#8b949e;margin-top:8px}.mz-store{display:flex;gap:10px;align-items:center;justify-content:space-between;background:linear-gradient(90deg,#e5484d22,#161b22);border:1px solid #e5484d55;border-radius:12px;padding:12px;margin:10px 0}
.mz-store a{white-space:nowrap}.mz-lock{border:1px dashed #f0b429;border-radius:12px;padding:14px;text-align:center;color:#f0b429}`;
const st=document.createElement('style');st.textContent=css;document.head.appendChild(st);
C.isMember=()=>localStorage.getItem(C.MEMBER_KEY)==='1';
C.renderPlans=(el,o)=>{const L=C.MEMBERSHIP_LINKS;el.innerHTML=`<div class="mz-plans">
<div class="mz-plan"><h3>Free</h3><div class="mz-price">$0</div><ul>${o.free.map(x=>`<li>${x}</li>`).join('')}</ul><span class="mz-btn alt">${C.isMember()?'Included':'Current plan'}</span></div>
<div class="mz-plan pro"><span class="mz-tag">BEST VALUE</span><h3>Member</h3><div class="mz-price">${o.mo}<small>/month</small></div><div class="muted note tiny">or ${o.yr}/year (${o.save})</div>
<ul>${o.pro.map(x=>`<li>${x}</li>`).join('')}</ul><a class="mz-btn" href="${L.monthly}" target="_blank" rel="noopener">Join monthly · ${o.mo}</a><a class="mz-btn alt" href="${L.yearly}" target="_blank" rel="noopener">Join yearly · ${o.yr}</a></div></div>
<p class="mz-ftc">Secure checkout by Payhip. Cancel anytime. ${C.isMember()?'<b style="color:#3fb950">Member features unlocked on this device.</b>':''}</p>`;};
C.renderGear=(el,compact)=>{el.innerHTML=`<div class="mz-gear">${Object.values(C.AFFILIATE).map(g=>`<div class="mz-g"><span class="i">${g.icon}</span><b>${g.name}</b>${compact?'':`<p>${g.note}</p>`}<a href="${g.url}" target="_blank" rel="sponsored noopener">View on Amazon</a></div>`).join('')}</div><p class="mz-ftc">${C.FTC_DISCLOSURE} Prices and availability are shown on Amazon.</p>`;};
C.renderStore=(el,txt)=>{el.innerHTML=`<div class="mz-store"><div><b>Digital Cultra Store</b><div class="tiny note muted">${txt}</div></div><a class="mz-btn" href="${C.STORE_URL}" target="_blank" rel="noopener">Shop now</a></div>`;};
})();
