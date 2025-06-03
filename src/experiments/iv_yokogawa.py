#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

"""
This example demonstrates how to make a graphical interface to preform
IV characteristic measurements. There are a two items that need to be
changed for your system:

1) Correct the GPIB addresses in IVProcedure.startup for your instruments
2) Correct the directory to save files in MainWindow.queue

Run the program by changing to the directory containing this file and calling:

python iv_yokogawa.py

IF YOUR NANOVOLTMETER STOPS WORKING AND SHOWS PERIODIC NOISE,
HIT THE DCV1 BUTTON A LOT AND MAYBE DCV2 BUTTOM SOME NUMBER OF TIMES.

Good luck!
"""

import sys
from time import sleep
import numpy as np
import sys
import os
from datetime import date
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)

from local_instrument.Yokogawa_GS200 import YokogawaGS200
from local_instrument.keithley2182 import Keithley2182
from pymeasure.display.Qt import QtWidgets
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import (
    Procedure, FloatParameter, unique_filename, Results
)
from helpers.helper_functions import np_hysteresis
import logging
log = logging.getLogger('')
log.addHandler(logging.NullHandler())


class IVYokoProcedure(Procedure):

    max_current = FloatParameter('Maximum Current', units='A', default=2e-3)
    min_current = FloatParameter('Minimum Current', units='A', default=-2e-3)
    current_step = FloatParameter('Current Step', units='A', default=2e-5)
    delay = FloatParameter('Delay Time', units='ms', default=20)
    sample = "YBCO1"

    DATA_COLUMNS = ['Current (A)', 'Voltage (V)', 'Resistance (ohm)']

    def startup(self):
        log.info("Setting up instruments")
        self.meter = Keithley2182("GPIB::7")
        self.meter.reset()
        
        self.meter.active_channel = 1
        self.meter.channel_function = "voltage"
        
        self.meter.ch_1.setup_voltage(auto_range=True, nplc=1)
        # self.meter.select_input_terminal()#"FRONT") 
        self.source = YokogawaGS200("GPIB::4")
        self.source.reset()
        # Enable the source
        self.source.source_enabled = True

        # Set the source mode to 'current'
        self.source.source_mode = 'current'

        # Set the source range to an appropriate value
        self.source.source_range = self.max_current*5

        # Set the current limit (if needed, for safety)
        self.source.current_limit = self.max_current*1.2

        
        
        log.info("Set up complete!")
        sleep(1)

    def execute(self):
        currents=np_hysteresis(self.min_current, self.max_current, self.current_step)
        
        steps = len(currents)

        log.info("Starting to sweep through current")
        for i, current in enumerate(currents):
            log.debug("Measuring at current: %g mA" % current)
            self.source.source_range = self.max_current*1.2
            self.source.source_level = current
            self.source.source_enabled = True
            # Or use self.source.ramp_to_current(current, delay=0.1)
            sleep(self.delay * 1e-3)

            voltage = self.meter.voltage
            if abs(current) <= 1e-10:
                resistance = np.nan
            else:
                resistance = voltage / current
            data = {
                'Current (A)': current,
                'Voltage (V)': voltage,
                'Resistance (ohm)': resistance
            }
            self.emit('results', data)
            self.emit('progress', 100. * i / steps)
            if self.should_stop():
                log.warning("Catch stop command in procedure")
                break

    def shutdown(self):
        
        self.source.source_level = 0
        self.source.source_enabled = False
        self.source.reset()
        
        log.info("Finished")


class IVYokoWindow(ManagedWindow):

    def __init__(self):
        super().__init__(
            procedure_class=IVYokoProcedure,
            inputs=[
                'max_current', 'min_current', 'current_step',
                'delay',
            ],
            displays=[
                'max_current', 'min_current', 'current_step',
                'delay', 
            ],
            x_axis='Current (A)',
            y_axis='Voltage (V)'
        )
        self.setWindowTitle('IV Measurement')

    def queue(self):
        directory = "./"  # Change this to the desired directory
        filename = unique_filename(directory, prefix="IV")

        procedure = self.make_procedure()
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)

        self.manager.queue(experiment)


def iv_yokogawa(mw):
    """Run the IV Yoko procedure."""
    mw.window = IVYokoWindow()
    mw.window.show()
    

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = IVYokoWindow()
    window.show()
    sys.exit(app.exec())
