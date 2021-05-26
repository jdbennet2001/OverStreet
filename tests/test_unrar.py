from os import path, mkdir, rename, listdir, stat, remove
import sys

# Note, unrar requires a seperate installation documented here: https://pypi.org/project/unrar/
from unrar import rarfile
from shutil import rmtree, make_archive

import time

proj_path = path.abspath('.')
sys.path.append(proj_path)  # VSCode hackery, ensure project relative imports work

proj_path = path.abspath('..')
sys.path.append(proj_path)  # VSCode hackery, ensure project relative imports work

from lib.comic import convert_to_zip

import imagehash   
import io

from PIL import Image

# Can list files in a given archive
def test_unrar():

    # Find the archive
    test_path = path.dirname(path.realpath(__file__))
    data_path = path.join(test_path, 'data/Injustice - Year Zero 006 (2020) (digital) (Son of Ultron-Empire).cbr')
    data_path = path.abspath(data_path)

    rar = rarfile.RarFile(data_path)

    files = rar.namelist()

    assert len(files) > 0 # Got some files!

    pass

# Generate a cbz file from a cbr source
def test_covert():
    
    # Find the archive
    test_path = path.dirname(path.realpath(__file__))
    cbr_path = path.join(test_path, 'data/Injustice - Year Zero 006 (2020) (digital) (Son of Ultron-Empire).cbr')
    cbr_path = path.abspath(cbr_path)

    # Gen a test directory
    cbz_path = convert_to_zip(cbr_path, remove_old=False)

    cbz_size = stat(cbz_path).st_size
    cbr_size = stat(cbr_path).st_size

    assert cbz_size == approx(cbr_size, rel=0.1) # allow 10% deviation between archive types

    # Clean up
    remove(cbz_path)

    pass

def test_cover_hashing():

    # Find the archive
    test_path = path.dirname(path.realpath(__file__))
    cbr_path = path.join(test_path, 'data/Injustice - Year Zero 006 (2020) (digital) (Son of Ultron-Empire).cbr')
    cbr_path = path.abspath(cbr_path)

    rar = rarfile.RarFile(cbr_path)

    files = rar.namelist()
    
    images = [x for x in files if x.lower().endswith('jpg') or x.lower().endswith('jpeg') or x.lower().endswith('png') or x.lower().endswith('gif')]
    images.sort()

    cover_file = images[0]

    image_data = rar.read(cover_file)

    img = Image.open(io.BytesIO(image_data))
    img.save('out.jpg', 'PNG')

    cover_img_hash = imagehash.phash(img)
    cover_hash = str(cover_img_hash)

    pass



