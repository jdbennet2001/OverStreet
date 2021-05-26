'''
Classify waiting (on-deck) comics using difference hashing and persisted model

This is the main utility of the program. It's used to file comics.
'''

import sys
import io
import json
import time
import imagehash
import argparse
import pickle
import numpy as np

from os import path, getcwd
from math import floor
from PIL import Image
from redis import Redis

proj_path = path.abspath('.')
sys.path.append(proj_path)  # VSCode hackery, ensure project relative imports work

proj_path = path.abspath('..')
sys.path.append(proj_path)  # VSCode hackery, ensure project relative imports work

from lib.db import hashes, issueSummary
from lib.contents import contents
from lib.comic import  pages,  has_tag, convert_to_zip
from lib.pipeline import cover_hash, hamming, intersection

rs = Redis()

SCORE_THRESHOLD = 0.95 # Threshold for declaring a match with a given comic

REDIS_DATA = 'score-data'

def pipeline(directory):

    # Prep the files
    convert_files(directory)

    # Get the new list...
    files = contents(directory)
    comics = [x for x in files if x.endswith('cbz') or x.endswith('cbr')]

    # Classification model
    model = load_model()

    # Comic Vine issue / volume information
    cvIssues = hashes()

    results = []

    for i, comic in enumerate(comics):
        print( f'==> {i}/{len(comics)} ==> processing ==> {path.basename(comic)}')

        try:
            basename = path.basename(comic)

            if rs.hexists(REDIS_DATA, basename ):
                print( f'==> skipping ==> {basename} ==> redis')
                continue

            if has_tag(comic):
                print( f'==> skipping ==> {basename} ==> tagged')
                continue

            page_count = pages(comic)

            if labled(comic):
                match = match_by_label(comic)
            else:
                match = match_by_cover(comic, cvIssues, model)

            # Have we seen this before? Check if it's already labeled
            state = 'labeled' if  labled(comic) else 'pending'

            # Find comic vine entries that pass a reasonable threshold
            result =  {'location' : comic,  'comic': basename, 'state' : state,  'page_count': page_count, 'match' : match.copy()}
            rs.hset( REDIS_DATA, basename, json.dumps(result) )
            print( f" ==> {match['volume_name']}, {match['issue_number']} ==> distance: {match['distance']}, score: {match['score']}")

        except Exception as e:
            print( f' ==> Exception {e}')

    results = []
    for key in rs.hkeys(REDIS_DATA):
        entry = rs.hget(REDIS_DATA, key)
        results.append( json.loads(entry))

    with open('filing.json', 'w') as outfile:
        json.dump(results, outfile, indent=4)  

# Tagging works best with CBZ files, walk the directory converting all RAR archives prior to scanning
def convert_files(directory):

    # Find all comics
    files = contents(directory)

    # Convert cbr to cbz
    cbrs = [x for x in files if x.endswith('cbr')]

    print(f'Converting cbr => cbz, {len(cbrs)} files in the queue')
    
    for i, cbr in enumerate(cbrs):
        try:
            print(f'==> Pipeline conversion, {i}/{len(cbrs)}')
            convert_to_zip(cbr, remove_old=True)
        except Exception as e:
            print( f'==> Conversion error ==> {e} for ==> {cbr}')

    return cbrs

def match_by_label(comic):
    issue_number = issueNumber(comic)
    volume_number = volumeNumber(comic)
    match = issueSummary(volume_number, issue_number)
    return match

def match_by_cover(comic, cvIssues, model):

    hash = cover_hash(comic)
    page_count = pages(comic)
    basename = path.basename(comic)

    # Performance fix, only evaluate entries with similar file names / comic vine volume names
    candidates = [candidate for candidate in cvIssues if intersection(basename, candidate['volume_name'])]

    # Find the scores for each candidate
    scores = [ score(basename, page_count, hash, x, model) for x in candidates]

    # Find the best matches
    def get_distance(x):
        return x['distance']

    # Sort, descending
    scores.sort(key=get_distance)

    match = scores[0]

    return  match

# Check if this issue is already classified, and labeled
def labled(comic):
    try:
        issue_number = issueNumber(comic)
        volume_number = volumeNumber(comic)
        return volume_number and issue_number
    except:
        return False



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

'''
   Generate a vector of the form: 
    ['pages', 'distance', 'volume_count_of_issues', 'first_issue', 'DC', 'Marvel']
   and use that to identify matches (> 95% certainty) between a new image and the database
'''
def score(name, page_count, cover_hash, cvIssue, model ):



    distance = hamming(cover_hash, cvIssue['hash'])

    # if name == 'Action Comics 1010 (2019) (Webrip) (The Last Kryptonian-DCP).cbr' and cvIssue['issue_number'] == '1010':
    #     print( f' == > distance = {distance}')

    volume_count_of_issues = cvIssue['volume_count_of_issues']
    DC = (cvIssue['publisher'] == 'DC Comics')
    Marvel = (cvIssue['publisher'] == 'Marvel')
    first_issue = cvIssue['issue_number'] == str(1)
    vector = [page_count, distance, volume_count_of_issues, first_issue, DC, Marvel]
    sample = np.array([vector])
    scores =model.predict_proba(sample)[0]
    (miss, hit) = scores    # Returns numpy.float32 values, convert to native types
    cvIssue['score'] = hit.item()
    cvIssue['distance'] = distance
    return cvIssue
 
def hash_data():

    KEY = 'comicvine-hash-data'

    if rs.exists(KEY):
        data = rs.get(KEY)
        return json.loads(data)

    data = hashes()
    rs.set(KEY, json.dumps(data))
    return data

def load_model():
    model_location = path.join(getcwd(), 'notebooks/model.pkl')
    model = pickle.load(open(model_location, 'rb'))
    return model

my_parser = argparse.ArgumentParser(description='ML Classification code. Check for new comics and file them.')

# Add the arguments
my_parser.add_argument('--dir',  dest='dir',  help='Target directory (usually on-deck)')

args = my_parser.parse_args()

if  args.dir is None:
    print( 'Missing command line arguments. Run program with -h for feedback on necessary parameters.')
    exit(-1)

if not path.exists(args.dir):
    print(f'Source directory not found {args.dir}')
    exit(-2)

pipeline(args.dir)


