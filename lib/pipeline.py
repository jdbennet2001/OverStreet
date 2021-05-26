'''
Functions that used to generate model data and to evaluate new samples
'''

import io
import imagehash

from PIL import Image
from lib.comic import extract_cover

# Calculate the normalized Hamming distance between two strings.
def hamming(s1, s2):
    
    assert len(s1) == len(s2)
    return float(sum(c1 != c2 for c1, c2 in zip(s1, s2))) / float(len(s1))

# Hash comparision is slow. Check for common tokens between two strings to filter out disjoint strings.
def intersection(s1, s2):

    if not s2 or not s1: # Sanity check, empty strings
        return False

    # Remove short tokens from the first string, just to toss out filler words
    tokens1 = [x for x in s1.split(' ') if len(x) > 3]
    set1 = set( tokens1 )

    tokens2 = s2.split(' ')
    overlap = set1.intersection(tokens2)

    if len(overlap) > 0:
        return True
    else:
        return False

def cover_hash(location):

    image_data = extract_cover(location)
    img = Image.open(io.BytesIO(image_data))

    cover_img_hash = imagehash.dhash(img)
    cover_hash = str(cover_img_hash)
    return cover_hash

