#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 22:44:01 2018

@author: matthewszhang
"""
import os
import os.path as osp
import numpy as np
import glob
import shutil

from adrenalan.classification import setup, dynamic_run
from googlemaps.client import Client
import googlemaps.places as Places

KEY = 'AIzaSyBwj6mhh8CdAixwINve65aCmvxKJTuBLoM'
CLIENT = Client(KEY)
RADIUS = 100
MAXIMG = 3

def get_nearby_locations(coordinates, **kwargs):
    assert isinstance(coordinates, tuple)
    results = Places.places_nearby(CLIENT, coordinates, RADIUS, **kwargs)
    return results['results']

def write_picture(ret, name, iteration=0, tempdir='tmp'):
    tempdir = osp.join(os.getcwd(), tempdir)
    if not osp.exists(tempdir):
        os.makedirs(tempdir)
    f = open(osp.join(tempdir.encode('utf-8'), 
                      name.encode('utf-8') + 
                      '{}.jpeg'.format(iteration).encode('utf-8')), 'wb')
    for chunk in ret:
        if chunk:
            f.write(chunk)
    f.close()

def get_photos(results, tempdir='tmp'):
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
        
def classify(directory='tmp'):
    image_dir = osp.join(os.getcwd(), directory)
    output_class_dict = {}
    valid_images = [".jpeg"]
    paths = []
    names = []
    for f in os.listdir(image_dir):
        name, ext = os.path.splitext(f)
        if ext.lower() not in valid_images:
            continue
        paths.append(osp.join(image_dir, f))
        names.append(name)
    classifications = dynamic_run(paths)
    for i in range(len(classifications)):
        output_class_dict[names[i]] = classifications[i]
    return output_class_dict

def classify_single(abs_path):
    logits = dynamic_run([abs_path])
    return logits[0]

def compute_kls_with_labels(logits, dictionary):
    min_kl = 1000
    min_item = None
    kl_dict = {}
    for item in dictionary:
        assert dictionary[item].shape == logits.shape
        kl = np.sum(dictionary[item] * (np.log(dictionary[item] - \
                                        np.log(logits))))
        if item[:-1] in kl_dict:
            kl_dict[item[:-1]] = min(kl, kl_dict[item[:-1]])
        else:
            kl_dict[item[:-1]] = kl
            
    for item in kl_dict:
        if kl_dict[item] < min_kl:
            min_item = item
    
    assert min_item is not None
    return min_item
    
def cleanup(tempdir):
    shutil.rmtree(osp.join(os.getcwd(), tempdir))

def main(coords, tempdir='tmp', toclassify='6.jpeg'):
    setup()
    results = get_nearby_locations(coords)
    get_photos(results, tempdir)
    classify_dict = classify(tempdir)
    logits = classify_single(osp.join(os.getcwd(), toclassify))
    location = compute_kls_with_labels(logits, classify_dict)
    print(location)
    #cleanup(tempdir)

DEFAULT_COORD = (43.6653, -79.4049)

if __name__ == '__main__':
    main(DEFAULT_COORD)
    