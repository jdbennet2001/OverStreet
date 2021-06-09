'''
Walk the on-deck directory looking for tagged comics. 
Migrate them to the publisher / series boxes
'''

import sys
import shutil
import argparse

from os import path, listdir, makedirs

proj_path = path.abspath('.')
sys.path.append(proj_path)  # VSCode hackery, ensure project relative imports work

proj_path = path.abspath('..')
sys.path.append(proj_path)  # VSCode hackery, ensure project relative imports work

from lib.contents import contents
from lib.comic import type, has_tag, get_tags

ON_DECK_DIRECTORY = 'unfiled'   # Where are the new comics?

PUBLISHER_DIRECTORIES = ['DC Comics', 'Marvel', 'Other']

def execute(catalog):

    # 
    volumes = getVolumes(catalog)

    # Find comics that need to be filed
    comics = waiting_comics(catalog)

    # Get a list of known series for each publisher
    DC_series = listdir( path.join(catalog, 'DC Comics') )
    Marvel_series = listdir( path.join(catalog, 'Marvel') )
    Other_series = listdir( path.join(catalog, 'Other') )

    for comic in comics:

        tags = get_tags(comic)
        if ( tags['publisher'] == 'DC Comics'):
            move(comic, DC_series, path.join(catalog, 'DC Comics'), tags)
        elif ( tags['publisher'] == 'DC Comics'):
            move( comic, Marvel_series, path.join(catalog, 'Marvel'), tags )
        else:
            move(comic, Other_series, path.join(catalog, 'Other'), tags )

    pass

# Build a dictionary of volume - location for all known volumes
def getVolumes(catalog):

    comics = contents(catalog)
    comics = [x for x in comics if volumeNumber(x) is not None]

    volumes = {}

    for comic in comics:
        volume = volumeNumber(comic)    
        volumes[volume] = path.dirname(comic)

    return volumes


# Returns the volume number from a given comic's parent directory
def volumeNumber(comic):
    dir = path.basename( path.dirname(comic) )
    tokens = dir.split( ' ' )
    volumes = [x for x in tokens if x.startswith('(') and x.endswith(')')]
    if ( len(volumes) == 1):
        volume = volumes[0].lstrip('(').rstrip(')')
        return volume

# Basic filing logic
def move(comic, series, directory, tags, volumes):
    volume_id = tags['volume_id']
    volume_name = tags['volume_name']
    volume_start = tags['volume_start']
    basename = path.basename(comic)

    # Use Volume ID
    if volume_id in volumes:
        volume_directory = volumes[volume_id]
        target = path.join( volume_directory, basename)
        return mv( comic, target )

    # Use series
    series_dir = next(folder for folder in series if volume_name in folder)
    if series_dir is not None:
        target = path.join( series_dir, basename)
        return mv( comic, target )

    # Generate new entry
    target = path.join( directory, f'{directory}/{volume_name} {volume_start} ({volume_id}/{basename}' )
    mv( comic, target )

    

def mv(source, destination):
    print( f' ==> {source} ==> {destination}')

# Return a list of all comics in the queue
def waiting_comics(catalog):

    comics = contents(path.join(catalog, ON_DECK_DIRECTORY))

    comics = [x for x in comics if type(x) == 'zip']

    comics = [x for x in comics if has_tag(x)]

    return comics



# Create the parser
my_parser = argparse.ArgumentParser(description='Move all new (tagged) comics to the official catalog in DC/Marvel/Other directories. ')

# Add the arguments
my_parser.add_argument('--catalog',  dest='catalog',  help='Comic location, example /Volumes/LocalDASD/comics')

args = my_parser.parse_args()

if args.catalog is None:
    print( 'Missing arguments. Run with -h for details')
    exit(-1)

if not path.exists(args.catalog):
    print( f'Catalog {args.catalog} not found.')
    exit(-2)


execute(args.catalog)