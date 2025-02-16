#!/bin/bash
./run_ramulator.sh resnet18 32
./run_ramulator.sh resnet18 512
./run_ramulator_mnk.sh vit_s 32
./run_ramulator_mnk.sh vit_s 512
./run_ramulator_mnk.sh vit_b 32
./run_ramulator_mnk.sh vit_b 512
./run_ramulator_mnk.sh vit_bg 32
./run_ramulator_mnk.sh vit_bg 512
./run_ramulator_mnk.sh vit_h 32
./run_ramulator_mnk.sh vit_h 512
./run_ramulator_mnk.sh vit_l 32
./run_ramulator_mnk.sh vit_l 512
