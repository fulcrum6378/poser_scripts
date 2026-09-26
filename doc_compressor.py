import os.path
from typing import Iterable, List

POSER_EXTENSIONS = {
    'pz3': 'pzz',
    'pz2': 'pzz',  # TODO
    'cr2': 'crz',
    'fc2': 'fcz',
    'hr2': 'hrz',
    'hd2': 'hdz',
    'pp2': 'ppz',
}


def choose_poser_docs(allowed_extensions: Iterable[str]) -> List[str]:
    if poser.DialogSimple.YesNo('Select Yes for a single file\nNo for a directory') == 1:
        file_chooser = poser.DialogFileChooser(
            poser.kDialogFileChooserOpen, None, f'Select a Poser file')
    else:
        file_chooser = poser.DialogDirChooser(0, 'Select a directory from the library', None)
    continuum = file_chooser.Show()

    pzs: List[str] = []
    if continuum:
        request = file_chooser.Path()

        if os.path.isfile(request):
            pzs.append(request)
        elif os.path.isdir(request):
            for dir_path, dir_names, filenames in os.walk(request):
                for filename in filenames:
                    if '.' not in filename: continue
                    ext = os.path.splitext(filename)
                    if ext in allowed_extensions:
                        pz_path = os.path.join(dir_path, filename)
                        if os.path.isfile(pz_path):
                            pzs.append(pz_path)
        else:
            print('The address is not available.')
            quit()
    return pzs


if __name__ == '__main__':
    for pz_path in choose_poser_docs(list(POSER_EXTENSIONS.keys())):
        pz = open(pz_path, 'r').read()
        ext = os.path.splitext(pz_path)
        dm = os.path.getmtime(pz_path)
        gzip.open(pz_path, 'wb').write(pz.encode())
        # TODO continue coding...
