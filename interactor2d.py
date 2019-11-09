import vtk
import math
from BuildFunctions import *

class CustomInteractor(vtk.vtkInteractorStyleTrackballActor):

    def __init__(self, renderer, renWin, objects_dic):
        super().__init__()
        self.AddObserver('LeftButtonPressEvent', self.OnLeftButtonDown)
        self.AddObserver('LeftButtonReleaseEvent', self.OnLeftButtonRelease)
        self.AddObserver('MouseMoveEvent', self.OnMouseMove)
        self.AddObserver('RightButtonPressEvent', self.OnRightButtonDown)
        self.AddObserver('RightButtonReleaseEvent', self.OnRightButtonRelease)
        self.AddObserver('MiddleButtonPressEvent', self.OnMiddleButtonDown)
        self.AddObserver('MiddleButtonReleaseEvent', self.OnMiddleButtonRelease)
        self.rotation = False
        self.scale = False

        self.objects_dic = objects_dic

        self.renderer = renderer
        self.chosenPiece = None
        self.renWin = renWin

    def OnRightButtonDown(self, obj, eventType):
        clickPos = self.GetInteractor().GetEventPosition()

        picker = vtk.vtkPropPicker()
        picker.Pick(clickPos[0], clickPos[1], 0, self.renderer)
        actor = picker.GetActor()
        self.chosenPiece = actor

    def OnRightButtonRelease(self, obj, eventType):
        self.chosenPiece = None

    def OnLeftButtonRelease(self, obj, eventType):
        self.chosenPiece = None
        vtk.vtkInteractorStyleTrackballActor.OnMiddleButtonUp(self)


    def OnLeftButtonDown(self, obj, eventType):
        clickPos = self.GetInteractor().GetEventPosition()

        picker = vtk.vtkPropPicker()
        picker.Pick(clickPos[0], clickPos[1], 0, self.renderer)
        actor = picker.GetActor()
        self.chosenPiece = actor
        if self.chosenPiece:

                vtk.vtkInteractorStyleTrackballActor.OnMiddleButtonDown(self)
                self.renderer.ResetCamera()
        # self.renderer.ResetCamera()

    def updateObjects(self, objects_dic):
        self.objects_dic = objects_dic

    def OnMiddleButtonDown(self, obj, eventType):
        clickPos = self.GetInteractor().GetEventPosition()

        picker = vtk.vtkPropPicker()
        picker.Pick(clickPos[0], clickPos[1], 0, self.renderer)
        actor = picker.GetActor()
        self.chosenPiece = actor
        if self.chosenPiece:
            actor_color = self.chosenPiece.GetProperty().GetColor()
            if actor_color == (.5, 0, .5) or actor_color == (.5, .5, 0) or actor_color[0] == .8:
                vtk.vtkInteractorStyleTrackballActor.OnRightButtonDown(self)
                self.scale = True
            else:
                self.rotation = True

    def OnMiddleButtonRelease(self, obj, eventType):
        self.chosenPiece = None
        self.rotation = False
        # Interactive Scale of the trajectory actors stand by
        if self.scale:
            self.scale = False
            vtk.vtkInteractorStyleTrackballActor.OnRightButtonUp(self)

    def OnMouseMove(self, obj, eventType):
        if self.chosenPiece is not None:
            actor_color = self.chosenPiece.GetProperty().GetColor()
            if self.rotation:
                if actor_color == (.3, .3, .3):
                    mouse_pos_pas = self.GetInteractor().GetLastEventPosition()
                    mouse_pos = self.GetInteractor().GetEventPosition()
                    rotate_x = mouse_pos[0] - mouse_pos_pas[0]
                    self.chosenPiece.RotateZ(rotate_x)
                    self.renWin.Render()

            # Interactive Scale of the trajectory actors stand by
            elif self.scale:
                mouse_pos_pas = self.GetInteractor().GetLastEventPosition()
                mouse_pos = self.GetInteractor().GetEventPosition()
                scale_y = mouse_pos[1] - mouse_pos_pas[1]
                if actor_color == (.5, 0, .5) or actor_color[2] == 1:
                    self.chosenPiece = self.objects_dic["detector"]
                    self.setTrajectoryPosition("detector_trajectory", scale_y)
                    self.chosenPiece = self.objects_dic["detector_trajectory"][0]

                elif actor_color == (.5, .5, 0) or actor_color[2] == 0:
                    self.chosenPiece = self.objects_dic["source"]
                    self.setTrajectoryPosition("source_trajectory", scale_y)
                    self.chosenPiece = self.objects_dic["source_trajectory"][0]
                self.renWin.Render()
                self.renderer.ResetCamera()

            else:
                if actor_color != (.5, 0, .5) and actor_color != (.5, .5, 0) and actor_color[0] != .8:
                    vtk.vtkInteractorStyleTrackballActor.OnMouseMove(self)

                    if actor_color == (0.3, 0.3, 0.3):
                        if "detector_trajectory" in self.objects_dic:
                            self.setTrajectoryPosition("detector_trajectory")

                    elif actor_color == (1, 1, 1):
                        if "source_trajectory" in self.objects_dic:
                            self.setTrajectoryPosition("source_trajectory")
                    self.renderer.ResetCamera()

        else:
            vtk.vtkInteractorStyleTrackballActor.OnMouseMove(self)

    def setTrajectoryPosition(self, trajectory_type, bonus_radius = 0):
        x, y, z = self.chosenPiece.GetPosition()
        polydata = vtk.vtkPolyData.SafeDownCast(self.objects_dic[trajectory_type][0].GetMapper().GetInput())
        projections = polydata.GetNumberOfPoints()//10

        point1 = polydata.GetPoint(0)
        point2 = polydata.GetPoint(projections*10//2)
        radius = round(point1[0] - point2[0])/2
        radius += bonus_radius

        self.renderer.RemoveActor(self.objects_dic[trajectory_type][0])
        self.renderer.RemoveActor(self.objects_dic[trajectory_type][1])
        trajectory, trajectory_nodes = buildCircleCurve(projections, radius, self.chosenPiece.GetPosition(), trajectory_type[:-11])
        self.renderer.AddActor(trajectory)
        self.renderer.AddActor(trajectory_nodes)
        self.objects_dic[trajectory_type] = (trajectory, trajectory_nodes)
