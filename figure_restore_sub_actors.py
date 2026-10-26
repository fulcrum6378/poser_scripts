import poser


def restore_children_recursively(actor: poser.ActorType) -> None:
    for child in actor.Children():
        if not child.IsBodyPart(): continue
        child.Restore()
        restore_children_recursively(child)


scene = poser.Scene()
restore_children_recursively(scene.CurrentActor())
scene.Draw()
