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

publishers = ['Panini Comics', 'Abril', 'Planeta DeAgostini']

TAG_DATA = 'tag-queue'

keys = rs.hkeys(TAG_DATA)

for i, key in enumerate(keys):

    path_to_file = key.decode('utf-8')

    if  not path.exists(path_to_file):
        print( f'==> skipping {path_to_file}, file not found')
        rs.hdel(TAG_DATA, key)
        continue

    print( f' ==> {i} / {len(keys)} ==>{path_to_file}')

    try:
        value = rs.hget(TAG_DATA, key)
        metadata = json.loads(value)

        if metadata['publisher'] in publishers:
            print( f'==> skipping, bad publisher')
            continue

        add_tag(metadata, key.decode('utf-8'))

        source_file = path.basename( metadata['source'] )
        if not source_file[0].isdigit(): # Skip files that start with a number, probably a existing arc or compilation
            rename(metadata['source'], metadata['target'])
    except Exception as e:
        print( f'== exception {e} for {path_to_file}')
    

    rs.hdel(TAG_DATA, key)
