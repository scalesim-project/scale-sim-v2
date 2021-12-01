# Systolic array code

This directory contains sample RTL code for implemeting basic traditional systolic array with 8bit and bf16 word operands.

Following items are included:

 - systolic_array_8bit_MAC_PE: Paramterizable RTL for systolic array with 8bit words. This RTL can support Output Stationary (OS), Weight Stationary (WS), and Input Stationary (IS) dataflow. Unfortunately we do not have the control logic implemented yet.

 - BF16_processing_element : MAC unit with BFloat 16 word operands. This PE is designed to work in WS mode only. However, given the similarity of operation in IS and WS mode, a little hacking might enable IS operation. 

Authors:
1) Ananda Samajdar
2) Eric Qin
