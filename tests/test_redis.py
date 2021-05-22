import json
from os import path, getcwd


def test_find_match():

    data_location = path.join( getcwd(), 'tests/data/hash-matches.json')

    with open(data_location, "r") as read_file:
        records = json.load(read_file)

    volume_id = 3790
    issue_number = 91

    # Correctly mark issues as match/no match
    for record in records:
        summary = record['summary']
        record['match'] = (record.get('summary').get('volume_id') == str(volume_id) and record.get('summary').get('issue_number') == str(issue_number))

    match = any(record['match'] == True for record in records)

    assert match

    



