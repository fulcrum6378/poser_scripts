# this script is executed twice
figure = poser.Scene().CurrentFigure()
if figure.Name() != 'TRIJNTJE':
    figure.SetName('TRIJNTJE')

    body = figure.Actor('BODY')
    body.CreateValueParameter('Aroused')
    # calling body.LoadMaterialCollection() here makes Poser crash!

else:
    poser.ExecFile('remove_empty_daz_params_silent.py')
