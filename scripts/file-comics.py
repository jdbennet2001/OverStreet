'''
Walk the on-deck directory looking for tagged comics. 
Migrate them to the publisher / series boxes
'''

import sys
import shutil
import argparse

from os import path, listdir, makedirs
from redis import StrictRedis

rs = StrictRedis(decode_responses='utf-8')

proj_path = path.abspath('.')
sys.path.append(proj_path)  # VSCode hackery, ensure project relative imports work

proj_path = path.abspath('..')
sys.path.append(proj_path)  # VSCode hackery, ensure project relative imports work

from lib.contents import contents
from lib.comic import type, has_tag, get_tags

ON_DECK_DIRECTORY = 'on-deck'   # Where are the new comics?

PUBLISHER_DIRECTORIES = ['DC Comics', 'Marvel', 'Other']

def execute(catalog):

   # Find comics that need to be filed
    comics = waiting_comics(catalog)

    volumes = getVolumes(catalog)


    # Get a list of known series for each publisher
    DC_series = listdir( path.join(catalog, 'DC Comics') )
    Marvel_series = listdir( path.join(catalog, 'Marvel') )
    Other_series = listdir( path.join(catalog, 'Other') )


    print( f'----------- filing {len(comics)} comics ------------')

    for comic in comics:

        tags = get_tags(comic)
        if ( tags['publisher'] == 'DC Comics'):
            move(comic, DC_series, path.join(catalog, 'DC Comics'), tags, volumes)
        elif ( 'Marvel' in tags['publisher'] ):
            move( comic, Marvel_series, path.join(catalog, 'Marvel'), tags, volumes )
        else:
            move(comic, Other_series, path.join(catalog, 'Other'), tags, volumes )

    pass

# Build a dictionary of volume - location for all known volumes
def getVolumes(catalog):

    VOLUME_KEY = 'volume_map'

    # Use cached data..
    if rs.exists(VOLUME_KEY):
        return rs.hgetall(VOLUME_KEY)

    # Use Redis as a temporary cache to help in debugging`
    comics = contents(catalog)
    comics = [x for x in comics if volumeNumber(x) is not None]

    for comic in comics:
        volume = volumeNumber(comic)    
        rs.hset(VOLUME_KEY, volume, path.dirname(comic) )

    return rs.hgetall(VOLUME_KEY)

# Returns the volume number from a given comic's parent directory
def volumeNumber(comic):
    dir = path.basename( path.dirname(comic) )
    tokens = dir.split( ' ' )
    volumes = [x for x in tokens if x.startswith('(') and x.endswith(')')]
    if ( len(volumes) == 1):
        volume = volumes[0].lstrip('(').rstrip(')')
        return volume

TRADE_COUNT_PAGE_THRESHOLD = 112

# Basic filing logic
def move(comic, series, directory, tags, volumes):
    volume_id = tags['volume_id']

    volume_name = tags['volume_name']
    volume_name = volume_name.replace(':', '-')

    volume_start = tags['volume_start']
    page_count = tags['page_count']

    basename = path.basename(comic)
    basename = basename.replace(':', '-')

    series_dir = find_series(series, volume_name)

    # Trade paperbacks have a special filing structure
    if page_count >= TRADE_COUNT_PAGE_THRESHOLD:
        if series_dir:
            target = path.join( directory, series_dir, f'Trades/{basename}')
        else:
            target = path.join( directory, volume_name, f'Trades/{basename}')
        return mv (comic, target, 'trade')

    # Use Volume ID
    if volume_id in volumes:
        volume_directory = volumes[volume_id]
        target = path.join( volume_directory, basename)
        return mv( comic, target, 'volume insert' )

    # Use series
    
    if series_dir is not None:
        target = path.join( directory, series_dir, f'{volume_name} {volume_start} ({volume_id})/{basename}')
        volumes[volume_id] = path.dirname(target)
        return mv( comic, target, 'series insert' )

    # Generate new entry
    target = path.join( directory, f'{directory}/{volume_name}/{volume_name} {volume_start} ({volume_id})/{basename}' )
    volumes[volume_id] = path.dirname(target)
    series.append(volume_name)
    mv( comic, target, 'series new' )

def find_series(series, volume_name):

  folders = [folder for folder in series if folder in volume_name]

  # There might be multiple matches, find the longest one 
  folders.sort(key=len, reverse=True)

  if  folders:
      return folders[0]
  else:
      return None
    

def mv(source, destination, reason='sys-call'):

    # Remove non-ascii characters
  
    destination = destination.replace('?', '')
    destination = destination.replace('"', '-')

    print( f' ==>{reason} ==>  {path.basename(source)} ==> {destination}')
    makedirs( path.dirname(destination), exist_ok=True)
    shutil.move(source, destination)

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