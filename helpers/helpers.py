# Helper functions and variables for the whole project

from pathlib import Path
from datetime import datetime
import itertools
import pandas as pd

import helpers.power_model as pm

# Debug flag
# debug = True
debug = False

# Overall metadata
dataset_path = Path('europe')
seconds_per_day = 24*60*60
bin_size = 5*60 # 5-minute bins

# Data selection 

# .. for analysis
analysis_start = '2020-06-01'
analysis_end   = '2022-12-27'
# Date to timestamp conversion
def ymd_to_timestamp(value: str) -> int:
    dt = datetime.strptime(value, "%Y-%m-%d")
    return int(dt.timestamp())
start_ts = ymd_to_timestamp(analysis_start)
end_ts   = ymd_to_timestamp(analysis_end)

# .. for ploting
plot_start = '2020-11-01'
plot_end   = '2020-11-16'

# Define the bounds for the link capacity settings
def capacity_bounds(x):
    if x <= 10:
        return 10
    elif x <= 25:
        return 25
    # elif x <= 50:
    #     return 50
    else:
        return 100
    
def all_port_configs(number_of_ports, allow_sleeping=False):
    """Generate all possible permutation of port rate configs for a
    given number of ports. 
    When `allow_sleeping` is True, a port rate of `0` is allowed.
    """

    # Load the power model
    port_power, base_power = pm.power_model()

    # Prepare data structures
    rate_options = ['010', '025', '100']
    if allow_sleeping:
        rate_options.insert(0, '000')
    config_rate = []
    config_power = []

    # ..Generate all combinaisons
    for element in itertools.product(rate_options, repeat=number_of_ports):
        # .. compute the corresponding power
        power = 0
        for i in element:
            power += port_power[int(i)]['static_power']

        config_power.append(power)
        config_rate.append([int(e) for e in element])

    # .. Push in a dataframe
    df = pd.DataFrame(config_rate)

    # .. Compute the maximum rate 
    df['max_capacity'] = df.sum(axis=1)
    # .. Add the power value
    df['power'] = config_power
    # .. drop duplicate configs
    df.drop_duplicates(subset='max_capacity', keep='last', inplace=True)
    # .. sort
    df.sort_values(by='power', inplace=True)

    return df