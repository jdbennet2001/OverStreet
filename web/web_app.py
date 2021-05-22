import pathlib
import json

from os import path

directory = pathlib.Path(__file__).parent.absolute()
modelLocation = path.join( directory, 'model.json')
queueLocation = path.join( directory, 'queue.json')

# Load data
if path.exists(modelLocation):
    with open(modelLocation) as f:
        model = json.load(f)
else:
    model = {}



with open(queueLocation) as f:
    queue = json.load(f)

# Filter out existing data
queue = [x for x in queue if x['basename'] not in model]


# Returns the next comic in the queue, from queue.json c
# Defined as [ {location: ... , basename: ..., suggestions: [...]}]
def comic(offset=0):


    issue = queue.pop()

    issue['remaining'] = len(queue)

    return issue


# We know stuff about a comic, let's store it in the model.json file
def update_model(data):

    model[ data['issue'] ] = data['id']

    with open(modelLocation, 'w') as outfile:
        json.dump(model, outfile, indent=4)

