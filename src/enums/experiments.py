from enum import Enum

from experiments.fieldsweep_4probe import field_sweep_4_probe
from experiments.fieldsweep_4probe_lockin import field_sweep_4_probe_lockin
from experiments.iv_yokogawa import iv_yokogawa
from experiments.iv_keithley import iv_keithley
from experiments.tempsweep_4probe import temp_sweep_4_probe

from experiments.set_temperature import set_temperature
from experiments.set_current import set_current

class Experiment(Enum):
    FIELD_SWEEP_4_PROBE = "Field Sweep (4 Probe)"
    FIELD_SWEEP_4_PROBE_LOCKIN = "Field Sweep with Lock-in (4 Probe)"
    IV_YOKOGAWA = "IV (Yokogawa)"
    IV_KEITHLEY = "IV (Keithley)"
    TEMPSWEEP_4_PROBE = "Temperature Sweep (4 Probe)"
    SET_TEMPERATURE = "Set Temperature"
    SET_CURRENT = "Set Current"

    def __str__(self):
        return self.value
    
    def choices(): 
        return [experiment.value for experiment in Experiment]


experiments = {
    Experiment.FIELD_SWEEP_4_PROBE: field_sweep_4_probe,
    Experiment.FIELD_SWEEP_4_PROBE_LOCKIN: field_sweep_4_probe_lockin,
    Experiment.IV_YOKOGAWA: iv_yokogawa,
    Experiment.IV_KEITHLEY: iv_keithley,
    Experiment.TEMPSWEEP_4_PROBE: temp_sweep_4_probe,
    Experiment.SET_TEMPERATURE: set_temperature,
    Experiment.SET_CURRENT: set_current,
}
