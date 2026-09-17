import poser

import character_dossier
import v4_material_loader

import importlib
importlib.reload(character_dossier)
importlib.reload(v4_material_loader)

scene = poser.Scene()
figure_name = scene.CurrentFigure().Name()
shaders = character_dossier.load_dossier(figure_name, None, None)['Shaders']
for mat in scene.CurrentFigure().Materials():
    v4_material_loader.inject_material(mat, shaders, None)
scene.Draw()
