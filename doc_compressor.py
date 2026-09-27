import gzip
import os
import poser
from typing import Iterable, List, Optional, Tuple

POSER_EXTENSIONS = {
    'pz3': 'pzz',
    'pz2': 'p2z',
    'cr2': 'crz',
    'cm2': 'cmz',
    'lt2': 'ltz',
    'hd2': 'hdz',
    'hr2': 'hrz',
    'pp2': 'ppz',
    'mt5': 'mz5',
    'fc2': 'fcz',
    'mc6': 'mcz',
    'mcl': 'mlz',
}


def choose_poser_docs(allowed_extensions: Iterable[str]) \
        -> Tuple[Optional[str], List[str]]:

    if poser.DialogSimple.YesNo('Select Yes for a single file\nNo for a directory') == 1:
        file_chooser = poser.DialogFileChooser(
            poser.kDialogFileChooserOpen, None, f'Select a Poser file')
    else:
        file_chooser = poser.DialogDirChooser(0, 'Select a directory from the library', poser.Libraries()[0])
    continuum = file_chooser.Show()

    request = None
    pzs: List[str] = []
    if continuum:
        request = file_chooser.Path()

        if os.path.isfile(request):
            pzs.append(request)
        elif os.path.isdir(request):
            for dir_path, dir_names, filenames in os.walk(request):
                for filename in filenames:
                    if '.' not in filename: continue
                    ext = filename.rsplit('.', 1)[1]
                    if ext in allowed_extensions:
                        pz_path = os.path.join(dir_path, filename)
                        if os.path.isfile(pz_path):
                            pzs.append(pz_path)
        else:
            print('The address is not available.')
            quit()
    return request, pzs


if __name__ == '__main__':
    count = 0
    for uncompressed_path in choose_poser_docs(list(POSER_EXTENSIONS.keys()))[1]:
        data = open(uncompressed_path, 'r').read()
        path_no_ext, ext = uncompressed_path.rsplit('.', 1)
        date_modified = os.path.getmtime(uncompressed_path)
        compressed_path = path_no_ext + '.' + POSER_EXTENSIONS[ext]
        gzip.open(compressed_path, 'wb').write(data.encode())
        os.utime(compressed_path, (date_modified, date_modified))
        os.remove(uncompressed_path)
        count += 1
    if count > 0:
        print(f'{count} files were compressed.')
