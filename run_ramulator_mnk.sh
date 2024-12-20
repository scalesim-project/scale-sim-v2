#!/bin/bash
topology="topologies/models/${1}.csv"
python3 scalesim/scale.py -c ./configs/google.cfg -t ${topology} -i gemm > ${1}_${2}_orig_out
python3 scripts/dram_sim.py -topology $1
python3 scripts/dram_latency.py -topology $1
python3 scalesim/scale.py -c ./configs/google_ramulator_${2}.cfg -t ${topology} -i gemm > ${1}_${2}_stall_out
cp ${1}_${2}_orig_out ./results/dram_results/stall_cycles
cp ${1}_${2}_stall_out ./results/dram_results/stall_cycles
