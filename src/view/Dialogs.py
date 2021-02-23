from PyQt5.QtWidgets import QDialog, QLineEdit, QDialogButtonBox, QFormLayout, QLabel, QRadioButton, QGridLayout, QFileDialog

class Dialogs(QDialog):
        def __init__(self, parent=None):
            super().__init__(parent)

        def detectorNumbers(self):
            self.setWindowTitle("Choose the number of detectors")

            self.numbers = QLineEdit(self)
            self.size = QLineEdit(self)
            buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)

            layout = QFormLayout(self)
            layout.addRow("Number of Detectors", self.numbers)
            layout.addRow("Size of each Detector", self.size)
            layout.addWidget(buttonBox)

            buttonBox.accepted.connect(self.accept)
            buttonBox.rejected.connect(self.reject)

        def getDetInputs(self):
            return (int(self.numbers.text()), int(self.size.text()))

        def actorTrajectory(self, proj_numbers):
            self.setWindowTitle("Choose the Trajectory configuration")

            buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)


            label_projections = QLabel("Number of Projections:")
            self.projections = QLineEdit(self)

            label_trajectory = QLabel("Trajectory Type: ")
            self.circle_button = QRadioButton("Circle Trajectory")
            self.circle_button.setChecked(True)
            self.straight_button = QRadioButton("Straight Trajectory")
            self.custom_button = QRadioButton("Custom Trajectory")

            if (proj_numbers != None):
                self.projections.setText(str(proj_numbers))

            grid_layout = QGridLayout()
            grid_layout.addWidget(label_projections, 1, 0)
            grid_layout.addWidget(self.projections, 1, 1)
            grid_layout.addWidget(label_trajectory, 2, 0)
            grid_layout.addWidget(self.circle_button, 2, 1)
            grid_layout.addWidget(self.straight_button, 3, 1)
            grid_layout.addWidget(self.custom_button, 4, 1)
            grid_layout.addWidget(buttonBox, 5, 1)

            self.setLayout(grid_layout)

            buttonBox.accepted.connect(self.accept)
            buttonBox.rejected.connect(self.reject)

        def getTrajInputs(self):
            if(self.circle_button.isChecked()):
                return (int(self.projections.text()), "circle_trajectory")
            elif(self.straight_button.isChecked()):
                return (int(self.projections.text()), "straight_trajectory")
            elif(self.custom_button.isChecked()):
                return (int(self.projections.text()), "custom_trajectory")
            # else:
            #     return error

        def trajectoryAngles(self):
            self.setWindowTitle("choose the angle variation during projection")
            self.setGeometry(200, 500, 400, 100)

            self.angle = QLineEdit(self)
            buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
            label = QLabel("To leave this mode just left click anywhere")
            label.setStyleSheet('color: red')
            layout = QFormLayout(self)
            layout.addRow("Angle Variation:", self.angle)
            layout.addWidget(label)
            layout.addWidget(buttonBox)

            buttonBox.accepted.connect(self.accept)
            buttonBox.rejected.connect(self.reject)

        def getTrajectoryAngles(self):
            return (int(self.angle.text()))

        def xyPosition(self):
            self.setWindowTitle("Choose the coordinates")

            self.x = QLineEdit(self)
            self.y = QLineEdit(self)
            buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)

            layout = QFormLayout(self)
            layout.addRow("X Axis", self.x)
            layout.addRow("Y axis", self.y)
            layout.addWidget(buttonBox)
            buttonBox.accepted.connect(self.accept)
            buttonBox.rejected.connect(self.reject)


        def getxyInputs(self):
            return (int(self.x.text()), int(self.y.text()))

        def getFilePath(self):
            fname = QFileDialog.getOpenFileName(self, 'Open file','/home', "*.png *.jpg")
            image_path = fname[0]
            return image_path