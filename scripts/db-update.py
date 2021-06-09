'''
Import export data to the DB from disk, Used to make Postgres as the source of truth for the system
'''

'''
Test code trying to match existing cbz files to the pHash database
'''
import argparse
import psycopg2
import json
import sys
import imagehash 

from PIL import Image
from os import path, listdir, remove

proj_path = path.abspath('.')
sys.path.append(proj_path)  # VSCode hackery, ensure project relative imports work

proj_path = path.abspath('..')
sys.path.append(proj_path)  # VSCode hackery, ensure project relative imports work

from lib.contents import contents

conn = psycopg2.connect(
    host="localhost",
    database="overstreet",
    user="postgres",
    password="admin")


def createVolumesTable():
    cur = conn.cursor()

    # Drop existing table, if available
    cur.execute('drop table if exists ComicVineVolumes')

    # id, name, publisher, start_year, count_of_issues, month, description, url, image

    # Generate new table
    cur.execute( 'CREATE TABLE IF NOT EXISTS ComicVineVolumes (id text, name text, publisher text, start_year text, count_of_issues int, month text, description text, url text, image text )')

    cur.close()
    conn.commit()

'''
Issue data is stored in a single directory, with files labeled {YYYY-MM}.json
'''
def importVolumes(disk):

    directory = path.abspath( path.join( disk, 'education/data/comic-vine/volumes' ) )
    files = listdir(directory)

    files = [x for x in files if x.endswith('json')]

    # We have data, let's create the table
    createVolumesTable()

    cur = conn.cursor()

    for i, file in enumerate(files):

        with open(path.join(directory, file), "r", encoding='utf-8') as read_file:
            volumes = json.load(read_file)

        print( f'==> {i}/{len(files)} ==> (volumes) ==> {file}')

        for volume in volumes:
            try:
                importVolume(cur, volume)
            except Exception as e:
                print( f'Volume parsing error: {volume.get("name")}, {e}')

    cur.close()
    conn.commit()

'''
Push a single volume into the ComicVineVolumes table
'''
def importVolume(curr, record):

    id = str(record['id']), 
    name = record['name']

    try:
        publisher = record.get('publisher', {}).get('name', 'Other')
    except:
        publisher = 'Other'

    try:
        start_year = int(record['start_year'])
    except:
        # print( f'Skipping {name}, invalid start year {record.get("start_year")}')
        return

    count_of_issues =record['count_of_issues']

    description = record['description']
    url = record['site_detail_url']
    image = record['image']['medium_url']
    month = record['date_added'][0:7]
    
    curr.execute('insert into ComicVineVolumes(id, name, publisher, start_year, count_of_issues, month, description, url, image) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)', (id, name, publisher, start_year, count_of_issues, month, description, url, image))



def createIssuesTable():

    cur = conn.cursor()

    # Drop existing table, if available
    cur.execute('drop table if exists ComicVineIssues')

    # Generate new table
    cur.execute( 'CREATE TABLE IF NOT EXISTS ComicVineIssues ( id text, year int, volume_id text, volume_name text, volume_url text, name text, image text, cover_date text, description text, issue_number text, url text, month text )')

    cur.close()
    conn.commit()

'''
Issue data is stored in a single directory, with files labeled {YYYY-MM}.json
'''
def importIssues(disk):

    cur = conn.cursor()

    directory = path.abspath( path.join( disk, 'education/data/comic-vine/issues' ) )
    files = listdir(directory)

    files = [x for x in files if x.endswith('.json')]
    files.reverse()

    # We have data, let's create the table
    createIssuesTable()

    for i, file in enumerate(files):

        try:
            with open(path.join(directory, file), "r",  encoding='utf-8') as read_file:
                issues = json.load(read_file)
        except Exception as e:
            print( f'Bad file: {file}, {e}')
            remove( path.join(directory, file) )

        print( f'==> {i}/{len(files)} ==> (issues) ==> {file}')

        for issue in issues:
            importIssue(cur, issue)

    cur.close()
    conn.commit()

'''
Push a single issue into the ComicVineIssues table
'''
def importIssue(curr, record):


    image = record['image']

    id = record['id'], 
    
    (year, month, day) = record['cover_date'].split('-')

    volume = record['volume']
    volume_id = volume['id']
    volume_name = volume['name']
    volume_url = volume['site_detail_url']

    name = record['name']
    cover_date = record['cover_date']
    description = record['description']
    issue_number = record['issue_number']
    url = record['site_detail_url']

    image = record['image']['medium_url']

    full_month = f'{year}-{month}'
    
    curr.execute('insert into ComicVineIssues(id, year, volume_id, volume_name, volume_url, name, image, cover_date, description, issue_number, url, month) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', (id, year, volume_id, volume_name, volume_url, name, image, cover_date, description, issue_number, url, full_month))

# Make sure there's a table
def createHashTable():

    cur = conn.cursor()

    # Drop existing table, if available
    # cur.execute('drop table if exists pHash')

    # Generate new table
    cur.execute( 'CREATE TABLE IF NOT EXISTS pHash ( id text, name text, hash text, location text )')

    cur.close()
    conn.commit()

# Load existing hashes to prevent duplicate processes
def queryExistingHashes():

    names = []

    # Pull data
    curr = conn.cursor()
    curr.execute('SELECT name from pHash')

    results = curr.fetchmany(250)
    while results is not None:
        names = names + results
        results = curr.fetchone()

    curr.close()

    return names

# Map the file names to id/hash tuples and persist to Postgres
def genHashes(root, files):

    curr = conn.cursor()

    for i, file in enumerate(files):
        
        name = path.basename(file)
        (id, ext) = path.splitext(name)
        location = file.removeprefix(root)

        try:
            image_hash = imagehash.dhash(Image.open(file))
            hash = str(image_hash)
            print( f'.. ==> {i}/{len(files)} => {file} ==>  {hash}')

            curr.execute('insert into pHash(id, name, hash, location) values(%s,%s,%s, %s)', (id, name, hash, location))
        except Exception as e:
            print( f' ==> exception processing {file}')


    curr.close()
    conn.commit()

def importHashes(disk):
    # DB Setup
    createHashTable()             # Make sure the table exists
    hashes = queryExistingHashes()   # Get a list of files that have already been processed

    directory = path.abspath( path.join( disk, 'education/data/comic-vine/covers' ) )

    # Get all files in the CV cover directory
    files = contents(directory)

    # Filter out just the covers
    all_covers = [x for x in files if x.endswith('jpg') and not 'AppleDouble' in x]

    # Grab the existing hash list and find what
    new_covers = [ x for x in all_covers if not path.basename(x) in hashes ]

    # New files! Let's go!
    genHashes(directory, new_covers)

# Create the parser
my_parser = argparse.ArgumentParser(description='Pull comic vine data from the specified disk and build all necessary postgres tables. ')

# Add the arguments
my_parser.add_argument('--disk',  dest='disk',  help='Disk containing data (Example: /Volumes/Storage, path data added later.)')

args = my_parser.parse_args()

if  args.disk is None:
    print( 'Missing command line arguments. Run program with -h for feedback on necessary parameters.')
    exit(-1)

if not path.exists(args.disk):
    print(f'disk directory not found {args.disk}')
    exit(-2)

if not path.exists( path.join(args.disk, 'education')):
    print(f'Comic vine directory not found {args.disk}/education')
    exit(-3)



importHashes(args.disk)
importIssues(args.disk)
importVolumes(args.disk)

