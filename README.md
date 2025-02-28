# SCALE-Sim + Accerlegy Integration for Enabling Energy and Power Estimation of Systolic CNN-Accelerator

## Requirement

### Install SCALE-Sim

Please install SCALE-Sim following the instructions in the main branch: https://github.com/scalesim-project/scale-sim-v2/tree/main 

### Install Accelergy

Please install Accelergy following the instructions in their github repo
https://github.com/Accelergy-Project/accelergy 

For more accurate estimation, please install accelergy-plug-ins for 3rd party, technology-based estimators
CACTI - https://github.com/Accelergy-Project/accelergy-cacti-plug-in.git 
Aladdin - https://github.com/Accelergy-Project/accelergy-aladdin-plug-in.git

## Run

Run the following command:

```$ cd rundir-accelergy ```

```$ ./run_all.sh -c <path_to_config_file> -t <path_to_topology_file> -p <path_to_scale-sim_log_dir> -o <path_to_output_dir> ```

For Example: 

```$ ./run_all.sh -c ../configs/scale.cfg -t ../topologies/conv_nets/test.csv -p ../test_runs/ -o ./output ```

## Tool Inputs
### Configuration File
The configuration file is used to specify the architecture and run parameters for the simulations. 

Built based upon SCALE-Sim, we add additional parameters for action count extraction.
* SRAM_row_size: the size of the row buffer (block) that each SRAM access loads
* SRAM_bank_size: temporal capacity for the memory to keep previously-accessed data (with more than one row buffer per bank)
* DRAM_row_size, _bank_size: same concept as SRAM

The rest of the parameters are the same as (https://github.com/scalesim-project/scale-sim-v2).

### Topology File
The topology file is a CSV file which decribes the layers of the workload topology.
For more details, please refer to (https://github.com/scalesim-project/scale-sim-v2) 

### Additional compound components for Accelergy
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

## Contributing to the project

We are happy for your contributions and would love to merge new features into our stable codebase. To ensure continuity within the project, please consider the following workflow.

When contributing to this repository, please first discuss the change you wish to make via issue,
email, or any other method with the owners of this repository before making a change.

### Pull Request Process

1. Ensure any install or build dependencies are removed before the end of the layer when doing a
   build. Please do not commit temporary files to the repo.
2. Update the documentation in the documentation/-folder with details of changes to the interface, this includes new environment
   variables, exposed ports, useful file locations and container parameters.
3. Add a tutorial how to use your new feature in form of a jupyter notebook to the documentation, as well. This makes sure that others can use your code!
4. Add test cases to our unit test system for your contribution.
5. Increase the version numbers in any example’s files and the README.md to the new version that this
   Pull Request would represent. The versioning scheme we use is [SemVer](http://semver.org/). Add your changes to the CHANGELOG.md. Address the issue numbers that you are solving.
4. You may merge the Pull Request in once you have the sign-off of two other developers, or if you
   do not have permission to do that, you may request the second reviewer to merge it for you.


## Developers

Main devs:
* Ananda Samajdar (@AnandS09)
* Jan Moritz Joseph (@jmjos)

Contributers:
* Ritik Raj (@ritikraj7)
* Zishen Wan (@zishenwan)

Maintainers and Advisors
* Yuhao Zhu
* Paul Whatmough
* Tushar Krishna

Past contributors
* Vineet Nadella
* Sachit Kuhar
