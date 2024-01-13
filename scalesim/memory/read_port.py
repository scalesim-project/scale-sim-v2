# Dummy memory like interface to service the requests of the last level memory

class read_port:
    """
    Class to define dummy memory like interface to service the requests of the last level memory
    """
    def __init__(self):
        """
        The constructor method for the class
        """
        self.latency = 1

    def set_params(self, latency):
        """
        Method to set the backing buffer hit latency for housekeeping.

        :param hit_latency: Hit latency of the backing buffer

        :return: None
        """
        self.latency = latency

    def get_latency(self):
        """
        Method to get the backing buffer hit latency for housekeeping.

        :return: Hit latency of the backing buffer
        """
        return self.latency

    # The incoming read requests will be needed when the capability of port is expanded
    # At the moment its kept for compatibility
    def service_reads(self, incoming_requests_arr_np, incoming_cycles_arr):
        """
        Method to service read request by the read buffer. 
        As a dummy memory, everything is a hit

        :return: List of out cycles by adding the hit latency to the incoming cycles
        """
        out_cycles_arr = incoming_cycles_arr + self.latency
        return out_cycles_arr
