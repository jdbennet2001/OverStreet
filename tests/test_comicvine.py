import sys

from os import path, remove

proj_path = path.abspath('.')
sys.path.append(proj_path)  # VSCode hackery, ensure project relative imports work

proj_path = path.abspath('..')
sys.path.append(proj_path)  # VSCode hackery, ensure project relative imports work

from lib.comicvine import issue_data, volume_data, download_image, timespan, sync

API_KEY = "fc5d9ab899fadd849e4cc3305a73bd3b99a3ba1d"

# Check that issues data can be downloaded
def test_issue_data():
    issues = issue_data('2021-01', API_KEY)

    assert len(issues) > 0

# Can download a month's worth of volume data
def test_volume_data():
    volumes = volume_data('2021-01', API_KEY)
    assert( len(volumes) > 0 )

# Can download cover data for an issue
def test_cover_data():
    source = "https://comicvine1.cbsistatic.com/uploads/scale_medium/0/3125/157167-18058-111906-1-detective-comics.jpg"
    
    test_path = path.dirname(path.realpath(__file__))
    target = path.join(test_path, 'data/detective_1.jpg')

    # Delete old files
    if path.exists(target):
        remove(target)

    # Grab a new one
    download_image(source, target)

    
    assert path.exists(target)

    pass

# Can figure out all the months being processed
def test_timespan():

    months = timespan()

    assert '2021-02' in months

def test_sync():
    sync('/Volumes/Storage/education/data/comic-vine', API_KEY)


