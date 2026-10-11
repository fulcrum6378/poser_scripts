import poser

scene = poser.Scene()
figure = scene.CurrentFigure()

# get and analyse figure
figure_obj, figure_supported = figure.GeomFileName().split('\\')[-1], True
if figure_obj == 'blMilWom_v4b.obj':  # Victoria 4
    figure_type = 'V4'
    feet_x_rot = -27.046
elif figure_obj == 'blMilMan_m4b.obj':  # Michael 4
    figure_type = 'M4'
    feet_x_rot = -25.848
else:
    poser.DialogSimple.MessageBox('This figure is not supported for measurements.')
    figure_supported = False

if figure_supported:
    figure.Actor('rFoot').Parameter('xrot').SetValue(feet_x_rot)
    figure.Actor('lFoot').Parameter('xrot').SetValue(feet_x_rot)
    figure.DropToFloor()
    scene.Draw()
