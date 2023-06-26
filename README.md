# Does rate adaptation at daily timescales make sense?

This repository contains the artifact accompanying the following paper:

> Romain Jacob, Jackie Lim, and Laurent Vanbever. 2023.  
_Does rate adaptation at daily timescales make sense?._  
In 2nd Workshop on Sustainable Computer Systems (HotCarbon ’23),  
July 9, 2023, Boston, MA, USA. ACM, New York, NY, USA, 7 pages.  
https://doi.org/10.1145/3604930.3605713

We provide a conda environment file to install all depencies required.

```bash
# Re-create the required environment
conda env create -n OVH --file environment.yml
# Activate it
conda activate OVH
```

The [`hotcarbon23.ipynb`](hotcarbon23.ipynb) walks through the analysis presented in the paper. Most likely, that is where you should start. 

All the scripts used for the analysis are provided: 

- [`helpers/download_OVH.py`](helpers/download_OVH.py) allows to conveniently download the entire OVH dataset (beware, it's about 54GB).
- `parse_*.py` are the scipts used to parse the dataset (not all are used at the moment). These scripts are not optimized; re-running them on the entire dataset takes a couple of days and a lot of memory. (Re)use at your own risk.
- `*.csv` are the script outputs, which we provide for convenience. 