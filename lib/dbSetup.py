'''
Import data into Postgres
'''

from os import path
from PIL import Image

import imagehash 
import psycopg2



from lib.contents import contents

conn = psycopg2.connect(
    host="localhost",
    database="overstreet",
    user="postgres",
    password="admin")

# Make sure there's a table
def _gen_hash_table():

    cur = conn.cursor()

    # Drop existing table, if available
    cur.execute('drop table if exists pHash')

    # Generate new table
    cur.execute( 'CREATE TABLE IF NOT EXISTS pHash ( id text, name text, hash text, location text )')

    cur.close()
    conn.commit()

# Map the file names to id/hash tuples and persist to Postgres
def _hash_covers(root, files):

    curr = conn.cursor()

    for file in files:
        
        name = path.basename(file)
        (id, ext) = path.splitext(name)
        location = file.removeprefix(root)

        try:
            image_hash = imagehash.dhash(Image.open(file))
            hash = str(image_hash)
            print( f'.. ==> {file} ==>  {hash}')

            curr.execute('insert into pHash(id, name, hash, location) values(%s,%s,%s, %s)', (id, name, hash, location))
        except Exception as e:
            print( f' ==> exception processing {file}')


    curr.close()
    conn.commit()

# Refresh the list of cover / hash values
def importCovers(directory):
    covers_dir = path.join(directory, 'covers')
    covers = contents(covers_dir)
    covers = [x for x in covers if x.endswith('jpg')]

    # Create the local table
    _gen_hash_table()

    # Fill with hash values
    _hash_covers(directory, covers)
    
  