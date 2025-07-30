
"""
Módulo interactor2d
-------------------
Define a classe CustomInteractor para manipulação de eventos de interação 2D
em ambientes VTK, permitindo seleção, rotação, escala e atualização de objetos
em simulações de tomografia.
"""

from .BuildFunctions import *
from src.settings import OBJECT_COLOR, SOURCE_COLOR, SOURCE_NODES_COLOR, SOURCE_TRAJECTORY_COLOR, DETECTOR_COLOR, DETECTOR_NODES_COLOR, DETECTOR_TRAJECTORY_COLOR

class CustomInteractor(vtk.vtkInteractorStyleTrackballActor):
    """Classe customizada para interação 2D com objetos VTK.

    Permite manipulação de seleção, rotação, escala e atualização de atores
    em uma cena VTK, utilizada em simulações de tomografia.
    """

    def __init__(self, renderer, renWin, objects_dic):
        """Inicializa o interator customizado.

        Args:
            renderer: Instância do renderer VTK.
            renWin: Instância da janela de renderização VTK.
            objects_dic: Dicionário de objetos da cena.
        """
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

        self.objects_dic = objects_dic
        self.renderer = renderer
        self.chosenPiece = None
        self.renWin = renWin

    def OnRightButtonDown(self, obj, eventType):
        """Evento de pressionar o botão direito do mouse.

        Seleciona o ator sob o cursor.
        """
        clickPos = self.GetInteractor().GetEventPosition()

        picker = vtk.vtkPropPicker()
        picker.Pick(clickPos[0], clickPos[1], 0, self.renderer)
        actor = picker.GetActor()
        self.chosenPiece = actor

    def OnRightButtonRelease(self, obj, eventType):
        """Evento de soltar o botão direito do mouse.

        Remove a seleção do ator.
        """
        self.chosenPiece = None

    def OnLeftButtonRelease(self, obj, eventType):
        """Evento de soltar o botão esquerdo do mouse.

        Remove seleção e apaga trajetórias de ângulos se necessário.
        """
        self.chosenPiece = None
        if self.erase_angles_demonstrator:
            for actor in self.objects_dic['trajectory_angles']:
                self.renderer.RemoveActor(actor)
            self.renderer.ResetCamera()
            self.erase_angles_demonstrator = False
            self.objects_dic['trajectory_angles'] = []
        vtk.vtkInteractorStyleTrackballActor.OnMiddleButtonUp(self)


    def OnLeftButtonDown(self, obj, eventType):
        """Evento de pressionar o botão esquerdo do mouse.

        Seleciona ator e prepara para apagar ângulos se necessário.
        """
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
        """Atualiza o dicionário de objetos da cena.

        Args:
            objects_dic: Novo dicionário de objetos.
        """
        self.objects_dic = objects_dic

    def OnMiddleButtonDown(self, obj, eventType):
        """Evento de pressionar o botão do meio do mouse.

        Seleciona ator e define modo de escala ou rotação.
        """
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
        """Evento de soltar o botão do meio do mouse.

        Finaliza escala ou rotação do ator.
        """
        self.chosenPiece = None
        self.rotation = False
        # Interactive Scale of the trajectory actors stand by
        if self.scale:
            self.scale = False
            vtk.vtkInteractorStyleTrackballActor.OnRightButtonUp(self)

    def OnMouseMove(self, obj, eventType):
        """Evento de movimentação do mouse.

        Aplica rotação, escala ou movimentação ao ator selecionado.
        """
        if self.chosenPiece is not None:
            actor_color = self.chosenPiece.GetProperty().GetColor()
            if self.rotation:
                if actor_color == DETECTOR_COLOR:
                    # Calcula a diferença de posição do mouse para aplicar rotação ao ator
                    mouse_pos_pas = self.GetInteractor().GetLastEventPosition()
                    mouse_pos = self.GetInteractor().GetEventPosition()
                    rotate_x = mouse_pos[0] - mouse_pos_pas[0]
                    self.chosenPiece.RotateZ(rotate_x)
                    self.renWin.Render()

            # Interactive Scale of the trajectory actors stand by
            elif self.scale:
                # Calcula a diferença de posição do mouse para aplicar escala à trajetória
                mouse_pos_pas = self.GetInteractor().GetLastEventPosition()
                mouse_pos = self.GetInteractor().GetEventPosition()
                scale_y = mouse_pos[1] - mouse_pos_pas[1]
                # Identifica se o ator é uma trajetória de detector ou fonte
                if actor_color == DETECTOR_TRAJECTORY_COLOR or actor_color[2] == 1:
                    # Atualiza a posição e escala da trajetória do detector
                    self.chosenPiece = self.objects_dic["detector"]
                    self.setTrajectoryPosition("detector_trajectory", scale_y)
                    self.chosenPiece = self.objects_dic["detector_trajectory"][0]

                elif actor_color == SOURCE_TRAJECTORY_COLOR or actor_color[2] == 0:
                    # Atualiza a posição e escala da trajetória da fonte
                    self.chosenPiece = self.objects_dic["source"]
                    self.setTrajectoryPosition("source_trajectory", scale_y)
                    self.chosenPiece = self.objects_dic["source_trajectory"][0]
                self.renWin.Render()
                self.renderer.ResetCamera()

            else:
                # Caso não seja rotação nem escala, delega movimentação padrão do VTK
                if actor_color != DETECTOR_TRAJECTORY_COLOR and actor_color != SOURCE_TRAJECTORY_COLOR and actor_color[0] != .8:
                    vtk.vtkInteractorStyleTrackballActor.OnMouseMove(self)

                    # Atualiza a posição da trajetória do detector se necessário
                    if actor_color == DETECTOR_COLOR:
                        if "detector_trajectory" in self.objects_dic:
                            self.setTrajectoryPosition("detector_trajectory")

                    # Atualiza a posição da trajetória da fonte se necessário
                    elif actor_color == SOURCE_COLOR:
                        if "source_trajectory" in self.objects_dic:
                            self.setTrajectoryPosition("source_trajectory")
                    self.renderer.ResetCamera()

        else:
            # Se nenhum ator estiver selecionado, executa movimentação padrão do VTK
            vtk.vtkInteractorStyleTrackballActor.OnMouseMove(self)

    def setTrajectoryPosition(self, trajectory_type, bonus_radius = 0):
        """Atualiza a posição da trajetória do ator selecionado.

        Args:
            trajectory_type: Tipo de trajetória ('detector_trajectory' ou 'source_trajectory').
            bonus_radius: Valor adicional para o raio da trajetória.
        """
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
