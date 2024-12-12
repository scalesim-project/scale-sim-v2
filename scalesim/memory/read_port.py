# Dummy memory like interface to service the requests of the last level memory
import numpy as np
from scalesim.scale_config import scale_config as config
from bisect import bisect_left

class read_port:
    def __init__(self):
        self.latency = 1
        self.ramulator_trace = False
        self.latency_matrix = []
        self.bw = 10
        self.request_queue_size = 100
        self.request_queue_status = 0
        self.stall_cycles = 0
        self.request_array = []
        self.count = 0
        self.config = config()
    
    def def_params( self,
                    config = config(),
                    latency_file = ''
                ):
        self.config = config
        self.ramulator_trace = self.config.get_ramulator_trace()
        self.request_queue_size = self.config.get_req_buf_sz_rd()
        self.bw = self.config.get_bandwidths_as_list()[0]
        if self.ramulator_trace == True:
            self.latency_matrix = np.load(latency_file)
        

    def set_params(self, latency):
        self.latency = latency

    def get_latency(self):
        return self.latency

    def find_latency(self):
        #num_valid_request = len([num for num in incoming_request if num!=-1.0])
        if(self.count < len(self.latency_matrix)):
            #latency_out = max(self.latency_matrix[self.count:self.count+num_valid_request])
            latency_out = self.latency_matrix[self.count]
            #print(str(self.count)+ ' ' + str(latency_out))
            #self.count+=num_valid_request
            self.count+=1
        else:
            latency_out = self.latency
            #print("Extra requests")
        return latency_out

    # The incoming read requests will be needed when the capability of port is expanded
    # At the moment its kept for compatibility
    def service_reads(self, incoming_requests_arr_np, incoming_cycles_arr):
        if self.ramulator_trace is False:
            out_cycles_arr = incoming_cycles_arr + self.latency
            return out_cycles_arr

        updated_req_timestamp = incoming_cycles_arr[0]
        out_cycles_arr = np.zeros(incoming_requests_arr_np.shape[0])
        for i in range(len(incoming_cycles_arr)):
            out_cycles_arr[i] = incoming_cycles_arr[i] + self.stall_cycles + self.find_latency()
            #print(str(incoming_cycles_arr[i]) + ' ' + str(out_cycles_arr[i]) + ' ' +str(self.stall_cycles))
            self.request_array.append(out_cycles_arr[i])
            if len(self.request_array) == self.request_queue_size:
                updated_req_timestamp = incoming_cycles_arr[i] + self.stall_cycles
                self.request_array.sort()
                if self.request_array[0] >= updated_req_timestamp:
                    self.stall_cycles += self.request_array[0] - updated_req_timestamp
                    updated_req_timestamp = self.request_array[0]
                    self.request_array.pop(0)
                else:
                    index = bisect_left(self.request_array,updated_req_timestamp)
                    if index == len(self.request_array):
                        self.request_array = []
                    else:
                        self.request_array = self.request_array[index:]
            elif len(self.request_array) > self.request_queue_size:
                self.request_array = self.request_array[-self.request_queue_size:]
        
        self.stall_cycles=0
        return out_cycles_arr
