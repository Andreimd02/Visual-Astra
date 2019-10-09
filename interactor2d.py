import vtk

class CustomInteractor(vtk.vtkInteractorStyleTrackballCamera):

    def __init__(self, renderer, renWin):
        self.AddObserver('LeftButtonPressEvent', self.OnLeftButtonDown)
        self.AddObserver('LeftButtonReleaseEvent', self.OnLeftButtonRelease)
        self.AddObserver('MouseMoveEvent', self.OnMouseMove)

        self.renderer = renderer
        self.chosenPiece = None
        self.renWin = renWin

    def OnRightButtonDown(self):
        clickPos = self.GetInteractor().GetEventPosition()

        picker = vtk.vtkPropPicker()
        picker.Pick(clickPos[0], clickPos[1], 0, self.renderer)
        actor = picker.GetActor2D()
        self.chosenPiece = actor
        vtk.vtkInteractorStyleTrackballCamera.OnRightButtonDown(self)

    def OnRightButtonRelease(self):
        self.chosenPiece = None
        vtk.vtkInteractorStyleTrackballCamera.OnRightButtonUp(self)

    def OnLeftButtonRelease(self, obj, eventType):
        print(self.chosenPiece.GetPosition())
        self.chosenPiece = None
        vtk.vtkInteractorStyleTrackballCamera.OnLeftButtonUp(self)

    def OnLeftButtonDown(self, obj, eventType):
        clickPos = self.GetInteractor().GetEventPosition()

        picker = vtk.vtkPropPicker()
        picker.Pick(clickPos[0], clickPos[1], 0, self.renderer)
        actor = picker.GetActor2D()
        self.chosenPiece = actor
        vtk.vtkInteractorStyleTrackballCamera.OnLeftButtonDown(self)

    def OnMouseMove(self, obj, eventType):
        if self.chosenPiece is not None:

            mousePos = self.GetInteractor().GetEventPosition()

            self.chosenPiece.SetPosition(mousePos[0], mousePos[1])

            self.renWin.Render()
        else :
            vtk.vtkInteractorStyleTrackballCamera.OnMouseMove(self)

