import os
import poser
import subprocess
from typing import Dict, List
from zipfile import ZipFile

from commons import WINRAR
from doc_collect_required_content import print_bytes


def read_zip_contents(archive_path: str) -> List[str]:
    zf = ZipFile(archive_path, 'r')
    file_list = ''
    for entry in zf.filelist:
        if len(file_list) != 0:
            file_list += '\n'
        file_list += entry.filename
    zf.close()
    file_list = file_list.replace('/', '\\')
    exclude_prefix = spot_runtime_in_archive(file_list)
    return exclude_file_list_with_prefix(file_list, exclude_prefix)


def read_rar_contents(archive_path: str) -> List[str]:
    file_list: str = subprocess.run(
        [WINRAR, 'lb', archive_path], capture_output=True, text=True
    ).stdout
    exclude_prefix = spot_runtime_in_archive(file_list)
    return exclude_file_list_with_prefix(file_list, exclude_prefix)


def spot_runtime_in_archive(file_list: str) -> str:
    """Return the path to the Runtime directory inside a list of contents of an archive."""

    try:
        end = file_list.index('Runtime\\') + 8
    except ValueError:
        try:
            end = file_list.index('runtime\\') + 8
        except ValueError:
            raise FileNotFoundError('This archive has no Runtime directory!')
    try:
        begin = file_list[:end].rindex('\n') + 1
    except ValueError:
        begin = 0
    return file_list[begin:end]


def exclude_file_list_with_prefix(file_list: str, exclude_prefix: str) -> List[str]:
    contents: list[str] = []
    for file in file_list.split('\n'):
        file = file.lower()
        if file.startswith(exclude_prefix.lower()):
            contents.append(file[file.index('runtime\\'):])
    return contents


if __name__ == '__main__':
    file_chooser = poser.DialogFileChooser(poser.kDialogFileChooserOpen, None, f'Select an archive')
    continuum = file_chooser.Show()
    request = file_chooser.Path()
    libraries: Dict[str, str] = {}

    if continuum:
        for library in poser.Libraries():
            libraries[library.split(os.path.sep)[-1]] = library
        choice = poser.DialogSimple.AskMenu(
            'Runtime Uninstaller', 'Select a library:', tuple(libraries.keys()))
        continuum = choice is not None and len(choice) > 0

    if continuum:
        os.chdir(libraries[choice])
        removables: List[str]
        if request.endswith('.zip'):
            removables = read_zip_contents(request)
        elif request.endswith('.rar'):
            removables = read_rar_contents(request)
        else:
            raise Exception('Only ZIP and RAR archives are allowed!')

        directories: List[str] = []
        total_removed, total_removed_bytes = 0, 0
        for removable in removables:
            removable_path = os.path.join(os.getcwd(), removable)
            if os.path.isdir(removable_path):
                directories.append(removable_path)
            elif os.path.isfile(removable_path):
                total_removed_bytes += os.path.getsize(removable_path)
                os.remove(removable_path)
                total_removed += 1
            else:
                print('WARNING:', removable_path, 'does not exist!')

        print(total_removed, 'files were deleted reducing', print_bytes(total_removed_bytes))

        # remove empty parent directories
        do_not_remove = ['runtime', 'geometries', 'libraries', 'camera', 'character', 'face', 'hair', 'hand',
                         'light', 'materials', 'pose', 'props', 'scene', 'python', 'poserScripts', 'textures']
        for removable in directories:
            removable_path = os.path.join(os.getcwd(), removable)
            if not os.path.isdir(removable_path):
                continue
            if len(os.listdir(removable_path)) == 0:
                os.rmdir(removable_path)

            parent_path = removable_path
            for _ in range(4):
                parent_path = os.path.dirname(parent_path)
                if not os.path.isdir(parent_path): continue
                if os.path.basename(parent_path).lower() in do_not_remove: break
                if len(os.listdir(parent_path)) == 0:
                    os.rmdir(parent_path)
