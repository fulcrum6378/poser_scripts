import os

from v4_material_loader import inject_material

ASK_MODE = 1  # 0=>AskMenu, 1=>FileChooser

scene = poser.Scene()
figure = scene.CurrentFigure()
assert figure is not None

runtimes = poser.Libraries()
chosen_runtime = runtimes[-1]
for runtime in runtimes:
    if runtime.endswith('Experimental'):
        chosen_runtime = runtime
runtime_marker = os.path.sep + 'Runtime' + os.path.sep

manifest = {  # default to London
    'Face': {'ColorTexture': 'Danae:LondonV4:HR_Nat_London.jpg'},
    'Eyelashes': {'OpacityTexture': 'Danae:LondonV4:Eyes:LASH_London.jpg'},
    'Eyes': {'ColorTexture': 'Danae:LondonV4:Eyes:EyesBrown_London.jpg'},
    'Lips': {'ColorTexture': 'Danae:LondonV4:HR_MU1_London.jpg'},
    'Mouth': {'ColorTexture': 'Danae:LondonV4:TEETH_London.jpg'},
    'Torso': {'ColorTexture': 'Danae:LondonV4:Body:HR_London_Torso.jpg'},
    'Limbs': {'ColorTexture': 'Danae:LondonV4:Body:London_Limbs.jpg'}
}

if ASK_MODE == 0:  # ASK MENU

    dir_chooser = poser.DialogDirChooser(0, 'Select a texture directory',
                                         os.path.join(chosen_runtime, 'Runtime', 'Textures'))
    continuum = dir_chooser.Show()

    if continuum:
        txr_root_dir = dir_chooser.Path()
        if runtime_marker not in txr_root_dir:
            raise Exception()
        txr_path_runtime_index = txr_root_dir.rindex(runtime_marker)
        textures = []
        texture_names = []
        for txr_dir in os.walk(txr_root_dir):
            for texture_name in txr_dir[2]:
                texture_path = os.path.join(txr_dir[0], texture_name)
                textures.append(texture_path[txr_path_runtime_index:].replace(os.path.sep, ':'))
                texture_names.append(texture_path[len(txr_root_dir) + 1:])

        for shader_name in manifest.keys():
            choice = poser.DialogSimple.AskMenu(
                f'Assign a texture to {shader_name}', shader_name, tuple(texture_names))
            if choice is not None and len(choice) > 0:
                manifest[shader_name][list(manifest[shader_name].keys())[0]] = \
                    textures[texture_names.index(choice)]

elif ASK_MODE == 1:  # FILE CHOOSER

    continuum = True
    default_dir = chosen_runtime
    cancelled = 0
    for shader_name in manifest.keys():
        file_chooser = poser.DialogFileChooser(
            poser.kDialogFileChooserOpen, default_dir, f'Assign a texture to {shader_name}'
        )
        if file_chooser.Show():
            choice = file_chooser.Path()
            manifest[shader_name][list(manifest[shader_name].keys())[0]] = \
                choice[choice.rindex(runtime_marker) + 18:].replace(os.path.sep, ':')
        else:
            cancelled += 1
            if cancelled == 3:
                continuum = False
                break

if continuum:
    for mat in figure.Materials():
        inject_material(mat, manifest, None)
    scene.Draw()
