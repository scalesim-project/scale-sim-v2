import argparse

from scalesim.scale_sim import scalesim

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
    args = parser.parse_args()
    topology = args.t
    config = args.c
    logpath = args.p #+ topology.split('/')[-1].split('.')[0]
    inp_type = args.i
    save_trace = args.s

    gemm_input  = False
    save_space  = False
 
 

    if inp_type == 'gemm':
        gemm_input = True

    if save_trace == 'Y':
        save_space = False
    else:
        save_space = True

    s = scalesim(save_disk_space=save_space, 
                 verbose=True,
                 config=config,
                 topology=topology,
                 input_type_gemm=gemm_input
                 )
    s.run_scale(top_path=logpath)
