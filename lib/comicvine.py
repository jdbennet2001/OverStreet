'''
Utility functions centered around the comic vine database
'''
from os import path, mkdir, listdir
from datetime import datetime
from time import sleep
from dateutil.relativedelta import relativedelta

import requests
import json

from lib.contents import contents

from redis import Redis

rs = Redis()

'''
Return all issue data for a given month 
'''
def issue_data(month, api_key):

    PAGE_SIZE = 100
    offset = 0

    results = []

    expected_results = 1e6
    

    url = "http://comicvine.gamespot.com/api/issues"

    payload = ""
    headers = { 'user-agent' : 'insomnia/2020.4.2' }

    while (len(results) < expected_results):

        querystring = {"api_key": api_key,"resource":"issue","format":"json","filter":f'cover_date:{month}-01|{month}-31', "offset": offset}

        response = requests.request("GET", url, data=payload, headers=headers, params=querystring)

        assert response.status_code  == 200

        payload = json.loads(response.text)

        expected_results = payload['number_of_total_results']
        results = results + payload['results']
        offset = offset + PAGE_SIZE

        print( f'{len(results)}, for offset {offset}')

    return results


'''
Return all issue data for a given month 
'''
def volume_data(month, api_key):

    PAGE_SIZE = 100
    offset = 0

    results = []

    expected_results = 1e6
    

    url = "http://comicvine.gamespot.com/api/volumes"

    payload = ""
    headers = { 'user-agent' : 'insomnia/2020.4.2' }

    while (len(results) < expected_results):

        querystring = {"api_key":api_key, "format":"json","filter":f'date_added:{month}-01|{month}-31', "offset": offset}

        response = requests.request("GET", url, data=payload, headers=headers, params=querystring)

        assert response.status_code  == 200

        payload = json.loads(response.text)

        expected_results = payload['number_of_total_results']
        results = results + payload['results']
        offset = offset + PAGE_SIZE

        sleep(15)   #Support rate limiting

        print( f'{len(results)}, of {expected_results} results')

    return results

'''
Return all (mising) covers
'''
def download_covers(issues, covers_dir):

    covers = listdir(covers_dir) if path.exists(covers_dir) else []

    for i, issue in enumerate(issues):

        source = issue['image']['medium_url']
        target = path.join(covers_dir, f"{issue['id']}.jpg")

        if  path.basename(target) in covers:
            print(f"==> {i}/{len(issues)} : {covers_dir} ==> {issue['volume']['name']}, #{issue['issue_number']} ==> exists")
        elif path.exists(target):
            print(f"==> {i}/{len(issues)} : {covers_dir} ==> {issue['volume']['name']}, #{issue['issue_number']} ==> skipped")
        else:
            print( f"==> {i}/{len(issues)} : {covers_dir} ==> {issue['volume']['name']}, #{issue['issue_number']} ==> {path.basename(target)}")
            download_image( source, target )
            # sleep(2)       # Rate limiting to avoid overloading

# Download an image to disk
def download_image(source, target):

    directory = path.dirname(target)

    if  not path.exists(directory):
        mkdir(directory)

    r = requests.get(source, allow_redirects=True)
    open(target, 'wb').write(r.content)

'''
Return all story arcs
'''


'''
Download a fresh set of story arc data
'''
def story_arc_list(directory, api_key):

    story_arcs_file = path.join(directory, 'story_arcs/story_arcs.json')
    
    # Sanity check, data already exists. Don't download a second time
    (data, exists) = loadJSON(story_arcs_file, allowCache=True)
    if exists: # Data already on disk, just return
        return data

    url = "http://comicvine.gamespot.com/api/story_arcs"
    data =  comic_vine_results(url, api_key)
    saveJSON(story_arcs_file, data, allowCache=True)

    return data

'''
Download the details for known story arcs
'''
def story_arc_details(directory, story_arcs, api_key):

    story_arcs_file = path.join(directory, 'story_arcs/story_arc_details.json')

    (details, exists) = loadJSON(story_arcs_file, default={}, allowCache=True)

    # Filter out known stories
    arcs = [x for x in story_arcs if str(x['id']) not in details]
    
    # Download new information
    for i, arc in enumerate(arcs):
        id = arc['id']
        print( f'==> processing arc {i}/{len(arcs)} (of {len(story_arcs)}) ==> id {id}')
        data =  comic_vine_results(f'http://comicvine.gamespot.com/api/story_arc/{id}', api_key)
        details[id] = data

        # save in memory, just to handle the inevitable reboot
        cacheJSON(story_arcs_file, details)    

    # Save to disk.. and we're done..
    saveJSON(story_arcs_file, details)

    return details
    
    
   
