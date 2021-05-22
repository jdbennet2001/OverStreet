import argparse
import sys

from os import path

proj_path = path.abspath('.')
sys.path.append(proj_path)  # VSCode hackery, ensure project relative imports work

proj_path = path.abspath('..')
sys.path.append(proj_path)  # VSCode hackery, ensure project relative imports work

from lib.comicvine import sync

def main( comicVine, api_key ):
    sync( comicVine, api_key)


# Create the parser
my_parser = argparse.ArgumentParser(description='Basic classification code')

# Add the arguments
my_parser.add_argument('--comicvine',  dest='comicvine',  help='ComicVine directory')
my_parser.add_argument('--apikey', dest='apikey', help='ComicVine API Key')

args = my_parser.parse_args()

if args.comicvine is None or args.apikey is None:
    print( 'Missing arguments, run with -h for help')
    exit(-1)


main( args.comicvine, args.apikey)