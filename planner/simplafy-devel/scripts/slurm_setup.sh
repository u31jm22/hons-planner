#!/bin/bash
module load miniconda3 
pushd ..
conda create --name simplafy --file requirements.txt python=3.11
popd