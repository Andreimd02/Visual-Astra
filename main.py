from src.view.SimulationWindow import SimulationWindow
from PyQt5.QtWidgets import QApplication
import sys

if len(sys.argv) > 1:
    command = sys.argv[1]

    if command == "teste":
        print('teste')
        app = QApplication(sys.argv)
        window = SimulationWindow({'projection': 'Single Slice 2D', 'rotate-conf': 'Conv Circular'})
        
        #create trajectorys
        object_type = "detector"
        projs = 30
        object_type_trajectory = "detector_trajectory"
        trajectory_type = "circle_trajectory"

        window.objects_dic[object_type_trajectory] = []
        window.updateTrajectorys(object_type, projs, trajectory_type, object_type_trajectory)

        object_type = "source"
        projs = 30
        object_type_trajectory = "source_trajectory"
        trajectory_type = "circle_trajectory"

        window.objects_dic[object_type_trajectory] = []
        window.updateTrajectorys(object_type, projs, trajectory_type, object_type_trajectory)



        sys.exit(app.exec())    


app = QApplication(sys.argv)
window = SimulationWindow({'projection': 'Single Slice 2D', 'rotate-conf': 'Conv Circular'})
sys.exit(app.exec())