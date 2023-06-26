#!/bin/python3
# Romain Jacob

from pathlib import Path
from pyDataverse.api import NativeApi, DataAccessApi
from pyDataverse.models import Dataverse

base_url = 'https://dataverse.uclouvain.be/'
DOI = "doi:10.14428/DVN/0LNXDQ"
download_path = Path('dataset')

api = NativeApi(base_url)
data_api = DataAccessApi(base_url)
dataset = api.get_dataset(DOI)

files_list = dataset.json()['data']['latestVersion']['files']

for file in files_list:
    filename = file["dataFile"]["filename"]
    file_id = file["dataFile"]["id"]
    print("File name {}, id {}".format(filename, file_id))

    response = data_api.get_datafile(file_id)
    with open(download_path/filename, "wb") as f:
        f.write(response.content)
