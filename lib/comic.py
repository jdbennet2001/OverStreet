'''
cb* utilities
'''
import zipfile
import imagehash   
import io

from unrar import rarfile
from PIL import Image

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

# Check if the directory has a pre-assigned volume ID
def hasVolume(archive):
    pass
