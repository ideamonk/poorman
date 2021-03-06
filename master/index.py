# -*- coding: utf-8 -*-
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from PoorMan import Datastore as pd

class TestOut(webapp.RequestHandler):
    def get(self):
        print 'Content-Type: text/html'
        print
        print '===== PLAIN set_data TEST ====='
        keyname = pd.set_data('mynewkey2', 'mypoordata22222', 'text/plain')
        print 'stored on slave as', keyname
        print 'verification - ', pd.get_url('mynewkey2')
        print '===== BINARY set_data TEST ====='
        keyname = pd.set_data('mynewimage2', open('static/test.png','rb').read(), 'image/png')
        print 'verification - ', pd.get_url('mynewimage2')
        print '===== PLAIN get_data TEST ====='
        print 'got back -', pd.get_data('mynewkey2'), '- though ajax would be efficient'
        #print '===== deleting mynewkey2 ====='
        #print pd.del_data ('mynewkey2')
        print '===== testing update_stats ====='
        print 'JSON stats --', pd.update_stats()
        print '===== upload form ====='
        print pd.get_upload_box(pd.get_rich_slave(),'','http://localhost:8080/test')
        print
application = webapp.WSGIApplication(
                            [
                                ('/add_upload/(.*)',pd.AddUpload),
                                ('/test', TestOut)
                            ],
                            debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()