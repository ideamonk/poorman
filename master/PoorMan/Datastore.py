# -*- coding: utf-8 -*-
import urllib2

def set(key, data, mime):
    '''
    from slaves, select best one
    store the data there
    on success make [ key | slave | id | mime ] entry
    on fail notify
    '''

def get_url(key):
    '''
    look for which slave has this key
    return http://slave/get?id=22342352352
    '''
