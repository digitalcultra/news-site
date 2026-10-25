# Extra sections: Buried & Blind (celebrity), Sports, Crime & Court. Real public RSS only; headlines link to the original outlet.
# LEGAL: blind items are republished only as the source titled them, labeled "Blind item via <source>". We never guess or add who an item is about.
import re, time, html
GN='https://news.google.com/rss/search?hl=en-US&gl=US&ceid=US:en&q='
LEGAL=re.compile(r"\b(su(e|es|ed|ing)|lawsuit|court|judge|jury|trial|charged|charges|indict\w*|arrest\w*|plea|pleads?|sentenc\w*|convict\w*|alleg\w*|accus\w*|investigat\w*|probe|police|felony|misdemeanor|settle\w*|custody|restraining|DUI|fraud|assault|scandal|banned|suspend\w*|doping|gambling|subpoena|prosecut\w*|attorney|lawyer|legal|bail|prison|jail|verdict|appeal|testif\w*|deposition)\b",re.I)
BLIND=re.compile(r"blind item|blind gossip|\bblind\b.*\b(rumou?r|gossip)\b",re.I)
# (name, lean, scope, url, filter)  filter: None=all items, 'legal'=legal/scandal keywords only, 'blind'=blind items only
SECTIONS={
 'buried-blind':{'title':'Buried & Blind','desc':'Celebrity blind items republished exactly as their original outlets published them, plus celebrity court and legal stories that get little coverage.',
  'src':[
   ('Crazy Days and Nights','gossip','blind','https://www.crazydaysandnights.net/feeds/posts/default?alt=rss','blind'),
   ('Blind Gossip','gossip','blind','https://blindgossip.com/feed/','blind'),
   ('Google News: "blind item"','gossip','blind',GN+'%22blind+item%22+when:14d','blind'),
   ('Page Six','gossip','celebrity','https://pagesix.com/feed/','blindlegal'),
   ('TMZ','gossip','celebrity','https://www.tmz.com/rss.xml','blindlegal'),
   ('Perez Hilton','gossip','celebrity','https://perezhilton.com/feed/','blindlegal'),
   ('Just Jared','gossip','celebrity','https://www.justjared.com/feed/','blindlegal'),
   ('Deadline','trade','celebrity','https://deadline.com/feed/','legal'),
   ('Variety','trade','celebrity','https://variety.com/feed/','legal'),
   ('Google News: celebrity court cases','aggregator','celebrity',GN+'celebrity+(lawsuit+OR+court+OR+arrested+OR+charged+OR+sued)+when:7d','legal'),
  ]},
 'sports':{'title':'Sports: Scandals, Courts & Buried Stories','desc':'Sports scandals, court and legal cases, and underreported sports stories from sports outlets across the field.',
  'src':[
   ('ESPN','center','sports','https://www.espn.com/espn/rss/news','legal'),
   ('CBS Sports','center','sports','https://www.cbssports.com/rss/headlines/','legal'),
   ('Yahoo Sports','center','sports','https://sports.yahoo.com/rss/','legal'),
   ('BBC Sport','international','sports','https://feeds.bbci.co.uk/sport/rss.xml','legal'),
   ('Deadspin','independent','sports','https://www.deadspin.com/rss','legal'),
   ('Defector','independent','sports','https://defector.com/feed',None),
   ('Sportico (sports business & law)','trade','sports','https://www.sportico.com/feed/','legal'),
   ('Google News: athlete legal cases','aggregator','sports',GN+'athlete+(lawsuit+OR+indicted+OR+arrested+OR+charged+OR+scandal)+when:7d','legal'),
  ]},
 'crime-court':{'title':'Crime & Court','desc':'Crime and court stories from across the nation and world, including cases the major outlets skip, from court-focused outlets and primary records.',
  'src':[
   ('Courthouse News','independent','national','https://www.courthousenews.com/feed/',None),
   ('Law&Crime','independent','national','https://lawandcrime.com/feed/',None),
   ('The Marshall Project','independent','national','https://www.themarshallproject.org/rss/recent.rss',None),
   ('The Appeal','independent','national','https://theappeal.org/feed/',None),
   ('Above the Law','independent','national','https://abovethelaw.com/feed/','legal'),
   ('DOJ press','primary','primary','https://www.justice.gov/news/rss?type=press_release',None),
   ('9th Circuit opinions (CourtListener)','primary','primary','https://www.courtlistener.com/feed/court/ca9/',None),
   ('OCCRP (organized crime & corruption, world)','international','world','https://www.occrp.org/en/feed',None),
   ('Google News: trials & sentencings','aggregator','national',GN+'(trial+OR+sentenced+OR+indicted+OR+verdict)+when:3d','legal'),
   ('Google News: world court cases','aggregator','world',GN+'(court+OR+trial+OR+sentenced)+world+when:3d','legal'),
  ]},
}
CTA='<div class="b" style="display:block;padding:12px;margin:18px 0;border-color:#e5484d"><b>Subscribe to Digital Cultra News for more stories like this.</b> <a href="/#membership">Join here</a></div>'
NOTE={'buried-blind':'<p class="m"><b>About blind items:</b> blind items are unverified gossip. We republish only the headline exactly as the original outlet published it, credit and link that outlet, and <b>never guess or add who an item is about</b>. Court and legal items describe allegations unless a court has ruled; everyone is presumed innocent until proven guilty.</p>',
 'sports':'<p class="m">Legal items describe allegations unless a court has ruled. Every headline links to its original outlet.</p>',
 'crime-court':'<p class="m">Charges and lawsuits are allegations until proven in court. Every headline links to its original outlet or court record.</p>'}
