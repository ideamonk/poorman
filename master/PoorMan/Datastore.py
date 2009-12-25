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
            slave = self.request.headers.get('Referer').split(
                                            'ttp://', 1)[1].split('/', 1)[0]
            entry = MasterDataStore (keyname = self.request.get('filename') + \
                        str(time.time()), slave = slave, slave_key_name = _key)
            entry.put()
        else:
            self.response.out.write ('I am not your master son')
        
def get_rich_slave():
    # returns richest among the poor slaves
    query = PoorSlave.gql('ORDER BY bytes')
    best_node = query.fetch(1)
    return best_node[0].slave


def update_stats():
    q = PoorSlaves.all()
    nodes = q.fetch(limit=1000)
    json = '['
    for node in nodes:
        url = 'http://' + node.slave + '/update'
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


def get_upload_box(slave,extra):
    slave_url = 'http://' + slave + '/upload'
    form = '''  <form action="%s" method="POST" %s>
                    <input type="file" name="poorupload">
                </form> ''' % ( slave_url, extra )
    return form


def set_data(_key, data, mime):
    url = 'http://' + get_rich_slave() + '/set'
    try:
        entry = MasterDataStore.get(_key)
        # _key exists
        content_type, slave_data = mimehack.encode_multipart_formdata(
                    [('link', __LINK__), ('mime', mime), ('keyname', entry.slave_key_name)],
                    [('data', 'data', data)] )
    except:
        # _key is new
        content_type, slave_data = mimehack.encode_multipart_formdata(
                [('link', __LINK__), ('mime', mime), ('keyname','None')],
                [('data', 'data', data)] )
                

    result = urlfetch.fetch( url, payload=slave_data, method = 'POST',
                    headers = {'Content-Type':content_type},
                    allow_truncated = False, follow_redirects = False,
                    deadline = 10)
                    
    if result.status_code == 200:
        entry = MasterDataStore (keyname = _key, slave = __SERVER__,
                                            slave_key_name=str(result.content))
        entry.put()
        return result.content


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
    try:
        entry = MasterDataStore.get(_key)
    except:
        return 'key not found'
    url = 'http://' + entry.slave + '/dev/' + entry.slave_key_name
    result = urlfetch.fetch(url, payload = {'link':__LINK__}, method = 'GET')
    if result.status_code == 200:
        return result.content