import poser

scene = poser.Scene()
figure = scene.CurrentFigure()
figure.Actor('BODY').Parameter('scale').SetValue(
    figure.ConformTarget().Actor('BODY').Parameter('scale').Value()
)
scene.Draw()
