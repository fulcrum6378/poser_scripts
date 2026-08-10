from typing import Dict

morphforms: Dict[poser.ParmType, float] = {}


def resolve_actor(actor: poser.ActorType) -> None:
    resolve_dependencies(actor.Parameter('xrot'), True)
    resolve_dependencies(actor.Parameter('yrot'), True)
    resolve_dependencies(actor.Parameter('zrot'), True)

    for child in actor.Children():
        if child.IsBodyPart():
            resolve_actor(child)


def resolve_dependencies(parameter: poser.ParmType, set_value: bool) -> float:
    if parameter.ValueOperations() is None:
        return parameter.Value()

    global morphforms
    final: float = parameter.UnaffectedValue()
    for value_op in parameter.ValueOperations():
        if value_op.SourceParameter() not in morphforms:
            coefficient = resolve_dependencies(value_op.SourceParameter(), False)
            morphforms[value_op.SourceParameter()] = coefficient
            value_op.SourceParameter().SetValue(0.0)
        else:
            coefficient = morphforms[value_op.SourceParameter()]

        if value_op.Type() == poser.kValueOpTypeCodeDELTAADD:
            final += coefficient * value_op.Strength()

    if set_value:
        parameter.SetValue(final)
    else:
        if final > parameter.MaxValue():
            final = parameter.MaxValue()
        elif final < parameter.MinValue():
            final = parameter.MinValue()
    return final


# resolve rotations for all body parts
figure = poser.Scene().CurrentFigure()
resolve_actor(figure.Actor('BODY'))

# resolve translations only for Hip
hip = figure.Actor('hip')
resolve_dependencies(hip.Parameter('xtran'), True)
resolve_dependencies(hip.Parameter('ytran'), True)
resolve_dependencies(hip.Parameter('ztran'), True)
