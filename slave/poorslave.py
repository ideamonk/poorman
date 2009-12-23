# -*- coding: utf-8 -*-
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import urllib2

__LINK__ = 'mypassword'

class DataStore(db.Model):
    data = db.BlobProperty()
    mime = db.StringProperty()

class SetData(webapp.RequestHandler):
    def get(self):
        self.post()

    def post(self):
        '''
        auth  >>  add [data,mime] to your datastore  >>  return the keyname
        '''
        self.response.headers['Content-Type'] = 'text/plain'
        if self.request.get('link') == __LINK__:
            new_content = DataStore(data=db.Blob(str(self.request.get('data'))),
                                                mime=self.request.get('mime'))
            new_content.put()
            self.response.out.write (new_content.key())
        else:
            self.response.out.write("You do not have authority over this poor man's slave.")

class GetData(webapp.RequestHandler):
    def get(self,keyname):
        '''
            check if exists >>  get the record with id=id >>  print its mime
            >> print its content
        '''
        try:
            content = DataStore.get (keyname)
            if (content != None):
                self.response.headers['Content-Type'] = content.mime
                self.response.out.write(content.data)
            else:
                self.response.out.write("not found")
        except:
            self.response.out.write("bad key")

class DelData(webapp.RequestHandler):
    def get(self,keyname):
        '''  auth >>  del that key '''
        if self.request.get('link') == __LINK__:
            try:
                content = DataStore.get (keyname)
                content.delete()
                self.response.out.write("deleted")
            except:
                self.response.out.write("bad key")
        else:
            self.response.out.write("You do not have authority over this poor man's slave.")
                        
class Banner(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('This is a PoorMan\'s slave.')

application = webapp.WSGIApplication(
                            [
                                ('/get/(.*)', GetData),
                                ('/set', SetData),
                                ('/del/(.*)', DelData),
                                ('/(.*)', Banner)
                            ],
                            debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()