import os,sys,unittest,re
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Import helpers without binding the HTTP port
src=open(os.path.join(os.path.dirname(os.path.dirname(__file__)),'server.py')).read().split('http.server.ThreadingHTTPServer')[0]
src=src.replace('mailer.start(news)','pass')
ns={}
exec(compile(src,'server.py','exec'),ns)

class WorldSearch(unittest.TestCase):
    def test_empty(self):
        out=ns['world_search']('')
        self.assertEqual(out['query'],'')
        self.assertEqual(out['stories'],[])
    def test_sanitize_and_shape(self):
        out=ns['world_search']('ukraine <b> war')
        self.assertNotIn('<', out['query'])
        self.assertIn('ukraine', out['query'].lower())
        for k in ('stories','feeds_ok','feeds_total','generated','query'):
            self.assertIn(k,out)
        self.assertIsInstance(out['stories'], list)
    def test_cache(self):
        a=ns['world_search']('sudan shelter')
        b=ns['world_search']('sudan shelter')
        self.assertEqual(a['generated'], b['generated'])

if __name__=='__main__':
    unittest.main()
