import sys

from os import path, remove

proj_path = path.abspath('.')
sys.path.append(proj_path)  # VSCode hackery, ensure project relative imports work

proj_path = path.abspath('..')
sys.path.append(proj_path)  # VSCode hackery, ensure project relative imports work

from web.web_app import comic

# Get an item from the queue
def test_queue():
    
    item = comic()

    assert item


