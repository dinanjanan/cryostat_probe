from enum import Enum
from lakeshore import Model336

class HeaterSetting(Enum):
    LOW = "Low (PID: 50, 50, 0 ; Range: Low)"
    MEDIUM = "Medium (PID: 100, 50, 0 ; Range: Medium)"
    HIGH = "High (PID: 100, 50, 0 ; Range: High)"

    def __str__(self):
        return self.value
    
    @classmethod
    def pid(self, setting):
        if setting == HeaterSetting.LOW:
            return (50, 50, 0)
        elif setting == HeaterSetting.MEDIUM:
            return (100, 50, 0)
        elif setting == HeaterSetting.HIGH:
            return (100, 50, 0)
        
    @classmethod
    def range(self, setting):
        if setting == HeaterSetting.LOW:
            return Model336.HeaterRange.LOW
        elif setting == HeaterSetting.MEDIUM:
            return Model336.HeaterRange.MEDIUM
        elif setting == HeaterSetting.HIGH:
            return Model336.HeaterRange.HIGH

    @classmethod
    def choices(cls):
        return [choice.value for choice in cls]

class CurrentSource(Enum):
    YOKOGAWA_GS200 = "Yokogawa GS200"
    KEITHLEY_2600 = "Keithley 2600"

    def __str__(self):
        return self.value

    @classmethod
    def choices(cls):
        return [choice.value for choice in cls]