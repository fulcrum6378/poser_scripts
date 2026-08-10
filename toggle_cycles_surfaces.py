scene = poser.Scene()
figure = scene.CurrentFigure()

turn_cycles_on = None
for material in figure.Materials():
    tree = material.ShaderTree()
    roots = []
    has_cycles_surface = False
    for node in tree.Nodes():
        if not node.IsRoot(): continue
        roots.append(node)
        if node.Type() == 'CyclesSurface':
            has_cycles_surface = True
    if len(roots) == 1: continue

    prev_chosen_root = material.ShaderTree().RendererRootNode(poser.kRenderEngineCodeSUPERFLY)
    if has_cycles_surface and turn_cycles_on is None:
        turn_cycles_on = prev_chosen_root.Type() != 'CyclesSurface'

    for root in roots:
        if turn_cycles_on:
            if root.Type() == 'CyclesSurface':
                material.ShaderTree().SetRendererRootNode(poser.kRenderEngineCodeSUPERFLY, root)
                break
        else:
            if root.Type() != 'CyclesSurface':
                material.ShaderTree().SetRendererRootNode(poser.kRenderEngineCodeSUPERFLY, root)
                break
scene.Draw()
