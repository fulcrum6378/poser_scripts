import os

import poser

versions = {
    'Christie': 1,
    'Espinela': 2,
    'Zoey': 4,
}

# find the morphs directory
scene = poser.Scene()
figure = scene.CurrentFigure()
character = figure.Name().capitalize()
obj_dir = os.environ['ONEDRIVE'] + rf'\Projects\Characters\{character}\Sculpture on V4'
if not os.path.isdir(obj_dir):
    raise Exception('This character has no morphs directory.')

# determine the selection
selection = []
text_entry = poser.DialogTextEntry(
    0, 'Which morphs should be loaded?\n(use `-` for ranges and `,` for separation)')
if text_entry.Show() == 1:

    if len(text_entry.Text().strip()) > 0:
        for spl1 in text_entry.Text().split(','):
            if '-' not in spl1:
                selection.append(int(spl1))
            else:
                spl2 = spl1.split('-')
                max_ = int(spl2[1])
                selection.extend(list(range(int(spl2[0]), max_)))
                selection.append(max_)


    def load_morph(name: str, path: str):
        figure.LoadFullBodyMorph(path)
        parm = body.Parameter(name)
        parm.SetMinValue(0.0)
        parm.SetMaxValue(1.0)
        parm.SetSensitivity(1.0)


    # load the selected morphs, if there was no selection, load all
    if len(selection) == 0:
        for obj in os.listdir(obj_dir):
            if not obj.startswith(f'{character} v{versions[character]}.') or not obj.endswith('.obj'):
                continue
            path = rf'{obj_dir}\{obj}'
            load_morph(obj[:-4], path)
    else:
        body = figure.Actor('BODY')
        for selected in selection:
            name = f'{character} v{versions[character]}.{selected:03d}'
            path = rf'{obj_dir}\{name}.obj'
            if os.path.isfile(path):
                load_morph(name, path)
            else:
                print(name, 'was not found!')
