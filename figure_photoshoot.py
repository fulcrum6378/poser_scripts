import poser

TARGET_FACE = 0
TARGET_HEAD = 1
DOLLY_MULTIPLIER = 0.0038149298209603575

target: int = 0
continuum: bool = True

if continuum:
    scene = poser.Scene()
    cam: poser.ActorType = scene.CurrentCamera()
    figure: poser.FigureType = scene.CurrentFigure()

    if cam.Name() in ['Left Camera', 'Right Camera',
                      'Top Camera', 'Bottom Camera',
                      'Front Camera', 'Back Camera',
                      'Face Camera', 'Posing Camera',
                      'RHand Camera', 'LHand Camera'] \
            or cam.Name().startswith('Shadow Cam Lite'):
        for cam in scene.Cameras():
            if cam.Name() == 'Main Camera':
                scene.SetCurrentCamera(cam)
                break

    cam.Parameter('focal').SetValue(50)
    cam.Parameter('hither').SetValue(0)
    cam.Parameter('pitch').SetValue(0)

    z, y, x = 0, 0, 0
    body_scale = figure.Actor('BODY').Parameter('scale').Value()

    if target == TARGET_FACE:
        z = -286.5 + (body_scale * 51.5)
        y = (body_scale * 192.2440171) * (180.55 / 192.2440171)
        x = body_scale * 1

    elif target == TARGET_HEAD:
        pass

    cam.Parameter('dollyZ').SetValue(z * DOLLY_MULTIPLIER)
    cam.Parameter('dollyY').SetValue(y * DOLLY_MULTIPLIER)
    cam.Parameter('dollyX').SetValue(x * DOLLY_MULTIPLIER)
