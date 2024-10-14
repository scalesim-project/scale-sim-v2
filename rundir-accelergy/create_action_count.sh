#!/bin/bash

python3 create_action_count.py --saved_folder scale-sim-v2/test_runs --run_name scale_example_run_32x32_os --arch_name systolic_array --SRAM_row_size 2 --DRAM_row_size 2 --config scale-sim-v2/configs/scale.cfg

cp scale-sim-v2/test_runs/scale_example_run_32x32_os/action_count.yaml ./accelergy_input/action_count.yaml

mv scale-sim-v2/test_runs/scale_example_run_32x32_os  scale-sim-v2/output/scale_sim_output_scale_example_run_32x32_os

