'''
Sort a bucket of comic into their:
    /publisher/volume/series/issue
respective slots
'''

import json
from os import listdir, path

maps = [
    {"1000000": "DC One Million"},
    {"Legionnaires", "Legion of Super-Heroes"},
    {"Convergence": "Convergence"},
    {" Futures End": " Futures End"},
    {"Crisis on Multiple Earths" : "Crisis on Multiple Earths"},
    
]

drive = "/Volumes/Seagate Expansion Drive/comics"
publishers = ['DC Comics', 'Marvel', 'Other']

series = []

for publisher in publishers:
    directory = path.join( drive, publisher)
    children = listdir(directory)
    for child in children:
        series.append( {'name': child, 'series': child})

with open('series.json', 'w') as f:
    json.dump(series, f, indent=4)
