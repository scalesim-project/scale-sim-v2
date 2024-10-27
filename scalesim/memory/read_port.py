"""
Dummy memory like interface to service the requests of the last level memory
"""

class read_port:
    """
    Class to define dummy memory like interface to service the requests of the last level memory
    """
    #
    def __init__(self):
        """
        __init__ method.
        """
        self.latency = 1

    #
    def set_params(self, latency):
        """
        Method to set the backing buffer hit latency for housekeeping.
        """
        self.latency = latency

    #
    def get_latency(self):
        """
        Method to get the backing buffer hit latency for housekeeping.
        """
        return self.latency

    # The incoming read requests will be needed when the capability of port is expanded
    # At the moment its kept for compatibility
    def service_reads(self, incoming_requests_arr_np, incoming_cycles_arr):
        """
        Method to service read request by the read buffer. As a dummy memory, everything is a hit.
        """
        out_cycles_arr = incoming_cycles_arr + self.latency
        return out_cycles_arr
