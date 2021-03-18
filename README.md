# Systolic CNN AcceLErator Simulator (SCALE Sim) v2

SCALE Sim is a simulator for systolic array based accelerators for Convolution, Feed Forward, and any layer that uses GEMMs.
This is a refreshed version of the simulator with feature enhancements, restructured code to aid feature additions, and ease of distribution.

The previous version of the simulator can be found [here](https://github.com/ARM-software/SCALE-Sim).

## Getting started in 30 seconds

### *Installing the package*

Getting started is simple! SCALE-Sim is completely written in python and is available both as a package and could be run from source.

You can install SCALE-Sim in your environment using the following command

```$ pip3 install scalesim```

Alternatively you can install the package from the source as well

```$ python3 setup.py install```

### *Launching a run*

SCALE-Sim can be run by using the ```scale.py``` script from the repository and providing the paths to the architecture configuration, and the topology descriptor csv file.

```$ python3 scale.py -c <path_to_config_file> -t <path_to_topology_file>```

Try it now in this jupyter [notebook](https://github.com/scalesim-project/scalesim-tutorial-materials/blob/main/scaledemo.ipynb).

### *Running from source*

The above method uses the installed package for running the simulator.
In cases where you would like to run directly from the source, the following command should be used instead.

```$ python3 <scale_sim_repo_root>/scalesim/scale.py -c <path_to_config_file> -t <path_to_topology_file>```

If you are running from sources for the first time and do not have all the dependencies installed, please install them first  using the following command.

```$ pip3 install -r <scale_sim_repo_root>/requirements.txt```

## Tool inputs

SCALE-Sim uses two input files to run, a configuration file and a topology file.

### Configuration file

The configuration file is used to specify the architecture and run parameters for the simulations. 
The following shows a sample config file:

![sample config](https://github.com/scalesim-project/scale-sim-v2/blob/main/documentation/resources/config-file-example.png "sample config") 

The config file has three sections. The "*general*" section specifies the run name, which is user specific. The "*architecture_presets*" section describes the parameter of the systolic array hardware to simulate. 
The "*run_preset*" section specifies if the simulator should run with user specified bandwidth, or should it calculate the optimal bandwidth for stall free execution. 

The detailed documentation for the config file could be found **here (TBD)**

### Topology file

The topology file is a *CSV* file which decribes the layers of the workload topology. The layers are typically described as convolution layer parameters as shown in the example below.

![sample topo](https://github.com/scalesim-project/scale-sim-v2/blob/main/documentation/resources/topo-file-example.png "sample topo")

For other layer types, SCALE-Sim also accepts the workload desciption in M, N, K format of the equivalent GEMM operation as shown in the example below **TBD**.

The tool however expects the inputs to be in the convolution format by default. When using the mnk format for input, please specify using the  ```-i gemm``` switch, as shown in the example below.

```$ python3 <scale sim repo root>/scalesim/scale.py -c <path_to_config_file> -t <path_to_mnk_topology_file> -i gemm```

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

Detailed documentation about the tool can be found **here (TBD)**

We also recommend referring to the following papers for insights on SCALE-Sim's potential. 

[1] Samajdar, A., Zhu, Y., Whatmough, P., Mattina, M., & Krishna, T.;  **"Scale-sim: Systolic cnn accelerator simulator."** arXiv preprint arXiv:1811.02883 (2018). [\[pdf\]](https://arxiv.org/abs/1811.02883)

[2] Samajdar, A., Joseph, J. M., Zhu, Y., Whatmough, P., Mattina, M., & Krishna, T.; **"A systematic methodology for characterizing scalability of DNN accelerators using SCALE-sim"**. In 2020 IEEE International Symposium on Performance Analysis of Systems and Software (ISPASS). [\[pdf\]](https://cpb-us-w2.wpmucdn.com/sites.gatech.edu/dist/c/332/files/2020/03/scalesim_ispass2020.pdf)

## Citing this work

If you found this tool useful, please use the following bibtex to cite us

```
@article{samajdar2018scale,
  title={SCALE-Sim: Systolic CNN Accelerator Simulator},
  author={Samajdar, Ananda and Zhu, Yuhao and Whatmough, Paul and Mattina, Matthew and Krishna, Tushar},
  journal={arXiv preprint arXiv:1811.02883},
  year={2018}
}

@inproceedings{samajdar2020systematic,
  title={A systematic methodology for characterizing scalability of DNN accelerators using SCALE-sim},
  author={Samajdar, Ananda and Joseph, Jan Moritz and Zhu, Yuhao and Whatmough, Paul and Mattina, Matthew and Krishna, Tushar},
  booktitle={2020 IEEE International Symposium on Performance Analysis of Systems and Software (ISPASS)},
  pages={58--68},
  year={2020},
  organization={IEEE}
}
```

## Contributing to the project

**TODO** Provide detailed steps on making pull request

## Developers

* Ananda Samajdar
* Jan Moritz Joseph
* Yuhao Zhu
* Paul Whatmough
* Tushar Krishna