def comic_vine_results(url, api_key, query={}, timeout=7.5):
    PAGE_SIZE = 100
    offset = 0

    results = []

    expected_results = 1e6

    queryAuth = {'api_key': api_key, 'format' : 'json'} # Keep auth / metadata separate to keep the logs clean

    headers = { 'user-agent' : 'insomnia/2020.4.2' }

    while (len(results) < expected_results):

        query.update({'offset': offset}) 
        
        response = requests.request("GET", url, data='', headers=headers, params={**query, **queryAuth})

        assert response.status_code  == 200

        payload = json.loads(response.text)

        expected_results = payload['number_of_total_results']

        data = payload['results']

        results = data if (type(data) is dict) else results + data

        # Sanity check, got a single result back
        if type(data) is dict:
            print( f'  ==> comicvine ==> {url}  : {json.dumps(query)} ==> (dict)')    
            expected_results = 1 # No more data...
        else:
            print( f'  ==> comicvine ==> {url}  : {json.dumps(query)} ==> (list) ==> {len(results)}, of {expected_results} results')
            offset = offset + PAGE_SIZE

        sleep(timeout) #Rate limiting...


    return results

'''
Load JSON from disk
@return {data (disk or default), flag (file exists)}
'''
def loadJSON(location, default=[], allowCache=False):
    
    print( f'==> loading ==> {location}')

    if allowCache and rs.exists(location):
        print( f'  <== cache <== {location}')
        data = rs.get(location)
        return (json.loads(data), True)

    if not path.exists(location):
        print( f'  <== default(s) <== {json.dumps(default)}')
        return (default, False)

    with open(location, 'r') as infile:
        data = json.load(infile)    
    print( f'  <== disk <== {location}')
    return (data, True)

def cacheJSON(location, data):
    print( f'  ==> caching ==> {location}')
    rs.set(location, json.dumps(data))
    print( f'  <== done')

def saveJSON(location, data, allowCache=False):

    if allowCache: # Dump data to local cache to help with error detection / performance
        print( f'==> caching ==> {location}')
        rs.set(location, json.dumps(data))

    print( f'==> writing ==> {location}')
    with open(location, 'w') as outfile:
        json.dump(data, outfile, indent=4)   

    print( f'<== done')

# Generate a list of months covered by the comicvine database
def timespan():

    months = []

    # (eg: March 31st->29th Feb an July 31st->June 30th)
    month = datetime.now() - relativedelta(months=1)

    # Most of the data is guaranteed to be there. Just check the last year.
    while month > datetime(2020, 1 ,1):
        months.append( month.strftime('%Y-%m') )
        month = month - relativedelta(months=1)

    return months



# ComicVine data is keep on the network file server. Sync that with the 'source of truth' prior to updating the database system
def sync(directory, apikey):

    history = timespan()

    print( f'==> Checking missing data ==> months')

    months = [x for x in history if not path.exists( path.join(directory, f'issues/{x}.json'))]

    for month in months:

        print( f'==> {month} ==> issues ')

        issues = issue_data(month, apikey)

        issue_file =  path.join(directory, f'issues/{month}.json')
        with open(issue_file, 'w') as outfile:
            json.dump(issues, outfile, indent=4)

            sleep(60)

    
    # Download missing volume data
    volumes = [x for x in months if not path.exists( path.join(directory, f'volumes/{x}.json'))]
    print(f'Syncing volumes {volumes}')

    for volume in volumes:
        print(f'==> {volume} ==> volumes')
        data = volume_data(volume, apikey)

        file =  path.join(directory, f'volumes/{volume}.json')
        print(f"==> {volume} ==> {file}")

        with open(file, 'w', encoding='utf-8') as outfile:
            json.dump(data, outfile, indent=4)

 
    # Download missing covers
    for month in history:

        issue_file =  path.join(directory, f'issues/{month}.json')
        
        if rs.exists(issue_file): # Sanity check, avoid processing months that have already been flagged
            print( f' ==> skipping ==> {issue_file} ==> covers')
            continue
        else:
            print( f' ==> checking ==> {issue_file} ==> covers')

        with open(issue_file, 'r', encoding='utf-8') as infile:
            issues = json.load(infile, )
        
        download_covers(issues, path.join(directory, f"covers/{month}") )

        rs.set(issue_file, json.dumps(issues)) #Month has been processed.. save that information to prevent duplicate processing.

    # Find all known story arcs
    story_arcs = story_arc_list(directory, apikey)

    # And make sure we have records for each
    story_arc_data = story_arc_details(directory, story_arcs, apikey)

    return months




