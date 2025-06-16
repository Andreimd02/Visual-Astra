import vtk
import numpy as np
from src.settings import OBJECT_COLOR, SOURCE_COLOR, SOURCE_NODES_COLOR, SOURCE_TRAJECTORY_COLOR, DETECTOR_COLOR, DETECTOR_NODES_COLOR, DETECTOR_TRAJECTORY_COLOR


def buildCubeActor(x_length = 30, y_length = 15, position = (100, 20), color = DETECTOR_COLOR):
    cube = vtk.vtkCubeSource()
    cube.SetXLength(x_length)
    cube.SetYLength(y_length)
    cube.SetVLength(v_length)
    cube.Update()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(cube.GetOutputPort())

    actor = vtk.vtkActor()


    actor.SetPosition(position[0], position[1], 0)

    actor.GetProperty().SetColor(color)
    # "teste"

    return actor

def buildDiskActor(inner_radius = 0, outer_radius = 20, position = (100, 20), color = SOURCE_COLOR):
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

def buildStraightTrajectory(projections, size, position, obj):
    polydata = vtk.vtkPolyData()
    points = vtk.vtkPoints()

    theta = np.linspace(0, 2 * size, projections)

    x = theta
    for k in range(projections):
        points.InsertNextPoint(x[k] + position[0], position[1], 0)

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
    spline_filter.SetInputData(polydata)
    spline_filter.SetNumberOfSubdivisions(polydata.GetNumberOfPoints() * 10)
    spline_filter.SetSpline(spline)

    spline_mapper = vtk.vtkPolyDataMapper()
    spline_mapper.SetInputConnection(spline_filter.GetOutputPort())

    spline_actor = vtk.vtkActor()
    spline_actor.SetMapper(spline_mapper)
    if obj == "source":
        spline_actor.GetProperty().SetColor(SOURCE_TRAJECTORY_COLOR)
    if obj == "detector":
        spline_actor.GetProperty().SetColor(DETECTOR_TRAJECTORY_COLOR)

    array = vtk.vtkUnsignedCharArray()
    array.SetName('colors')
    array.SetNumberOfComponents(3)
    array.SetNumberOfTuples(projections)
    color = 255 // projections
    if obj == "source":
        for k in range(projections):
            array.InsertTuple3(k, 2, color * (k + 1), 1)
    if obj == "detector":
        for k in range(projections):
            array.InsertTuple3(k, 2, 1, color * (k + 1))

    polydata_colored = vtk.vtkPolyData()
    polydata_colored.ShallowCopy(polydata)
    polydata_colored.GetPointData().SetScalars(array)

    nodes = vtk.vtkSphereSource()
    nodes.SetRadius(3)
    nodes.SetPhiResolution(10)
    nodes.SetThetaResolution(10)

    nodes_glyph = vtk.vtkGlyph3D()
    nodes_glyph.SetSourceConnection(nodes.GetOutputPort())
    nodes_glyph.SetInputData(polydata_colored)

    nodes_glyph.SetColorModeToColorByScalar()
    nodes_glyph.SetInputData(polydata_colored)
    #
    nodes_mapper = vtk.vtkPolyDataMapper()
    nodes_mapper.SetInputConnection(nodes_glyph.GetOutputPort())

    nodes_actor = vtk.vtkActor()
    nodes_actor.SetMapper(nodes_mapper)
    if obj == "source":
        nodes_actor.GetProperty().SetColor(SOURCE_NODES_COLOR)
    if obj == "detector":
        nodes_actor.GetProperty().SetColor(DETECTOR_NODES_COLOR)

    return (spline_actor, nodes_actor)


def buildCircleTrajectory(projections ,radius, position, obj):

    polydata = vtk.vtkPolyData()
    points = vtk.vtkPoints()

    theta = np.linspace(0, 2 * np.pi, projections)
    r = radius

    x = r * np.cos(theta)
    y = r * np.sin(theta)
    for k in range(projections):
        points.InsertNextPoint(x[k]+position[0]+r, y[k]+position[1], 0)

    lines = vtk.vtkCellArray()
    lines.InsertNextCell(projections)

    for k in range(projections):
        lines.InsertCellPoint(k)

    polydata.SetPoints(points)
    polydata.SetLines(lines)
    polydata.GetPoints()

    spline = vtk.vtkCardinalSpline()
    spline.SetLeftConstraint(2)
    spline.SetRightConstraint(2)
    spline.SetLeftValue(0.0)
    spline.SetRightValue(0.0)

    spline_filter = vtk.vtkSplineFilter()
    spline_filter.SetInputData(polydata)
    spline_filter.SetNumberOfSubdivisions(polydata.GetNumberOfPoints() * 10)
    spline_filter.SetSpline(spline)

    spline_mapper = vtk.vtkPolyDataMapper()
    spline_mapper.SetInputConnection(spline_filter.GetOutputPort())

    spline_actor = vtk.vtkActor()
    spline_actor.SetMapper(spline_mapper)
    if obj == "source":
        spline_actor.GetProperty().SetColor(SOURCE_TRAJECTORY_COLOR)
    if obj == "detector":
        spline_actor.GetProperty().SetColor(DETECTOR_TRAJECTORY_COLOR)

    array = vtk.vtkUnsignedCharArray()
    array.SetName('colors')
    array.SetNumberOfComponents(3)
    array.SetNumberOfTuples(projections)
    color = 255//projections
    if obj == "source":
        for k in range(projections):
            array.InsertTuple3(k, 2, color*(k+1), 1)
    if obj == "detector":
        for k in range(projections):
            array.InsertTuple3(k, 2, 1, color*(k+1))


    polydata_colored = vtk.vtkPolyData()
    polydata_colored.ShallowCopy(polydata)
    polydata_colored.GetPointData().SetScalars(array)

    nodes = vtk.vtkSphereSource()
    nodes.SetRadius(3)
    nodes.SetPhiResolution(10)
    nodes.SetThetaResolution(10)

    nodes_glyph = vtk.vtkGlyph3D()
    nodes_glyph.SetSourceConnection(nodes.GetOutputPort())
    nodes_glyph.SetInputData(polydata_colored)

    nodes_glyph.SetColorModeToColorByScalar()
    nodes_glyph.SetInputData(polydata_colored)
    #
    nodes_mapper = vtk.vtkPolyDataMapper()
    nodes_mapper.SetInputConnection(nodes_glyph.GetOutputPort())

    nodes_actor = vtk.vtkActor()
    nodes_actor.SetMapper(nodes_mapper)
    if obj == "source":
        nodes_actor.GetProperty().SetColor(SOURCE_NODES_COLOR)
    if obj == "detector":
        nodes_actor.GetProperty().SetColor(DETECTOR_NODES_COLOR)

    return (spline_actor, nodes_actor)

# def buildCustomTrajectory():
#     contour_widget = vtk.vtkContourWidget()
#     contour_representation = vtk.vtkOrientedGlyphContourRepresentation()
#     contour_representation.GetLinesProperty().SetColor(1, 0, 0)
#     contour_widget.SetRepresetation(contour_representation)
#
#


