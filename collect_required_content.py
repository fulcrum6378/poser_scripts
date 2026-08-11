import math
import os
import shutil
from typing import Set, Tuple

import poser


def collect_pz3_required_paths(pz3_path: str, silent: bool = True) -> Tuple[Set[str], bool]:
    """
    Index all path references in the PZ3 file

    Note: Putting the current document path as the default value will be stored in cache and mess things up
    if you open a different document later.
    """

    all_available = True

    pz3: str = open(pz3_path, 'r').read()
    references: Set[str] = set()
    seek = 0
    while True:
        try:
            # choose the earliest path
            uc = pz3.find(':Runtime:', seek)
            lc = pz3.find(':runtime:', seek)
            if uc == -1 and lc == -1: break
            seek = uc if uc < lc or lc == -1 else lc

            # define the bounds and substring
            end = pz3.find('\n', seek)
            path = pz3[seek:end].strip()
            if path[-1] == '"': path = path[:-1]

            # add the path to the collection and prepare for the next loop
            references.add(path)
            seek += len(path)

        except Exception as e:
            print(f'Exception occurred at index {seek}')
            raise e
    pz3 = ''
    if not silent: print(f'Collected {len(references)} references from the PZ3 file.')

    # resolve the references
    required_paths: Set[str] = set()
    for reference in references:
        if not find_file_in_runtime_paths(reference, required_paths):
            all_available = False
    if not silent: print('Path resolution complete.')

    return required_paths, all_available


def find_file_in_runtime_paths(reference: str, required_paths: Set[str]) -> bool:
    path = None
    for content in poser.Libraries():
        candidate = content + reference.replace(':', os.path.sep)
        if os.path.isfile(candidate):
            path = candidate
            break
    if path is not None:
        required_paths.add(path)
    elif reference.endswith('.obj'):
        return find_file_in_runtime_paths(reference.replace('.obj', '.obz'), required_paths)
    else:
        return False
    return True


def copy_to(copy_to_path: str, required_paths: Set[str]):
    if not os.path.isdir(copy_to_path):
        os.mkdir(copy_to_path)
    for path in required_paths:
        for content_path in poser.Libraries():
            if path.startswith(content_path):
                dest = copy_to_path + path[len(content_path):]
                break
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        if not os.path.isfile(dest) or os.path.getsize(path) != os.path.getsize(dest):
            shutil.copy2(path, dest)


def convert_size(size_bytes):
    """https://stackoverflow.com/a/14822210/10728785"""
    if size_bytes == 0: return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 3)
    if s % 1 == 0: s = int(s)
    return "%s %s" % (s, size_name[i])


if __name__ == '__main__':
    dialogue = poser.DialogDirChooser(
        0,
        'Select a destination for the new Runtime...',
        os.path.join(os.environ['USERPROFILE'] + '\\Desktop\\'))
    continuum = dialogue.Show()

    if continuum:
        required_paths, all_copied = collect_pz3_required_paths(poser.Scene().DocumentPath(), silent=False)
        copy_to_path = dialogue.Path()
        copy_to(copy_to_path, required_paths)
        print(f"All the{'' if all_copied else ' other'} required files were copied.")

        # measure the size of the runtime
        total_size = 0
        for dir_path, dir_names, filenames in os.walk(os.path.join(copy_to_path, 'Runtime')):
            for filename in filenames:
                total_size += os.path.getsize(os.path.join(dir_path, filename))
        print('Total size of the Runtime:', convert_size(total_size))
