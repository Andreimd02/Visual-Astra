from src.view.SimulationWindow import SimulationWindow
from PyQt5.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)
window = SimulationWindow({'projection': 'Single Slice 2D', 'rotate-conf': 'Conv Circular'})
sys.exit(app.exec())