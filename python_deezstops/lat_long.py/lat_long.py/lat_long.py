
import geocoder
import requests
import json


def current_location() -> tuple:
    '''Return a tuple containing (lat, long).'''
    
    data = requests.get('http://freegeoip.net/json/').json()
    return (data['latitude'], data['longitude'])

if __name__ == "__main__":
    print(current_location())