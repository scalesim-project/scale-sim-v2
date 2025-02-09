
import argparse
import os

import torch
import torch.nn as nn

from torchvision import models, datasets
from torchvision.transforms import ToTensor
from torchinfo import summary

from scalesim import topology_utils


base_dir = '../topologies/custom'


# creates topology file from PyTorch module
def create_conv_topo(model, path=base_dir, filename='', input_dim=(2, 3, 224, 224), include_lin=False):
    if filename == '':
        filename = model.__class__.__name__+'_custom.csv'

    topo = topology_utils.topologies()
    prev_arr, curr_arr = [], []
    last = 0

    model_stats = summary(model, input_size=input_dim, col_names=('input_size','output_size','num_params','kernel_size'), verbose=1)
    idx = 1
    for layer in model_stats.summary_list:
        if layer.class_name == 'Conv2d':
            if prev_arr:
                prev_arr[6] = last
                topo.topo_arrays.append(prev_arr)
                idx += 1
            curr_arr.append(layer.class_name+'_{}'.format(idx))  # layer name
            curr_arr.append(layer.input_size[2])  # IFMAP height
            curr_arr.append(layer.input_size[3])  # IFMAP width
            curr_arr.append(layer.kernel_size[0])  # filter height
            curr_arr.append(layer.kernel_size[1])  # filter width
            curr_arr.append(layer.input_size[1])  # channels
            curr_arr.append(0)  # output channels (num filters)
            curr_arr.append(layer.module.stride[0])  # stride
            prev_arr = curr_arr
            curr_arr = []
        elif layer.class_name == 'Linear' and include_lin:
            if prev_arr:
                prev_arr[6] = last
                topo.topo_arrays.append(prev_arr)
                idx += 1
            curr_arr.append(layer.class_name+'_{}'.format(idx))  # layer name
            print(layer.input_size)
            curr_arr.append(1)  # IFMAP height
            curr_arr.append(1)  # IFMAP width
            curr_arr.append(1)  # filter height
            curr_arr.append(1)  # filter width
            curr_arr.append(layer.input_size[1])  # channels
            curr_arr.append(0)  # output channels (num filters)
            curr_arr.append(1)  # stride
            prev_arr = curr_arr
            curr_arr = []
        last = layer.input_size[1]
    # last layer
    if prev_arr:
        prev_arr[6] = last
        topo.topo_arrays.append(prev_arr)

    topo.topo_load_flag = True
    topo.write_topo_file(path=path, filename=filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', metavar='PyTorch module name', type=str,
                        default='alexnet',
                        help="Class name of PyTorch module to turn into SCALESim topology"
                        )
    parser.add_argument('-p', metavar='Path to directory', type=str,
                        default='../topologies/custom',
                        help="Directory at which to save the created topology file"
                        )
    parser.add_argument('-f', metavar='File name', type=str,
                        default='alexnet_custom.csv',
                        help="File name for SCALESim topology"
                        )
    parser.add_argument('-l', metavar='Include linear layers?', type=bool,
                        default=False,
                        help="Boolean deciding whether or not to include nn.Linear layers in topology"
                        )


    args = parser.parse_args()
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)

    model_name = args.m
    print(model_name)
    print(args.p)
    try:
        model = getattr(models, model_name)(pretrained=True)
    except:
        print('PyTorch module does not exist')
        exit()

    path = args.p
    file_name = args.f
    include_lin = args.l

    create_conv_topo(model, path=path, filename=file_name, include_lin=include_lin)