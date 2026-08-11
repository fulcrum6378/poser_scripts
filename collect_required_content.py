import os
from typing import Set, Tuple


def collect_pz3_required_paths(
        pz3_path: str = poser.Scene().DocumentPath(),
        silent: bool = True,
) -> Tuple[Set[str], bool]:
    """index all path references in the PZ3 file"""

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


def find_file_in_runtime_paths(reference: str, required_paths: Set) -> bool:
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
        print(f'`{reference}` was not found in any content paths you mentioned!')
        return False
    return True
