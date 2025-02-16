import argparse
import os

import torch
import torch.nn as nn

from scalesim.scale_sim import scalesim
from torch_to_topo import create_conv_topo
from torchvision import models, datasets

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
    # Changes from torch_to_topo files
    parser.add_argument('-m', metavar='PyTorch module name', type=str,
                        default='',
                        help="Class name of PyTorch module to turn into SCALESim topology"
                        )
    parser.add_argument('-l', metavar='Include linear layers?', type=bool,
                        default=False,
                        help="Boolean deciding whether or not to include nn.Linear layers in topology"
                        )    

    args = parser.parse_args()
    topology = args.t
    config = args.c
    logpath = args.p
    inp_type = args.i

    if args.m != '':
        # Changes from torch_to_topo files
        path = '../topologies/custom/'
        if not os.path.exists(path):
            os.makedirs(path)
        include_lin = args.l
        model_name = args.m
        model = getattr(models, model_name)(pretrained=True)
        file_name = model_name + '.csv'
        create_conv_topo(model, path=path, filename=file_name, include_lin=include_lin)

        topology = path + file_name

    gemm_input = False
    if inp_type == 'gemm':
        gemm_input = True

    s = scalesim(save_disk_space=True, verbose=True,
                 config=config,
                 topology=topology,
                 input_type_gemm=gemm_input
                 )
    s.run_scale(top_path=logpath)
