import numpy as np
from pymeasure.experiment.parameters import ListParameter

from enums.sweep_type import SweepType

def np_linear(min_value, max_value, step_value):
    # Calculate the number of points
    num_points = abs(int(np.round((max_value - min_value) / step_value))) + 1
    
    # Handle cases where num_points might be less than 1
    if num_points < 1:
        raise ValueError("Invalid range or step value resulting in non-positive number of points.")
    
    # Use np.linspace to generate the values
    values = np.linspace(min_value, max_value, num_points)
    
    return values

def tabular_values(start_values, end_values, step_values):
    if len(start_values) != len(end_values) or len(start_values) != len(step_values):
        raise ValueError("Start values, end values, and step values must all have the same length.")
    
    values = []
    for i in range(len(start_values)):
        new_values = list(np_linear(start_values[i], end_values[i], step_values[i]))
        if values and new_values[0] == values[-1]:
            new_values = new_values[1:]
        values += new_values
    
    return np.array(values)                      

def np_hysteresis(low, high, step, type = SweepType.B1):
    result = {}
    up = np_linear(0, high, step)
    down = np_linear(high-step, low, -step)
    up2 = np_linear(low+step, high, step)
    down2 = np_linear(high-step, 0, -step)
    
    if type == SweepType.B1:
        up2 = np_linear(low+step, 0, step)
        result = {
            "fields": np.concatenate((up, down, up2)),
            "passover": []
        }
    elif type == SweepType.B2:
        result = {
            "fields": np.concatenate((up, down, up2)),
            "passover": [down2]
        }
    elif type == SweepType.B3:
        result = {
            "fields": np.concatenate((down, up2)),
            "passover": [up, down2]
        }

    return result


if __name__ == "__main__":
    end_fields = ListParameter("End fields", units="T", default=[0,2,-2],choices=None)
    start_fields = ListParameter("Start fields", units="T", default=[2,-2,0],choices=None)
    field_steps = ListParameter("Field steps", units="T", default=[0.1,0.1,0.1],choices=None)
    print(tabular_values(start_values=start_fields, end_values=end_fields, step_values=field_steps))

    