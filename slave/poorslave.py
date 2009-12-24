# -*- coding: utf-8 -*-
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.db import stats
from google.appengine.ext.webapp.util import run_wsgi_app

import urllib2

__LINK__ = 'bXlwYXNzd29yZGlzc29zaW1wbGUK'

class DataStore(db.Model):
    data = db.BlobProperty()
    mime = db.StringProperty()

class SetData(webapp.RequestHandler):
    def get(self):
        self.post()

    def post(self):
        '''
        verify master
            if keyname='None' add [data,mime] to own datastore
            else verify link,
                    replace [data,mime] appropriately
            return the keyname
        '''
        self.response.headers['Content-Type'] = 'text/plain'
        
        # TODO: verify is referer is __MASTER__
        keyrequest = self.request.get('keyname')
        data_received = db.Blob(str(self.request.get('data'))
        mime = self.request.get('mime')
        
        if (keyrequest == 'None'):
            # new data
            new_content = DataStore(data=data_received, mime=mime)
            new_content.put()
            self.response.out.write (new_content.key())
        else:
            # old data to be replaced
            if self.request.get('link') == __LINK__:
                try:
                    content = DataStore.get(keyrequest)
                    content.data = data_received
                    content.mime = mime
                    content.put()
                    self.response.out.write (content.key())
                except db.KindError:
                    self.response.out.write ("key not found")
            else:
                self.response.out.write("no authority on this slave")


class GetData(webapp.RequestHandler):
    def get(self,keyname):
        try:
            content = DataStore.get (keyname)
            self.response.headers['Content-Type'] = content.mime
            self.response.out.write(content.data)
        except:
            self.response.out.write("key not found")


class DelData(webapp.RequestHandler):
    def get(self,keyname):
        ''' verify link
            delete key '''
        self.response.headers['Content-Type'] = 'text/plain'
        if self.request.get('link') == __LINK__:
            try:
                content = DataStore.get (keyname)
                content.delete()
                self.response.out.write("deleted")
            except:
                self.response.out.write("key not found")
        else:
            self.response.out.write("no authority on this slave")

class SendUpdate(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        if self.request.get('link') == __LINK__:
            global_stat = stats.GlobalStat.all().get()
            self.response.out.write("%d" % global_stat.bytes)
        else:
            self.response.out.write("no authority on this slave")
            
class Banner(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('This is a PoorMan\'s slave. Please leave it alone.')

application = webapp.WSGIApplication(
                            [
                                ('/get/(.*)', GetData),
                                ('/set', SetData),
                                ('/del/(.*)', DelData),
                                ('/update', SendUpdate),
                                ('/(.*)', Banner)
                            ],
                            debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()