from PyQt5.QtWidgets import QMainWindow, QMenu, QApplication, QFrame, QVBoxLayout, QAction
from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QIcon
from View.Dialogs import Dialogs
from BuildFunctions import *
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from interactor2d import CustomInteractor
from vtk.util import numpy_support
from AstraCustom import *
import sys
import math
import scipy.io as io
import skimage.io as io
import pylab
import time

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
        self.background_renderer = vtk.vtkRenderer()

        self.setBackground()
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

        self.image = None
        self.detector_numbers = 1

        self.show()
        self.interactor.Initialize()

    def setBackground(self):
        super_quadric = vtk.vtkSuperquadricSource()
        super_quadric.SetPhiRoundness(1.1)
        super_quadric.SetThetaRoundness(.2)

        super_quadric_mapper = vtk.vtkPolyDataMapper()
        super_quadric_mapper.SetInputConnection(super_quadric.GetOutputPort())


        super_quadric_actor = vtk.vtkActor()
        super_quadric_actor.SetMapper(super_quadric_mapper)

        self.background_renderer.SetLayer(0)
        self.background_renderer.InteractiveOff()
        self.renderer.SetLayer(1)

        self.vtkWidget.GetRenderWindow().SetNumberOfLayers(2)
        self.vtkWidget.GetRenderWindow().AddRenderer(self.background_renderer)
        self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)


        jpeg_reader = vtk.vtkJPEGReader()
        ## change to get a relative path
        jpeg_reader.SetFileName('/home/andrei/Área de Trabalho/Pesquisa/AstraUI/Resources/images.jpeg')
        jpeg_reader.Update()
        image_data = jpeg_reader.GetOutput()
        image_actor = vtk.vtkImageActor()
        image_actor.SetInputData(image_data)

        self.renderer.AddActor(super_quadric_actor)
        self.background_renderer.AddActor(image_actor)

        origin = image_data.GetOrigin()
        spacing = image_data.GetSpacing()
        extent = image_data.GetExtent()

        camera = self.background_renderer.GetActiveCamera()
        camera.ParallelProjectionOn()

        xc = origin[0] + 0.5 * (extent[0] + extent[1]) * spacing[0]
        yc = origin[1] + 0.5 * (extent[2] + extent[3]) * spacing[1]
        # xd = (extent[1] - extent[0] + 1) * spacing[0]
        yd = (extent[3] - extent[2] + 1) * spacing[1]
        d = camera.GetDistance()
        camera.SetParallelScale(0.5 * yd)
        camera.SetFocalPoint(xc, yc, 0.0)
        camera.SetPosition(xc, yc, d)

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

        play_action = QAction(QIcon("/home/andrei/Área de Trabalho/Pesquisa/AstraUI/Resources/play.png"), 'play', self)
        play_action.triggered.connect(self.playSimulation)
        toolbar = self.addToolBar("ToolBar")
        toolbar.addAction(play_action)

    def playSimulation(self):
        polydata_source = vtk.vtkPolyData.SafeDownCast(self.objects_dic['source_trajectory'][0].GetMapper().GetInput())
        projections = polydata_source.GetNumberOfPoints() // 10
        projections +=1
        polydata_detector = vtk.vtkPolyData.SafeDownCast(self.objects_dic['detector_trajectory'][0].GetMapper().GetInput())

        object = self.objects_dic['object']
        object_x, object_y, _ = object.GetCenter()
        src_vector = []
        det_vector = []
        u_vector = []

        traj_dialog = Dialogs()
        traj_dialog.trajectoryAngles()

        if traj_dialog.exec():
            angle_variation = traj_dialog.getTrajectoryAngles()


        angles = np.linspace(0, angle_variation, projections)

        det = self.objects_dic['detector']
        x_min, x_max, y_min, y_max, _, _ = det.GetBounds()
        angle = math.atan2(y_max - y_min, x_max - x_min) * 180
        angle = angle / math.pi

        for k in range(projections):
            src_x, src_y, _ = polydata_source.GetPoint(k*10)
            src_x = src_x - object_x
            src_y = src_y - object_y

            src_vector.append((src_x, src_y))

            det_x, det_y, _ = polydata_detector.GetPoint(k*10)
            det_x = det_x - object_x
            det_y = det_y - object_y

            det_vector.append((det_x, det_y))
            if k < projections-1:
                det.SetPosition((det_x, det_y, 0))
                det.RotateZ(angles[k] + angle + 90)
                x_min, x_max, y_min, y_max, _, _ = det.GetBounds()
                u_vector.append((x_min, y_min))
            else:
                u_vector.append(u_vector[0])

        # pylab.plot(np.array(src_vector)[:, 0], np.array(src_vector)[:, 1])
        # pylab.plot(np.array(det_vector)[:, 0], np.array(det_vector)[:, 1])
        # pylab.plot(np.array(u_vector)[:, 0], np.array(u_vector)[:, 1])
        # pylab.show()

        matrix = np.array([[src_vector[k][0], src_vector[k][1], det_vector[k][0], det_vector[k][1], u_vector[k][0], u_vector[k][1]] for k in range(projections)])

        # astra = Astra(self.image)
        fanflat_simulation(self.detector_numbers, matrix)

    def initWindow(self):
        # self.setWindowIcon(QtGui.QIcon("letter.png")) ##Define a icon
        self.createMenu()
        self.setWindowIcon(self.icon)
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

    def contextMenuEvent(self, event):
        self.interactor.GetInteractorStyle().OnRightButtonDown(None, None)
        if(self.interactor.GetInteractorStyle().chosenPiece is not None):

            actor_color = self.interactor.GetInteractorStyle().chosenPiece.GetProperty().GetColor()
            trajectory_colors = [(.8, .8, 0), (.5, .5, 0), (.8, .8, 1), (0.5, 0.0, 0.5)]
            detector_trajectory_colors = [(0.5, 0, 0.5), (.8, .8, 1)]
            source_trajectory_colors = [(.5, .5, 0), (.8, .8, 0)]

            #Detector color
            if(actor_color == (0.3, 0.3, 0)):
                object_type = "detector"
                object_type_trajectory = "detector_trajectory"
                contextMenu = QMenu(self)
                set_pos = contextMenu.addAction("Set position")
                det_num = contextMenu.addAction("DetectorNumbers")
                set_trajectory = contextMenu.addAction("Set trajectory")
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
                        self.detector_numbers = numbers
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

            #Source color
            elif(actor_color == (1, 1, 1)):
                object_type = "source"
                object_type_trajectory = "source_trajectory"
                contextMenu = QMenu(self)
                set_pos = contextMenu.addAction("Set position")
                set_trajectory = contextMenu.addAction("Set trajectory")
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

            elif actor_color in trajectory_colors:
                object_type = ""
                object_type_trajectory = ""

                if actor_color in detector_trajectory_colors:
                    object_type = "detector"
                    object_type_trajectory = "detector_trajectory"
                elif actor_color in source_trajectory_colors:
                    object_type = "source"
                    object_type_trajectory = "source_trajectory"


                contextMenu = QMenu(self)
                set_angle = contextMenu.addAction("Set Angles")

                action = contextMenu.exec_(self.mapToGlobal(event.pos()))

                if action == set_angle:
                    traj_dialog = Dialogs()
                    traj_dialog.trajectoryAngles()

                    if traj_dialog.exec():
                        angle_variation = traj_dialog.getTrajectoryAngles()
                        self.createTrajectorySimulation(angle_variation, self.objects_dic[object_type_trajectory], self.objects_dic[object_type])

            #object color
            elif actor_color == (0.9, 0.9, 0.9):
                contextMenu = QMenu(self)
                choose_image = contextMenu.addAction("Choose Image")

                action = contextMenu.exec_(self.mapToGlobal(event.pos()))

                if action == choose_image:

                    obj_dialog = Dialogs()
                    path = obj_dialog.getFilePath()

                    self.changeObjectImage(path)


        self.interactor.GetInteractorStyle().OnRightButtonRelease(None, None)

    def createTrajectorySimulation(self, angle_variation, trajectory_actors, actor):
        trajectory = trajectory_actors[0]
        trajectory_nodes = trajectory_actors[1]
        trajectory_type = trajectory_actors[2]

        trajectory_polydata = vtk.vtkPolyData.SafeDownCast(trajectory.GetMapper().GetInput())
        projection_numbers = trajectory_polydata.GetNumberOfPoints() // 10

        actor_polydata = vtk.vtkPolyData.SafeDownCast(actor.GetMapper().GetInput())
        new_actors = []

        angles = np.linspace(0, angle_variation, projection_numbers)
        for k in range(0, projection_numbers):
            point = trajectory_polydata.GetPoint(k*10)
            new_actor_polydata = vtk.vtkPolyData()
            new_actor_polydata.CopyStructure(actor_polydata)

            new_actor_mapper = vtk.vtkPolyDataMapper()
            new_actor_mapper.SetInputData(new_actor_polydata)

            new_actor = vtk.vtkActor()
            new_actor.SetMapper(new_actor_mapper)

            new_actor.SetPosition(point[0], point[1], 0)

            traj = self.objects_dic['detector']
            x_min, x_max, y_min, y_max, _, _ = traj.GetBounds()
            original_angle = math.atan2(y_max - y_min, x_max - x_min) * 180
            original_angle = original_angle / math.pi

            new_actor.RotateZ(angles[k] + original_angle + 90)
            new_actor.GetProperty().SetOpacity(0.1)
            new_actors.append(new_actor)
            self.renderer.AddActor(new_actor)

        self.objects_dic['trajectory_angles'] = new_actors
        self.interactor.GetInteractorStyle().updateObjects(self.objects_dic)

    def changeObjectImage(self, path):

        im = io.imread(path)
        self.image = im
        # im = io.imresize(im, 10)
        print (im)
        im = np.array(im)

        image_data = vtk.vtkImageData()
        image_array = numpy_support.numpy_to_vtk(im.ravel(), deep=True, array_type=vtk.VTK_UNSIGNED_CHAR)

        image_data.SetDimensions((im.shape[0], im.shape[1], 1))
        image_data.SetOrigin([0, 0, 0])
        image_data.GetPointData().SetScalars(image_array)

        image_filter = vtk.vtkImageDataGeometryFilter()
        image_filter.SetInputData(image_data)
        image_filter.Update()

        image_mapper = vtk.vtkPolyDataMapper()
        image_mapper.SetInputConnection(image_filter.GetOutputPort())

        image_actor = vtk.vtkActor()
        image_actor.SetMapper(image_mapper)
        image_actor.GetProperty().SetColor(0.9, 0.9, 0.9)
        self.renderer.RemoveActor(self.object)
        self.object = image_actor
        self.renderer.AddActor(self.object)

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
            trajectory, trajectory_nodes = buildCircleTrajectory(projs, radius, actor.GetPosition(), object[:-11])
            self.renderer.AddActor(trajectory)
            self.renderer.AddActor(trajectory_nodes)
            self.objects_dic[object] = (trajectory, trajectory_nodes, "circle_trajectory")

        elif trajectory_type == "straight_trajectory":
            trajectory, trajectory_nodes = buildStraightTrajectory(projs, radius, actor.GetPosition(), object[:-11])
            self.renderer.AddActor(trajectory)
            self.renderer.AddActor(trajectory_nodes)
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


    ##doesn't work yet because vtkRenderWindowInteractor have troubles to deal with vtkContourWidget
    def buildCustomTrajectory(self):

        render_window = vtk.vtkRenderWindow()
        render_window.AddRenderer(self.renderer)

        render_interactor = vtk.vtkRenderWindowInteractor()
        # self.vtkWidget.SetRenderWindow(render_window)
        render_interactor.SetRenderWindow(render_window)

        contour_widget = vtk.vtkContourWidget()
        contour_widget.SetInteractor(render_interactor)
        contour_widget.CreateDefaultRepresentation()

        render_interactor.Initialize()

        contour_widget.On()
        render_window.Render()

        render_interactor.Start()
        # contour_widget.Off()
        self.renderer.ResetCamera()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SimulationWindow({'projection': 'Single Slice 2D', 'rotate-conf': 'Conv Circular'})
    sys.exit(app.exec())
