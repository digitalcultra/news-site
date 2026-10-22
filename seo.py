# Server-rendered, crawlable SEO pages. No JS needed. Headlines link to original outlets; summaries are derived only from our own coverage data.
import hashlib, html, json, time, datetime
from seo_config import SITE_URL, SITE_NAME, LOGO, CONTACT_EMAIL
E=html.escape
def sid(s): return hashlib.sha1(s['items'][0]['u'].encode()).hexdigest()[:12]
def iso(ts): return datetime.datetime.fromtimestamp(ts,datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
def section(s):
    sc=s['scopes']
    if any(x.startswith('local') for x in sc): return 'local'
    return 'national' if 'national' in sc else 'world'
ORG={"@type":"NewsMediaOrganization","name":SITE_NAME,"url":SITE_URL+"/","logo":{"@type":"ImageObject","url":SITE_URL+LOGO},
     "publishingPrinciples":SITE_URL+"/editorial-policy","correctionsPolicy":SITE_URL+"/editorial-policy#corrections"}
def ld(o): return '<script type="application/ld+json">%s</script>'%json.dumps(o).replace('</','<\\/')
def page(title,desc,path,body,lds=(),ogtype='website'):
    url=SITE_URL+path; t=E(title); d=E(desc[:160])
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
      f'<title>{t}</title><meta name="description" content="{d}"><link rel="canonical" href="{url}">'
      '<meta name="robots" content="index,follow,max-image-preview:large">'
      f'<meta property="og:type" content="{ogtype}"><meta property="og:site_name" content="{E(SITE_NAME)}"><meta property="og:title" content="{t}">'
      f'<meta property="og:description" content="{d}"><meta property="og:url" content="{url}"><meta property="og:image" content="{SITE_URL}{LOGO}">'
      f'<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{t}"><meta name="twitter:description" content="{d}">'
      f'<link rel="alternate" type="application/rss+xml" title="{E(SITE_NAME)}" href="{SITE_URL}/feed.xml">'
      '<style>body{font:16px/1.5 system-ui,sans-serif;max-width:760px;margin:auto;padding:12px;background:#0b0d12;color:#e8e8ee}a{color:#7cc4ff}.m{color:#9aa}.b{display:inline-block;border:1px solid #445;border-radius:9px;padding:1px 8px;margin:2px;font-size:13px}nav a{margin-right:12px}</style>'
      + ''.join(ld(x) for x in lds) +
      f'</head><body><nav><a href="/">{E(SITE_NAME)}</a><a href="/section/local">Local</a><a href="/section/national">National</a><a href="/section/world">World</a><a href="/about">About</a></nav><main>{body}</main>'
      '<footer class="m"><p><a href="/about">About</a> · <a href="/contact">Contact</a> · <a href="/editorial-policy">Editorial policy</a> · <a href="/feed.xml">RSS</a></p></footer></body></html>')
def summary(s):
    lv=', '.join(f'{k}: {v}' for k,v in sorted(s['leans'].items()))
    return (f"{s['n']} outlet(s) covered this story between {iso(s['first'])[:16].replace('T',' ')} and {iso(s['last'])[:16].replace('T',' ')} UTC. "
            f"Coverage by source type — {lv}. Verification status: {s['status']}."+ (' Why flagged: '+'; '.join(s['why'])+'.' if s['why'] else ''))
def story_page(s):
    path='/story/'+sid(s); sm=summary(s)
    li=''.join(f'<li><a href="{E(i["u"])}" rel="nofollow noopener" target="_blank">{E(i["t"])}</a> <span class="m">— {E(i["s"])} ({E(i["lean"])}), {iso(i["ts"])[:10]}</span></li>' for i in s['items'])
    badges=''.join(f'<span class="b">{E(k)}: {v}</span>' for k,v in s['leans'].items())
    body=(f'<article><h1>{E(s["title"])}</h1><p class="m">Aggregated headline — original reporting is by the linked outlets. Updated {iso(s["last"])}</p>'
          f'<section><h2>Context</h2><p>{E(sm)}</p><p>{badges} <span class="b">{E(s["status"])}</span></p></section>'
          f'<section><h2>Read the original coverage</h2><ul>{li}</ul></section></article>')
    art={"@context":"https://schema.org","@type":"NewsArticle","headline":s['title'][:110],"description":sm[:300],
         "datePublished":iso(s['first']),"dateModified":iso(s['last']),"mainEntityOfPage":SITE_URL+path,
         "image":[SITE_URL+LOGO],"author":{"@type":"Organization","name":SITE_NAME,"url":SITE_URL+"/about"},"publisher":ORG,
         "isBasedOn":[i['u'] for i in s['items']],"citation":[{"@type":"CreativeWork","url":i['u'],"name":i['t'],"publisher":{"@type":"Organization","name":i['s']}} for i in s['items']],
         "articleSection":section(s).title()}
    return page(s['title']+' | '+SITE_NAME, sm, path, body, [art], 'article')
