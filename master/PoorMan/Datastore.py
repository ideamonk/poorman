# -*- coding: utf-8 -*-
import urllib2

__LINK__ = 'mypassword'

def set_data(key, data, mime):
    '''
    from slaves, select best one
    store the data there
    on success make [ key | slave | id | mime ] entry
    on fail notify
    '''

def get_url(key):
    '''
    look for which slave has this key
    return http://slave/get/22342352352
    '''

def get_data(key):
    '''
    look for slave that has id
    fetch data from crafted url
    ignore 1st mime line
    return remaining strinpped data
    '''

def del(key):
    '''
    look for slave that holds the key
    tell the slave to delete the key
    return True/False
    '''

    