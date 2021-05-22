import sys
import io
import json
import time
import imagehash
import argparse

from math import floor
from PIL import Image
from redis import Redis

rs = Redis()

from os import path, remove

proj_path = path.abspath('.')
sys.path.append(proj_path)  # VSCode hackery, ensure project relative imports work

proj_path = path.abspath('..')
sys.path.append(proj_path)  # VSCode hackery, ensure project relative imports work

from lib.contents import contents
from lib.db import hashes, summary
import lib.comic as comicUtils



# Maximum Hamming distance required to determine a match (0.0 - 1.0)
HAMMING_THRESH = 0.0

def hamming(s1, s2):
    '''
    Calculate the normalized Hamming distance between two strings.
    '''
    assert len(s1) == len(s2)
    return float(sum(c1 != c2 for c1, c2 in zip(s1, s2))) / float(len(s1))

# Check if a file has already been processed
def processed( basename, results):

    found =  any( result['comic'] == basename for result in results)
    return found

def closest(hash, candidates, volume_id, issue_number):

    results = []

    def get_distance(result):
        return result['distance']

    for candidate in candidates:
        candidate['distance'] = hamming(hash, candidate['hash'])
        results.append(candidate)

    # Sort, descending, for account data
    results.sort(key=get_distance)

    index = 0

    # Find the index of the actual match
    for i, x in enumerate(results):
        index = i if x['volume_id'] == str(volume_id) and x['issue_number'] == str(issue_number) else index

    # Push that to the start of the list
    results.insert(0, results.pop(index))

    return results

# Hash comparision is slow, filter the list to speed things up
def search(comic, issues):
 
    # Remove short tokens from the first string, just to toss out filler words
    tokens1 = [x for x in comic.split(' ') if len(x) > 3]
    set1 = set( tokens1 )

    # Returns True if the intersection of str1 and str2 is non-null
    def intersection(str2):

        if not str2: # Sanity check, empty strings
            return False

        tokens2 = str2.split(' ')
        overlap = set1.intersection(tokens2)

        if len(overlap) > 0:
            return True
        else:
            return False

    results = [x for x in issues if intersection(x['volume_name'])]

    if results:
        return results
    else:
        return issues

# Returns the volume number from a given comic's parent directory
def volumeNumber(comic):
    dir = path.basename( path.dirname(comic) )
    tokens = dir.split( ' ' )
    volumes = [x for x in tokens if x.startswith('(') and x.endswith(')')]
    if ( len(volumes) == 1):
        volume = volumes[0].lstrip('(').rstrip(')')
        return int(volume, base=10)
     
# Returns the issue number from a given comic's name
def issueNumber(comic):
    file = path.basename(comic)
    tokens = file.split( ' ' )
    numbers = [x for x in tokens if x.startswith('#')]
    if ( len(numbers) == 1):
        number = numbers[0].lstrip('#')
        return int(number, base=10)

# Check if a comic has both a volume and an issue_number
def isLabeled(comic):
    try:
        issue = issueNumber(comic)
        volume = volumeNumber(comic)
        return issue and volume
    except Exception as e:
        return False

def classify(CATALOG, HASH_OUTPUT):

    # Get all the comics to be processed
    files = contents(CATALOG)

    comics = [x for x in files if isLabeled(x)]

    # Find the potential hashes
    issues = hashes()

    results = []

    for count, comic in enumerate(comics):

        try:

            start = time.time()

            basename = path.basename(comic)

            if rs.exists(basename):
                print( f'==> Skipping ==> {basename}, already processed')
                continue
            else:
                print( f'==> parsing ==> {count}/ {len(comics)} => {comic}')

            issue_number = issueNumber(comic)
            volume_number = volumeNumber(comic)

            image_data = comicUtils.extract_cover(comic)

            img = Image.open(io.BytesIO(image_data))

            cover_img_hash = imagehash.dhash(img)
            cover_hash = str(cover_img_hash)

            comic_hashes = search(basename, issues)

            distances = closest(cover_hash, comic_hashes, volume_number, issue_number)

            # Let's show the best match
            candidates = distances[:5]

            # How many pages are there?
            pages = comicUtils.pages(comic)

            for  i, candidate in enumerate(candidates):

                cv = summary(candidate['id'])

                match = cv['volume_id'] == str(volume_number) and cv['issue_number'] == str(issue_number)

                print( f" {i} => {cv['volume_name']} ({cv['volume_id']}) ({cv['month']}) #{cv['issue_number']},  {cv['name']}  ({cv['url']}) match={match} (distance={candidate['distance']}) ")

                result = {'comic': path.basename(comic), 'location': comic, 'pages' : pages, 'match' : match, 'distance': candidate['distance']}
                result.update(cv)

                # Dump everything into redis, serialize later
                rs.lpush(basename, json.dumps(result))

            end = time.time()

            print( f'{floor(time.time() - start)} seconds elapsed (processing time)')


        except Exception as e:
            print( f'Exception parsing {path.basename(comic)}, {e}')


def serialize():

    samples = []

    # Pull data from Redis
    keys = rs.keys('*cb*')
    for i, key in enumerate(keys):
        print( f'==> redis ==> {i}/{len(keys)} ==> {key} ==> json')
        entries = rs.lrange(key, 0, -1)
        samples = samples + entries
    
    # Deserialize
    data = []
    for sample in samples:
        data.append( json.loads(sample) )

    with open('samples.json', 'w') as outfile:
        json.dump(data, outfile, indent=4)    

    print( f'==> samples.json ==> {len(keys)} serialized')
  


# Create the parser
my_parser = argparse.ArgumentParser(description='ML Classification code. Walk a directory generating potential matches for each file.')

# Add the arguments
my_parser.add_argument('--dir',  dest='dir',  help='Target directory to be scanned')
my_parser.add_argument('--out',  dest='out',  help='Output, JSON, file')

args = my_parser.parse_args()

if  args.dir is None or args.out is None:
    print( 'Missing command line arguments. Run program with -h for feedback on necessary parameters.')
    exit(-1)


if not path.exists(args.dir):
    print(f'Source directory not found {args.dir}')
    exit(-1)

# Walk directory adding all new file information to disk
classify(args.dir, args.out)

# Save information to 'sample.json' for later model processing
serialize()
