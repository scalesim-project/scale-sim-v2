#!/bin/bash

########### User Input ##########################

while getopts c:t:p:o: flag
do
    case "${flag}" in
        c) scsimCfg=${OPTARG};;
        t) scsimTplg=${OPTARG};;
        p) scsimOutput=${OPTARG};;        
        o) allOutput=${OPTARG};;
    esac
done 

if [[ $scsimCfg == ""  ||  $scsimTplg == ""  || $allOutput == "" ]]; then
 echo "Not enough input files privoded"
 echo "./run_all.sh -c <path_to_config_file> -t <path_to_topology_file> -p <path_to_scale-sim_log_dir> -o <path_to_final_output_dir>"
 exit 0
fi

echo "config file: $scsimCfg";
echo "topology file: $scsimTplg";
echo "scsim log dir: $scsimOutput";
echo "output dir: $allOutput";

################################################

scsimCfg=$(realpath $scsimCfg)
scsimTplg=$(realpath $scsimTplg)
scsimOutput=$(realpath $scsimOutput)
allOutput=$(realpath  $allOutput)

rm -f accelergy_input/*.yaml
mkdir -p $allOutput

# Generate Accelergy::architecture.yaml from ScaleSim::scale.cfg
python3 preprocess.py -c $scsimCfg -t $scsimTplg -p $scsimOutput -o $allOutput

# Run Scale-sim
cd ..
python3 scale.py -c $scsimCfg -t $scsimTplg -p $scsimOutput

# Extract Accelergy::action_count.yaml from ScaleSim::reuslts
cd rundir-accelergy
./create_action_count.sh


# Run Accelergy
./run_accelergy.sh


# Post-Process
# gen_plot.ipynb
