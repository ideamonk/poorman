# -*- coding: utf-8 -*-
from google.appengine.api import urlfetch
from google.appengine.ext import db
import urllib2
import mimehack

myslaves = [
            'http://poormanslave1.appspot.com' ]
'''            'http://poormanslave2.appspot.com'
            'http://poormanslave3.appspot.com',
            'http://poormanslave4.appspot.com',
            'http://poormanslave5.appspot.com',
            'http://poormanslave6.appspot.com'
        ]
'''
class MasterDataStore(db.Model):
    keyname = db.StringProperty()
    slave = db.StringProperty()
    slave_key_name = db.StringProperty()

class Slaves(db.Model):
    bytes = db.IntegerProperty()

def set_data(_key, data, mime):
    '''
    from slaves, select best one
    store the data there
    on success make [ key | slave | id | mime ] entry
    on fail notify
    '''
    content_type, slave_data = mimehack.encode_multipart_formdata(
                        [('link',__LINK__),('mime',mime)],[('data','data',data)])
                        
    result = urlfetch.fetch(__SERVER__ + "/set", payload=slave_data,
                method="POST", headers={'Content-Type':content_type},
                allow_truncated=False, follow_redirects=False, deadline=10)
                
    if result.status_code == 200:
        entry = MasterDataStore (keyname=_key,slave=__SERVER__, slave_key_name=str(result.content))
        entry.put()
        return result.content

def get_url(_key):
    '''
    look for which slave has this key
    return http://slave/get/22342352352
    '''
    q = MasterDataStore.all().filter("keyname =", _key)
    entry = q.fetch(1)[0]
    return entry.slave + "/get/" + entry.slave_key_name
    
    
def get_data(_key):
    '''
    look for slave that has id
    fetch data from crafted url
    ignore 1st mime line
    return remaining strinpped data
    '''

def del_data(_key):
    '''
    look for slave that holds the key
    tell the slave to delete the key
    return True/False
    '''