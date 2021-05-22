'''
Test database calls
'''

import sys

from os import path, remove

proj_path = path.abspath('.')
sys.path.append(proj_path)  # VSCode hackery, ensure project relative imports work

proj_path = path.abspath('..')
sys.path.append(proj_path)  # VSCode hackery, ensure project relative imports work

from lib.db import issueSummary

def test_issue_data():
    data = issueSummary(23194, 1)
    
    assert data['issue_number'] == '91'


