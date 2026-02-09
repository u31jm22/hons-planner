#!/bin/bash
pushd ..

BASE=`pwd`
echo ${BASE}
export PYTHONPATH=PYTHONPATH:`pwd`/src

mkdir -p tmp/prodcell
mkdir -p tmp/blocksworld
pushd src
python -m generators.prodcell.prodcell -p 4 -fb 1 -tb 7 -b 2 -pb 1 -f pddl "${BASE}/tmp/prodcell"
python -m generators.blocksworld.blocksworld -fb 3 -tb 8 -st 3 -f pddl "${BASE}/tmp/blocksworld"
# python -m generators.prodcell.prodcell -p 4 -fb 1 -tb 4 -b 2 -pb 1 -f pddl ${BASE}/tmp/prodcell
# python -m generators.blocksworld.blocksworld -fb 3 -tb 5 -st 3 -f pddl ${BASE}/tmp/blocksworld