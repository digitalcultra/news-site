# Brevo email: contact sync, daily local digest, Insider breaking alerts. Stdlib only.
# All network calls are wrapped so the site never crashes. The API key is never logged.
import os,json,time,re,html,threading,datetime,urllib.request,urllib.parse,urllib.error,hashlib,hmac
from zoneinfo import ZoneInfo
import seo
from seo_config import SITE_URL,SITE_NAME
API='https://api.brevo.com/v3'
TZ=ZoneInfo('America/Chicago')
PAYHIP='https://payhip.com/b/rx0Sb'
DAILY_LIST='Daily Local'; INSIDER_LIST='Insider'
DIGEST_HOUR=7; DIGEST_MAX=250; ALERT_MAX_PER_DAY=3; ALERT_EVERY=900
STATES={'AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY','DC'}
_lists={}; _lock=threading.Lock(); _state={'last_alert':0,'digest_day':None,'attrs':False}
STORY_CACHE={}  # sid -> story, so emailed local stories have a working /story/ page
def key(): return os.environ.get('BREVO_API_KEY','').strip()
def enabled(): return bool(key())
def log(*a): print('[mailer]',*a,flush=True)
def api(method,path,body=None):
    req=urllib.request.Request(API+path,method=method,data=json.dumps(body).encode() if body is not None else None,
        headers={'api-key':key(),'accept':'application/json','content-type':'application/json'})
    try:
        with urllib.request.urlopen(req,timeout=20) as r:
            t=r.read(); return r.status,(json.loads(t) if t else {})
    except urllib.error.HTTPError as e:
        try: d=json.loads(e.read() or b'{}')
        except Exception: d={}
        return e.code,d
def parse_loc(city,state=''):
    city=(city or '').strip(); st=(state or '').strip().upper()[:2]
    m=re.match(r'^(.*?)[,\s]+([A-Za-z]{2})$',city)
    if not st and m and m.group(2).upper() in STATES: city,st=m.group(1).strip(),m.group(2).upper()
    return city.title(),(st if st in STATES else '')
def list_id(name):
    with _lock:
        if name in _lists: return _lists[name]
        c,d=api('GET','/contacts/lists?limit=50&offset=0')
        for l in (d.get('lists') or []):
            if l.get('name')==name: _lists[name]=l['id']; return l['id']
        c,f=api('GET','/contacts/folders?limit=10&offset=0')
        fid=((f.get('folders') or [{}])[0]).get('id')
        if not fid:
            c,f=api('POST','/contacts/folders',{'name':SITE_NAME}); fid=f.get('id')
        c,d=api('POST','/contacts/lists',{'name':name,'folderId':fid})
        if d.get('id'): _lists[name]=d['id']; return d['id']
        log('list create failed',c); return None
def ensure_attrs():
    if _state['attrs']: return
    for a in ('CITY','STATE','DC_LAST','DC_ALERTS'): api('POST','/contacts/attributes/normal/'+a,{'type':'text'})  # 400 if exists: fine
    _state['attrs']=True
def upsert_contact(email,city,state=''):
    if not enabled(): return False
    try:
        ensure_attrs(); ci,st=parse_loc(city,state); lid=list_id(DAILY_LIST)
        c,d=api('POST','/contacts',{'email':email,'updateEnabled':True,'attributes':{'CITY':ci,'STATE':st},'listIds':[lid] if lid else []})
        if c not in (200,201,204): log('contact upsert status',c); return False
        return True
    except Exception as e: log('upsert error',type(e).__name__); return False
def list_contacts(name,cap=1000):
    lid=list_id(name); out=[]
    if not lid: return out
    off=0
    while len(out)<cap:
        c,d=api('GET','/contacts/lists/%d/contacts?limit=500&offset=%d'%(lid,off))
        cs=d.get('contacts') or []
        out+=[x for x in cs if not x.get('emailBlacklisted')]
        if len(cs)<500: break
        off+=500
    return out[:cap]
