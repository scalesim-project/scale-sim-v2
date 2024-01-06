# This is shell module to ensure continuity
import numpy as np


class write_port:
    """
    Class to define dummy memory like interface to service the requests of the last level memory
    """
    def __init__(self):
        """
        The constructor method for the class
        """
        self.latency = 0

    def service_writes(self, incoming_requests_arr_np, incoming_cycles_arr_np):
        """
        Method to service read request by the dummy write buffer. 

        :return: List of out cycles 
        """
        out_cycles_arr_np = incoming_cycles_arr_np + self.latency
        out_cycles_arr_np = out_cycles_arr_np.reshape((out_cycles_arr_np.shape[0], 1))
        return out_cycles_arr_np
