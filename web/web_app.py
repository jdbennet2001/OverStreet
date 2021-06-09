
from posixpath import dirname
import sys
import json

from os import path, rename
from pathlib import Path

from PIL.Image import NONE

proj_path = path.abspath('.')
sys.path.append(proj_path)  # VSCode hackery, ensure project relative imports work

proj_path = path.abspath('..')
sys.path.append(proj_path)  # VSCode hackery, ensure project relative imports work

from lib.comic import add_tag, convert_to_zip

from redis import Redis
rs = Redis()

REDIS_DATA = 'score-data'

TAG_DATA = 'tag-queue'

# SKIP_LIST = ['Injustice', '']

# Returns a list of all comics waiting to be filed
def comics():

    keys = rs.hkeys(REDIS_DATA)
    # Redis returns byte data, decode as utf-8
    keys = [x.decode('utf-8') for x in keys]

    # Skip the series we know are user generated
    keys = [x for x in keys if 'The Legion of Super-Heroes Chronology' not in x ]

    # And return a dict. Lists aren't supported
    return { 'keys' : keys }


# Return information about a single comic in the queue
def comic(key, delete=False):
    data = rs.hget(REDIS_DATA, key)

    # Remove the data

    return json.loads(data)

def tag(comic):
    
    data = rs.hget(REDIS_DATA, comic)

    if data is NONE:
        return

    metadata = json.loads(data)
    target = path.join( path.dirname(comic), target_name(metadata))
    source = comic

    metadata.update( {'source': source, 'target' : target})

    rs.hdel(REDIS_DATA, comic)
    rs.hset(TAG_DATA, comic, json.dumps(metadata))

    print( f'==> {rs.hlen(TAG_DATA)} ==> {path.basename(target)}')


    
# What should this archive be called?
def target_name(metadata):

    volume_name = metadata['volume_name']
    issue_number = str(metadata['issue_number']).rjust(3, '0')
    name = metadata['name']
    cover_date = metadata['cover_date']

    cname = f"{volume_name} #{issue_number} ({metadata['cover_date']})"
    target = f"{cname} - {name}" if name else cname
    target = target.replace('/', '-')
    target = target.replace('?', '')
    target = target.replace(':', ' ')
    return f'{target}.cbz'

def skip(comic):
    rs.hdel(REDIS_DATA, comic)

    


