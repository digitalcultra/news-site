# Digital Cultra News dev server: static files + /api/news (fetch, parse, cluster). Headlines/links only.
import http.server, urllib.request, urllib.parse, re, time, json, html, concurrent.futures as cf, email.utils, xml.etree.ElementTree as ET
from sources import SOURCES, fallback, STATES
CACHE={}; STOP=set("a an the of to in on for and or but is are was were be by with at from as it its this that after over into new says say said amid about how why what who will has have had not no up out more than us vs his her their they he she we you your our live video watch".split())
def fetch(src):
    u=src[3]; c=CACHE.get(u)
    if c and time.time()-c[0]<600: return c[1]
    items=[]
    try:
        raw=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0 DigitalCultraNews'}),timeout=12).read()
        root=ET.fromstring(raw)
        for el in root.iter():
            tag=el.tag.split('}')[-1]
            if tag not in('item','entry'):continue
            g=lambda n:next((x for x in el if x.tag.split('}')[-1]==n),None)
            fo=lambda *ns:next((x for x in map(g,ns) if x is not None),None)
            t=g('title'); l=g('link'); d=fo('pubDate','published','updated','date')
            title=html.unescape(re.sub('<[^>]+>','',(t.text or '') if t is not None else '')).strip()
            link=(l.get('href') or l.text or '').strip() if l is not None else ''
            ts=0
            if d is not None and d.text:
                try: ts=email.utils.parsedate_to_datetime(d.text).timestamp()
                except Exception:
                    try: import datetime; ts=datetime.datetime.fromisoformat(d.text.strip().replace('Z','+00:00')).timestamp()
                    except Exception: pass
            orig=None
            if 'news.google.com' in u:
                m=re.search(r'\s+-\s+([^-]+)$',title); orig=m.group(1).strip() if m else None; title=re.sub(r'\s+-\s+[^-]+$','',title)
            if title and link: items.append({'t':title,'u':link,'ts':ts or time.time(),'s':src[0],'lean':src[1],'scope':src[2],**({'orig':orig} if orig else {})})
            if len(items)>=40:break
    except Exception as e: items=None
    CACHE[u]=(time.time(),items); return items
def toks(t): return {w for w in re.findall(r"[a-z0-9']+",t.lower()) if len(w)>2 and w not in STOP}
def cluster(items):
    cl=[]
    for it in sorted(items,key=lambda x:-x['ts']):
        k=toks(it['t']); best=None;bs=0
        for c in cl:
            inter=len(k&c['k']); s=inter/max(1,min(len(k),len(c['k'])))
            if inter>=3 and s>bs and s>=.45: best,bs=c,s
        if best: best['items'].append(it); best['k']|=k
        else: cl.append({'k':set(k),'items':[it]})
    out=[]; now=time.time()
    for c in cl:
        its=c['items']; srcs={i['s'] for i in its}; leans={}
        for i in its: leans.setdefault(i['lean'],set()).add(i['s'])
        media=[l for l in leans if l!='primary']; n=len(srcs)
        if 'primary' in leans: status='Primary document'
        elif n>=2: status='Multiple independent sources'
        else: status='Single source - unverified'
        sides={'left','right'}&set(media); first=min(i['ts'] for i in its); last=max(i['ts'] for i in its)
        score=0; why=[]
        if 'primary' in leans and len([s for s in srcs])-len(leans['primary'])<=1: score+=3; why.append('Primary document, little/no media pickup')
        if 2<=n<=3: score+=1; why.append('Covered by only %d outlets'%n)
        if len(sides)==1 and n>=2: score+=2; why.append('Covered by only one side (%s)'%next(iter(sides)))
        if n>=2 and now-last>36*3600 and last-first<12*3600: score+=1; why.append('Coverage stopped quickly')
        scopes=sorted({i['scope'] for i in its})
        out.append({'title':its[0]['t'],'items':sorted(its,key=lambda x:x['ts']),'n':n,'leans':{k:len(v) for k,v in leans.items()},
          'status':status,'score':score,'why':why,'scopes':scopes,'first':first,'last':last})
    return out
