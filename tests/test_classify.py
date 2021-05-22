'''
Classify an image's hash against the database
(Requires all the database tables)
'''

import psycopg2
import psycopg2.extras

'''
 Return potential matches for a comic.
 @param hash value for comic cover
'''
def hash_matches(hash_id, cursor):

    sql = ("select "
        "p.id, p.hash, "
        "ci.name, ci.description, ci.image, ci.month,  ci.issue_number, ci.url, ci.cover_date, "
        "cv.name as volume_name, cv.publisher, cv.start_year as volume_start, "
        "cv.image as volume_image, cv.url as volume_url, cv.count_of_issues as volume_count_of_issues "
        "from phash as p "
    "left outer join ComicVineIssues as ci on (p.id = ci.id) "
    "left outer join ComicVineVolumes as cv on (cv.id = ci.volume_id) "
    f"where p.id = '{hash_id}'")

    data = cursor.execute(sql)

    matches = []

    results = cursor.fetchmany(250)
    while results is not None:
        matches = matches + results
        results = cursor.fetchone()
    

    return results


# Can use an image's hash to generate a set of potential matches against the database
def test_image_classify():
    
    conn = psycopg2.connect(
        host="localhost",
        database="overstreet",
        user="postgres",
        password="admin")

    cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor) # Return results a dict

    # Look up the comic in the database
    matches = hash_matches('39172', cur)

    cur.close()

    # Got one result back
    assert len(matches) == 1

