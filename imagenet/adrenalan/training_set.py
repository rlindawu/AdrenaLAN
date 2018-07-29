#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 28 09:26:29 2018

@author: matthewszhang
"""
import os
import os.path as osp
from adrenalan.utils import get_photos
from adrenalan.classification import setup, dynamic_run, human_output_prediction
from googlemaps.client import Client
import googlemaps.places as Places

RADIUS = MAX = 50000

KEY = 'AIzaSyBwj6mhh8CdAixwINve65aCmvxKJTuBLoM'
CLIENT = Client(KEY)
MAXIMG = 3
DIR_EXT = 'test/'

def grep_training_images(categories, cities, **kwargs):
    
    
    for category in categories:
        if not osp.exists(osp.join(os.getcwd(), DIR_EXT + category)):
            os.makedirs(osp.join(os.getcwd(), DIR_EXT + category))
    for coordinates in cities:
        for category in categories:
            results = Places.places_nearby(
                    CLIENT, coordinates, RADIUS, type=category, **kwargs
                    )
            get_photos(results['results'], DIR_EXT + category)
            
            
CITIES = [
          (40.7128, -74.0060)
        ]
if __name__ == '__main__':
    with open('categories.txt', 'r') as f:        
        categories = f.readlines()
        
    categories = [c.strip() for c in categories]
    
    grep_training_images(['taxi_stand'], CITIES)
    