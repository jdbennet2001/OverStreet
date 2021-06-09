'''
Classify waiting (on-deck) comics using difference hashing and persisted model

This is the main utility of the program. It's used to file comics.
'''

from posixpath import basename
import sys
import io
import json
import time
import imagehash
import argparse
import pickle
import filetype
import numpy as np

from os import path, getcwd,  utime, stat
from redis import Redis

proj_path = path.abspath('.')
sys.path.append(proj_path)  # VSCode hackery, ensure project relative imports work

proj_path = path.abspath('..')
sys.path.append(proj_path)  # VSCode hackery, ensure project relative imports work

from lib.db import hashes, issueSummary
from lib.contents import contents
from lib.comic import  pages,  has_tag, convert_to_zip, add_tag
from lib.pipeline import cover_hash, hamming, intersection

rs = Redis()

SCORE_THRESHOLD = 0.95 # Threshold for declaring a match with a given comic

REDIS_DATA = 'score-data'


FILTERED_PUBLISHERS = ['Panini Comics', 'Abril', 'Planeta DeAgostini', 'Editorial Televisa']

def pipeline(directory):

    # Get the new list...
    files = contents(directory)

    # Drop series known to be untaggable 
    comics = [x for x in files if not 'manga' in x]
    comics = [x for x in files if not 'Trigan' in x]
    comics = [x for x in files if not 'PS238' in x]
    comics = [x for x in files if not 'Strange Tales' in x]

    # Comic Vine issue / volume information
    cvIssues = hashes()

    # Take out the European copies
    cvIssues = [x for x in cvIssues if not x['publisher'] in FILTERED_PUBLISHERS]

    results = []

    for i, comic in enumerate(comics):
        print( f'==> {i}/{len(comics)} ==> processing ==> {path.basename(comic)}')


        try:

            if rs.hexists(REDIS_DATA, comic):
                print( f'==> skipping ==> {basename} ==> redis')
                continue

            mtime = path.getmtime(comic) 

            comic = convert_file(comic)

            basename = path.basename(comic)

            if type(comic) != 'zip':
                print( f'==> skipping ==> {basename} ==> bad type')
                continue

            if has_tag(comic):
                print( f'==> skipping ==> {basename} ==> tagged')
                continue

            is_labeled = labled(comic)

            if is_labeled:
                match = match_by_label(comic)
                
                # Good enough, tag it now
                add_tag(match, comic) 

            else:
                match = match_by_cover(comic, cvIssues)

                # Save to Redis for later review
                rs.hset(REDIS_DATA, comic, json.dumps(match))

            set_file_modification_time(comic, mtime)

            # Find comic vine entries that pass a reasonable threshold
            print( f" ==> {match['volume_name']}, {match['issue_number']} (labeled = {is_labeled}) ==> distance: {match['distance']}\n\n\n")

        except Exception as e:
            print( f' ==> Exception {e}')

    results = {}

    for key in rs.hkeys(REDIS_DATA):
        string_data = rs.hget(REDIS_DATA, key)
        results[key.decode('utf-8')] = json.loads(string_data)

    with open("tags.json", "w") as tags_file:
        json.dump(results, tags_file, indent=4)            


def set_file_modification_time(filename, mtime):
    """
    Set the modification time of a given filename to the given mtime.
    mtime must be a datetime object.
    """
    st = stat(filename)
    atime = st.st_atime
    utime(filename, times=(atime, mtime))

# Tagging works best with CBZ files, walk the directory converting all RAR archives prior to scanning
def convert_file(file):

    extension = type(file)
    if extension == 'rar':
        print( f' ==> {extension} ==> {path.basename(file)} ==> converting')
        return convert_to_zip(file, remove_old=True)
    else:
        print( f' ==> {extension} ==>  {path.basename(file)} ==> no coversion')
        return file


def type(path_to_archive):
    try:
         extension = filetype.guess(path_to_archive).extension
         return extension
    except Exception as e:
        print( f' ==> {path_to_archive} ==> Invalid File Type')
        return None

def match_by_label(comic):
    issue_number = issueNumber(comic)
    volume_number = volumeNumber(comic)
    match = issueSummary(volume_number, issue_number)
    match['distance'] = None
    return match

def match_by_cover(comic, cvIssues):

    hash = cover_hash(comic)
    page_count = pages(comic)
    basename = path.basename(comic)

    # Performance fix, only evaluate entries with similar file names / comic vine volume names
    candidates = [candidate for candidate in cvIssues if intersection(basename, candidate['volume_name'])]

    # Find the scores for each candidate
    scores = [ score(basename, page_count, hash, x) for x in candidates]

    # Find the best matches
    def get_distance(x):
        return x['distance']

    # Sort, descending
    scores.sort(key=get_distance)

    match = scores[0]
    match.update( {'page_count': page_count, 'basename' : basename, 'comic': comic})

    return  match

# Check if this issue is already classified, and labeled
def labled(comic):
    try:
        issue_number = issueNumber(comic)
        volume_number = volumeNumber(comic)
        return volume_number is not None and issue_number is not None
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
def score(name, page_count, cover_hash, cvIssue ):



    distance = hamming(cover_hash, cvIssue['hash'])

    # if name == 'Action Comics 1010 (2019) (Webrip) (The Last Kryptonian-DCP).cbr' and cvIssue['issue_number'] == '1010':
    #     print( f' == > distance = {distance}')

    volume_count_of_issues = cvIssue['volume_count_of_issues']
    DC = (cvIssue['publisher'] == 'DC Comics')
    Marvel = (cvIssue['publisher'] == 'Marvel')
    first_issue = cvIssue['issue_number'] == str(1)
    vector = [page_count, distance, volume_count_of_issues, first_issue, DC, Marvel]
    sample = np.array([vector])
    # scores =model.predict_proba(sample)[0]
    # (miss, hit) = scores    # Returns numpy.float32 values, convert to native types
    # cvIssue['score'] = hit.item()
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


