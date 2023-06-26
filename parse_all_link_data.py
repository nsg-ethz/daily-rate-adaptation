# Produces
# - all_link_data.csv

from pathlib import Path
from datetime import datetime

import pandas as pd

import helpers.helpers as helper

# Load meta parameters
plot_range_start = helper.plot_start
plot_range_end = helper.plot_end
debug = helper.debug

# Load metadata
data_path = Path('per-link-data')
meta_file = 'link_metadata.csv'
meta_data = pd.read_csv(meta_file)

# Concatenate all link_data
df_list = []

# Build up the figure
file_count = 0
total_files = len(meta_data)
for link_id in meta_data['link']:

    # .. load the link data
    link_data = pd.read_csv(str(data_path/link_id)+'.csv')
    link_data['timestamp'] = pd.to_datetime(link_data['timestamp'],unit='s')
    link_data.set_index('timestamp', inplace=True)
    
    # .. filter for the date range of interest
    link_data = link_data.loc[plot_range_start < link_data.index]
    link_data = link_data.loc[link_data.index  < plot_range_end]
    
    df_list.append(link_data)

    # log progress
    file_count +=1
    if file_count%100 == 0:
        print('#file parsed: {} (out of {})'.format(file_count, total_files))

    if debug & (file_count == 100):
        break


# Save final data
file_id = 'all_link_data'
file_name = file_id + '_' + plot_range_start + '_' + plot_range_end +'.csv'
all_link_data = pd.concat(df_list)
all_link_data.to_csv(file_name, index=False, mode='w')
