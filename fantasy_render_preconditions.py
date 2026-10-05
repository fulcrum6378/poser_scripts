import poser

def check_scene(for_old_poser: bool) -> str:
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

        # if we have enough memory, subdivision is recommended
        if not for_old_poser and figure.Name().isupper() and figure.NumbSubdivRenderLevels() == 0:
            errors += f'{figure_name} better have a higher subdivision level.\n'

    # detect errors in lights
    for light in scene.Lights():
        light_name = light.Name()
        is_light_on = light.On() == 1

        # detect if any preview lights are not disabled (Poser 11 renders preview lights)
        if is_light_on and for_old_poser and light.LightPreview() == 1:
            errors += f'Preview light {light.Name()} is on!\n'

        # detect if any lights have disabled shadows
        if is_light_on and light.Shadow() == 0:
            errors += f'Light {light_name} has disabled shadows!\n'

        # detect if any test lights are on
        if is_light_on and 'Test' in light_name:
            errors += f'Light {light_name} is on!\n'

    return errors
