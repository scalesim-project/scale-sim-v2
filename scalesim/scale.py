"""
This file is the main script for running SCALE-Sim with the given topology and configuration files.
It handles argument parsing and execution.
"""

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
                        default="../test_runs",
                        help="Path to log dir"
                        )
    parser.add_argument('-i', metavar='input type', type=str,
                        default="conv",
                        help="Type of input topology, gemm: MNK, conv: conv"
                        )

    args = parser.parse_args()
    topology = args.t
    config = args.c
    logpath = args.p
    inp_type = args.i

    GEMM_INPUT = False
    if inp_type == 'gemm':
        GEMM_INPUT = True

    s = scalesim(save_disk_space=True, verbose=True,
                 config=config,
                 topology=topology,
                 input_type_gemm=GEMM_INPUT
                 )
    s.run_scale(top_path=logpath)
