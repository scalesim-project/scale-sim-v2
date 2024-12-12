#!/bin/bash
topology="topologies/conv_nets/${1}.csv"
python3 scalesim/scale.py -c ./configs/google.cfg -t ${topology}
python3 scripts/dram_sim.py -topology $1
python3 scripts/dram_latency.py -topology $1
python3 scalesim/scale.py -c ./configs/google_ramulator.cfg -t ${topology}

