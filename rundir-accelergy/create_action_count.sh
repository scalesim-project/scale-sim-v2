#!/bin/bash

python3 create_action_count.py --saved_folder /home/zwan63/Research/SCALE-Sim-Accelergy/test_runs --run_name scale_example_run_32x32_os --arch_name systolic_array --SRAM_row_size 2 --DRAM_row_size 2 --config /home/zwan63/Research/SCALE-Sim-Accelergy/configs/scale.cfg

cp /home/zwan63/Research/SCALE-Sim-Accelergy/test_runs/scale_example_run_32x32_os/action_count.yaml ./accelergy_input/action_count.yaml

rm -rf /home/zwan63/Research/SCALE-Sim-Accelergy/rundir-accelergy/output/scale_sim_output_scale_example_run_32x32_os

cp -rf /home/zwan63/Research/SCALE-Sim-Accelergy/test_runs/scale_example_run_32x32_os  /home/zwan63/Research/SCALE-Sim-Accelergy/rundir-accelergy/output/scale_sim_output_scale_example_run_32x32_os

