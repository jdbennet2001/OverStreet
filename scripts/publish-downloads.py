'''
Convert all .cbr files in a given directory to .cbz
'''
import argparse
import filetype
import sys
import shutil
from os import path, makedirs

proj_path = path.abspath('.')
sys.path.append(proj_path)  # VSCode hackery, ensure project relative imports work

proj_path = path.abspath('..')
sys.path.append(proj_path)  # VSCode hackery, ensure project relative imports work

from lib.contents import contents
from lib.comic import convert_to_zip

# Convert RAR files to CBZ
def convert(path_to_directory):
    files = contents(path_to_directory)

    files = [x for x in files if x.endswith('cbr')]

    for file in files:
        convert_to_zip(file)

# Move files to external storage
def move(path_to_directory, path_to_target):
    files = contents(path_to_directory)
    files = [x for x in files if x.endswith('cbz')]

    for i, file in enumerate(files):
        relpath = path.relpath(file, path_to_directory)
        target = path.join( path_to_target, relpath)
        target = path.abspath(target)
        
        print( f' ==> {i}/{len(files)} ==>  {relpath} ==> {target}')
        makedirs( path.dirname(target), exist_ok=True)
        shutil.move(file, target)



def type(path_to_archive):
    try:
         extension = filetype.guess(path_to_archive).extension
         return extension
    except Exception as e:
        print( f' ==> {path_to_archive} ==> Invalid File Type')
        return None

# Create the parser
my_parser = argparse.ArgumentParser(description='Convert files and publish downloads to private cloud ')

# Add the arguments
my_parser.add_argument('--directory',  dest='directory',  help='Directory to be converted.')
my_parser.add_argument('--target', dest='target', help='Target directory to move files to')

args = my_parser.parse_args()

DEFAULT_DIRECTORY = "C:/Users/Jon Bennett/Downloads"
DEFAULT_TARGET = "z:/comics/on-deck"


if  args.directory is None:
    print( f'Missing command line arguments (directory). Using defaults {DEFAULT_DIRECTORY}')
    args.directory = DEFAULT_DIRECTORY

if  args.target is None:
    print( f'Missing command line arguments (target). Using defaults {DEFAULT_TARGET}')
    args.target = DEFAULT_TARGET

if not path.exists(args.directory):
    print(f'Directory {args.directory} not found')
    exit(-2)

if args.target is not None and not path.exists(args.target):
    print( f'Target {args.target} not found')
    exit(-3)

convert(args.directory)

if args.target is not None:
    move(args.directory, args.target)