import vtk
import math

class CustomInteractor(vtk.vtkInteractorStyleTrackballActor):

    def __init__(self, renderer, renWin):
        super().__init__()
        self.AddObserver('LeftButtonPressEvent', self.OnLeftButtonDown)
        self.AddObserver('LeftButtonReleaseEvent', self.OnLeftButtonRelease)
        self.AddObserver('MouseMoveEvent', self.OnMouseMove)
        self.AddObserver('RightButtonPressEvent', self.OnRightButtonDown)
        self.AddObserver('RightButtonReleaseEvent', self.OnRightButtonRelease)
        self.AddObserver('MiddleButtonPressEvent', self.OnMiddleButtonDown)
        self.AddObserver('MiddleButtonReleaseEvent', self.OnMiddleButtonRelease)
        self.rotation = False

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
        vtk.vtkInteractorStyleTrackballActor.OnMiddleButtonDown(self)

    def OnMiddleButtonDown(self, obj, eventType):
        clickPos = self.GetInteractor().GetEventPosition()

        picker = vtk.vtkPropPicker()
        picker.Pick(clickPos[0], clickPos[1], 0, self.renderer)
        actor = picker.GetActor()
        self.chosenPiece = actor
        self.rotation = True

    def OnMiddleButtonRelease(self, obj, eventType):
        self.chosenPiece = None

    def OnMouseMove(self, obj, eventType):
        if self.rotation:
            if self.chosenPiece is not None:
                mouse_pos_pas = self.GetInteractor().GetLastEventPosition()
                mouse_pos = self.GetInteractor().GetEventPosition()
                rotate_x = mouse_pos[0] - mouse_pos_pas[0]

                self.chosenPiece.RotateZ(rotate_x)
                self.renWin.Render()

            else:
                vtk.vtkInteractorStyleTrackballActor.OnMouseMove(self)
        else:
            vtk.vtkInteractorStyleTrackballActor.OnMouseMove(self)