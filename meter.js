/* Digital Cultra News: metered join prompt. Client-side only; page HTML stays fully crawlable. */
(function(){
  var FREE=5,K='dcn_story_opens',D='dcn_join_dismissed',P='https://payhip.com/b/rx0Sb';
  var M=window.MEMBERSHIP_LINKS||{monthly:'https://payhip.com/order?link=rx0Sb&pricing_plan=63Wd1yX9zw',yearly:'https://payhip.com/order?link=rx0Sb&pricing_plan=ZwzKa405G9'};
  function get(k){try{return JSON.parse(localStorage.getItem(k))}catch(e){return null}}
  function set(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}
  if(/(^|; )dcn_owner=1/.test(document.cookie)){set('dcn_member','1');var ob=document.createElement('div');ob.style.cssText='position:fixed;left:12px;bottom:12px;z-index:9998;background:#3b2a00;color:#ffd166;border:1px solid #ffd166;border-radius:20px;padding:6px 12px;font:13px system-ui';ob.innerHTML='Owner preview \u00b7 member view \u00b7 <a style="color:#fff" href="/preview?exit=1">Exit</a>';document.body.appendChild(ob);return}
  var WEEK=7*864e5,now=Date.now(),isStory=/^\/story\//.test(location.pathname);
  var st=get('dcn_meter');if(!st||!st.t||now-st.t>=WEEK||!Array.isArray(st.s))st={t:0,s:[]};
  try{localStorage.removeItem(D);localStorage.removeItem(K)}catch(e){}
  function allow(key){if(st.s.indexOf(key)>=0)return true;if(st.s.length>=FREE)return false;if(!st.t)st.t=Date.now();st.s.push(key);set('dcn_meter',st);used=st.s.length;left=Math.max(0,FREE-used);upd();return true}
  var used=st.s.length,left=Math.max(0,FREE-used);
  var css=document.createElement('style');css.textContent=
  '.dcm-bar{position:fixed;left:12px;bottom:12px;z-index:9998;background:#111a2b;color:#dfe6f3;border:1px solid #2a3a5a;border-radius:20px;padding:6px 12px;font:13px system-ui}.dcm-bar a{color:#7fb4ff}'+
  '.dcm-ov{position:fixed;inset:0;z-index:2147483647;overflow:auto;background:rgba(5,10,20,.96);display:flex;align-items:center;justify-content:center;padding:16px}'+
  '.dcm-box{max-width:440px;width:100%;background:#0f1726;color:#e8eefa;border:1px solid #2a3a5a;border-radius:14px;padding:20px;font:15px/1.45 system-ui;position:relative}'+
  '.dcm-box h2{margin:0 0 6px;font-size:20px}.dcm-box ul{padding-left:18px;margin:8px 0}.dcm-x{position:absolute;top:8px;right:10px;background:none;border:0;color:#aab;font-size:22px;cursor:pointer}'+
  '.dcm-b{display:block;text-align:center;margin:8px 0;padding:10px;border-radius:9px;background:#3b82f6;color:#fff;text-decoration:none;font-weight:600}.dcm-b.alt{background:#1e293b;border:1px solid #3b82f6}'+
  '.dcm-f{border-top:1px solid #2a3a5a;margin-top:12px;padding-top:10px}.dcm-f input{width:100%;box-sizing:border-box;margin:4px 0;padding:8px;border-radius:7px;border:1px solid #334;background:#0b1220;color:#fff}.dcm-f button{width:100%;padding:8px;border-radius:7px;border:0;background:#22c55e;color:#04210f;font-weight:600;cursor:pointer}.dcm-s{font-size:12px;opacity:.7}';
  document.head.appendChild(css);
  var bar=document.createElement('div');bar.className='dcm-bar';
  function upd(){bar.innerHTML=left>0?(left+' of '+FREE+' free stories left · <a href="'+P+'" target="_blank" rel="noopener">Insider</a>'):'Free stories used · <a href="#" id="dcm-open">Join Insider</a>';var a=document.getElementById('dcm-open');if(a)a.onclick=function(e){e.preventDefault();show()}}
  upd();document.body.appendChild(bar);
  function show(){
    if(document.querySelector('.dcm-ov'))return;
    var o=document.createElement('div');o.className='dcm-ov';o.setAttribute('role','dialog');
    o.innerHTML='<div class="dcm-box"><h2>Join Digital Cultra News Insider</h2>'+
    '<p>You\u2019ve read your '+FREE+' free stories. this week. Join Insider to keep reading \u2014 your free stories reset 7 days after your first one.</p>'+
    '<ul><li>Local breaking-news email alerts</li><li>Full underreported section</li><li>Ad-free site</li><li>Early access to story videos</li></ul>'+
    '<a class="dcm-b" href="'+M.monthly+'" target="_blank" rel="noopener">$4 / month</a><a class="dcm-b alt" href="'+M.yearly+'" target="_blank" rel="noopener">$36 / year</a>'+
    '<p class="dcm-s">Already a member? <a style="color:#7fb4ff" href="'+(window.MEMBERSHIP_PAGE||P)+'" target="_blank" rel="noopener">Open your Payhip membership</a> or use your owner/member link.</p><form class="dcm-f"><b>Get a free daily local email instead</b><input type="email" name="email" placeholder="Email" required><input name="city" placeholder="City" required><button>Sign me up</button><div class="dcm-s">One email a day. Unsubscribe anytime.</div></form></div>';
    document.body.appendChild(o);
    if(!isStory){var x=document.createElement('button');x.className='dcm-x';x.textContent='\u00d7';x.onclick=function(){o.remove()};o.firstChild.appendChild(x)}
    o.querySelector('form').onsubmit=function(e){e.preventDefault();var f=e.target,s=f.querySelector('.dcm-s');
      fetch('/api/signup',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:f.email.value,city:f.city.value})})
      .then(function(r){return r.json()}).then(function(j){s.textContent=j.ok?'You\u2019re on the list! Thanks.':'Please check your email address.';})
      .catch(function(){s.textContent='Could not save right now, try again later.'})};
  }
  function lock(){var a=document.querySelector('article');if(a){var keep=a.querySelector('h1');Array.prototype.slice.call(a.children).forEach(function(c){if(c!==keep)c.remove()});var p=document.createElement('p');p.textContent='Insider members only. Join to read this story.';a.appendChild(p)}
    document.documentElement.style.overflow='hidden';show();
    new MutationObserver(function(){if(!document.querySelector('.dcm-ov'))show()}).observe(document.body,{childList:true})}
  window.DCNMeter={allow:function(k){if(allow(k))return true;show();return false}};
  if(isStory&&!allow(location.pathname))lock();
})();
