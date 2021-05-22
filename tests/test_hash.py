from PIL import Image
from os import path, listdir

import imagehash   
import json

'''
Can generate a hash signature for a comic cover
'''
def test_hash():

    test_path = path.dirname(path.realpath(__file__))
    data_path = path.join(test_path, 'data/flash-91-cover.jpg')


    # Generate a hash for Flash 91 cover image
    cover_hash = imagehash.phash(Image.open(data_path))

    assert hash is not None

'''
Find similar image in a directory by comparing the perceptual hash values
'''
def test_image_match():

    test_path = path.dirname(path.realpath(__file__))
    data_path = path.join(test_path, 'data/flash-91-cover.jpg')
    covers_path = path.join(test_path, 'data/covers')

    # Generate a hash for Flash 91 cover image
    target_hash = imagehash.phash(Image.open(data_path))
    target_key = str(target_hash)

    hashes = {'target' : target_key}

    # Check flash 91 against all images in directory
    for cover in listdir(covers_path):
        cover_path = path.join(covers_path, cover)
        cover_hash = imagehash.phash(Image.open(cover_path))
        match = cover_hash == target_hash
        hashes[cover] = str(cover_hash) # pHash values are arrays of data, but can be converted to hex codes for storage

    # Found a match
    assert hashes['39172.jpg'] == target_key

    # Save the data for later inspection
    with open('data.json', 'w') as fp:
        json.dump(hashes, fp, indent=4)