def news(state,city):
    srcs=[s for s in SOURCES if not s[2].startswith('local:')]
    loc=[s for s in SOURCES if s[2].startswith('local:%s:'%state) and (s[2].endswith(':*') or s[2].endswith(':'+city) or not city)]
    if not any(s[2].endswith(':'+city) for s in loc) and state in STATES: loc.append(fallback(state,city))
    srcs+=loc; ok=0; items=[]; failed=[]
    with cf.ThreadPoolExecutor(24) as ex:
        for s,r in zip(srcs,ex.map(fetch,srcs)):
            if r: ok+=1; items+=r
            else: failed.append(s[0])
    seen=set(); items=[i for i in items if not ((i['s'],i['t']) in seen or seen.add((i['s'],i['t'])))]
    cutoff=time.time()-5*86400; items=[i for i in items if i['ts']>cutoff]
    return {'feeds_total':len(srcs),'feeds_ok':ok,'failed':failed,'sources':[{'name':s[0],'lean':s[1],'scope':s[2]} for s in srcs],'stories':cluster(items),'generated':time.time()}
import seo, sections
SEOC=[0,None]
def seo_stories():
    if time.time()-SEOC[0]>600: SEOC[1]=sorted(news('IL','Chicago')['stories'],key=lambda s:(-s['score'],-s['last'])); SEOC[0]=time.time()
    return SEOC[1]
