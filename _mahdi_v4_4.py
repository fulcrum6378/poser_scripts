# this script is executed twice
figure = poser.Scene().CurrentFigure()
if figure.Name() != 'MAHDI':
    figure.SetName('MAHDI')

    body = figure.Actor('BODY')
    body.CreateValueParameter('Tall')
    # calling body.LoadMaterialCollection() here makes Poser crash!

else:
    poser.ExecFile('remove_empty_daz_params_silent.py')
