from .BuildFunctions import *
from src.settings import OBJECT_COLOR, SOURCE_COLOR, SOURCE_NODES_COLOR, SOURCE_TRAJECTORY_COLOR, DETECTOR_COLOR, DETECTOR_NODES_COLOR, DETECTOR_TRAJECTORY_COLOR
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
        self.erase_angles_demonstrator = False
        self.erase_angles_demonstrator = True

        self.objects_dics = objects_dics

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
        if self.erase_angles_demonstrator:
            for actor in self.objects_dic['trajectory_angles']:
                self.renderer.RemoveActor(actor)
            self.renderer.ResetCamera()
            self.erase_angles_demonstrator = False
            self.objects_dic['trajectory_angles'] = []
        vtk.vtkInteractorStyleTrackballActor.OnMiddleButtonUp(self)


    def OnLeftButtonDown(self, obj, eventType):
        clickPos = self.GetInteractor().GetEventPosition()
        if 'trajectory_angles' in self.objects_dic:
            if len(self.objects_dic) > 0:
                self.erase_angles_demonstrator = True
                self.OnLeftButtonRelease(obj, eventType)

        picker = vtk.vtkPropPicker()
        picker.Pick(clickPos[0], clickPos[1], 0, self.renderer)
        actor = picker.GetActor()
        self.chosenPiece = actor
        if self.chosenPiece:

            vtk.vtkInteractorStyleTrackballActor.OnMiddleButtonDown(self)
            self.renderer.ResetCamera()
        self.renderer.ResetCamera()

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
            if actor_color == DETECTOR_TRAJECTORY_COLOR or actor_color == SOURCE_TRAJECTORY_COLOR or actor_color[0] == .8:
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
                if actor_color == DETECTOR_COLOR:
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
                if actor_color == DETECTOR_TRAJECTORY_COLOR or actor_color[2] == 1:
                    self.chosenPiece = self.objects_dic["detector"]
                    self.setTrajectoryPosition("detector_trajectory", scale_y)
                    self.chosenPiece = self.objects_dic["detector_trajectory"][0]

                elif actor_color == SOURCE_TRAJECTORY_COLOR or actor_color[2] == 0:
                    self.chosenPiece = self.objects_dic["source"]
                    self.setTrajectoryPosition("source_trajectory", scale_y)
                    self.chosenPiece = self.objects_dic["source_trajectory"][0]
                self.renWin.Render()
                self.renderer.ResetCamera()

            else:
                if actor_color != DETECTOR_TRAJECTORY_COLOR and actor_color != SOURCE_TRAJECTORY_COLOR and actor_color[0] != .8:
                    vtk.vtkInteractorStyleTrackballActor.OnMouseMove(self)

                    if actor_color == DETECTOR_COLOR:
                        if "detector_trajectory" in self.objects_dic:
                            self.setTrajectoryPosition("detector_trajectory")

                    elif actor_color == SOURCE_COLOR:
                        if "source_trajectory" in self.objects_dic:
                            self.setTrajectoryPosition("source_trajectory")
                    self.renderer.ResetCamera()

        else:
            vtk.vtkInteractorStyleTrackballActor.OnMouseMove(self)

    def setTrajectoryPosition(self, trajectory_type, bonus_radius = 0):
        polydata = vtk.vtkPolyData.SafeDownCast(self.objects_dic[trajectory_type][0].GetMapper().GetInput())
        projections = polydata.GetNumberOfPoints()//10

        self.renderer.RemoveActor(self.objects_dic[trajectory_type][0])
        self.renderer.RemoveActor(self.objects_dic[trajectory_type][1])

        if self.objects_dic[trajectory_type][2] == 'circle_trajectory':
            point1 = polydata.GetPoint(0)
            point2 = polydata.GetPoint(projections*10//2)
            radius = round(point1[0] - point2[0])/2
            radius += bonus_radius

            trajectory, trajectory_nodes = buildCircleTrajectory(projections, radius, self.chosenPiece.GetPosition(), trajectory_type[:-11])
            self.objects_dic[trajectory_type] = (trajectory, trajectory_nodes, "circle_trajectory")
        if self.objects_dic[trajectory_type][2] == 'straight_trajectory':
            point1 = polydata.GetPoint(0)
            point2 = polydata.GetPoint(projections*10)
            radius = round(point2[0] - point1[0])/2
            radius += bonus_radius


            trajectory, trajectory_nodes = buildStraightTrajectory(projections, radius, self.chosenPiece.GetPosition(), trajectory_type[:-11])
            self.objects_dic[trajectory_type] = (trajectory, trajectory_nodes, "straight_trajectory")
        self.renderer.AddActor(trajectory)
        self.renderer.AddActor(trajectory_nodes)
