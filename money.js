// News-site monetization wiring. Member gating is a CLIENT-SIDE FLAG ONLY (see README).
(function(){
const $=s=>document.querySelector(s), member=isMember();
renderPlans($('#planbox'),{mo:'$4',yr:'$36',save:'save 25%',
 free:['Headlines from every side','Local, national & world feeds','Top 3 underreported stories'],
 pro:['Full Underreported section','Daily “what they buried” email digest','Location alerts for your city/state','No ads']});
renderGear($('#gear'),true);
renderStore($('#store1'),'Family Emergency Kits for all 50 states, guides & more.');
renderStore($('#store2'),'Kits, guides & shirts.');renderStore($('#store3'),'Family Emergency Kits, FACT Book, Survival Guide & shirts.');
function route(){const m=location.hash==='#membership';$('#plans').classList.toggle('hidden',!m);
 const prof=localStorage.getItem('dcn_profile');$('#app').classList.toggle('hidden',m||!prof);$('#onb').classList.toggle('hidden',m||!!prof);if(m)scrollTo(0,0);}
addEventListener('hashchange',route);if(location.hash==='#membership')route();
// gate underreported: free users see first 3
function gate(){if(member)return;const u=$('#under');if(!u)return;[...u.children].forEach((c,i)=>c.style.display=i<3?'':'none');$('#ulock').classList.toggle('hidden',u.children.length<=3);}
new MutationObserver(gate).observe($('#under'),{childList:true});gate();
$('#nl').onsubmit=e=>{e.preventDefault();const em=$('#nlem').value.trim(),k='dcn_newsletter',l=JSON.parse(localStorage.getItem(k)||'[]');
 if(!l.includes(em))l.push(em);localStorage.setItem(k,JSON.stringify(l));$('#nlmsg').textContent='Subscribed! (saved on this device until the email service is connected)';$('#nlem').value='';};
})();
