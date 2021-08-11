'''
Convert all .cbr files in a given directory to .cbz
'''
import argparse
import filetype
import sys
import shutil
import json
from os import path, rename

proj_path = path.abspath('.')
sys.path.append(proj_path)  # VSCode hackery, ensure project relative imports work

proj_path = path.abspath('..')
sys.path.append(proj_path)  # VSCode hackery, ensure project relative imports work

from lib.contents import contents

CATALOG_DIR = '/Volumes/Storage/comics/'

# Return a list of all unique directories for a given file list
def directories(files):

    dirs = set()

    for file in files:
        dirname = path.dirname(file)
        dirs.add(dirname)

    return list(dirs)

'''
Checks a string for a year (1930 - 2025)
Returns the year (as a string value) if it exists.
'''
def getYear(dir):
    years = range( 1930, 2025)
    years = [ str(x) for x in years]
    
    for year in years:
        if f' {year} ' in dir:
            return year

def getAction(source):
    year = getYear(source)
    basename = path.basename(source)
    basename = basename.replace(year, '')
    basename = basename.replace( '  ', ' ')
    basename = year + ' ' + basename
    target = path.join(path.dirname(source), basename)

    return {'source' : source, 'target' : target }

# Find all files
archives = contents(CATALOG_DIR)

# Extract (unique) directories
dirs = directories(archives)

# Filter out ComicVine volumes
volumes = [x for x in dirs if getYear(x)]

# Map out how to rename them
actions = [getAction(x) for x in volumes ]

# Dump the data (QA/Undo)
with open("rename_actions.json", "w") as write_file:
    json.dump(actions, write_file, indent=4)

# Rename
for action in actions:
    source = action['source']
    target = action['target']
    print( f'{source} => {target}')

    try:
        rename( source, target)
    except Exception as e:
        print(f'Exception mapping {path.basename(source)} to {path.basename(target)}, {e}')

print( f'{len(actions)} items')