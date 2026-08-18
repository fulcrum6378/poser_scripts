import poser

# get and analyse figure
figure = poser.Scene().CurrentFigure()
figure_obj, figure_supported = figure.GeomFileName().split('\\')[-1], True
if figure_obj == 'blMilWom_v4b.obj':  # Victoria 4
    coefficient = 192.2440171
    pronoun = 'She'
elif figure_obj == 'blMilMan_m4b.obj':  # Michael 4
    coefficient = 199.2582679
    pronoun = 'He'
else:
    poser.DialogSimple.MessageBox('This figure is not supported for measurements.')
    figure_supported = False

if figure_supported:
    scale = figure.Actor('BODY').Parameter('scale')
    poser.DialogSimple.MessageBox(f'{pronoun} is {round(scale.Value() * coefficient, 2)} cm tall.')
