# Produces
# - rate_adaptation_<start_date>_<end_date>.csv

from pathlib import Path
from datetime import datetime

import pandas as pd
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

# Setting the date range we use
start_date = helper.analysis_start
end_date   = helper.analysis_end
start_ts = helper.start_ts
end_ts   = helper.end_ts

# Data structures
stats = []
header = ['#links', 'util_1way', 'util_2ways']
header_full = ['timestamp', '10_count', '25_count', '100_count', 'total_count', ]

# Start parsing
for file in dataset_path.iterdir(): 
    file_count += 1

    # .. filter out log files lying around
    if (file.suffix == '.log'): continue

    # .. extract time data
    timestamp = int(file.stem.split('_')[2])

    # bound analysis to the desired date range
    if (timestamp < start_ts) or (timestamp > end_ts) :
        continue

    # dict = {key = src_dst_label, value = [ #links, sum_load ]}
    link_data = {}

    # read each file
    with open(file, "r") as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    # extract the data for each link
    label = -1
    for src in data:

        for link in data[src]['links']:
            dst = link['peer']
            load = link['load']
            label = link['label']

            # build the link ID (directional)
            link_ID = "{}_{}_{}".format(src,dst,label) 

            # store the link data
            if link_ID in link_data: 
                # we already have a link, add load and increment
                # -> that's a case of duplicated link label
                link_data[link_ID][0] += 1
                link_data[link_ID][1] += load
            else:
                # add new link data
                link_data[link_ID] = [1, load]

    # Second pass, get the max of the two directions
    for link_ID in link_data:
        end_points = link_ID.split('_')
        mirror_link_ID = end_points[1] + '_' + end_points[0] + '_' + end_points[2] 
        if mirror_link_ID in link_data:
            max_req = max(link_data[link_ID][1], link_data[mirror_link_ID][1])
        else: 
            max_req = link_data[link_ID][1]
        link_data[link_ID].append(max_req)

    # Compute the sum of links required
    # -> sum of all the last keys gives the number of required end points up
    #    that is, twice the number of links
    df = pd.DataFrame.from_dict(link_data, orient='index', columns=header)
    df['req_capacity'] = df['util_2ways'].apply(helper.capacity_bounds)
    req_capacity = df.groupby(by='req_capacity').count()['util_2ways']
    # .. save the counts
    tmp = [timestamp]
    if 10 in req_capacity: tmp.append(req_capacity[10]) 
    else: tmp.append(0)
    if 25 in req_capacity: tmp.append(req_capacity[25]) 
    else: tmp.append(0)
    if 100 in req_capacity: tmp.append(req_capacity[100]) 
    else: tmp.append(0)
    tmp.append(len(df))
    stats.append(tmp)

    # log progress
    if file_count%100 == 0:
        print('#file parsed: {} (out of {})'.format(file_count, total_files))

    # debugging
    if debug & (file_count >= 3):
        break

# Save final data
file_id = 'rate_adaptation'
file_name = file_id + '_' + start_date + '_' + end_date +'.csv'
tmp = pd.DataFrame(stats, columns=header_full)
tmp.to_csv(file_name, index=False, mode='w')