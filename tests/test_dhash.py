'''
Trying using a distance hash with hamming distance to determine difference between different images
'''

import sys

from os import path, remove

proj_path = path.abspath('.')
sys.path.append(proj_path)  # VSCode hackery, ensure project relative imports work

proj_path = path.abspath('..')
sys.path.append(proj_path)  # VSCode hackery, ensure project relative imports work

from lib.dbSetup import importCovers

def test_cover_imports():
    count = importCovers('/Volumes/LocalDASD/education/data/comic-vine')

    assert count > 0
