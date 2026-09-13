import importlib
import poser

import v4_material_loader
from character_dossier import load_dossier

importlib.reload(v4_material_loader)

scene = poser.Scene()
for mat in scene.CurrentFigure().Materials():
    v4_material_loader.inject_material(mat, load_dossier()['Shaders'], None)
scene.Draw()
