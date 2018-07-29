#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 28 09:32:10 2018

@author: matthewszhang
"""
import os
import os.path as osp
import string
from googlemaps.client import Client
import googlemaps.places as Places

RADIUS = MAX = 50000

KEY = 'AIzaSyBwj6mhh8CdAixwINve65aCmvxKJTuBLoM'
CLIENT = Client(KEY)
MAXIMG = 5

def parse_name(name):
    return ''.join(filter(lambda x: x in string.printable, name))

def write_picture(ret, name, iteration=0, tempdir='tmp'):
    tempdir = osp.join(os.getcwd(), tempdir)
    name = parse_name(name)
    if not osp.exists(tempdir):
        os.makedirs(tempdir)
    try:    
        exists = 1
        while exists:
            fname = osp.join(tempdir, 
                          name + 
                          '{}.jpeg'.format(iteration))
            name = name + '-copy'
            
            if not osp.isfile(fname):
                exists = 0
                
        f = open(fname, 'wb')
        for chunk in ret:
            if chunk:
                f.write(chunk)
        f.close()
    except:
        return

def get_photos(results, tempdir='tmp'):
    '''
    INPUT|
    results - results of places.search API
    
    OUTPUT|
    None, stores photos to tempdir
    '''
    
    for item in results:
        #if 'political' in item['types']:
        #    continue
        try:
            detailed = Places.place(CLIENT, item['place_id'])['result']['photos']
            
            for i in range(min(len(detailed), MAXIMG)):
                imageret = Places.places_photo(CLIENT,
                                      detailed[i]['photo_reference'],
                                      max_width=500)
                write_picture(imageret, item['name'], iteration=i, tempdir=tempdir)
        except:
            try:
                ret = Places.places_photo(CLIENT,
                                      item['photos'][0]['photo_reference'],
                                      max_width=500) 
            except:
                continue
            write_picture(ret, item['name'], tempdir=tempdir)
        