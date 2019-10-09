from PyQt5.QtWidgets import QMainWindow, QMenu, QDialog, QInputDialog, QApplication, QDialogButtonBox, QFrame, QVBoxLayout, QFormLayout, QAction, QPushButton, QLineEdit, QLabel
from PyQt5 import QtGui
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from interactor2d import CustomInteractor
import sys


''' a ordem eh monta a tela
    cria o frame do vtk
    chama o renderer
    cria os actors
    cria o interactor
    chama o loop
'''

def buildDiskActor(inner_radius = 0, outer_radius = 20, position = (100, 20), color = (1, 1, 1)):
    disk = vtk.vtkDiskSource()
    disk.SetInnerRadius(inner_radius)
    disk.SetOuterRadius(outer_radius)
    disk.SetRadialResolution(100)
    disk.SetCircumferentialResolution(100)
    disk.Update()

    mapper = vtk.vtkPolyDataMapper2D()
    mapper.SetInputConnection(disk.GetOutputPort())

    actor = vtk.vtkActor2D()
    actor.SetMapper(mapper)

    actor.SetPosition(position[0], position[1])

    actor.GetProperty().SetColor(color)

    return actor

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
        self.xraysource = buildDiskActor(position=(100, 130), color=(240, 240, 0))
        self.renderer.AddActor(self.xraysource)

        self.object = buildDiskActor(position=(350, 300), color=(0, 240, 240))
        self.renderer.AddActor(self.object)

        self.bar = buildDiskActor(position=(500, 400), color=(240, 0, 240))
        self.renderer.AddActor(self.bar)

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
    ##    save_action.triggered()

    def initWindow(self):
        # self.setWindowIcon(QtGui.QIcon("letter.png")) ##Define a icon
        self.createMenu()
        self.setWindowIcon(self.icon)
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

    def contextMenuEvent(self, event):
        self.interactor.GetInteractorStyle().OnRightButtonDown()
        if(self.interactor.GetInteractorStyle().chosenPiece is not None):
            contextMenu = QMenu(self)
            set_pos = contextMenu.addAction("set position")
            action = contextMenu.exec_(self.mapToGlobal(event.pos()))
            if action == set_pos:
                pos_dialog = PositionDialog()
                if(pos_dialog.exec()):
                    x, y =  pos_dialog.getInputs()
                    self.interactor.GetInteractorStyle().chosenPiece.SetPosition(x, y)
            self.interactor.GetInteractorStyle().chosenPiece = None

    def positionDialog(self):
        text, result = QInputDialog.getText(self, "Coordenadas", "Digite os valores de X e Y")
        if(result == True):
            return text

class PositionDialog(QDialog):
        def __init__(self, parent=None):
            super().__init__(parent)

            self.setWindowTitle("Chosse the coordinates")

            self.x = QLineEdit(self)
            self.y = QLineEdit(self)
            buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self);

            layout = QFormLayout(self)
            layout.addRow("X Axis", self.x)
            layout.addRow("Y axis", self.y)
            layout.addWidget(buttonBox)

            buttonBox.accepted.connect(self.accept)
            buttonBox.rejected.connect(self.reject)

        def getInputs(self):
            return (int(self.x.text()), int(self.y.text()))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SimulationWindow({'projection': 'Single Slice 2D', 'rotate-conf': 'Conv Circular'})
    sys.exit(app.exec())
