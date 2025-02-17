# This is shell module to ensure continuity
import numpy as np


class write_port:
    def __init__(self):
        self.latency = 0

    def service_writes(self, incoming_requests_arr_np, incoming_cycles_arr_np):
        out_cycles_arr_np = incoming_cycles_arr_np + self.latency
        out_cycles_arr_np = out_cycles_arr_np.reshape((out_cycles_arr_np.shape[0], 1))
        return out_cycles_arr_np
