from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow, QLabel, QLineEdit, QVBoxLayout, QMenu, QSizePolicy, QSpacerItem, QComboBox
from PySide6.QtCore import Qt

import sys

from enums.experiments import Experiment, experiments

class MainWindow(QMainWindow):
    chosen_experiment = next(iter(Experiment))  # Default to the first experiment

    def __init__(self):
        super().__init__()

        self.button_checked = True

        self.setWindowTitle("Cryostat Experiment Manager")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        label = QLabel("Select an experiment to run:")
        layout.addWidget(label)

        exp_selector = QComboBox()
        exp_selector.addItems(Experiment.choices())
        exp_selector.currentTextChanged.connect(lambda text: self.on_experiment_selected(text))
        layout.addWidget(exp_selector)

        next_btn = QPushButton("Continue")

        next_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # prevents stretching
        next_btn.setCheckable(True)
        next_btn.clicked.connect(lambda: self.on_next_btn_clicked())
        next_btn.setChecked(self.button_checked)
        next_btn.setStyleSheet("padding: 10px 20px;")
        layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))  # pushes button up
        layout.addWidget(next_btn)
        layout.setAlignment(next_btn, Qt.AlignRight)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

    def on_experiment_selected(self, text):
        self.chosen_experiment = Experiment(text)

    def on_next_btn_clicked(self):
        if self.chosen_experiment:
            experiment_func = experiments.get(self.chosen_experiment)
            if experiment_func:
                experiment_func(self)
                # self.close()  # Close the main window after opening the experiment configuration window
            else:
                print("No experiment function found for:", self.chosen_experiment)
        else:
            print("No experiment selected.")
    

app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec()
