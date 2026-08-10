def normalise_rotation(r: float) -> float:
    while r > 180.0 or r < -180.0:
        if r > 0.0: r -= 360.0
        else: r += 360.0
    return r


# get initial information
scene = poser.Scene()
figure = scene.CurrentFigure()
rEye, lEye = figure.Actor('rEye'), figure.Actor('lEye')
del figure
camera = scene.Actor('Face Camera')
upDown: float = normalise_rotation(camera.Parameter('pitch').Value()) * 0.5
sideSide: float = normalise_rotation(camera.Parameter('yaw').Value()) * 0.5
del camera

# consider body parts and other parents
cam_x, cam_y, cam_z = 0.0, 0.0, 0.0
parent = rEye.Parent()
while parent is not None:
    if parent.Parameter('xrot') is not None:
        x = parent.Parameter('xrot').Value()
        y = parent.Parameter('yrot').Value()
        z = parent.Parameter('zrot').Value()
    elif parent.Parameter('xRotate') is not None:
        x = parent.Parameter('xRotate').Value()
        y = parent.Parameter('yRotate').Value()
        z = parent.Parameter('zRotate').Value()
    else:
        break

    actor_name = parent.InternalName().split(':')[0]
    if actor_name in ['head', 'neck', 'chest', 'abdomen']:
        upDown += x * -0.5
        sideSide += y * -0.5
        if actor_name == 'head':
            sideSide += z
    else:
        cam_x += x
        cam_y += y
        cam_z += z

    parent = parent.Parent()
del parent

# adjust camera rotations
x = -normalise_rotation(cam_x) * 1.5
y = -normalise_rotation(cam_y) * 0.5
# z = normalise_rotation(cam_z)
del cam_x, cam_y, cam_z
upDown += x
sideSide += y

# set values
rEye.Parameter('xrot').SetValue(upDown)
lEye.Parameter('xrot').SetValue(upDown)
rEye.Parameter('yrot').SetValue(sideSide)
lEye.Parameter('yrot').SetValue(sideSide)
scene.Draw()
