import poser

# this script is executed twice
figure = poser.Scene().CurrentFigure()
if figure.Name() != 'CHRISTIE':
    figure.SetName('CHRISTIE')

    figure.SetSkinType(3)  # Poser Unimesh
    figure.SetNumbSubdivRenderLevels(1)

    body = figure.Actor('BODY')

else:
    poser.ExecFile('figure_remove_empty_daz_params_silent.py')
    poser.ExecFile('character_material_loader.py')
