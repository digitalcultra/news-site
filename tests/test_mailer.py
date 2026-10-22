import os,sys,time,unittest,datetime
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.pop('BREVO_API_KEY',None)
import mailer
def S(t,score=3,scopes=('local:IL:Chicago',),age=3600):
    now=time.time()
    return {'title':t,'items':[{'u':'https://ex.com/'+t,'t':t}],'n':2,'status':'Multiple independent sources','score':score,
            'why':['Covered by only 2 outlets'],'scopes':list(scopes),'first':now-age,'last':now-age/2}
class T(unittest.TestCase):
    def test_digest_html(self):
        h=mailer.render_digest([S('Water <main> break'),S('Other')],'Chicago','IL','https://x/u?e=a&t=b')
        self.assertIn('Top buried stories near you',h); self.assertIn('Water &lt;main&gt; break',h)
        self.assertIn(mailer.SITE_URL+'/story/',h); self.assertIn(mailer.PAYHIP,h)
        self.assertIn('Insider members get real-time alerts for your area',h)
        self.assertIn('Unsubscribe',h); self.assertIn('https://x/u?e=a&amp;t=b',h); self.assertIn(mailer.SITE_NAME,h)
        self.assertNotIn('<main>',h)
    def test_alert_html(self):
        h=mailer.render_alert(S('Fire'),'Chicago','IL','https://x/u'); self.assertIn('Breaking near Chicago, IL',h); self.assertIn('Fire',h)
    def test_empty_digest(self): self.assertIn('No new buried stories',mailer.render_digest([],'','','u'))
    def test_parse_loc(self):
        self.assertEqual(mailer.parse_loc('chicago, il'),('Chicago','IL')); self.assertEqual(mailer.parse_loc('Peoria'),('Peoria',''))
    def test_pick_and_local(self):
        a=S('Local',1); b=S('Nat',2,('national',)); c=S('Zero',0,('national',))
        p=mailer.pick_digest([a,b,c],'IL','Chicago'); self.assertEqual([x['title'] for x in p],['Local','Nat'])
        self.assertFalse(mailer.is_local(a,'TX','Austin'))
    def test_noop_without_key(self):
        self.assertFalse(mailer.enabled()); self.assertFalse(mailer.upsert_contact('a@b.co','Chicago'))
        self.assertEqual(mailer.tick(),{'ok':True,'enabled':False}); self.assertFalse(mailer.unsubscribe('a@b.co','x'))
if __name__=='__main__': unittest.main()
