import poser

# this script is executed twice
figure = poser.Scene().CurrentFigure()
if figure.Name() != 'TRIJNTJE':
    figure.SetName('TRIJNTJE')

    body = figure.Actor('BODY')
    body.CreateValueParameter('Aroused')

else:
    poser.ExecFile('figure_remove_empty_daz_params_silent.py')
    poser.ExecFile('character_material_loader.py')
