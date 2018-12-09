#!/bin/bash

# you need to have anaconda installed first

# create a conda environment for publications (pubs)
conda create --name pubs python=2.7
# activate conda environment
source activate pubs
# install packages
conda install netcdf4 ipython matplotlib numpy scipy terminaltables seaborn pandas basemap
# setup conda env in jupyter notebook
conda install ipykernel
python -m ipykernel install --name pubs --display-name Python2(pubs)
