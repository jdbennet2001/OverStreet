'''
Extract image from file
'''
import zipfile
import imagehash   
import io

from PIL import Image
from os import path


def test_extract_cover():

    # Find the archive
    test_path = path.dirname(path.realpath(__file__))
    data_path = path.join(test_path, 'data/The Flash #091 ( 1994-06-01) - Out of Time.cbz')
    data_path = path.abspath(data_path)

    # Extrat the first file
    archive = zipfile.ZipFile(data_path, 'r')
    names = archive.namelist()
    name = names[0]
    imgdata = archive.read(name)

    # Should be getting raw bytes back
    assert type(imgdata) == bytes

    pass

# Should be able to get a phash for the archive
def test_extract_phash():

    # Find the archive
    test_path = path.dirname(path.realpath(__file__))
    data_path = path.join(test_path, 'data/The Flash #091 ( 1994-06-01) - Out of Time.cbz')
    data_path = path.abspath(data_path)

    # Extrat the first file
    archive = zipfile.ZipFile(data_path, 'r')
    names = archive.namelist()
    name = names[0]
    image_data = archive.read(name)

    img = Image.open(io.BytesIO(image_data))
    img.save('out.jpg', 'PNG')

    cover_img_hash = imagehash.phash(img)
    cover_hash = str(cover_img_hash)
    
    assert cover_hash == 'e34e986858672d9e'




