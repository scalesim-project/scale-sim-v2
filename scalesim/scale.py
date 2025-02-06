import argparse
import multiprocessing as mp
import os
import sys
import shutil
from scalesim.scale_sim import scalesim

mp.set_start_method('spawn',True)

def worker( num,
            save_space,
            config,
            topology,
            gemm_input,
            logpath
        ):
    """ Running multiple layers in parallel with python multi-processing
    """

    print("Running Layer {}".format(str(num)))
    s = scalesim(layer_id = num,
                 save_disk_space=save_space, 
                 verbose=True,
                 config=config,
                 topology=topology,
                 input_type_gemm=gemm_input
                 )
    logpath_layer = logpath + "_runs_" + str(num)
    s.run_scale(top_path=logpath_layer)

def layerSplit(topology):
    """Split the topology file to individual file with layers
    """
    
    # Variable initializations
    filelist=[]
    layers = []
    header = ''
    dirpath = 'parallel'
    inputWorkers = len(topology) - 1

    # Single thread implementation
    if inputWorkers == 1:           
        filelist.append(topology)
        return (filelist)
     
    # Check and remove if the result folder already exist
    path = os.path.join(os.getcwd(),dirpath)
    if os.path.isdir(path):
        shutil.rmtree(path)
    os.mkdir(path)

    # Extract each layer of the model topology file
    with open(topology,'r') as f:
        for line in f.readlines():
            if header =='':
                header = line
            else:
                layers.append(line)
    f.close()

    for i in range(len(layers)):
        filename = os.path.join(path, "layer_"+ str(i))
        f = open(filename,'w')
        f.write(header)
        f.write(layers[i])
        f.close()
        filelist.append(filename)
    
    return(filelist)
    



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', metavar='Topology file', type=str,
                        default="../topologies/conv_nets/test.csv",
                        help="Path to the topology file"
                        )
    parser.add_argument('-c', metavar='Config file', type=str,
                        default="../configs/scale.cfg",
                        help="Path to the config file"
                        )
    parser.add_argument('-p', metavar='log dir', type=str,
                        default="./results/",
                        help="Path to log dir"
                        )
    parser.add_argument('-i', metavar='input type', type=str,
                        default="conv",
                        help="Type of input topology, gemm: MNK, conv: conv"
                        )
    parser.add_argument('-s', metavar='save trace', type=str,
                        default="Y",
                        help="Save Trace: (Y/N)"
                        )
    parser.add_argument('-w', metavar='parallel run', type=str,
                        default="Y",
                        help="Run tasks in parallel: (Y/N)"
                        )

    args = parser.parse_args()
    topology = args.t
    config = args.c
    logpath = args.p + topology.split('/')[-1].split('.')[0]
    inp_type = args.i
    save_trace = args.s
    run_parallel = args.w

    gemm_input  = False
    save_space  = False
 
 

    if inp_type == 'gemm':
        gemm_input = True

    if save_trace == 'Y':
        save_space = False
    else:
        save_space = True
    
    if run_parallel == "Y":
        layers = layerSplit(topology)
        for i in range(len(layers)):
            p = mp.Process(target=worker, 
                            args = ( i,
                                    save_space,
                                    config,
                                    layers[i],
                                    gemm_input,
                                    logpath
                                    ) 
                            )
            p.start()
    else:
        s = scalesim(layer_id = -1,
                 save_disk_space=save_space, 
                 verbose=True,
                 config=config,
                 topology=topology,
                 input_type_gemm=gemm_input
                 )
        s.run_scale(top_path=logpath)




