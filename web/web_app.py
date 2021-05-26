
from posixpath import dirname
import sys
import json

from os import path, rename
from pathlib import Path

proj_path = path.abspath('.')
sys.path.append(proj_path)  # VSCode hackery, ensure project relative imports work

proj_path = path.abspath('..')
sys.path.append(proj_path)  # VSCode hackery, ensure project relative imports work

from lib.comic import add_tag, convert_to_zip

from redis import Redis
rs = Redis()

REDIS_DATA = 'score-data'
REDIS_TAG  = 'queue-tag'
REDIS_SKIP = 'queue-skip'


# Returns a list of all comics waiting to be filed
def comics():
    keys = rs.hkeys(REDIS_DATA)
    # Redis returns byte data, decode as utf-8
    keys = [x.decode('utf-8') for x in keys]

    # Remove any comics that are already processed
    keys = [x for x in keys if is_pending(x)]
    
    # And return a dict. Lists aren't supported
    return { 'keys' : keys }

def is_pending(key):
    data =rs.hget(REDIS_DATA, key)
    profile = json.loads(data)
    return profile['state'] == 'pending'

# Return information about a single comic in the queue
def comic(key):
    data = rs.hget(REDIS_DATA, key)
    return json.loads(data)


def set_state(key, status):
    data =rs.hget(REDIS_DATA, key)
    profile = json.loads(data)
    profile['state'] = status
    rs.hset(REDIS_DATA, key, json.dumps(profile))

    # Dump data for debugging
    results = []
    for key in rs.hkeys(REDIS_DATA):
        entry = rs.hget(REDIS_DATA, key)
        results.append( json.loads(entry))

    with open('score.json', 'w') as outfile:
        json.dump(results, outfile, indent=4) 





    