def set_attr(email,attrs): api('PUT','/contacts/'+urllib.parse.quote(email),{'attributes':attrs})
# unsubscribe tokens: HMAC of email with the API key (never exposed); tokens unchanged across restarts
def utoken(email): return hmac.new(key().encode(),email.lower().encode(),hashlib.sha256).hexdigest()[:24]
def unsub_url(email): return f"{SITE_URL}/api/unsubscribe?e={urllib.parse.quote(email)}&t={utoken(email)}"
def unsubscribe(email,token):
    if not enabled() or not hmac.compare_digest(utoken(email),token or ''): return False
    c,d=api('PUT','/contacts/'+urllib.parse.quote(email),{'emailBlacklisted':True})
    return c in (200,204)
# ---------- rendering (pure, unit-tested) ----------
E=lambda s:html.escape(str(s),quote=True)
def story_url(s): return f"{SITE_URL}/story/{seo.sid(s)}"
def _wrap(title,inner,unsub):
    return f'''<!doctype html><html><body style="margin:0;background:#f4f4f6;font-family:Arial,Helvetica,sans-serif;color:#111">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:20px">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;background:#fff;border-radius:10px">
<tr><td style="padding:18px 22px;background:#111;color:#fff;border-radius:10px 10px 0 0;font-size:20px;font-weight:bold">{E(SITE_NAME)}</td></tr>
<tr><td style="padding:22px"><h1 style="font-size:20px;margin:0 0 14px">{E(title)}</h1>{inner}</td></tr>
<tr><td style="padding:16px 22px;font-size:12px;color:#666;border-top:1px solid #eee">
You get this because you signed up at {E(SITE_NAME)}. <a href="{E(unsub)}" style="color:#666">Unsubscribe</a> &middot; <a href="{E(SITE_URL)}" style="color:#666">{E(SITE_URL.split('//')[-1])}</a><br>
&copy; {E(SITE_NAME)}{('<br>'+E(os.environ.get('ORG_ADDRESS',''))) if os.environ.get('ORG_ADDRESS') else ''}</td></tr></table></td></tr></table></body></html>'''
def _row(s):
    why='; '.join(s.get('why') or [])
    return (f'<div style="margin:0 0 16px"><a href="{E(story_url(s))}" style="font-size:16px;font-weight:bold;color:#0b57d0;text-decoration:none">{E(s["title"])}</a>'
            f'<div style="font-size:13px;color:#555;margin-top:4px">{E(s["n"])} outlet(s) &middot; {E(s["status"])}{(" &middot; "+E(why)) if why else ""}</div></div>')
def render_digest(stories,city,state,unsub):
    where=', '.join(x for x in (city,state) if x) or 'your area'
    rows=''.join(_row(s) for s in stories) or '<p>No new buried stories today. Check the site for the latest.</p>'
    inner=(f'<p style="margin:0 0 16px;color:#333">Stories near {E(where)} and nationwide that few outlets are covering.</p>{rows}'
           f'<p style="margin:18px 0 0;padding:12px;background:#fff6e0;border-radius:8px;font-size:14px">Insider members get real-time alerts for your area. '
           f'<a href="{E(PAYHIP)}" style="color:#0b57d0;font-weight:bold">Join Insider</a></p>')
    return _wrap('Top buried stories near you',inner,unsub)
def render_alert(s,city,state,unsub):
    where=', '.join(x for x in (city,state) if x)
    inner=(f'<p style="margin:0 0 12px;color:#b00020;font-weight:bold">Breaking near {E(where)}</p>{_row(s)}'
           f'<p><a href="{E(story_url(s))}" style="display:inline-block;background:#111;color:#fff;padding:10px 16px;border-radius:6px;text-decoration:none">Read the story</a></p>')
    return _wrap('Insider alert: '+s['title'][:90],inner,unsub)
def send(to,subject,htmlbody):
    c,d=api('POST','/smtp/email',{'sender':{'email':os.environ.get('SENDER_EMAIL',''),'name':os.environ.get('SENDER_NAME',SITE_NAME)},
        'to':[{'email':to}],'subject':subject,'htmlContent':htmlbody,
        'headers':{'List-Unsubscribe':'<%s>'%unsub_url(to)}})
    return c in (200,201,202)
# ---------- jobs ----------
_news=None  # set by server: fn(state,city)->dict
_feed_cache={}
def local_stories(state,city):
    k=(state,city)
    if k in _feed_cache and time.time()-_feed_cache[k][0]<900: return _feed_cache[k][1]
    st=_news(state or 'IL',city)['stories']; _feed_cache[k]=(time.time(),st)
    for s in st: STORY_CACHE[seo.sid(s)]=s
    if len(STORY_CACHE)>5000:
        for k2 in list(STORY_CACHE)[:2000]: STORY_CACHE.pop(k2,None)
    return st
