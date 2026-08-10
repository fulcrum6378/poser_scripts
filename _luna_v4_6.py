# this script is executed twice
figure = poser.Scene().CurrentFigure()
if figure.Name() != 'LUNA':
    figure.SetName('LUNA')

    body = figure.Actor('BODY')
    body.CreateValueParameter('Muscular')
    body.CreateValueParameter('Giantess')
    # calling body.LoadMaterialCollection() here makes Poser crash!

else:
    poser.ExecFile('remove_empty_daz_params_silent.py')
