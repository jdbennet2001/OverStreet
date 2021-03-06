import sys

from os import path

proj_path = path.abspath('.')
sys.path.append(proj_path)  # VSCode hackery, ensure project relative imports work

proj_path = path.abspath('..')
sys.path.append(proj_path)  # VSCode hackery, ensure project relative imports work

metadata =  {
            "id": "710100",
            "hash": "d866468f9aaeaedd",
            "name": "Hunted Part 6",
            "description": "<p><em>HUNTED AFTERMATH!</em></p><p><em>The fallout from \"HUNTED\" continues to loom, and much of Peter's life is called into question.</em></p><p><em>What is left of Spider-Man after living through the harrowing hunt?!</em></p><h4>List of covers and their creators:</h4><table data-max-width=\"true\"><thead><tr><th scope=\"col\">Cover</th><th scope=\"col\">Name</th><th scope=\"col\">Creator(s)</th><th scope=\"col\">Sidebar Location</th></tr></thead><tbody><tr><td>Reg</td><td>Regular Cover</td><td>Humberto Ramos &amp; Edgar Delgado</td><td>1</td></tr><tr><td>Var</td><td>Connecting Variant Cover</td><td>Aaron Kuder &amp; Morry Hollowell</td><td>6</td></tr><tr><td>Var</td><td>Marvel Battle Lines Variant Cover (Spider-Punk)</td><td>Heejin Jeon</td><td>7, 8</td></tr><tr><td>Var</td><td>Connecting Variant Cover</td><td>Leinil Francis Yu &amp; Sunny Gho</td><td>5</td></tr><tr><td>RE</td><td>ComicXposure Exclusive Variant Cover</td><td>Lucio Parrillo</td><td>3</td></tr><tr><td>RE</td><td>ComicXposure Exclusive Virgin Variant Cover</td><td>Lucio Parrillo</td><td>4</td></tr><tr><td>2nd</td><td>Second Printing Variant Cover</td><td>Humberto Ramos &amp; Edgar Delgado</td><td>2</td></tr></tbody></table>",
            "image": "https://comicvine1.cbsistatic.com/uploads/scale_medium/6/67663/6948497-22.jpg",
            "month": "2019-07",
            "issue_number": "22",
            "url": "https://comicvine.gamespot.com/the-amazing-spider-man-22-hunted-part-6/4000-710100/",
            "cover_date": "2019-07-01",
            "volume_id": "112161",
            "volume_name": "The Amazing Spider-Man",
            "publisher": "Marvel",
            "volume_start": "2018",
            "volume_image": "https://comicvine1.cbsistatic.com/uploads/scale_medium/6/67663/6506202-01.jpg",
            "volume_url": "https://comicvine.gamespot.com/the-amazing-spider-man/4050-112161/",
            "volume_count_of_issues": 46
        }

from lib.comic import add_tag

def test_tag():

    test_path = path.dirname(path.realpath(__file__))
    path_to_file = path.join(test_path, 'data/Injustice - Year Zero 006 (2020) (digital) (Son of Ultron-Empire).cbz')
    path_to_file = path.abspath(path_to_file)

    add_tag(metadata, path_to_file)

