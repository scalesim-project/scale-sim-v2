#!/bin/bash

path="./"

sed -i "s/run_name = scale_example_run_32x32_os/run_name = scale_example_run_32x32_ws/" $path/configs/scale.cfg
sed -i "s/Dataflow : os/Dataflow : ws/" $path/configs/scale.cfg
sed -i "s/save_disk_space=True/save_disk_space=False/" $path/scalesim/scale.py
# sed -i "s/verbose=True/verbose=False/" $path/scalesim/scale.py

source $path/venv/bin/activate

python3 $path/scalesim/scale.py -c $path/configs/scale.cfg -t $path/topologies/conv_nets/alexnet_part.csv 

CMP1=$(cmp $path/../test_runs/scale_example_run_32x32_ws/BANDWIDTH_REPORT.csv $path/test/golden_trace/BANDWIDTH_REPORT.csv)
CMP2=$(cmp $path/../test_runs/scale_example_run_32x32_ws/COMPUTE_REPORT.csv $path/test/golden_trace/COMPUTE_REPORT.csv)
CMP3=$(cmp $path/../test_runs/scale_example_run_32x32_ws/DETAILED_ACCESS_REPORT.csv $path/test/golden_trace/DETAILED_ACCESS_REPORT.csv)
CMP4=$(cmp $path/../test_runs/scale_example_run_32x32_ws/layer0/FILTER_DRAM_TRACE.csv $path/test/golden_trace/layer0/FILTER_DRAM_TRACE.csv)
CMP5=$(cmp $path/../test_runs/scale_example_run_32x32_ws/layer0/FILTER_SRAM_TRACE.csv $path/test/golden_trace/layer0/FILTER_SRAM_TRACE.csv)
CMP6=$(cmp $path/../test_runs/scale_example_run_32x32_ws/layer0/IFMAP_DRAM_TRACE.csv $path/test/golden_trace/layer0/IFMAP_DRAM_TRACE.csv)
CMP7=$(cmp $path/../test_runs/scale_example_run_32x32_ws/layer0/IFMAP_SRAM_TRACE.csv $path/test/golden_trace/layer0/IFMAP_SRAM_TRACE.csv)
CMP8=$(cmp $path/../test_runs/scale_example_run_32x32_ws/layer0/OFMAP_DRAM_TRACE.csv $path/test/golden_trace/layer0/OFMAP_DRAM_TRACE.csv)
CMP9=$(cmp $path/../test_runs/scale_example_run_32x32_ws/layer0/OFMAP_SRAM_TRACE.csv $path/test/golden_trace/layer0/OFMAP_SRAM_TRACE.csv)


if [ "$CMP1" != "" ]; then
    echo "Output does not match!" 
    exit 125
elif [ "$CMP2" != "" ]; then
    echo "Output does not match!" 
    exit 125
elif [ "$CMP3" != "" ]; then
    echo "Output does not match!" 
    exit 125
elif [ "$CMP4" != "" ]; then
    echo "Output does not match!" 
    exit 125
elif [ "$CMP5" != "" ]; then
    echo "Output does not match!" 
    exit 125
elif [ "$CMP6" != "" ]; then
    echo "Output does not match!" 
    exit 125
elif [ "$CMP7" != "" ]; then
    echo "Output does not match!" 
    exit 125
elif [ "$CMP8" != "" ]; then
    echo "Output does not match!" 
    exit 125
elif [ "$CMP9" != "" ]; then
    echo "Output does not match!" 
    exit 125
fi
