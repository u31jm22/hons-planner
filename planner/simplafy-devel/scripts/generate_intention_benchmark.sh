#!/bin/bash
pushd ..

BASE=`pwd`
echo ${BASE}
export PYTHONPATH=PYTHONPATH:`pwd`/src

mkdir -p tmp/prodcell
mkdir -p tmp/blocksworld
mkdir -p tmp/miconic
mkdir -p tmp/satellite
pushd src
# python -m generators.prodcell.prodcell -p 4 -fb 1 -tb 4 -b 2 -pb 1 -g 2 -i -f intention ${BASE}/tmp/prodcell
# python -m generators.blocksworld.blocksworld -fb 3 -tb 5 -st 3 -g 2 -i -f intention ${BASE}/tmp/blocksworld
python -m generators.prodcell.prodcell -p 4 -fb 2 -tb 6 -b 2 -pb 1 -g 2 -i -f intention "${BASE}/tmp/prodcell"
python -m generators.blocksworld.blocksworld -fb 3 -tb 9 -st 3 -g 2 -i -f intention "${BASE}/tmp/blocksworld"
python -m generators.miconic.miconic -f 10 -fp 2 -tp 10 -g 2 -i -o intention "${BASE}/tmp/miconic"
# Nasty manual generation of satellite benchmarks TODO Fix this
python -m generators.satellite.satellite 45 2 5 2 2 2 --format intention -o "${BASE}/tmp/satellite"
python -m generators.satellite.satellite 46 3 5 2 2 2 --format intention -o "${BASE}/tmp/satellite"
python -m generators.satellite.satellite 47 4 5 2 2 2 --format intention -o "${BASE}/tmp/satellite"
python -m generators.satellite.satellite 48 5 5 2 2 2 --format intention -o "${BASE}/tmp/satellite"
python -m generators.satellite.satellite 49 6 5 2 2 2 --format intention -o "${BASE}/tmp/satellite"
# python -m generators.prodcell.prodcell 4 4 10 2 1 2 ${BASE}/tmp/prodcell