scene = poser.Scene()
figure = scene.CurrentFigure()

# get and analyse figure
figure_obj, figure_supported = figure.GeomFileName().split('\\')[-1], True
if figure_obj == 'blMilWom_v4b.obj':  # Victoria 4
    figure_type = 'V4'
elif figure_obj == 'blMilMan_m4b.obj':  # Michael 4
    figure_type = 'M4'
else:
    poser.DialogSimple.MessageBox('This figure is not supported for measurements.')
    figure_supported = False

if figure_supported:
    scene.LoadLibraryPose(rf'Runtime\Libraries\Pose\Utilities\Stand On Foot - {figure_type}.pz2')
    figure.DropToFloor()
    scene.Draw()