SECT={'local':'Local news','national':'National news','world':'World news'}
import threading,os
SIGLOCK=threading.Lock(); SIGFILE=os.environ.get('SIGNUP_FILE','signups.json')
class H(http.server.SimpleHTTPRequestHandler):
    def out(self,body,ct,code=200):
        b=body.encode(); self.send_response(code); self.send_header('Content-Type',ct+'; charset=utf-8'); self.send_header('Cache-Control','public, max-age=300'); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        p=urllib.parse.urlparse(self.path); pa=p.path.rstrip('/') or '/'
        if pa=='/robots.txt': return self.out(seo.robots(),'text/plain')
        if pa=='/sitemap.xml': return self.out(seo.sitemap(seo_stories()),'application/xml')
        if pa=='/news-sitemap.xml': return self.out(seo.news_sitemap(seo_stories()),'application/xml')
        if pa=='/feed.xml': return self.out(seo.rss(seo_stories()),'application/rss+xml')
        if pa.strip('/') in seo.STATIC: return self.out(seo.static(pa.strip('/')),'text/html')
        if pa.startswith('/section/') and pa[9:] in SECT:
            k=pa[9:]; return self.out(seo.listing(SECT[k]+' | '+seo.SITE_NAME,SECT[k]+' from every side, with coverage labels and links to the original outlets.',pa,[s for s in seo_stories() if seo.section(s)==k]),'text/html')
        if pa.startswith('/story/'):
            m=next((s for s in seo_stories() if seo.sid(s)==pa[7:]),None)
            if not m: m=mailer.STORY_CACHE.get(pa[7:])
            return self.out(seo.story_page(m),'text/html') if m else self.out(seo.page('Not found','Story expired.','/404','<h1>Story no longer in feed</h1>'),'text/html',404)
        if pa.strip('/') in sections.SECTIONS or (pa.startswith('/section/') and pa[9:] in sections.SECTIONS):
            k=pa.strip('/').split('/')[-1]; return self.out(sections.render(k,sections.items(k,fetch),seo),'text/html')
        if pa=='/api/section':
            k=urllib.parse.parse_qs(p.query).get('k',[''])[0]
            if k not in sections.SECTIONS: return self.out('{"ok":false}','application/json',404)
            return self.out(json.dumps(sections.items(k,fetch)),'application/json')
        if pa=='/preview': return self.preview(p)
        if pa=='/api/tick': return self.tick(p)
        if pa=='/api/unsubscribe':
            q=urllib.parse.parse_qs(p.query)
            try: ok=mailer.unsubscribe(q.get('e',[''])[0][:120],q.get('t',[''])[0][:64])
            except Exception: ok=False
            return self.out(seo.page('Unsubscribe','Email preferences','/api/unsubscribe','<h1>%s</h1><p><a href="/">Back to the news</a></p>'%('You are unsubscribed.' if ok else 'That unsubscribe link is invalid or expired.')),'text/html')
        if p.path!='/api/news': return super().do_GET()
        q=urllib.parse.parse_qs(p.query); st=q.get('state',['IL'])[0][:2].upper(); ci=re.sub('[^A-Za-z .-]','',q.get('city',[''])[0])[:40]
        b=json.dumps(news(st,ci)).encode()
        self.send_response(200); self.send_header('Content-Type','application/json'); self.end_headers(); self.wfile.write(b)
    def preview(self,p):
        import hashlib,hmac,time
        q=urllib.parse.parse_qs(p.query); want=os.environ.get('OWNER_CODE_SHA256','92cd08c9d375ac14f3d761a264c0d58b7da34e168074b2cad5026ebad8004b1c')
        ip=(self.headers.get('X-Forwarded-For') or self.client_address[0]).split(',')[0].strip(); now=time.time()
        F=globals().setdefault('_PVFAIL',{})
        F[ip]=[t for t in F.get(ip,[]) if now-t<900]
        code=(q.get('k') or q.get('key') or [''])[0].strip().lower()
        if 'exit' in q:
            ck='dcn_owner=; Path=/; Max-Age=0; SameSite=Lax; Secure'; js="localStorage.removeItem('dcn_member');location.replace('/')"
        elif len(F[ip])<10 and code and hmac.compare_digest(hashlib.sha256(code.encode()).hexdigest(),want):
            ck='dcn_owner=1; Path=/; Max-Age=31536000; SameSite=Lax; Secure'; js="localStorage.setItem('dcn_member','1');location.replace('/')"
        else:
            ck=None; js=None
            if code: F[ip].append(now)
        b=('<!doctype html><meta name="robots" content="noindex,nofollow"><title>Preview</title><script>%s</script>'%js if js else '<!doctype html><meta name="robots" content="noindex,nofollow"><h1>Not found</h1>').encode()
        self.send_response(200 if js else 404); self.send_header('Content-Type','text/html; charset=utf-8'); self.send_header('Cache-Control','no-store'); self.send_header('X-Robots-Tag','noindex, nofollow'); self.send_header('Referrer-Policy','no-referrer')
        if ck: self.send_header('Set-Cookie',ck)
        self.end_headers(); self.wfile.write(b)
    def tick(self,p):
        try:
            tok=os.environ.get('TICK_TOKEN','')
            given=urllib.parse.parse_qs(p.query).get('token',[''])[0] or self.headers.get('X-Tick-Token','')
            if tok and given!=tok: return self.out('{"ok":false}','application/json',403)
            return self.out(json.dumps(mailer.tick()),'application/json')
        except Exception: return self.out('{"ok":false}','application/json',500)
    def do_POST(self):
        if urllib.parse.urlparse(self.path).path=='/api/tick': return self.tick(urllib.parse.urlparse(self.path))
        if urllib.parse.urlparse(self.path).path!='/api/signup': return self.out('{"ok":false}','application/json',404)
        try:
            n=min(int(self.headers.get('Content-Length',0)),2000); d=json.loads(self.rfile.read(n) or b'{}')
            em=str(d.get('email','')).strip()[:120]; ci=re.sub('[^A-Za-z .,-]','',str(d.get('city','')))[:60]
            if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$',em): return self.out('{"ok":false,"error":"email"}','application/json',400)
            with SIGLOCK:
                try: L=json.load(open(SIGFILE))
                except Exception: L=[]
                if not any(x['email'].lower()==em.lower() for x in L): L.append({'email':em,'city':ci,'t':int(time.time())})
                try: json.dump(L,open(SIGFILE,'w'))
                except Exception: pass
            try: mailer.upsert_contact(em,ci,str(d.get('state',''))[:2])
            except Exception: pass
            return self.out('{"ok":true}','application/json')
        except Exception: return self.out('{"ok":false}','application/json',400)
    def log_message(self,*a):pass
import os,mailer
mailer.start(news)
http.server.ThreadingHTTPServer(('0.0.0.0',int(os.environ.get('PORT','8795'))),H).serve_forever()
