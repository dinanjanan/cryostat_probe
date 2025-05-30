from time import sleep
import logging

from PySide6.QtWidgets import QWidget, QPushButton, QMainWindow, QLabel, QLineEdit, QVBoxLayout, QSizePolicy, QSpacerItem, QComboBox
from PySide6.QtCore import Qt

# instrument imports
from local_instrument.Yokogawa_GS200 import YokogawaGS200

# pymeasure imports for running the experiment
from pymeasure.experiment.parameters import FloatParameter, ListParameter
from pymeasure.display.Qt import QtWidgets
from pint import UnitRegistry
from pint.errors import UndefinedUnitError

from common import CurrentSource

# Set up logging
log = logging.getLogger("")
log.addHandler(logging.StreamHandler()) # Send logs to the console
log.setLevel(logging.INFO)

ureg = UnitRegistry()

class SetCurrentWindow(QMainWindow):
    source_choice = ListParameter("Source", choices=CurrentSource.choices(), default=next(iter(CurrentSource.choices())))
    current_limit = FloatParameter("Current limit", units="A", default=0)
    current = FloatParameter("Set current", units="A", default=0)

    def __init__(self):
        super().__init__()

        self.button_checked = True

        self.setWindowTitle("Set Current")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        setting_label = QLabel("Source:")
        layout.addWidget(setting_label)

        source_selector = QComboBox()
        source_selector.addItems(CurrentSource.choices())   # Add more sources: "Keithley 2600"
        source_selector.currentTextChanged.connect(lambda text: self.on_source_selected(text))
        layout.addWidget(source_selector)

        curr_limit_label = QLabel("Current Limit:")
        layout.addWidget(curr_limit_label)

        self.curr_limit_input = QLineEdit()
        self.curr_limit_input.setText("0 A")
        self.curr_limit_input.setCursorPosition(len(self.curr_limit_input.text()) - 2)  # Place cursor before 'A'
        self.curr_limit_input.textChanged.connect(lambda: self.validate_input(self.curr_limit_input))
        self.curr_limit_input.cursorPositionChanged.connect(lambda: self.ensure_unit_preserved(self.curr_limit_input))
        layout.addWidget(self.curr_limit_input)
        
        curr_label = QLabel("Current Limit:")
        layout.addWidget(curr_label)

        self.curr_input = QLineEdit()
        self.curr_input.setText("0 A")
        self.curr_input.setCursorPosition(len(self.curr_input.text()) - 2)  # Place cursor before 'A'
        self.curr_input.textChanged.connect(lambda: self.validate_input(self.curr_input))
        self.curr_input.cursorPositionChanged.connect(lambda: self.ensure_unit_preserved(self.curr_input))
        layout.addWidget(self.curr_input)

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

    def on_source_selected(self, source):
        self.source_choice = CurrentSource(source)
        print(self.source_choice)

    def ensure_unit_preserved(self, text_input):
        """Ensure that the cursor isn't allowed to change the unit."""
        text = text_input.text()
        if text_input.cursorPosition() >= len(text) - 1:
            # Move the cursor to the end of the value part
            text_input.setCursorPosition(len(text_input.text()) - 2)

    def validate_input(self, text_input):
        """Validate the input temperature and ensure it is in Kelvin."""
        text = text_input.text()
        number = text.split()[0]

        try:
            cursor_position = text_input.cursorPosition()
            print(number)
            if not number.replace('.', '', 1).isdigit() or len(text.split()) != 2:
                # Reset to last valid value
                if text_input == self.curr_limit_input:
                    text_input.setText(str(self.current_limit))
                else:
                    text_input.setText(str(self.current))
            
            quantity = ureg.Quantity(text)
            val = abs(quantity.magnitude)
            if quantity.units != ureg.ampere:
                log.error(f"Invalid unit: {quantity.units}. Expected Ampere.")
                return
            text_input.setText(f"{val} A")  # Update the input with the valid value
            # keep the cursor at the same position
            text_input.setCursorPosition(cursor_position)

            if text_input == self.curr_limit_input:
                self.current_limit = quantity
            else:
                self.current = quantity
        except (UndefinedUnitError, ValueError) as e:
            # Reset to last valid value
                if text_input == self.curr_limit_input:
                    text_input.setText(str(self.current_limit))
                else:
                    text_input.setText(str(self.current))

    def on_execute_btn_clicked(self):
        if self.source_choice == CurrentSource.YOKOGAWA_GS200:    
            self.source = YokogawaGS200("GPIB::4")
            self.source.reset()
            self.source.source_mode = "current"
            self.source.source_range = self.current_limit
            self.source.source_level = self.set_current
            self.source.current_limit = self.current_limit
            self.source.source_enabled = True
        elif self.source_choice == CurrentSource.KEITHLEY_2600:
            log.error("Keithley 2600 support is not implemented yet.")
    

def set_current(mw):
    print("Running Field Sweep 4 Probe experiment...")
    mw.window = SetCurrentWindow()
    mw.window.show()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = SetCurrentWindow()
    window.show()
    app.exec_()
