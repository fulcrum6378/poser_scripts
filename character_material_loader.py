import poser

import character_dossier

# import importlib
# importlib.reload(character_dossier)

scene = poser.Scene()
figure = scene.CurrentFigure()
actor = scene.CurrentActor()
if actor.IsProp() != 1:
    import v4_material_loader  # importlib.reload(v4_material_loader)

    shaders = character_dossier.load_dossier(figure.Name(), None, None)['Shaders']
    for mat in figure.Materials():
        v4_material_loader.inject_material(mat, shaders, None)

else:
    import g8_material_loader  # importlib.reload(g8_material_loader)

    actor_name = actor.Name()
    shaders = character_dossier.load_dossier(actor.Name(), None, None)['Shaders']
    for mat in actor.Materials():
        g8_material_loader.inject_material(mat, shaders, None)

scene.Draw()
