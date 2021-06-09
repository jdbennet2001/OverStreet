'''
cb* utilities
'''
import zipfile
import tempfile
import json
import filetype

from pathlib import PurePosixPath
from redis import Redis

from unrar import rarfile
from os import path, stat, remove, stat, rename, utime

from lib.bytes import humanbytes
from lib.contents import contents

rs = Redis()

REDIS_DATA = 'score-data'

IMAGE_TYPES = ['jpg', 'jpeg', 'png', 'gif']

def extract_cover(archive):

    if archive.endswith('cbz'):
        return _extract_zip_cover(archive)
    elif archive.endswith('cbr'):
        return _extract_rar_cover(archive)
    else:
        raise Exception(f'Invalid archive {archive}')

# Extract the first page of a RAR file
def _extract_rar_cover(archive):

    rar = rarfile.RarFile(archive)

    # Pull a list of all files
    files = rar.namelist()
    
    # Format the list as images, sorted in descending order
    images = [x for x in files if x.lower().endswith('jpg') or x.lower().endswith('jpeg') or x.lower().endswith('png') or x.lower().endswith('gif')]
    images.sort()

    # What the what?
    if not images:
        raise Exception( f'No cover image found for {archive}, pages are {files}')
  
    # Extract and return the first page
    image_data = rar.read(images[0])
    return image_data

# Extract the first page of a ZIP file
def _extract_zip_cover(archive):
    archive = zipfile.ZipFile(archive, 'r')
    files = archive.namelist()

    # Format the list as images, sorted in descending order
    images = [x for x in files if x.lower().endswith('jpg') or x.lower().endswith('jpeg') or x.lower().endswith('png') or x.lower().endswith('gif')]
    images.sort()

    if not images:
        raise( f'No cover image found for {archive}, pages are {files}')

    # Return the first page
    image_data = archive.read(images[0])
    return image_data

# Return the number of pages in the archive
def pages(archive):

    if archive.endswith('cbz'):
        pagelist = _pages_zip(archive)
    elif archive.endswith('cbr'):
        pagelist = _pages_rar(archive)

    return len(pagelist)

# Returns a sorted list of all pages in a ZIP archive
def _pages_zip(archive):
    archive = zipfile.ZipFile(archive, 'r')
    names = archive.namelist()

    images = [x for x in names if x.lower().endswith('jpg') or x.lower().endswith('jpeg') or x.lower().endswith('png') or x.lower().endswith('gif')]
    images.sort()

    return images

# Returns a sorted list of all pages in a RAR archive
def _pages_rar(archive):

    rar = rarfile.RarFile(archive)

    # Pull a list of all files
    files = rar.namelist()
    
    # Format the list as images, sorted in descending order
    images = [x for x in files if x.lower().endswith('jpg') or x.lower().endswith('jpeg') or x.lower().endswith('png') or x.lower().endswith('gif')]
    images.sort()

    return images

TAG_FILE = 'tags.json'
HASH_FILE = 'pending.json'

def has_tag(path_to_archive):

    # Assume ZIP archives
    with zipfile.ZipFile(path_to_archive, 'r') as myzip:
        pagelist = myzip.namelist()

        return TAG_FILE in pagelist or HASH_FILE in pagelist

def add_tag(tag_data, path_to_archive, tag_file=TAG_FILE):

    with tempfile.TemporaryDirectory() as tmpdirname:
        path_to_tmp_file = path.join(tmpdirname, tag_file)

        with open(path_to_tmp_file, 'w') as outfile:
            json.dump(tag_data, outfile, indent=4)

        print( f' ==> tag ==> {path.basename(path_to_tmp_file)} ==> {path_to_archive}')
        insert( path_to_tmp_file, path_to_archive)
        

def get_tags(path_to_archive):

    with zipfile.ZipFile(path_to_archive, 'r') as myzip:
        tagdata = myzip.read(TAG_FILE)

    return json.loads(tagdata)


def insert( path_to_file, path_to_archive):

    try:
        zip = zipfile.ZipFile(path_to_archive,'a')
        zip.write(path_to_file, path.basename(path_to_file))
        zip.close()
    except Exception as e:
        print( f'Exception tagging {path_to_archive}, {e}')
    
 
def convert_to_zip(path_to_archive, remove_old=True):

    path_to_archive = path.abspath(path_to_archive)
    (stem, ext) = path.splitext(path_to_archive)

    tmp_zip = f'{stem}._zip' 
    target_zip = f'{stem}.cbz'
  
    cbr_size = stat(path_to_archive).st_size
  
    print( f' ==> converting {path_to_archive} ({humanbytes(cbr_size)})==> to cbz')

    # Make temporary directory
    with tempfile.TemporaryDirectory() as tmpdirname:

        rar = rarfile.RarFile(path_to_archive)

        rar.extractall(tmpdirname)

        files = contents(tmpdirname)
        files.sort()

        print( f' ==> extracted {len(files)} files to ==> {tmpdirname}')

        zip = zipfile.ZipFile(tmp_zip,'w')
        for i, file in enumerate(files):
            print(f' <==  {path.basename(tmp_zip)} <== adding <== {i}/{len(files)} <== {path.basename(file)}')
            path_to_file = path.join(tmpdirname, file)
            zip.write(path_to_file, path.basename(file))
        zip.close()

    cbz_size = stat(tmp_zip).st_size
    print( f' <== done {tmp_zip} ({humanbytes(cbz_size)})')

    # Check that the new file is roughly the same size as the old one
    delta = (abs(cbz_size - cbr_size) / cbr_size)
    delta_percent = str(round(delta*100, 2))

    if (delta > 0.50):
        raise Exception(f'Unable to convert {path_to_archive},  {delta_percent}% difference in file sizes')

    # Delete the input file
    remove(path_to_archive)
    rename(tmp_zip, target_zip)

    return target_zip



# What should this archive be called?
def target_name(metadata):

    volume_name = metadata['volume_name']
    issue_number = str(metadata['issue_number']).rjust(3, '0')
    name = metadata['name']
    cover_date = metadata['cover_date']

    cname = f"{volume_name} #{issue_number} ({metadata['cover_date']})"
    target = f"{cname} - {name}" if name else cname
    target = target.replace('/', '-')
    target = target.replace('?', '')
    target = target.replace(':', ' ')
    return f'{target}.cbz'
 
def type(path_to_archive):
    try:
         extension = filetype.guess(path_to_archive).extension
         return extension
    except Exception as e:
        print( f' ==> {path_to_archive} ==> Invalid File Type')
        return None