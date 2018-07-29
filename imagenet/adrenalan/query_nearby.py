#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 22:44:01 2018

@author: matthewszhang
"""
import os
import os.path as osp
import numpy as np
import shutil

from adrenalan.classification import setup, dynamic_run, human_output_prediction
from adrenalan.utils import get_photos, parse_name
from adrenalan.inference import load_graph_default, inference
from googlemaps.client import Client
#from kivy.utils import platform
import googlemaps.places as Places

KEY = 'AIzaSyBwj6mhh8CdAixwINve65aCmvxKJTuBLoM'
CLIENT = Client(KEY)
RADIUS = 100
MAXIMG = 5
MAXLEN = 10
LF = osp.join(os.getcwd(), "model/output_labels.txt")
INVALID = ["administrative_area_level_1", "administrative_area_level_2",
"administrative_area_level_3", "administrative_area_level_4", "administrative_area_level_5",
"colloquial_area", "country", "floor", "geocode", "intersection", "locality",
"neighborhood", "political", "postal_town", "premise", "route", "sublocality", 
"sublocality_level_4", "sublocality_level_5", "sublocality_level_3",
"sublocality_level_2", "sublocality_level_1", "subpremise"]

def get_nearby_locations(coordinates, **kwargs):
    assert isinstance(coordinates, tuple)
    
    results = Places.places_nearby(CLIENT, coordinates,
                                   rank_by='distance',
                                   **kwargs)
    valid_list = []
    for item in results['results']:
        if all(typ not in INVALID for typ in item['types']):
            if len(set(item['types']).symmetric_difference(
                    set(['point_of_interest', 'establishment']))) > 0:
                valid_list.append(item)
    return valid_list[:min(MAXLEN, len(valid_list))]

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
        kl = np.sum(logits * (np.log(dictionary[item] - \
                                        np.log(logits))))
        ent = np.sum(dictionary[item] * (np.log(dictionary[item])))
        kl = kl - ent
        
        if item[:-1] in kl_dict:
            kl_dict[item[:-1]] = min(kl, kl_dict[item[:-1]])
        else:
            kl_dict[item[:-1]] = kl
            
    kl_sum = 0
    for item in kl_dict:
        kl_sum += np.exp(kl_dict[item])
        if kl_dict[item] < min_kl:
            min_item = item
            min_kl = kl_dict[item]
    print(kl_dict)
    
    assert min_item is not None
    return min_item
    
def cleanup(tempdir):
    shutil.rmtree(osp.join(os.getcwd(), tempdir))
    
def classify_inference(directory='tmp', graph=None):
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
    classifications = inference(paths, graph, LF)
    for i in range(len(classifications[0])):
        output_class_dict[names[i]] = classifications[0][i]
    return output_class_dict

def search(results, location):
    endswith = 1
    while endswith:
        if location.endswith('-copy'):
            location = location[:-5]
        else:
            endswith = 0
    for item in results:
        if parse_name(item['name']) == location:
            return item

def process_custom_1(coords1, coords2, toclassify='5.jpg', tempdir='tmp'):
    coords = (coords1, coords2)
    setup()
    logits = classify_single(osp.join(os.getcwd(), toclassify))
    query_term, _ = human_output_prediction(logits)
    assert isinstance(query_term, str)
    print(query_term)
    results = get_nearby_locations(coords)
    get_photos(results, tempdir)
    classify_dict = classify(tempdir)
    location = compute_kls_with_labels(logits, classify_dict)
    location_data = search(results, location)
    print(location_data)
    cleanup(tempdir)
    return location
    
ANDROID_PATH = NotImplementedError
    
def process_custom_2(coords1, coords2, toclassify='6.jpg', tempdir='tmp'):    
    coords = (coords1, coords2)
    #graph = load_graph_default(osp.join(os.getcwd(), 'model/output_graph.pb'))
    #logits = inference([osp.join(os.getcwd(), toclassify)], graph, LF)
    #query_term = logits[1][0]
    #print(query_term)
    #print(query_term)
    results = get_nearby_locations(coords)
#    get_photos(results, tempdir)
#    classify_dict = classify_inference(tempdir, graph)
#    location = compute_kls_with_labels(logits[0][0], classify_dict)
#    cleanup(tempdir)
    location = results[0]['name']
    return location

def process_wrapper(latitude, longitude, img_input, process = '2'):
    assert isinstance(latitude, float)
    assert isinstance(longitude, float)
    assert isinstance(img_input, str)
    
    if process == '1':
        return_val = process_custom_1(latitude, longitude, img_input)
        return return_val
    
    elif process == '2':
        return_val = process_custom_2(latitude, longitude, img_input)
        return return_val

DEFAULT_COORD = (40.7587, -73.9787)

if __name__ == '__main__':
    process_custom_2(*DEFAULT_COORD)
    