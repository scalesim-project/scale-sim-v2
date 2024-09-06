accelergy accelergy_input/*.yaml accelergy_input/components/*.yaml -o accelergy_output/scale_example_run_32x32_os -v 1

mv ./accelergy_output/scale_example_run_32x32_os  scale-sim-v2/output/accelergy_output_scale_example_run_32x32_os

rm -rf ./accelergy_output

