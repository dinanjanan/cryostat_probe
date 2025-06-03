from enum import Enum

from lakeshore import Model336
from pymeasure.instruments.keithley.keithley6221 import Keithley6221

from local_instrument.keithley2182 import Keithley2182
from local_instrument.Yokogawa_GS200 import YokogawaGS200   
from local_instrument.Lakeshore_LS625 import ElectromagnetPowerSupply
from local_instrument.Stanford_SR830 import SR830

class LocalInstrument(Enum):
    KEITHLEY_2182 = "Keithley 2182"
    KEITHLEY_6221 = "Keithley 6221"
    YOKOGAWA_GS200 = "Yokogawa GS200"
    LAKESHORE_LS625 = "Lakeshore LS625"
    LAKESHORE_MODEL336 = "Lakeshore Model 336"
    STANFORD_SR830 = "Stanford SR830"

    def __str__(self):
        return self.value

    def choices():
        return [instrument.value for instrument in LocalInstrument]

instruments = {
    LocalInstrument.KEITHLEY_2182: Keithley2182,
    LocalInstrument.KEITHLEY_6221: Keithley6221,
    LocalInstrument.YOKOGAWA_GS200: YokogawaGS200,
    LocalInstrument.LAKESHORE_LS625: ElectromagnetPowerSupply,
    LocalInstrument.LAKESHORE_MODEL336: Model336,
    LocalInstrument.STANFORD_SR830: SR830,
}

instrument_ports = {
    LocalInstrument.KEITHLEY_2182: "GPIB::7",
    LocalInstrument.KEITHLEY_6221: "GPIB::17",
    LocalInstrument.YOKOGAWA_GS200: "GPIB::4",
    LocalInstrument.LAKESHORE_LS625: "GPIB0::11::INSTR",
    LocalInstrument.LAKESHORE_MODEL336: "COM4",
    LocalInstrument.STANFORD_SR830: "GPIB::8::INSTR",
}

class LocalInstrumentManager(object):
    """
    Singleton class to manage local instruments.
    Ensures that only one instance of each instrument is created and reused.
    """

    connected_instruments = {}

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(LocalInstrumentManager, cls).__new__(cls)
            cls.instance._connect_instruments()

        return cls.instance

    def _connect_instruments(self):
        self._keithley_2182 = self._attempt_instrument_connection(
            instruments[LocalInstrument.KEITHLEY_2182], 
            instrument_ports[LocalInstrument.KEITHLEY_2182]
        )
        self._keithley_6221 = self._attempt_instrument_connection(
            instruments[LocalInstrument.KEITHLEY_6221], 
            instrument_ports[LocalInstrument.KEITHLEY_6221]
        )
        self._yokogawa_gs200 = self._attempt_instrument_connection(
            instruments[LocalInstrument.YOKOGAWA_GS200], 
            instrument_ports[LocalInstrument.YOKOGAWA_GS200]
        )
        self._lakeshore_ls625 = self._attempt_instrument_connection(
            instruments[LocalInstrument.LAKESHORE_LS625], 
            instrument_ports[LocalInstrument.LAKESHORE_LS625]
        )
        self._lakeshore_model336 = self._attempt_instrument_connection(
            instruments[LocalInstrument.LAKESHORE_MODEL336], 
            instrument_ports[LocalInstrument.LAKESHORE_MODEL336]
        )
        self._stanford_sr830 = self._attempt_instrument_connection(
            instruments[LocalInstrument.STANFORD_SR830], 
            instrument_ports[LocalInstrument.STANFORD_SR830]
        )

    def _attempt_instrument_connection(self, local_ins_type: LocalInstrument, *args, **kwargs):
        """
        Attempts to connect to an instrument of the specified class at the given port specified by *args
        or **kwargs.

        Returns the instrument instance if successful, None otherwise.
        """
        try:
            self.connected_instruments[local_ins_type] = True
            return instruments[local_ins_type](*args, **kwargs)
        except Exception as e:
            self.connected_instruments[local_ins_type] = False
            if len(args) > 0: 
                port = args[0]
            else:
                port = kwargs.values()[0]

            print(f"Failed to connect to {local_ins_type} at {port}: {e}")
            return None
        
    def is_connected(self, local_ins_type: LocalInstrument):
        """
        Checks if the specified local instrument is connected.
        
        Args:
            local_ins_type (LocalInstrument): The type of the local instrument to check.
        
        Returns:
            bool: True if the instrument is connected, False otherwise.
        """
        return self.connected_instruments.get(local_ins_type, False)
    
    def get_instrument(self, local_ins_type: LocalInstrument):
        """
        Returns the instrument instance if it is connected, otherwise returns None.
        
        Args:
            local_ins_type (LocalInstrument): The type of the local instrument to retrieve.
        
        Returns:
            Instrument instance or None if not connected.
        """
        if self.connected_instruments.get(local_ins_type):
            return getattr(self, f"_{local_ins_type.name.lower()}")
        else:
            return None

    def reset_instruments(self):
        if self.connected_instruments.get(LocalInstrument.KEITHLEY_6221):
            self._keithley_6221.reset()
        
        if self.connected_instruments.get(LocalInstrument.YOKOGAWA_GS200):
            self._yokogawa_gs200.source_level = 0
            self._yokogawa_gs200.source_enabled = False
            self._yokogawa_gs200.reset()
            
        if self.connected_instruments.get(LocalInstrument.KEITHLEY_2182):
            self._keithley_2182.reset()

        if self.connected_instruments.get(LocalInstrument.LAKESHORE_LS625):
            self._lakeshore_ls625.set_magnetic_field(0)
        
        if self.connected_instruments.get(LocalInstrument.LAKESHORE_MODEL336):
            # Usually does not need to be reset, just do it at shutdown.
            pass 
        
        if self.connected_instruments.get(LocalInstrument.STANFORD_SR830):
            self._stanford_sr830.reset()

    def close_instruments(self):
        self.reset_instruments()

        if self.connected_instruments.get(LocalInstrument.YOKOGAWA_GS200):
            self._yokogawa_gs200.shutdown()

        if self.connected_instruments.get(LocalInstrument.LAKESHORE_MODEL336):
            self._lakeshore_model336.set_control_setpoint(2, 0)
            self._lakeshore_model336.set_setpoint_ramp_parameter(2, False, 0)
            self._lakeshore_model336.all_heaters_off()
            self._lakeshore_model336.reset_instrument()
            self._lakeshore_model336.disconnect_usb()
