from PyQt5.QtWidgets import QMainWindow, QMenu, QApplication, QFrame, QVBoxLayout, QAction
from PyQt5 import QtGui, QtCore
from View.Dialogs import Dialogs
from BuildFunctions import *
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from interactor2d import CustomInteractor
from MouseWatch import MouseWatch
import sys
import math

''' a ordem eh monta a tela
    cria o frame do vtk
    chama o renderer
    cria os actors
    cria o interactor
    chama o loop
'''

class SimulationWindow(QMainWindow):
    def __init__(self, projection_conf):
        super().__init__()
        self.projection_conf = projection_conf
        self.title = "Choose the other configs"
        self.icon = QtGui.QIcon("Resources/mainIcon.png")
        self.top = 400
        self.left = 300
        self.width = 800
        self.height = 600

        self.projections_number = None
        self.objects_dic = {}

        self.initWindow()

        #VTKInteractor
        self.frame = QFrame()
        self.vl = QVBoxLayout()
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.vl.addWidget(self.vtkWidget)

        ##Vtk
        self.renderer = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)
        #

        # self.render_window = vtk.vtkRenderWindow()
        # self.render_window.AddRenderer(self.renderer)
        #
        # self.vtkWidget.SetRenderWindow(self.render_window)

        self.addActors()

        self.frame.setLayout(self.vl)
        self.setCentralWidget(self.frame)

        self.interactor = self.vtkWidget.GetRenderWindow().GetInteractor()
        self.addInteractor()

        self.show()
        self.interactor.Initialize()

    def addActors(self):
        self.xraysource = buildDiskActor(position=(100, 130))
        self.renderer.AddActor(self.xraysource)
        self.objects_dic['source'] = self.xraysource

        self.object = buildDiskActor(position=(350, 300), color=(0.9, 0.9, 0.9))
        self.renderer.AddActor(self.object)
        self.objects_dic['object'] = self.object

        self.detector = buildCubeActor(position=(500, 400))
        self.renderer.AddActor(self.detector)
        self.objects_dic['detector'] = self.detector
        self.renderer.ResetCamera()


    def addInteractor(self):

        inStyle = CustomInteractor(self.renderer, self.vtkWidget.GetRenderWindow(), self.objects_dic)
        self.interactor.SetInteractorStyle(inStyle)

    def createMenu(self):
        main_menu = self.menuBar()
        file_menu = main_menu.addMenu('file')
        edit_menu = main_menu.addMenu('Edit')
        view_menu = main_menu.addMenu('View')
        help_menu = main_menu.addMenu('Help')

        save_action = QAction(QtGui.QIcon("Resources/saveIcon.png"), 'Save', self)
        save_action.setShortcut("Ctrl+S")
        file_menu.addAction(save_action)

    def initWindow(self):
        # self.setWindowIcon(QtGui.QIcon("letter.png")) ##Define a icon
        self.createMenu()
        self.setWindowIcon(self.icon)
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

    def contextMenuEvent(self, event):
        self.interactor.GetInteractorStyle().OnRightButtonDown(None, None)
        if(self.interactor.GetInteractorStyle().chosenPiece is not None):

            if(self.interactor.GetInteractorStyle().chosenPiece.GetProperty().GetColor() == (0.3, 0.3, 0.3)):
                object_type = "detector"
                object_type_trajectory = "detector_trajectory"
                contextMenu = QMenu(self)
                set_pos = contextMenu.addAction("set position")
                det_num = contextMenu.addAction("DetectorNumbers")
                set_trajectory = contextMenu.addAction("set trajectory")
                action = contextMenu.exec_(self.mapToGlobal(event.pos()))

                if action == set_pos:
                    pos_dialog = Dialogs()
                    pos_dialog.xyPosition()

                    if (pos_dialog.exec()):
                        x, y = pos_dialog.getxyInputs()
                        self.interactor.GetInteractorStyle().chosenPiece.SetPosition(x, y, 0)

                        if(object_type_trajectory in self.objects_dic):
                            self.updateTrajectorys(object_type, self.projections_number, self.objects_dic[object_type_trajectory][2])

                        self.interactor.GetInteractorStyle().updateObjects(self.objects_dic)


                elif action == det_num:
                    det_dialog = Dialogs()
                    det_dialog.detectorNumbers()
                    if(det_dialog.exec()):

                        numbers, size = det_dialog.getDetInputs()
                        x, y, _ = self.interactor.GetInteractorStyle().chosenPiece.GetPosition()
                        new_actor = buildCubeActor(position=(x, y, 0), x_length=numbers*size)
                        self.renderer.RemoveActor(self.interactor.GetInteractorStyle().chosenPiece)
                        self.renderer.AddActor(new_actor)
                        self.objects_dic[object_type] = new_actor
                        self.interactor.GetInteractorStyle().updateObjects(self.objects_dic)


                elif action == set_trajectory:
                    traj_dialog = Dialogs()
                    traj_dialog.actorTrajectory(self.projections_number)
                    if(traj_dialog.exec()):
                        projs, trajectory_type = traj_dialog.getTrajInputs()
                        self.projections_number = projs
                        if object_type_trajectory in self.objects_dic:
                            self.updateTrajectorys(object_type, projs, trajectory_type, object_type_trajectory)
                        else:
                            self.objects_dic[object_type_trajectory] = []
                            self.updateTrajectorys(object_type, projs, trajectory_type, object_type_trajectory)

            elif(self.interactor.GetInteractorStyle().chosenPiece.GetProperty().GetColor() == (1, 1, 1)):
                object_type = "source"
                object_type_trajectory = "source_trajectory"
                contextMenu = QMenu(self)
                set_pos = contextMenu.addAction("set position")
                set_trajectory = contextMenu.addAction("set trajectory")
                action = contextMenu.exec_(self.mapToGlobal(event.pos()))

                if action == set_pos:
                    pos_dialog = Dialogs()
                    pos_dialog.xyPosition()

                    if (pos_dialog.exec()):
                        x, y = pos_dialog.getxyInputs()
                        self.interactor.GetInteractorStyle().chosenPiece.SetPosition(x, y, 0)

                        if(object_type_trajectory in self.objects_dic):
                            self.updateTrajectorys(object_type, self.projections_number, self.objects_dic[object_type_trajectory][2])
                        self.interactor.GetInteractorStyle().updateObjects(self.objects_dic)

                elif action == set_trajectory:
                    traj_dialog = Dialogs()
                    traj_dialog.actorTrajectory(self.projections_number)

                    if(traj_dialog.exec()):
                        projs, trajectory_type = traj_dialog.getTrajInputs()
                        self.projections_number = projs
                        if object_type_trajectory in self.objects_dic:
                            self.updateTrajectorys(object_type, projs, trajectory_type, object_type_trajectory)
                        else:
                            self.objects_dic[object_type_trajectory] = []
                            self.updateTrajectorys(object_type, projs, trajectory_type, object_type_trajectory)


        self.interactor.GetInteractorStyle().OnRightButtonRelease(None, None)


    def updateTrajectorys(self, actual_object, projs, trajectory_type, object_type):
        radius = 100
        if ("source_trajectory" in self.objects_dic):
            object_type = "source_trajectory"
            if len(self.objects_dic[object_type]) != 0:
                if self.objects_dic[object_type][2] == "circle_trajectory":
                    radius = self.getRadiusCircle(object_type)
                elif self.objects_dic[object_type][2] == "straight_trajectory":
                    radius = self.getRadiusStraight(object_type)
                self.renderer.RemoveActor(self.objects_dic[object_type][0])
                self.renderer.RemoveActor(self.objects_dic[object_type][1])

            self.setActorTrajectory(self.objects_dic["source"], projs, trajectory_type, object_type, radius = radius)

        radius = 100
        if ("detector_trajectory" in self.objects_dic):
            object_type = "detector_trajectory"
            if len(self.objects_dic[object_type]) != 0:
                if self.objects_dic[object_type][2] == "circle_trajectory":
                    radius = self.getRadiusCircle(object_type)
                elif self.objects_dic[object_type][2] == "straight_trajectory":
                    radius = self.getRadiusStraight(object_type)
                self.renderer.RemoveActor(self.objects_dic[object_type][0])
                self.renderer.RemoveActor(self.objects_dic[object_type][1])

            self.setActorTrajectory(self.objects_dic["detector"], projs, trajectory_type, object_type, radius = radius)

        self.interactor.GetInteractorStyle().updateObjects(self.objects_dic)

    def setActorTrajectory(self, actor, projs, trajectory_type, object, radius = 100):
        if trajectory_type == "circle_trajectory":
            traj_dialog = Dialogs()
            traj_dialog.trajectoryRadius()
            print(radius)
            trajectory, trajectory_nodes = buildCircleTrajectory(projs, radius, actor.GetPosition(), object[:-11])
            self.renderer.AddActor(trajectory)
            self.renderer.AddActor(trajectory_nodes)
            self.objects_dic[object] = (trajectory, trajectory_nodes, "circle_trajectory")

        elif trajectory_type == "straight_trajectory":
            trajectory, trajectory_nodes = buildStraightTrajectory(projs, radius, actor.GetPosition(), object[:-11])
            self.renderer.AddActor(trajectory)
            self.renderer.AddActor(trajectory_nodes)
            print(radius)
            self.objects_dic[object] = (trajectory, trajectory_nodes, "straight_trajectory")
        elif trajectory_type == "custom_trajectory":
            trajectory = self.buildCustomTrajectory()

            
        self.interactor.GetInteractorStyle().updateObjects(self.objects_dic)
        self.renderer.ResetCamera()

        # if(trajectory_type == "custom_trajectory"):
        #     self.trajectory = ContourWidget()

    def getRadiusCircle(self, object_type):
        polydata = vtk.vtkPolyData.SafeDownCast(self.objects_dic[object_type][0].GetMapper().GetInput())
        projections = polydata.GetNumberOfPoints() // 10

        point1 = polydata.GetPoint(0)
        point2 = polydata.GetPoint(projections * 10 // 2)
        radius = round(point1[0] - point2[0]) / 2
        return radius

    def getRadiusStraight(self, object_type):
        polydata = vtk.vtkPolyData.SafeDownCast(self.objects_dic[object_type][0].GetMapper().GetInput())
        projections = polydata.GetNumberOfPoints() // 10

        point1 = polydata.GetPoint(0)
        point2 = polydata.GetPoint(projections * 10)
        radius = round(point2[0] - point1[0]) / 2
        return radius

    def buildCustomTrajectory(self):

        inStyle = ContourInteractor(self.renderer, self.vtkWidget.GetRenderWindow(), self.objects_dic)
        self.interactor.SetInteractorStyle(inStyle)

        # render_window = vtk.vtkRenderWindow()
        # render_window.AddRenderer(self.renderer)
        #
        # render_interactor = vtk.vtkRenderWindowInteractor()
        # self.vtkWidget.SetRenderWindow(render_window)
        # render_interactor.SetRenderWindow(self.vtkWidget.GetRenderWindow())
        #
        # contour_widget = vtk.vtkContourWidget()
        # contour_widget.SetInteractor(self.interactor.GetInteractorStyle())
        # contour_widget.CreateDefaultRepresentation()

        # self.interactor.SetInteractorStyle(render_interactor)
        # # render_interactor.Initialize()
        #
        # contour_widget.On()
        # # render_window.Render()
        #
        # # render_interactor.Start()
        # self.vtkWidget.show()

        # self.renderer.ResetCamera()
        # self.renderer.Delete()
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SimulationWindow({'projection': 'Single Slice 2D', 'rotate-conf': 'Conv Circular'})
    sys.exit(app.exec())
