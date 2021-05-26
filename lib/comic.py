'''
cb* utilities
'''
import zipfile
import tempfile
import json
from redis import Redis

from unrar import rarfile
from os import path, listdir, remove, stat, rename

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
        raise( f'No cover image found for {archive}, pages are {files}')
  
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

def has_tag(path_to_archive):

    if path_to_archive.endswith('cbz'):
        pagelist = _pages_zip(path_to_archive)
    elif path_to_archive.endswith('cbr'):
        pagelist = _pages_rar(path_to_archive)

    return TAG_FILE in pagelist

def add_tag(tag_data, path_to_archive):

    with tempfile.TemporaryDirectory() as tmpdirname:
        path_to_tmp_file = path.join(tmpdirname, TAG_FILE)

        with open(path_to_tmp_file, 'w') as outfile:
            json.dump(tag_data, outfile)

        print( f'==> tag ==> {path_to_tmp_file} ==> {path_to_archive}')
        insert( path_to_tmp_file, path_to_archive)
        
        

def insert( path_to_file, path_to_archive):

    # Implicitly transform cbr files to cbz as they're being tagged
    if path_to_archive.endswith('cbr'):
        path_to_archive = convert_to_zip(path_to_archive)

    if path_to_archive.endswith('cbz'):
        zip = zipfile.ZipFile(path_to_archive,'a')
        zip.write(path_to_file, path.basename(path_to_file))
        zip.close()

    else:
        raise Exception(f'Unsupported archive type for file insert: {path_to_archive}') 

 
def convert_to_zip(path_to_archive, remove_old=True):

    if path_to_archive.endswith('cbz'):
        return path_to_archive # Nothing to do...

    cbr_size = stat(path_to_archive).st_size
    target_zip = path_to_archive.replace('cbr', 'cbz')

    print( f' ==> converting {path_to_archive} ({humanbytes(cbr_size)})==> to cbz')

    # Make temporary directory
    with tempfile.TemporaryDirectory() as tmpdirname:

        rar = rarfile.RarFile(path_to_archive)

        rar.extractall(tmpdirname)

        files = contents(tmpdirname)
        files.sort()

        print( f' ==> extracted {len(files)} files to ==> {tmpdirname}')

        zip = zipfile.ZipFile(target_zip,'w')
        for i, file in enumerate(files):
            print(f' <==  {path.basename(target_zip)} <== adding <== {i}/{len(files)} <== {path.basename(file)}')
            path_to_file = path.join(tmpdirname, file)
            zip.write(path_to_file, file)
        zip.close()

    cbz_size = stat(target_zip).st_size
    print( f' <== done {target_zip} ({humanbytes(cbz_size)})')
    

    # Check that the new file is roughly the same size as the old one
    delta = (abs(cbz_size - cbr_size) / cbr_size)

    if (delta > 0.1):
        raise Exception(f'Unable to convert {path_to_archive}, input size {cbr_size}, output {cbz_size}')

    # Delete the input file
    if remove_old:
        print(f' ==> removing ==> {path_to_archive}, size delta => {str(round(delta*100, 2))}%')
        remove(path_to_archive)

    return target_zip

def tag_perf(key):
    data = rs.hget(REDIS_DATA, key)
    entry =  json.loads(data)

    location = entry['location']
    match = entry['match']

    # We only support cbz files
    if location.endswith('cbr'):
        location = convert_to_zip(location)

    # Cover names have a set format
    path_to_target = path.join( path.dirname(location), target_name(match) )

    print( f' ==> rename {location} ==> {path_to_target}')

    rename( location, path_to_target)

    add_tag(match, path_to_target)

    return {'from' : location, 'to' : path_to_target}

# What should this archive be called?
def target_name(metadata):

    volume_name = metadata['volume_name']
    issue_number = str(metadata['issue_number']).rjust(3, '0')
    name = metadata['name']
    cover_date = metadata['cover_date']

    cname = f"{volume_name} #{issue_number} ({metadata['cover_date']})"
    target = f"{cname} - {name}" if name else cname
    return f'{target}.cbz'
 
