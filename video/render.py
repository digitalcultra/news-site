#!/usr/bin/env python3
"""Digital Cultra News: story JSON -> 1080x1920 vertical MP4 + PNG stills.
Usage: python3 render.py story.json [--out out/] [--secs 4]
Story JSON schema: see ../infographic.js header. Cards with no data are skipped."""
import json, sys, os, subprocess, argparse, re, math, http.server, threading, functools
from PIL import Image, ImageFilter
from playwright.sync_api import sync_playwright
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORDER=['title','coverage','timeline','numbers','claims','receipts']
W,H,FPS=1080,1920,30
def fit(s):
    s=dict(s); s['timeline']=sorted(s.get('timeline',[]),key=lambda e:e['ts'])
    if len(s['timeline'])>6: t=s['timeline']; s['timeline']=t[:3]+t[-3:]
    seen=[];[seen.append(x) for x in s.get('sources',[]) if x['name'] not in [y['name'] for y in seen]]; s['sources_all']=s.get('sources',[]); s['receipts_src']=seen
    return s
http.server.SimpleHTTPRequestHandler.log_message=lambda *a:None
def layers(story,outdir):
    httpd=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(http.server.SimpleHTTPRequestHandler,directory=ROOT))
    
    threading.Thread(target=httpd.serve_forever,daemon=True).start(); port=httpd.server_address[1]; res=[]
    with sync_playwright() as p:
        b=p.chromium.launch(executable_path='/usr/bin/google-chrome'); pg=b.new_page(viewport={'width':W,'height':H})
        pg.goto(f'http://127.0.0.1:{port}/video/card.html'); pg.wait_for_function('!!(window.DCNInfo&&window.show)')
        for i,c in enumerate(ORDER):
            st=dict(story)
            if c=='receipts': st['sources']=story['receipts_src'][:7]
            if c=='coverage': st['sources']=story['sources_all']
            if not pg.evaluate('([s,c])=>show(s,c,"all")',[st,c]): continue
            pg.wait_for_timeout(300); still=f'{outdir}/{i:02d}_{c}.png'; pg.screenshot(path=still)
            pg.evaluate('([s,c])=>show(s,c,"bg")',[st,c]); pg.wait_for_timeout(150); bgp=f'/tmp/dcn_bg_{c}.png'; pg.screenshot(path=bgp)
            pg.evaluate('([s,c])=>show(s,c,"card")',[st,c]); pg.wait_for_timeout(150); cp=f'/tmp/dcn_card_{c}.png'; pg.screenshot(path=cp,omit_background=True)
            res.append((c,still,bgp,cp))
        b.close()
    httpd.shutdown(); return res
ease=lambda t:1-(1-max(0,min(1,t)))**3
def frames(parts,secs):
    n=int(secs*FPS)
    for c,_,bgp,cp in parts:
        bg=Image.open(bgp).convert('RGB'); card=Image.open(cp).convert('RGBA'); bb=card.getbbox() or (0,0,W,H)
        for f in range(n):
            t=f/FPS; z=1+0.06*f/n  # slow push-in on fffuel background
            bw,bh=int(W*z),int(H*z); fr=bg.resize((bw,bh)).crop(((bw-W)//2,(bh-H)//2,(bw-W)//2+W,(bh-H)//2+H))
            a=ease(t/0.7); out=max(0,(t-(secs-0.35))/0.35)
            lay=card.copy()
            if c in('coverage','timeline','receipts'):  # wipe reveal top->bottom / left->right
                m=Image.new('L',(W,H),0); prog=ease(t/1.6)
                if c=='coverage': m.paste(255,(0,0,bb[0]+int((bb[2]-bb[0])*prog),H))
                else: m.paste(255,(0,0,W,bb[1]+int((bb[3]-bb[1])*prog)+40))
                m.paste(255,(0,0,W,bb[1]+170)); lay.putalpha(Image.composite(lay.getchannel('A'),Image.new('L',(W,H),0),m))
            alpha=lay.getchannel('A').point(lambda v:int(v*a*(1-out))); lay.putalpha(alpha)
            fr.paste(lay,(0,int(80*(1-a))-int(60*out)),lay); yield fr
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('story'); ap.add_argument('--out',default=os.path.join(ROOT,'video','out')); ap.add_argument('--secs',type=float,default=0,help='seconds per card (0 = auto, total ~24s)'); ap.add_argument('--name',default=None)
    a=ap.parse_args(); story=fit(json.load(open(a.story))); os.makedirs(a.out,exist_ok=True)
    name=a.name or re.sub(r'\W+','-',os.path.splitext(os.path.basename(a.story))[0]); sd=os.path.join(a.out,name+'_stills'); os.makedirs(sd,exist_ok=True)
    parts=layers(story,sd); mp4=os.path.join(a.out,name+'.mp4'); a.secs=a.secs or max(4.0,min(7.0,24/max(1,len(parts))))
    ff=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-pix_fmt','yuv420p','-crf','20','-preset','veryfast','-movflags','+faststart',mp4],stdin=subprocess.PIPE)
    for fr in frames(parts,a.secs): ff.stdin.write(fr.tobytes())
    ff.stdin.close(); ff.wait(); print(mp4, len(parts),'cards', sd)
if __name__=='__main__': main()