NOISE=re.compile(r"\b(odds|picks|prediction|clinical|vaccine|NSCLC|phase [123I]|chemotherapy|cancer|pembrolizumab)\b",re.I)
def keep(it,f):
    t=it['t']
    if NOISE.search(t): return False
    if f is None: return True
    if f=='blind': return bool(BLIND.search(t))
    if f=='legal': return bool(LEGAL.search(t))
    if f=='blindlegal': return bool(BLIND.search(t) or LEGAL.search(t))
    return True
def items(key,fetch):
    import concurrent.futures as cf
    S=SECTIONS[key]['src']; out=[]; ok=0; failed=[]
    with cf.ThreadPoolExecutor(12) as ex:
        for s,r in zip(S,ex.map(lambda s:fetch(s[:4]),S)):
            if r is None: failed.append(s[0]); continue
            ok+=1
            for it in r:
                if not keep(it,s[4]): continue
                it=dict(it); it['s']=it.get('orig') and '%s (found via Google News)'%it['orig'] or it['s']; it['blind']=bool(BLIND.search(it['t'])); out.append(it)
    seen=set(); out=[i for i in out if not (i['t'].lower() in seen or seen.add(i['t'].lower()))]
    cut=time.time()-14*86400; out=sorted([i for i in out if i['ts']>cut],key=lambda x:-x['ts'])[:80]
    return {'section':key,'title':SECTIONS[key]['title'],'feeds_total':len(S),'feeds_ok':ok,'failed':failed,'items':out,'generated':time.time()}
def render(key,d,seo):
    E=html.escape; rows=[]
    for i in d['items']:
        lab=('<span class="b" style="border-color:#e5484d">Blind item via %s</span> '%E(i.get('orig') or i['s'])) if i['blind'] else ('<span class="b">%s</span> '%E(i['s']))
        rows.append('<li style="margin:10px 0">%s<a href="%s" rel="nofollow noopener" target="_blank">%s</a> <span class="m">— via %s · %s UTC</span></li>'%(lab,E(i['u']),E(i['t']),E(i['s']),seo.iso(i['ts'])[:16].replace('T',' ')))
    src='; '.join(E(s[0]) for s in SECTIONS[key]['src'])
    body=('<h1>%s</h1><p>%s</p>%s%s<ul style="padding-left:0;list-style:none">%s</ul>%s<p class="m">Sources checked: %s. %d/%d feeds loaded.</p>'
          %(E(d['title']),E(SECTIONS[key]['desc']),NOTE[key],CTA,''.join(rows) or '<li>No items right now. Check back soon.</li>',CTA,src,d['feeds_ok'],d['feeds_total']))
    return seo.page(d['title']+' | '+seo.SITE_NAME,SECTIONS[key]['desc'],'/'+key,body)
