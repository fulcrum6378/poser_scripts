# this script is executed twice
figure = poser.Scene().CurrentFigure()
if figure.Name() != 'LUNA':
    figure.SetName('LUNA')

    figure.SetSkinType(3)  # Poser Unimesh
    figure.SetNumbSubdivRenderLevels(1)

    body = figure.Actor('BODY')
    body.CreateValueParameter('Muscular')
    body.CreateValueParameter('Giantess')
    body.CreateValueParameter('Svelte')
    # calling body.LoadMaterialCollection() here makes Poser crash!

else:
    poser.ExecFile('remove_empty_daz_params_silent.py')
