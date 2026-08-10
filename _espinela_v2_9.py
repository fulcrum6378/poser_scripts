# this script is executed twice
figure = poser.Scene().CurrentFigure()
if figure.Name() != 'ESPINELA':
    figure.SetName('ESPINELA')

    body = figure.Actor('BODY')
    body.CreateValueParameter('Amazon')
    body.CreateValueParameter('Aroused')
    # calling body.LoadMaterialCollection() here makes Poser crash!

else:
    poser.ExecFile('remove_empty_daz_params_silent.py')