def is_local(s,state,city):
    for sc in s.get('scopes',[]):
        if sc.startswith('local:%s:'%state) and (not city or sc.endswith(':*') or sc.lower().endswith(':'+city.lower())): return True
    return False
def pick_digest(stories,state,city,n=6):
    fresh=[s for s in stories if time.time()-s['last']<36*3600]
    loc=sorted([s for s in fresh if is_local(s,state,city)],key=lambda s:(-s['score'],-s['last']))
    rest=sorted([s for s in fresh if not is_local(s,state,city) and s['score']>0],key=lambda s:(-s['score'],-s['last']))
    return (loc[:3]+rest)[:n] if state else rest[:n]
def run_digest(now=None):
    now=now or datetime.datetime.now(TZ); day=now.strftime('%Y-%m-%d')
    if now.hour<DIGEST_HOUR or _state['digest_day']==day: return 0
    _state['digest_day']=day; sent=0
    for c in list_contacts(DAILY_LIST):
        if sent>=DIGEST_MAX: break
        a=c.get('attributes') or {}; em=c.get('email')
        if not em or a.get('DC_LAST')==day: continue  # survives restarts: per-contact marker in Brevo
        try:
            st,ci=(a.get('STATE') or ''),(a.get('CITY') or '')
            picks=pick_digest(local_stories(st,ci),st,ci)
            if not picks: continue
            if send(em,'Top buried stories near you',render_digest(picks,ci,st,unsub_url(em))):
                sent+=1; set_attr(em,{'DC_LAST':day})
        except Exception as e: log('digest error',type(e).__name__)
    log('digest sent',sent); return sent
def alert_worthy(s): return s.get('score',0)>=2 and time.time()-s['first']<6*3600
def run_alerts(now=None):
    now=now or datetime.datetime.now(TZ); day=now.strftime('%Y-%m-%d')
    if time.time()-_state['last_alert']<ALERT_EVERY-30: return 0
    _state['last_alert']=time.time(); sent=0
    for c in list_contacts(INSIDER_LIST,cap=300):
        a=c.get('attributes') or {}; em=c.get('email'); st=a.get('STATE') or ''; ci=a.get('CITY') or ''
        if not em or not st: continue
        try:
            rec=(a.get('DC_ALERTS') or '').split('|')  # "YYYY-MM-DD|count|sid,sid,..."
            cnt=int(rec[1]) if len(rec)>2 and rec[0]==day else 0
            seen=set(rec[2].split(',')) if len(rec)>2 else set()
            if cnt>=ALERT_MAX_PER_DAY: continue
            for s in local_stories(st,ci):
                if cnt>=ALERT_MAX_PER_DAY: break
                sid=seo.sid(s)
                if sid in seen or not alert_worthy(s) or not is_local(s,st,ci): continue
                if send(em,'Alert: '+s['title'][:90],render_alert(s,ci,st,unsub_url(em))):
                    cnt+=1; sent+=1; seen.add(sid)
                    set_attr(em,{'DC_ALERTS':'%s|%d|%s'%(day,cnt,','.join(list(seen)[-60:]))})
        except Exception as e: log('alert error',type(e).__name__)
    if sent: log('alerts sent',sent)
    return sent
_tick_lock=threading.Lock()
def tick():
    """Run whatever is due. Safe to call often (cron ping or background loop)."""
    if not enabled(): return {'ok':True,'enabled':False}
    if not _tick_lock.acquire(blocking=False): return {'ok':True,'busy':True}
    r={'ok':True,'enabled':True}
    try:
        try: r['digest']=run_digest()
        except Exception as e: log('digest job',type(e).__name__)
        try: r['alerts']=run_alerts()
        except Exception as e: log('alert job',type(e).__name__)
    finally: _tick_lock.release()
    return r
def start(news_fn):
    global _news; _news=news_fn
    if not enabled(): log('BREVO_API_KEY not set; email jobs off'); return
    def loop():
        time.sleep(60)
        while True:
            try: tick()
            except Exception: pass
            time.sleep(300)
    threading.Thread(target=loop,daemon=True).start(); log('email jobs on')
