'''
Postgres queries
'''

import psycopg2
import psycopg2.extras

conn = psycopg2.connect(
    host="localhost",
    database="overstreet",
    user="postgres",
    password="admin")

# Return information for a given issue ID
def summary(id):
    sql = ("select "
        "p.id, p.hash, "
        "ci.name, ci.description, ci.image, ci.month,  ci.issue_number, ci.url, ci.cover_date, "
        "cv.id as volume_id, cv.name as volume_name, cv.publisher, cv.start_year as volume_start, "
        "cv.image as volume_image, cv.url as volume_url, cv.count_of_issues as volume_count_of_issues "
        "from phash as p "
    "left outer join ComicVineIssues as ci on (p.id = ci.id) "
    "left outer join ComicVineVolumes as cv on (cv.id = ci.volume_id) "
    f"where p.id = '{id}'")

    cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor) # Return results a dict

    data = cursor.execute(sql)

    matches = []

    results = cursor.fetchone()
    return results

# Return information for a given issue / volume pair
def issueSummary(volume_id, issue_number):
    sql = ("select "
        "p.id, p.hash, "
        "ci.name, ci.description, ci.image, ci.month,  ci.issue_number, ci.url, ci.cover_date, "
        "cv.id as volume_id, cv.name as volume_name, cv.publisher, cv.start_year as volume_start, "
        "cv.image as volume_image, cv.url as volume_url, cv.count_of_issues as volume_count_of_issues "
        "from phash as p "
    "left outer join ComicVineIssues as ci on (p.id = ci.id) "
    "left outer join ComicVineVolumes as cv on (cv.id = ci.volume_id) "
    f"where ci.issue_number = '{issue_number}' "
    f"and ci.volume_id = '{volume_id}'")

    cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor) # Return results a dict

    data = cursor.execute(sql)

    matches = []

    results = cursor.fetchone()
    return results

# Return all hashes
def hashes():
    
    print( f' ==> Loading hash table')

    cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor) # Return results a dict

    sql =  ("select "
        "p.id, p.hash, "
        "ci.name, ci.description, ci.image, ci.month,  ci.issue_number, ci.url, ci.cover_date, "
        "cv.id as volume_id, cv.name as volume_name, cv.publisher, cv.start_year as volume_start, "
        "cv.image as volume_image, cv.url as volume_url, cv.count_of_issues as volume_count_of_issues "
        "from phash as p "
    "left outer join ComicVineIssues as ci on (p.id = ci.id) "
    "left outer join ComicVineVolumes as cv on (cv.id = ci.volume_id) ")

    cursor.execute(sql)

    records = []

    results = cursor.fetchmany(500)
    while results:
        records = records + results
        results = cursor.fetchmany(500)

    cursor.close()

    print( f' {len(records)} <== loaded')

    return records
