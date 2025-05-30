import numpy as np
from pymeasure.experiment.parameters import ListParameter

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

def np_hysteresis(low, high, step):
    """
    Aids in creating numpy area for hysteresis values.
    """
    up = np_linear(0, high, step)
    down = np_linear(high-step, low, -step)
    up2 = np_linear(low+step, high, step)
    down2 = np_linear(high-step, 0, -step)
    return np.concatenate((up,down,up2, down2))

if __name__ == "__main__":
    end_fields = ListParameter("End fields", units="T", default=[0,2,-2],choices=None)
    start_fields = ListParameter("Start fields", units="T", default=[2,-2,0],choices=None)
    field_steps = ListParameter("Field steps", units="T", default=[0.1,0.1,0.1],choices=None)
    print(tabular_values(start_values=start_fields, end_values=end_fields, step_values=field_steps))

    