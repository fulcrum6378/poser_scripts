import poser

scene = poser.Scene()

fantasy_render_preconditions.check_scene(scene)
continuum = len(errors) == 0
if not continuum:
    continuum = poser.DialogSimple.YesNo(errors + 'Do you want to continue?') == 1

if continuum:
    # noinspection PyUnusedImports
    import render_then_hibernate
