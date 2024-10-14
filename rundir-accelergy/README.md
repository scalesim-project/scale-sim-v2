# ECE6115-ICN-Project

## "SCALE-Sim + Accelergy: Enabling Timing Predictability and Energy Estimation of Systolic CNN-Accelerator"

## Requirement
### Python Environment setup
absl-py,
tqdm,
configparser,
numpy,
pandas,
cython,
PyYAML

### Install SCALE-Sim

Assumed already done

### Install Accelergy

Please install Accelergy following the instructions in their github repo
https://github.com/Accelergy-Project/accelergy 

For more accurate estimation, please install accelergy-plug-ins for 3rd party, technology-based estimators
CACTI - https://github.com/Accelergy-Project/accelergy-cacti-plug-in.git 
Aladdin - https://github.com/Accelergy-Project/accelergy-aladdin-plug-in.git

## Run
You need to provode 

    (1) SCALE-Sim configuration (edit './scale.cfg' to speficy systolic array configuration)

    (2) SCALE-Sim topology (choose one of the workload topology from '../topologies/') 

    (3) output directory (the directory name for results)

If you're running it on MacOS and cannot process -realpath in the bash code, run\
```$brew install coreutils```

Run the following command.  

```$ ./run_all.sh -c <path_to_config_file> -t <path_to_topology_file> -p <path_to_scale-sim_log_dir> -o <path_to_output_dir> ```

For Example, 

```$ ./run_all.sh -c ../configs/scale.cfg -t ../topologies/conv_nets/test.csv -p ../test_runs/ -o ./output ```

## Inputs
### Configuration File ( TODO : should be fixed )
Similar to SCALE-Sim, though we have some additional parameters for action count extraction.
Under "*run_preset*" section, 
* SRAM_row_size: the size of the row buffer (block) that each SRAM access loads
* SRAM_bank_size: temporal capacity for the memory to keep previously-accessed data (with more than one row buffer per bank)
* DRAM_row_size, _bank_size: same concept as SRAM, but DRAM energy estimation is not yet supproted
For mor details, pleaes refer to our report section 4.

The rest of the parameters are the same as (https://github.com/scalesim-project/scale-sim-v2) 

### Topology File
Same as SCALE-Sim, the topology file is a CSV file that describes the workload topology.
For more details, please refer to (https://github.com/scalesim-project/scale-sim-v2) 

### Additional compound components for Accelergy (Future Work)
If any other kinds fo compound componetns are to be included, please add them to ```./accelergy_input/components```
For more details, please refer to (http://accelergy.mit.edu/)

## Result
### Files
In the output directory,
* scale_sim_out_<run_name> contains performance results in .csv format. Summary in ```COMPUTE_REPORT.csv```
* accelergy_out_<run_name> contains energy estimation results in .yaml format. Summary in  ```energy_estimation.yaml```
More details can be found from each framework's github link.

### Visualization
```$ jupyter-notebook gen_plot.ipynb``` 
will also help to anaylize the result. Currently set to the example case (see the Single Run section).

## Others ( TODO : should be fixed)
### Modified files from the original source code
* scale-sim-v2-mod/scalesim/memory/double_buffered_scratchpad_mem.py
* scale-sim-v2-mod/scalesim/memory/double_buffered_scratchpad_mem_old.py 
* scale-sim-v2-mod/scalesim/memory/read_buffer.py
