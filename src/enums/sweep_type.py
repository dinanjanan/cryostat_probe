from enum import Enum

class SweepType(Enum):
    """
    Defines the different types of field sweeps.
    """
    
    B1 = "B1"
    """Starts at 0 and performs one full cycle."""
    B2 = "B2"
    """Starts at 0, and performs one and a quarter cycles, ending at the maximum."""
    B3 = "B3"
    """Starts at the maximum and performs one full cycle, ending at the maximum."""

    def __str__(self):
        return self.value

    def choices():
        """
        Returns a list of all available sweep types.
        """
        return [sweep_type.value for sweep_type in SweepType]
