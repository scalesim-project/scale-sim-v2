## Getting Started
.

### 30 seconds to SCALE-Sim!

Getting started is simple! SCALE-Sim is completely written in python. At the moment, it has dependencies on the following python packages. Make sure you have them in your environment.

* os
* subprocess
* numpy
* math
* configparser
* tqdm


### Custom Experiment

* Fill in the config file, scale.cfg with proper values.
* Move into "scale_sim_simulator" sub-directory
* Run the command: ```python scale.py```
* Wait for the run to finish

The config file scale.cfg contains two sections, architecture presets and network presets.  
Here is sample of the config file.  
![sample config](https://raw.githubusercontent.com/AnandS09/SCALE-Sim/master/images/config_example.png "sample config")  
Architecture presets are the variable parameters for SCALE-Sim, like array size, memory etc.

Network preset contains just one field for now, that is the path to the topology csv file.  
SCALE-Sim accepts topology csv in the format shown below.  
![yolo_tiny topology](https://raw.githubusercontent.com/AnandS09/SCALE-Sim/master/images/yolo_tiny_csv.png "yolo_tiny.csv")

Since SCALE-Sim is a CNN simulator please do not provide any layers other than convolutional or fully connected in the csv.
You can take a look at
[yolo_tiny.csv](https://raw.githubusercontent.com/AnandS09/SCALE-Sim/master/topologies/yolo_tiny.csv)
for your reference.

### Output

Here is an example output dumped to stdout when running Yolo Tiny (whose configuration is in yolo_tiny.csv):
![screen_out](https://github.com/AnandS09/SCALE-Sim/blob/master/images/output.png "std_out")

Also, the simulator generates read write traces and summary logs at ```./scale_sim_simulator/outputs/<run_name>/```.
There are three summary logs:

* Layer wise runtime and average utilization
* Layer wise MAX DRAM bandwidth log
* Layer wise AVG DRAM bandwidth log
* Layer wise breakdown of data movement and compute cycles

In addition cycle accurate SRAM/DRAM access logs are also dumped and could be accesses at ```./scale_sim_simulator/outputs/<run_name>/```

## Detailed Documentation
For detailed insights on using SCALE-Sim, you can refer to this [paper](https://arxiv.org/abs/1811.02883)

## Using MNK Operands
If a user would like to use SCALE-Sim to run non-CNN layers, scale_sim_simulator/run_nets_mnk.py has the logic to input custom IFMAP (input activations), FILTER (weights), OFMAP (output activations) in a GEMM format
* Run the command: ```python run_nets_mnk.py```
