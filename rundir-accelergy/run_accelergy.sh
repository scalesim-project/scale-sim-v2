accelergy accelergy_input/*.yaml accelergy_input/components/*.yaml -o accelergy_output/scale_example_run_32x32_os -v 1

rm -rf /home/zwan63/Research/SCALE-Sim-Accelergy/rundir-accelergy/output/accelergy_output_scale_example_run_32x32_os

mv ./accelergy_output/scale_example_run_32x32_os  /home/zwan63/Research/SCALE-Sim-Accelergy/rundir-accelergy/output/accelergy_output_scale_example_run_32x32_os

rm -rf ./accelergy_output

