from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow, QLabel, QLineEdit, QVBoxLayout, QMenu, QSizePolicy, QSpacerItem, QComboBox
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QAction

from enum import Enum

import sys

from fieldsweep_4probe import field_sweep_4_probe
from fieldsweep_4probe_lockin import field_sweep_4_probe_lockin
from iv_yokogawa import iv_yokogawa
from iv_keithley import iv_keithley
from tempsweep_4probe import temp_sweep_4_probe

from set_temperature import set_temperature
from set_current import set_current


class Experiment(Enum):
    FIELD_SWEEP_4_PROBE = "Field Sweep (4 Probe)"
    FIELD_SWEEP_4_PROBE_LOCKIN = "Field Sweep with Lock-in (4 Probe)"
    IV_YOKOGAWA = "IV (Yokogawa)"
    IV_KEITHLEY = "IV (Keithley)"
    TEMPSWEEP_4_PROBE = "Temperature Sweep (4 Probe)"
    SET_TEMPERATURE = "Set Temperature"
    SET_CURRENT = "Set Current"


experiments = {
    Experiment.FIELD_SWEEP_4_PROBE: field_sweep_4_probe,
    Experiment.FIELD_SWEEP_4_PROBE_LOCKIN: field_sweep_4_probe_lockin,
    Experiment.IV_YOKOGAWA: iv_yokogawa,
    Experiment.IV_KEITHLEY: iv_keithley,
    Experiment.TEMPSWEEP_4_PROBE: temp_sweep_4_probe,
    Experiment.SET_TEMPERATURE: set_temperature,
    Experiment.SET_CURRENT: set_current,
}


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
        exp_selector.addItems([exp.value for exp in Experiment])
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
                self.close()  # Close the main window after opening the experiment configuration window
            else:
                print("No experiment function found for:", self.chosen_experiment)
        else:
            print("No experiment selected.")
    

app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec()
