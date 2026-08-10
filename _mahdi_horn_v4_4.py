# this script is executed twice
figure = poser.Scene().CurrentFigure()
if figure.Name() != 'HORN':
    figure.SetName('HORN')

    body = figure.Actor('BODY')
    body.CreateValueParameter('ErectGrow')
    body.CreateValueParameter('ErectProlong')
    body.CreateValueParameter('ErectNarrow')
    body.CreateValueParameter('ErectRaise')
    # calling body.LoadMaterialCollection() here makes Poser crash!

else:
    body = figure.Actor('BODY')
    body.DeleteTarget('FBMBodyBuilder')
    body.DeleteTarget('FBMDefinition')
    body.DeleteTarget('FBMEmaciated')
    body.DeleteTarget('FBMJeremy')
    body.DeleteTarget('FBMSuperHero')
    body.DeleteTarget('FBMSmooth')
    body.DeleteTarget('FBMYoung')
    body.RemoveValueParameter('Uncircumcised')

    hip = figure.Actor('hip')
    hip.DeleteTarget('FBMBodyBuilder')
    hip.DeleteTarget('FBMDefinition')
    hip.DeleteTarget('FBMEmaciated')
    hip.DeleteTarget('FBMJeremy')
    hip.DeleteTarget('FBMSuperHero')
    hip.DeleteTarget('FBMSmooth')
    hip.DeleteTarget('FBMYoung')
    hip.DeleteTarget('Uncircumcised')

    gen01 = figure.Actor('gen01')
    gen01.DeleteTarget('FBMEmaciated')

    gen04 = figure.Actor('gen04')
    gen04.DeleteTarget('PBMUncircumcised01')
    gen04.DeleteTarget('PBMUncircumcised02')
    gen04.DeleteTarget('PBMUncircumcised03')
    gen04.DeleteTarget('PBMUncircumcised04')
    gen04.DeleteTarget('PBMUncircumcised05')

    testicles = figure.Actor('testicles')
    testicles.DeleteTarget('FBMJeremy')

    rThigh = figure.Actor('rThigh')
    rThigh.DeleteTarget('FBMBodyBuilder')
    rThigh.DeleteTarget('FBMDefinition')
    rThigh.DeleteTarget('FBMEmaciated')
    rThigh.DeleteTarget('FBMJeremy')
    rThigh.DeleteTarget('FBMSuperHero')
    rThigh.DeleteTarget('FBMSmooth')
    rThigh.DeleteTarget('FBMYoung')

    lThigh = figure.Actor('lThigh')
    lThigh.DeleteTarget('FBMBodyBuilder')
    lThigh.DeleteTarget('FBMDefinition')
    lThigh.DeleteTarget('FBMEmaciated')
    lThigh.DeleteTarget('FBMJeremy')
    lThigh.DeleteTarget('FBMSuperHero')
    lThigh.DeleteTarget('FBMSmooth')
    lThigh.DeleteTarget('FBMYoung')

    poser.ExecFile('remove_empty_daz_params_silent.py')
