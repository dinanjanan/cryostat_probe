from time import sleep
from enum import Enum
import logging
import sys
import os

from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow, QLabel, QLineEdit, QVBoxLayout, QMenu, QSizePolicy, QSpacerItem, QComboBox
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QAction

# instrument imports
from local_instrument.keithley2182 import Keithley2182
from local_instrument.Yokogawa_GS200 import YokogawaGS200
from lakeshore import Model336
from local_instrument.Lakeshore_LS625 import ElectromagnetPowerSupply

# pymeasure imports for running the experiment
from pymeasure.experiment import Procedure, Results, unique_filename
from pymeasure.experiment.parameters import FloatParameter, Parameter, ListParameter
from pymeasure.display.Qt import QtWidgets
from pymeasure.display.windows import ManagedWindow
from pint import UnitRegistry
from pint.errors import UndefinedUnitError

import numpy as np

from helpers.common import HeaterSetting


current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)

# Set up logging
log = logging.getLogger("")
log.addHandler(logging.NullHandler())
log.setLevel(logging.INFO)

ureg = UnitRegistry()


class SetTemperatureWindow(QMainWindow):
    temperature = FloatParameter("Set temperature", units="K", default=9)
    heater_setting = ListParameter("Heater setting", choices=HeaterSetting.choices(), default=HeaterSetting.LOW)  # Low/Medium/High, to do with Lakeshore 336: refer SOP

    def __init__(self):
        super().__init__()

        self.button_checked = True

        self.setWindowTitle("Set LS336 Temperature")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        temp_label = QLabel("Temperature:")
        layout.addWidget(temp_label)

        self.temp_input = QLineEdit()
        self.temp_input.setPlaceholderText("Enter temperature in K")
        self.temp_input.setText("9 K")
        self.temp_input.setCursorPosition(len(self.temp_input.text()) - 2)  # Place cursor before 'K'
        self.temp_input.textChanged.connect(self.validate_input)
        self.temp_input.cursorPositionChanged.connect(self.ensure_unit_preserved)
        layout.addWidget(self.temp_input)

        setting_label = QLabel("Heater Setting:")
        layout.addWidget(setting_label)

        setting_selector = QComboBox()
        setting_selector.addItems(HeaterSetting.choices())
        setting_selector.currentTextChanged.connect(lambda text: self.on_setting_selected(text))
        layout.addWidget(setting_selector)

        execute_btn = QPushButton("Execute")

        execute_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # prevents stretching
        execute_btn.setCheckable(True)
        execute_btn.clicked.connect(self.on_execute_btn_clicked)
        execute_btn.setChecked(self.button_checked)
        execute_btn.setStyleSheet("padding: 10px 20px;")
        layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))  # pushes button up
        layout.addWidget(execute_btn)
        layout.setAlignment(execute_btn, Qt.AlignRight)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

    def ensure_unit_preserved(self):
        """Ensure that the cursor isn't allowed to change the unit."""
        text = self.temp_input.text()
        if self.temp_input.cursorPosition() >= len(text) - 1:
            # Move the cursor to the end of the value part
            self.temp_input.setCursorPosition(len(self.temp_input.text()) - 2)

    def validate_input(self):
        """Validate the input temperature and ensure it is in Kelvin."""
        text = self.temp_input.text()
        number = text.split()[0]
        try:
            cursor_position = self.temp_input.cursorPosition()
            print(number)
            if not number.replace('.', '', 1).isdigit() or len(text.split()) != 2:
                self.temp_input.setText(str(self.temperature))  # Reset to last valid temperature
            
            quantity = ureg.Quantity(text)
            val = abs(quantity.magnitude)
            if quantity.units != ureg.kelvin:
                log.error(f"Invalid unit: {quantity.units}. Expected Kelvin.")
                return
            self.temp_input.setText(f"{val} K")  # Update the input with the valid value
            # keep the cursor at the same position
            self.temp_input.setCursorPosition(cursor_position)
            self.temperature = quantity 
        except (UndefinedUnitError, ValueError) as e:
            self.temp_input.setText(str(self.temperature))  # Reset to last valid temperature


    def on_setting_selected(self, text):
        self.heater_setting = HeaterSetting(text)

    def on_execute_btn_clicked(self):
         # Initialize the instruments, see resources.ipynb
        self.tctrl = Model336(
            com_port="COM4"
        )  # COM 4 - this is the one that controls sample, magnet, and radiation
        log.info("Model 336 is read")
        self.magnet = ElectromagnetPowerSupply("GPIB0::11::INSTR")
        self.tctrl.reset_instrument()
        self.magnet.set_magnetic_field(0)
        
        # Configure LS336 and stabilize at min_temperature
        self.tctrl.set_heater_pid(2, *HeaterSetting.pid(self.heater_setting))  
        # intended for low setting, may need to adjust for high
        # .set_heater_setup Heater 1 @ 50 Ohm, 1 Amp
        self.tctrl.set_heater_setup(
            2,
            self.tctrl.HeaterResistance.HEATER_25_OHM,
            self.power_amp,
            self.tctrl.HeaterOutputUnits.POWER,
        )
        # .set_heater_output_mode Heater 1 @ closed loop mode, CHANNEL_A for sample stage, True - Remains on after power cycle (?)
        self.tctrl.set_heater_output_mode(
            2,
            self.tctrl.HeaterOutputMode.CLOSED_LOOP,
            self.tctrl.InputChannel.CHANNEL_A,
            True,
        )
        # setpoint to min temperature and wait until stabilize
        self.tctrl.set_setpoint_ramp_parameter(2, False, 0)
        self.tctrl.set_control_setpoint(2, self.temperature)
        self.tctrl.set_heater_range(2, HeaterSetting.range(self.heater_setting))

        # heat sample stage to set temperature
        while True:
            if self.should_stop():
                log.warning("Catch stop command in procedure")                
                return
            if abs(self.tctrl.get_all_kelvin_reading()[0] - self.temperature) < 0.05:
                log.info("Temperature reached, sleeping 10 seconds for stablization.")
                break
            else:
                log.info(f"Current temperature: {self.tctrl.get_all_kelvin_reading()[0]}")
                sleep(1)

        # Let sample stay at min_temperature for 10 seconds to stabilize
        sleep(10)
        if self.should_stop():
            log.warning("Catch stop command in procedure")                
            return
        
        # Check that temperature of the magnet is cold enough, otherwise show error and stop heating
        if self.tctrl.get_all_kelvin_reading()[1] > 5.1:
            log.warning("Catch stop command in procedure. Magnet overheated")
            self.tctrl.all_heaters_off()
            self.magnet.set_current(0)
            sys.exit()
        else:
            log.info(f"Magnet cooled at temperature {self.tctrl.get_all_kelvin_reading()[1]} K")

        log.info("Shutting down")
        self.magnet.set_magnetic_field(0)
        self.tctrl.disconnect_usb()
    

def set_temperature(mw):
    print("Running Set Temperature Utility...")
    mw.window = SetTemperatureWindow()
    mw.window.show()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = SetTemperatureWindow()
    window.show()
    app.exec_()
