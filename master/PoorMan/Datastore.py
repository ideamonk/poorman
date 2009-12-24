# -*- coding: utf-8 -*-
from google.appengine.api import urlfetch
from google.appengine.ext import db
import urllib2
import mimehack

__LINK__ = 'bXlwYXNzd29yZGlzc29zaW1wbGUK'

class MasterDataStore(db.Model):
    keyname = db.StringProperty()
    slave = db.StringProperty()
    slave_key_name = db.StringProperty()

class PoorSlaves(db.Model):
    slave = db.StringProperty()
    bytes = db.IntegerProperty()

def GetRichSlave():
    # returns richest among the poor slaves
    query = PoorSlave.gql('ORDER BY bytes')
    best_node = query.fetch(1)
    return best_node[0].slave
    
def set_data(_key, data, mime):
    url = 'http://' + GetRichSlave() + '/set'
    try:
        entry = MasterDataStore.get(_key)
        # _key exists
        content_type, slave_data = mimehack.encode_multipart_formdata(
                    [('link', __LINK__), ('mime', mime), ('keyname', _key)],
                    [('data', 'data', data)] )
    except:
        # _key is new
        content_type, slave_data = mimehack.encode_multipart_formdata(
                [('link', __LINK__), ('mime', mime)], [('data', 'data', data)] )
                

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
    '''
    look for slave that holds the key
    tell the slave to delete the key
    return True/False
    '''