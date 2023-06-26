# Produces
# - link_sleeping.csv

from pathlib import Path

import pandas as pd
import numpy as np
import yaml

import helpers.helpers as helper

# Load meta parameters
dataset_path = helper.dataset_path
seconds_per_day = helper.seconds_per_day
bin_size = helper.bin_size
debug = helper.debug

# Progress tracking
total_files = len(list(dataset_path.rglob('*')))
file_count = 0

# Data structures
stats = []
header = ['#links', 'sum_util', 'req_link_1way', 'req_link_2ways']
header_full = ['#links', 'sum_util', 'req_link_1way', 'req_link_2ways', 'timestamp']

# Start parsing
for file in dataset_path.iterdir(): 
    file_count += 1

    # .. filter out log files lying around
    if (file.suffix == '.log'): continue
    
    # .. extract time data
    timestamp = int(file.stem.split('_')[2])

    # dict = {key = src_dst, value = [ #links, sum_load ]}
    host_data = {}

    # read each file
    with open(file, "r") as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    # extract the data for each link
    for src in data:

        for link in data[src]['links']:
            dst = link['peer']
            load = link['load']

            # build the link ID (directional)
            link_ID = "{}_{}".format(src,dst) 

            # store the link data
            if link_ID in host_data: 
                # we already have a link, add load and increment
                host_data[link_ID][0] += 1
                host_data[link_ID][1] += load
            else:
                # add new link data
                host_data[link_ID] = [1, load]

    # Second pass, count the number of links required
    for host_pair in host_data:
        req_links = int(np.ceil(host_data[host_pair][1]/100))
        host_data[host_pair].append(req_links)

    # Third pass, get the max of the two directions
    for host_pair in host_data:
        end_points = host_pair.split('_')
        mirror_pair = end_points[1] + '_' + end_points[0]
        max_req = max(host_data[host_pair][2], host_data[mirror_pair][2])
        host_data[host_pair].append(max_req)

    # Compute the sum of links required
    # -> sum of all the last keys gives the number of required end points up
    #    that is, twice the number of links
    df = pd.DataFrame.from_dict(host_data, orient='index', columns=header)
    tmp = df.sum().tolist()
    tmp.append(timestamp)
    stats.append(tmp)

    # log progress
    if file_count%100 == 0:
        print('#file parsed: {} (out of {})'.format(file_count, total_files))

    # debugging
    if debug & (file_count == 10):
        break

# Save final data
file_id = 'link_sleeping'
file_name = file_id +'.csv'
tmp = pd.DataFrame(stats, columns=header_full)
tmp.to_csv(file_name, index=False, mode='w')