# Produces
# - link_metadata.csv
# - link_metadata_withCounts.csv
# - link_duplicate.csv
# - per-link-data/<link>.csv

from pathlib import Path
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

# Data structures
per_link_data = {}
header = ['timestamp', 'load', '5-min-bin']
metadata = []
metadata_header = ['link', 'capacity', 'internal']
capacity = int(100) # 100 Gbps for all links
duplicate_link_IDs = [] # store the links that have duplicated IDs in the dataset
open('link_metadata.csv', 'w').close() # clear the file


# Start parsing
print("Extracting per-link utilization and metadata...")
for file in dataset_path.iterdir(): 
    file_count += 1

    # .. filter out log files lying around
    if (file.suffix == '.log'): continue

    # .. extract time data
    timestamp = int(file.stem.split('_')[2])
    bin = int(timestamp%seconds_per_day/bin_size)

    # read each file
    with open(file, "r") as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    # extract the data for each link
    for src in data:
        # The dataset contains duplicate labels for different links
        # This is most likely a bug from the data collection process
        # - Creating a unique label for each link does not work, 
        #   because it makes it impossible to connect links to 
        #   one another across files.
        # - Instead, we aggregate duplicate links and sum their load
        #   - This will be pessimistic wrt potential energy savings by turning
        #   links off.
        #   - It may also lead to links with more than 100% util.
        # - One alternative would be to aggregate using the maximum load.
        #   - This would "loose" some traffic
        # Note: we log the number of links with duplicate IDs, 
        # so we can get an idea of how big of an approximation this entails.
        ###
        label = -1
        for link in data[src]['links']:
            dst = link['peer']
            load = link['load']
            label = link['label']
            internal = (src[0].islower() and dst[0].islower())

            # build the link ID
            data_file_name = "{}_{}_{}".format(src,dst,label) 

            # store the metadata
            # -> duplicate entries will be removed before writing to file
            metadata.append([
                data_file_name,
                capacity,
                internal
            ])

            # # store the link data
            # if data_file_name in per_link_data: 
            #     last_timestamp = per_link_data[data_file_name][-1][0]
                
            #     # if the current and last timestamp match, 
            #     # we have a case of redundant links
            #     if last_timestamp == timestamp:
            #         # Add the load of the current link to what is already logged
            #         per_link_data[data_file_name][-1][1] += load
            #         # Save the link ID
            #         duplicate_link_IDs.append(data_file_name)

            #     else: # append to existing entry
            #         per_link_data[data_file_name].append([timestamp,load,bin])

            # else: # create a new entry
            #     per_link_data[data_file_name]=[[timestamp,load,bin]]

    # log progress
    if file_count%50 == 0:
        print('#file parsed: {} (out of {})'.format(file_count, total_files))
        # save wip and clear data structure to limit memory usage
        tmp = pd.DataFrame(metadata).drop_duplicates()
        tmp.to_csv('link_metadata.csv', header=False, index=False, mode='a')
        metadata = []

    # debugging
    if debug & (file_count == 10):
        break
                    
# Save the per-link data
print("... saving final metadata")

# .. save the metadata
# .. create data path if it does not exist already
tmp = pd.DataFrame(metadata, columns=metadata_header).drop_duplicates().sort_values(by='link')
tmp.to_csv('link_metadata.csv', index=False, mode='w')

tmp = pd.DataFrame(duplicate_link_IDs).drop_duplicates()
tmp.to_csv('link_duplicate.csv', index=False, mode='w')

# .. loop through the links
# print("... saving per-link data")
# data_path = Path('per-link-data')
# data_path.mkdir(parents=True, exist_ok=True)
# for link in per_link_data:

#     # .. load into pandas (allows easy dropping of duplicate entries)
#     # Note: we should anyway not have any duplicate anymore
#     tmp = pd.DataFrame(per_link_data[link], columns=header).drop_duplicates().sort_values(by='timestamp')

#     # .. generate file name
#     file_name = str(data_path / link)+'.csv'

#     # .. save as CSV
#     tmp.to_csv(file_name, index=False, mode='w')
print("... done.")


###
# Expand the metadata with counts
###
print("Add the link utilization counters...")
meta_file = 'link_metadata.csv'
meta_data = pd.read_csv(meta_file, names=metadata_header).drop_duplicates().sort_values(by='link')

# .. Create new columns in metadata
meta_data['below_10_count'] = 0
meta_data['below_25_count'] = 0
meta_data['below_50_count'] = 0
meta_data['above_50_count'] = 0
meta_data['total_count'] = 0

# .. Loop through all links
file_count = 0
total_files = len(meta_data)

for link in meta_data.link:
    # .. load the link data
    link_data = pd.read_csv(str(data_path/link)+'.csv')
    # .. compute the capacity bounds
    link_data['req_capacity'] = link_data['load'].apply(helper.capacity_bounds)
    req_capacity = link_data.groupby(by='req_capacity')['5-min-bin'].count()
    # .. save back into metadata
    if 10 in req_capacity: meta_data.loc[meta_data['link'] == link, 'below_10_count'] = req_capacity[10]
    if 25 in req_capacity: meta_data.loc[meta_data['link'] == link, 'below_25_count'] = req_capacity[25]
    if 50 in req_capacity: meta_data.loc[meta_data['link'] == link, 'below_50_count'] = req_capacity[50]
    if 100 in req_capacity: meta_data.loc[meta_data['link'] == link, 'above_50_count'] = req_capacity[100] 
    meta_data.loc[meta_data['link'] == link, 'total_count'] = len(link_data)
    
    # log progress
    file_count += 1
    if file_count%100 == 0:
        print('#file parsed: {} (out of {})'.format(file_count, total_files))

    # debugging
    if debug & (file_count == 10):
        break

meta_data.to_csv('link_metadata_withCounts.csv', index=False, mode='w')
print("... done.")