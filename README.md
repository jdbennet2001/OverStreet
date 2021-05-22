# OverStreet


Comics classification code that uses a mix of image algorithms and ML to identify comic archives to their corresponding ComicVine entries and file them.

## Command Line Scripts
| Script   | Description                                      | Usage |
|-------------|------------------------------------------------------------------------------------------------|-------------------------------------------------------------|
| cv-update   | Download latest updates from ComicVine to a set directory                                      | cv-update --dir /Volumes/Storage/education/data/comic-vine/ |
| db-update   | Walk ComicVine 'source of truth' system, rebuilding the database used for image classification | db-update --dir /Volumes/Storage/education/data/comic-vine/ |
| cb-classify | Walk a directory containing comics and generate a JSON file outlining ML matches for later use | cb-classify --dir ..  -out ...          |


