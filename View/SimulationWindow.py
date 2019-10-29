from PyQt5.QtWidgets import QMainWindow, QMenu, QApplication, QFrame, QVBoxLayout, QAction
from PyQt5 import QtGui
from View.Dialogs import Dialogs
from BuildFunctions import *
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from interactor2d import CustomInteractor
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

        self.initWindow()

        #VTKInteractor
        self.frame = QFrame()
        self.vl = QVBoxLayout()
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.vl.addWidget(self.vtkWidget)

        ##Vtk
        self.renderer = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)

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

        self.object = buildDiskActor(position=(350, 300))
        self.renderer.AddActor(self.object)

        self.detector = buildCubeActor(position=(500, 400))
        self.renderer.AddActor(self.detector)

        self.renderer.ResetCamera()


    def addInteractor(self):

        inStyle = CustomInteractor(self.renderer, self.vtkWidget.GetRenderWindow())
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
            ## checa se é um detector
            if(self.interactor.GetInteractorStyle().chosenPiece.GetProperty().GetColor() == (0.3, 0.3, 0.3)):
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

                elif action == det_num:
                    det_dialog = Dialogs()
                    det_dialog.detectorNumbers()
                    if(det_dialog.exec()):

                        numbers, size =  det_dialog.getDetInputs()
                        x, y, _ = self.interactor.GetInteractorStyle().chosenPiece.GetPosition()
                        new_actor = buildCubeActor(position=(x, y, 0), x_length=numbers*size)
                        self.renderer.RemoveActor(self.interactor.GetInteractorStyle().chosenPiece)
                        self.renderer.AddActor(new_actor)

                elif action == set_trajectory:
                    traj_dialog = Dialogs()
                    traj_dialog.actorTrajectory(self.projections_number)
                    if(traj_dialog.exec()):
                        projs, trajectory_type = traj_dialog.getTrajInputs()
                        self.projections_number = projs
                        # trocar projections_number dos dois detectors
                        self.setActorTrajectory(self.interactor.GetInteractorStyle().chosenPiece, projs, trajectory_type)


            else:
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

                elif action == set_trajectory:
                    traj_dialog = Dialogs()

                    traj_dialog.actorTrajectory(self.projections_number)
                    if(traj_dialog.exec()):
                        projs, trajectory_type = traj_dialog.getTrajInputs()
                        self.projections_number = projs
                        # trocar projections_number dos dois detectors
                        self.setActorTrajectory(self.interactor.GetInteractorStyle().chosenPiece, projs, trajectory_type)

        self.interactor.GetInteractorStyle().OnRightButtonRelease(None, None)

    def setActorTrajectory(self, actor, projs, trajectory_type):
        if(trajectory_type == "circle_trajectory"):
            self.trajectory, self.trajectory_nodes = buildCircleCurve(projs, 100, actor.GetPosition())
            self.renderer.AddActor(self.trajectory)
            self.renderer.AddActor(self.trajectory_nodes)
            self.renderer.ResetCamera()

        # if(trajectory_type == "custom_trajectory"):
        #     self.trajectory = ContourWidget()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SimulationWindow({'projection': 'Single Slice 2D', 'rotate-conf': 'Conv Circular'})
    sys.exit(app.exec())
