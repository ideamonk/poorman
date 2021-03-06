# -*- coding: utf-8 -*-
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import urlfetch
from google.appengine.ext import webapp
from google.appengine.ext import db
import mimehack
import urllib2
import time

__LINK__ = 'bXlwYXNzd29yZGlzc29zaW1wbGUK'

class MasterDataStore(db.Model):
    keyname = db.StringProperty()
    slave = db.StringProperty()
    slave_key_name = db.StringProperty()


class PoorSlaves(db.Model):
    slave = db.StringProperty()
    bytes = db.IntegerProperty()

class AddUpload(webapp.RequestHandler):
    def get(self,_key):
        self.response.headers['Content-Type'] = 'text/plain'
        if self.request.get('link') == __LINK__:
            slave = self.request.get('slavename')
            keyname = self.request.get('filename') + str(time.time())
            entry = MasterDataStore (keyname = keyname, slave = slave,
                                                        slave_key_name = _key)
            entry.put()
            self.response.out.write ('upload stored as %s.' % keyname)
        else:
            self.response.out.write ('I am not your master son')
        
def get_rich_slave():
    # returns richest among the poor slaves
    query = PoorSlaves.gql('ORDER BY bytes')
    best_node = query.fetch(1)
    return best_node[0].slave


def update_stats():
    q = PoorSlaves.all()
    nodes = q.fetch(limit=1000)
    json = '['
    for node in nodes:
        url = 'http://' + node.slave + '/update?link=' + __LINK__
        result = urlfetch.fetch(url)
        if result.status_code == 200:
            try:
                bytes = int(result.content)
                node.bytes = bytes
                node.put()
                json = json + ('{"n":"%s","b":"%s"},' % (node.slave, bytes))
            except:
                ''' nothing to do with this node '''
    json = json + ']'
    return json


def get_upload_box(slave,redirect,extra):
    slave_url = 'http://' + slave + '/upload'
    form = '''  <form action="%s" method="POST" %s enctype="multipart/form-data">
                    <input type="file" name="poorupload" />
                    <input type="submit" value="upload" />
                    <input type='hidden' name="redirect" valeue="%s" />
                </form> ''' % ( slave_url, extra, redirect )
    return form


def set_data(_key, data, mime):
    entry = MasterDataStore.all().filter("keyname =",_key).fetch(1)
    newentry = True
    
    if (len(entry) == 1):
        # _key exists
        newentry = False
        entry = entry[0]
        slave = entry.slave
        content_type, slave_data = mimehack.encode_multipart_formdata(
                    [('link', __LINK__), ('mime', mime), ('keyname', str(entry.slave_key_name))],
                    [('data', 'data', data)] )
    else:
        # _key is new
        slave = get_rich_slave()
        content_type, slave_data = mimehack.encode_multipart_formdata(
                [('link', __LINK__), ('mime', mime), ('keyname','None')],
                [('data', 'data', data)] )
                
    url = 'http://' + slave + '/set'
    result = urlfetch.fetch( url, payload=slave_data, method = 'POST',
                    headers = {'Content-Type':content_type},
                    allow_truncated = False, follow_redirects = False,
                    deadline = 10)

    if (newentry):
        if result.status_code == 200:
            entry = MasterDataStore (keyname = _key, slave = slave,
                                                slave_key_name=str(result.content))
            entry.put()
            return result.content
    else:
        ''' no need to modify master meta data, content is simple replaced '''
        return entry.slave_key_name

def get_url(_key):
    q = MasterDataStore.all().filter('keyname =', _key)
    entry = q.fetch(1)[0]
    return 'http://' + entry.slave + '/get/' + entry.slave_key_name
    
    
def get_data(_key):
    url = get_url(_key)
    result = urlfetch.fetch(url)
    if result.status_code == 200:
        return result.content


def del_data(_key):
    entry = MasterDataStore.all().filter("keyname =",_key).fetch(1)
    if (len(entry) == 1):
        url = 'http://' + entry[0].slave + '/del/' + entry[0].slave_key_name + \
                '?link=' + __LINK__
    result = urlfetch.fetch(url, method = 'GET')
    if result.status_code == 200:
        if (result.content == 'deleted'):
            entry[0].delete()
        return result.content
    else:
        return 'key not found'

