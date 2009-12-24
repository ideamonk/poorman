# -*- coding: utf-8 -*-
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from PoorMan import Datastore as pd

class TestOut(webapp.RequestHandler):
    def get(self):
        print "Content-Type: text/plain"
        print
        print "sending data"
        keyname = pd.set_data('mynewkey', 'mypoordata', 'text/plain')
        print "stored on slave as", keyname
        print "verification - ", pd.get_url('mynewkey')
        print 'storing image'
        keyname = pd.set_data('mynewimage', open('static/test.jpg','rb').read(), 'image/jpeg')
        print "verification - ", pd.get_url('mynewimage')
application = webapp.WSGIApplication(
                            [
                                ('/test', TestOut)
                            ],
                            debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()