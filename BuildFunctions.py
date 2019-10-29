import vtk
import numpy as np

def buildCubeActor(x_length = 30, y_length = 15, position = (100, 20), color = (0.3, 0.3, 0.3)):
    cube = vtk.vtkCubeSource()
    cube.SetXLength(x_length)
    cube.SetYLength(y_length)
    cube.Update()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(cube.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    actor.SetPosition(position[0], position[1], 0)

    actor.GetProperty().SetColor(color)

    return actor

def buildDiskActor(inner_radius = 0, outer_radius = 20, position = (100, 20), color = (1, 1, 1)):
    disk = vtk.vtkDiskSource()
    disk.SetInnerRadius(inner_radius)
    disk.SetOuterRadius(outer_radius)
    disk.SetRadialResolution(100)
    disk.SetCircumferentialResolution(100)
    disk.Update()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(disk.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    actor.SetPosition(position[0], position[1], 0)

    actor.GetProperty().SetColor(color)

    return actor

def buildCircleCurve(projections ,radius, position):

    polydata = vtk.vtkPolyData()
    points = vtk.vtkPoints()

    theta = np.linspace(0, 2 * np.pi, projections)
    r = 100.0

    x = r * np.cos(theta)
    y = r * np.sin(theta)
    for k in range(projections):
        points.InsertNextPoint(x[k]+position[0], y[k]+position[1], 0)
    lines = vtk.vtkCellArray()
    lines.InsertNextCell(projections)

    for k in range(projections):
        lines.InsertCellPoint(k)

    polydata.SetPoints(points)
    polydata.SetLines(lines)

    spline = vtk.vtkCardinalSpline()
    spline.SetLeftConstraint(2)
    spline.SetRightConstraint(2)
    spline.SetLeftValue(0.0)
    spline.SetRightValue(0.0)

    spline_filter = vtk.vtkSplineFilter()
    # spline_filter.SetInput(polydata)
    spline_filter.SetInputData(polydata)
    spline_filter.SetNumberOfSubdivisions(polydata.GetNumberOfPoints() * 10)
    spline_filter.SetSpline(spline)

    spline_mapper = vtk.vtkPolyDataMapper()
    spline_mapper.SetInputConnection(spline_filter.GetOutputPort())

    spline_actor = vtk.vtkActor()
    spline_actor.SetMapper(spline_mapper)

    nodes = vtk.vtkSphereSource()
    nodes.SetRadius(3)
    nodes.SetPhiResolution(10)
    nodes.SetThetaResolution(10)

    # polydata = vtk.vtkPolyData.SafeDownCast(spline.GetMapper().GetInputAsDataSet())
    # print(polydata.GetNumberOfCells)
    nodes_glyph = vtk.vtkGlyph3D()
    nodes_glyph.SetInputData(polydata)
    nodes_glyph.SetSourceConnection(nodes.GetOutputPort())

    nodes_mapper = vtk.vtkPolyDataMapper()
    nodes_mapper.SetInputConnection(nodes_glyph.GetOutputPort())

    nodes_actor = vtk.vtkActor()
    nodes_actor.SetMapper(nodes_mapper)
    nodes_actor.GetProperty().SetColor(0.8900, 0.8100, 0.3400)

    return (spline_actor, nodes_actor)

#
# def buildSplineSpheres(spline):
#     nodes = vtk.vtkSphereSource()
#     nodes.SetRadius(0.4)
#     nodes.SetPhiResolution(10)
#     nodes.SetThetaResolution(10)
#
#     polydata = vtk.vtkPolyData.SafeDownCast(spline.GetMapper().GetInputAsDataSet())
#     print(polydata.GetNumberOfCells)
#     glyph = vtk.vtkGlyph3D()
#     glyph.SetInputData(polydata)
#     glyph.SetSourceConnection(nodes.GetOutputPort())
#
#     mapper = vtk.vtkPolyDataMapper()
#     mapper.SetInputConnection(glyph.GetOutputPort())
#
#     nodes_actor = vtk.vtkActor()
#     nodes_actor.SetMapper(mapper)
#     nodes_actor.GetProperty().SetColor(0.8900, 0.8100, 0.3400)
#     nodes_actor.GetProperty().SetOpacity(.6)
#
#     return nodes_actor