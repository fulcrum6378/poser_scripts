import poser

# get and analyse figure
figure = poser.Scene().CurrentFigure()
figure_obj, figure_supported = figure.GeomFileName().split('\\')[-1], True
if figure_obj == 'blMilWom_v4b.obj':  # Victoria 4
    coefficient = 192.2440171
    pronoun = 'her'
elif figure_obj == 'blMilMan_m4b.obj':  # Michael 4
    coefficient = 199.2582679
    pronoun = 'his'
else:
    poser.DialogSimple.MessageBox('This figure is not supported for measurements.')
    figure_supported = False


if figure_supported:

    # prompt the desired height
    scale = figure.Actor('BODY').Parameter('scale')
    text_entry = poser.DialogTextEntry(0,
            f'Enter {pronoun} height in centimetres:',
            str(scale.Value() * coefficient))
    text_entry.Show()

    # parse user entry
    try:
        new_height = float(text_entry.Text())
    except:
        new_height = -1

    # final judgment
    if new_height >= 0:
        scale.SetValue(new_height / coefficient)
    else:
        poser.DialogSimple.MessageBox('Please enter a valid positive decimal number.')
