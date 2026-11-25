import poser

scene = poser.Scene()
polygons, vertices = 0, 0
for actor in scene.Actors():
    geom = actor.Geometry()
    if geom is not None:
        polygons += geom.NumPolygons()
        vertices += geom.NumVertices()
poser.DialogSimple.MessageBox(f'This scene has {polygons:,} polygons and {vertices:,} vertices.')
