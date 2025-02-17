#!/bin/bash

python3 create_action_count.py --saved_folder /home/zwan63/Research/scalesim_v3_ispass/scale-sim-v2/test_runs --run_name scale_example_run_32x32_os --arch_name systolic_array --SRAM_row_size 2 --DRAM_row_size 2 --config /home/zwan63/Research/scalesim_v3_ispass/scale-sim-v2/configs/scale.cfg

cp /home/zwan63/Research/scalesim_v3_ispass/scale-sim-v2/test_runs/scale_example_run_32x32_os/action_count.yaml ./accelergy_input/action_count.yaml

rm -rf /home/zwan63/Research/scalesim_v3_ispass/scale-sim-v2/rundir-accelergy/output/scale_sim_output_scale_example_run_32x32_os

mv /home/zwan63/Research/scalesim_v3_ispass/scale-sim-v2/test_runs/scale_example_run_32x32_os  /home/zwan63/Research/scalesim_v3_ispass/scale-sim-v2/rundir-accelergy/output/scale_sim_output_scale_example_run_32x32_os

