from os import listdir, path

'''
Recursively walk a set of directories and return list of all files
'''
def contents(directory):

    print(f'.. parsing {directory}')

    ls = []

    dir_list = listdir(directory)

    # Filter out hidden files
    dir_list = [x for x in dir_list if not x.startswith('.')]

    dir_list = [path.join(directory, x) for x in dir_list]

    # Store file data as <pathname> : <size in bytes>
    files = [x for x in dir_list if path.isfile(x)]
    for i, file in enumerate(files):
        ls.append(file)

    directories = [x for x in dir_list if path.isdir(x)]

    # Recursively walk child directories building a full list of files
    for i, directory in enumerate(directories):
        children = contents(directory)
        ls = ls + children

    return ls