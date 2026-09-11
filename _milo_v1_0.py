import poser

# this script is executed twice
figure = poser.Scene().CurrentFigure()
if figure.Name() != 'MILO':
    figure.SetName('MILO')

    # body = figure.Actor('BODY')

else:
    poser.ExecFile('figure_remove_empty_daz_params_silent.py')
    poser.ExecFile('character_material_loader.py')
