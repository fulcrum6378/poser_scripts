# this script is executed twice
figure = poser.Scene().CurrentFigure()
if figure.Name() != 'ZOEY':
    figure.SetName('ZOEY')

    # body = figure.Actor('BODY')
    # calling body.LoadMaterialCollection() here makes Poser crash!

else:
    poser.ExecFile('remove_empty_daz_params_silent.py')
