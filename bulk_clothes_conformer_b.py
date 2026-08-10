import os

tmp_path = os.path.join(os.environ['TEMP'], 'buld_clothes_conformer.txt')
if os.path.isfile(tmp_path):
    scene = poser.Scene()

    previous_figures = open(tmp_path, 'r').read().split('\n')
    new_figures = []
    for figure in scene.Figures():
        if figure.Name() not in previous_figures:
            new_figures.append(figure.Name())

    if len(new_figures) > 0:
        os.remove(tmp_path)

        conformee = None
        for figure_name in new_figures:
            figure = scene.Figure(figure_name)
            if figure.ConformTarget() is not None:
                conformee = figure.ConformTarget()

        if conformee is not None:
            for figure_name in new_figures:
                figure = scene.Figure(figure_name)
                if figure.ConformTarget() is None:
                    figure.ConformTo(conformee)
            scene.Draw()
