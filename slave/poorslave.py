# -*- coding: utf-8 -*-
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.db import stats
from google.appengine.ext.webapp.util import run_wsgi_app

import mimetypes
import urllib2
import os

__LINK__ = 'bXlwYXNzd29yZGlzc29zaW1wbGUK'
__MASTER__ = 'localhost:8080'

class DataStore(db.Model):
    data = db.BlobProperty()
    mime = db.StringProperty()

class SetData(webapp.RequestHandler):
    def get(self):
        self.post()

    def post(self):
        self.response.headers['Content-Type'] = 'text/plain'
        
        # TODO: verify is referer is __MASTER__
        keyrequest = self.request.get('keyname')
        data_received = db.Blob(str(self.request.get('data')))
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
                    self.response.out.write ('key not found')
            else:
                self.response.out.write('no authority on this slave')


class GetData(webapp.RequestHandler):
    def get(self,keyname):
        content = DataStore.get (keyname)
        
        if (content == None):
            self.response.out.write('key not found')
            return
            
        self.response.headers['Content-Type'] = content.mime
        self.response.out.write(content.data)

class DelData(webapp.RequestHandler):
    def get(self,keyname):
        self.response.headers['Content-Type'] = 'text/plain'
        if self.request.get('link') == __LINK__:
            try:
                content = DataStore.get (keyname)
                content.delete()
                self.response.out.write('deleted')
            except:
                self.response.out.write('key not found')
        else:
            self.response.out.write('no authority on this slave')


class SendUpdate(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        if self.request.get('link') == __LINK__:
            global_stat = stats.GlobalStat.all().get()
            try:
                self.response.out.write('%d' % global_stat.bytes)
            except:
                self.response.out.write('0')
        else:
            self.response.out.write('no authority on this slave')


class Upload(webapp.RequestHandler):
    # NOTE: __LINK__ cannot be passed here, as it cannot be passed
    #       insecurely through form's html
    def post(self):
        self.response.headers['Content-Type'] = 'text/plain'
        # TODO: verify is referer is __MASTER__
        data_received = db.Blob(str(self.request.get('poorupload')))
        filename = self.request.body_file.vars['poorupload'].filename
        #mime = mimetypes.types_map['.' + filename.split('.', 1)[1]]
        mime = self.request.body_file.vars['poorupload'].headers['content-type']
        
        new_content = DataStore(data=data_received, mime=mime)
        new_content.put()
        new_key = new_content.key()

        url = 'http://' + __MASTER__ + '/add_upload/' + str(new_key) + \
                    '?link=' + __LINK__ + '&filename=' + filename + \
                    '&slavemane=' + os.environ['HTTP_HOST']
                                
        result = urlfetch.fetch(url)
        if result.status_code == 200:
            self.redirect (self.request.get('redirect'))
        else:
            seld.response.out.write ('failed to upload')


class Banner(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write('This is a PoorMan\'s slave.' + \
                                                    ' Please leave it alone.')


application = webapp.WSGIApplication(
                            [
                                ('/get/(.*)', GetData),
                                ('/set', SetData),
                                ('/del/(.*)', DelData),
                                ('/update', SendUpdate),
                                ('/upload*', Upload),
                                ('/.*', Banner)
                            ],
                            debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()