def listing(title,desc,path,stories):
    li=''.join(f'<li><a href="/story/{sid(s)}">{E(s["title"])}</a> <span class="m">{s["n"]} outlet(s) · {E(s["status"])}</span></li>' for s in stories[:60])
    ws={"@context":"https://schema.org","@type":"WebSite","name":SITE_NAME,"url":SITE_URL+"/","publisher":ORG}
    org=dict(ORG,**{"@context":"https://schema.org"})
    return page(title,desc,path,f'<h1>{E(title)}</h1><p class="m">{E(desc)}</p><ul>{li}</ul>',[ws,org])
STATIC={
 'about':('About '+SITE_NAME,'What we are and how we work.',f'<h1>About {SITE_NAME}</h1><p>{SITE_NAME} is an aggregator. We collect headlines from 45+ public news feeds across the political spectrum, group stories about the same event, and label how widely and by whom each story is covered. We do not rewrite articles; every headline links to the original outlet.</p><p>Our own content is the coverage context on each story page (outlet counts, source-type labels, verification status), generated from the feed data. Run by the {SITE_NAME} team.</p>'),
 'contact':('Contact '+SITE_NAME,'How to reach us.',f'<h1>Contact</h1><p>Corrections, tips or questions: <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>.</p>'),
 'editorial-policy':('Editorial policy','How headlines are selected and labeled.','<h1>Editorial policy</h1><p>Sources are public RSS feeds tagged left, center, right, independent, international or primary document. Labels describe a source category, not a judgment of any story.</p><p>"Underreported" flags are rule-based (few outlets, one side only, coverage stopped quickly) and are shown with the reason.</p><p>We never invent facts, quotes or authors. Headlines and links belong to their original publishers.</p><h2 id="corrections">Corrections</h2><p>Report a mislabeled story via the contact page; we fix labels and source tags promptly.</p>')}
def static(k):
    t,d,b=STATIC[k]; return page(t+' | '+SITE_NAME,d,'/'+k,b,[dict(ORG,**{"@context":"https://schema.org"})])
def robots(): return f"User-agent: *\nAllow: /\nDisallow: /api/\nSitemap: {SITE_URL}/sitemap.xml\nSitemap: {SITE_URL}/news-sitemap.xml\n"
X=lambda s:html.escape(s,quote=True)
def sitemap(stories):
    u=['/','/section/local','/section/national','/section/world','/about','/contact','/editorial-policy']
    rows=''.join(f'<url><loc>{SITE_URL}{p}</loc></url>' for p in u)+''.join(f'<url><loc>{SITE_URL}/story/{sid(s)}</loc><lastmod>{iso(s["last"])}</lastmod></url>' for s in stories)
    return '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+rows+'</urlset>'
def news_sitemap(stories):
    cut=time.time()-48*3600
    rows=''.join(f'<url><loc>{SITE_URL}/story/{sid(s)}</loc><news:news><news:publication><news:name>{X(SITE_NAME)}</news:name><news:language>en</news:language></news:publication><news:publication_date>{iso(s["first"])}</news:publication_date><news:title>{X(s["title"])}</news:title></news:news></url>' for s in [x for x in stories if x['first']>cut][:1000])
    return '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">'+rows+'</urlset>'
def rss(stories):
    import email.utils as eu
    it=''.join(f'<item><title>{X(s["title"])}</title><link>{SITE_URL}/story/{sid(s)}</link><guid isPermaLink="true">{SITE_URL}/story/{sid(s)}</guid><pubDate>{eu.formatdate(s["first"],usegmt=True)}</pubDate><description>{X(summary(s))}</description></item>' for s in stories[:50])
    return f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>{X(SITE_NAME)}</title><link>{SITE_URL}/</link><description>Headlines from every side, with coverage context.</description><language>en</language>{it}</channel></rss>'
