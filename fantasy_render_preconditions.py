import poser

def check_scene() -> str:
    scene = poser.Scene()
    errors = ''

    # detect errors in figures
    for figure in scene.Figures():
        figure_name = figure.Name().capitalize()

        # detect if any secondary CyclesSurfaces are disabled
        for material in figure.Materials():
            for node in material.ShaderTree().Nodes():
                if node.Type() == 'CyclesSurface' and material.ShaderTree() \
                        .RendererRootNode(poser.kRenderEngineCodeSUPERFLY).Name() != node.Name():
                    errors += f'CyclesSurface in {figure_name}\'s {material.Name()} is disabled!\n'

        # detect if any V4/M4 eyebrows are visible which shouldn't
        try:
            eyebrows = figure.Actor('eyeBrow')
            if eyebrows.Visible() == 1:
                errors += f'{figure_name}\'s eyebrows are visible!\n'
        except poser.error:
            pass

    # detect errors in lights
    for light in scene.Lights():

        # detect if any preview lights are not disabled (Poser 11 renders preview lights)
        if light.LightPreview() == 1 and light.LightOn() == 1:
            errors += f'Preview light {light.Name()} is on!\n'

        # detect if any lights have disabled shadows
        if light.LightOn() == 1 and light.Shadow() == 0:
            errors += f'Light {light.Name()} has disabled shadows!\n'

    return errors
