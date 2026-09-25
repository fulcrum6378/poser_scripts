import poser
from enum import Enum


class Target(Enum):
    Body = 1
    Face = 2
    Head = 3
    Top = 4
    Bottom = 5


DOLLY_MULTIPLIER = 0.0038149298209603575
V4_HEIGHT = 192.2440171
M4_HEIGHT = 199.2582679

scene = poser.Scene()
cam: poser.ActorType = scene.CurrentCamera()
figure: poser.FigureType = scene.CurrentFigure()
figure_obj = figure.GeomFileName().split('\\')[-1]
if figure_obj == 'blMilWom_v4b.obj':
    figure_def_height = V4_HEIGHT
elif figure_obj == 'blMilMan_m4b.obj':
    figure_def_height = M4_HEIGHT
else:
    raise Exception('Unsupported figure')

target = poser.DialogSimple.AskMenu(
    'Photoshoot', 'Select a target', tuple(Target._member_names_))
continuum: bool = target is not None and len(target) > 0

if continuum:
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
    hip_scale = figure.Actor('hip').Parameter('scale').Value()
    neck_scale = figure.Actor('neck').Parameter('yScale').Value()
    head_scale = figure.Actor('head').Parameter('scale').Value()
    thigh_scale = figure.Actor('rThigh').Parameter('scale').Value()
    shin_scale = figure.Actor('rShin').Parameter('scale').Value()
    feet_scale = figure.Actor('rFoot').Parameter('scale').Value()
    v4_based_ratio = figure_def_height / V4_HEIGHT
    relative_scale = body_scale * v4_based_ratio

    z_body = 25 * relative_scale
    z_hip = 50 * hip_scale
    z_neck = 30 * neck_scale
    z_head = 51.5 * head_scale  # NEVER CHANGE THIS, ACCURATE IN FACE AND HEAD
    z_thigh = 90 * thigh_scale
    z_shin = 90 * shin_scale
    z_feet = 30 * feet_scale

    y_body = 40.55  # full body: 180.55
    y_hip = 17 * hip_scale
    y_neck = 9 * neck_scale
    y_head = 8 * head_scale
    y_thigh = 50 * thigh_scale
    y_shin = 46 * shin_scale
    y_feet = 10 * feet_scale

    if target == Target.Body.name:
        z = -205 + ((z_body + z_hip + z_neck + z_head + z_thigh + z_shin + z_feet) * relative_scale)
        y = (y_body + y_hip + y_neck + y_head + y_thigh + y_shin + y_feet) * relative_scale * 0.58

    elif target == Target.Face.name:
        z = -283 + (z_head * relative_scale)
        y = (y_body + y_hip + y_neck + y_head + y_thigh + y_shin + y_feet) * relative_scale

    elif target == Target.Head.name:
        z = -260 + (z_head * relative_scale)
        y = (y_body + y_hip + y_neck + y_head + y_thigh + y_shin + y_feet) * relative_scale

    elif target == Target.Top.name:
        pass  # TODO

    elif target == Target.Bottom.name:
        pass  # TODO

    x = body_scale * v4_based_ratio

    cam.Parameter('dollyZ').SetValue(z * DOLLY_MULTIPLIER)
    cam.Parameter('dollyY').SetValue(y * DOLLY_MULTIPLIER)
    cam.Parameter('dollyX').SetValue(x * DOLLY_MULTIPLIER)
