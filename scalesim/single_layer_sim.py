import os

from scalesim.scale_config import scale_config as cfg
from scalesim.topology_utils import topologies as topo
from scalesim.compute.operand_matrix import operand_matrix as opmat
from scalesim.compute.systolic_compute_os import systolic_compute_os
from scalesim.compute.systolic_compute_ws import systolic_compute_ws
from scalesim.compute.systolic_compute_is import systolic_compute_is
from scalesim.memory.double_buffered_scratchpad_mem import double_buffered_scratchpad as mem_dbsp


class single_layer_sim:
    def __init__(self):
        self.layer_id = 0
        self.topo = topo()
        self.config = cfg()

        self.op_mat_obj = opmat()
        self.compute_system = systolic_compute_os()
        self.memory_system = mem_dbsp()

        self.verbose = True

        # Report items : Compute report
        self.total_cycles = 0
        self.stall_cycles = 0
        self.num_compute = 0
        self.num_mac_unit = 0
        self.overall_util = 0
        self.mapping_eff = 0
        self.compute_util = 0

        # Report items : BW report
        self.avg_ifmap_sram_bw = 0
        self.avg_filter_sram_bw = 0
        self.avg_ofmap_sram_bw = 0
        self.avg_ifmap_dram_bw = 0
        self.avg_filter_dram_bw = 0
        self.avg_ofmap_dram_bw = 0

        # Report items : Detailed Access report
        self.ifmap_sram_start_cycle = 0
        self.ifmap_sram_stop_cycle = 0
        self.ifmap_sram_reads = 0

        self.filter_sram_start_cycle = 0
        self.filter_sram_stop_cycle = 0
        self.filter_sram_reads = 0

        self.ofmap_sram_start_cycle = 0
        self.ofmap_sram_stop_cycle = 0
        self.ofmap_sram_writes = 0

        self.ifmap_dram_start_cycle = 0
        self.ifmap_dram_stop_cycle = 0
        self.ifmap_dram_reads = 0

        self.filter_dram_start_cycle = 0
        self.filter_dram_stop_cycle = 0
        self.filter_dram_reads = 0

        self.ofmap_dram_start_cycle = 0
        self.ofmap_dram_stop_cycle = 0
        self.ofmap_dram_writes = 0

        self.params_set_flag = False
        self.memory_system_ready_flag = False
        self.runs_ready = False
        self.report_items_ready = False

    def set_params(self,
                   layer_id=0,
                   config_obj=cfg(), topology_obj=topo(),
                   verbose=True):

        self.layer_id = layer_id
        self.config = config_obj
        self.topo = topology_obj

        self.op_mat_obj.set_params(layer_id=self.layer_id,
                                   config_obj=self.config,
                                   topoutil_obj=self.topo,
                                   )

        self.dataflow = self.config.get_dataflow()
        if self.dataflow == 'os':
            self.compute_system = systolic_compute_os()
        elif self.dataflow == 'ws':
            self.compute_system = systolic_compute_ws()
        elif self.dataflow == 'is':
            self.compute_system = systolic_compute_is()

        arr_dims =self.config.get_array_dims()
        self.num_mac_unit = arr_dims[0] * arr_dims[1]
        self.verbose=verbose

        self.params_set_flag = True

    # This communicates that the memory is being managed externally
    # And the class will not interfere with setting it up
    def set_memory_system(self, mem_sys_obj=mem_dbsp()):
        self.memory_system = mem_sys_obj
        self.memory_system_ready_flag = True

    def run(self):
        assert self.params_set_flag, 'Parameters are not set. Run set_params()'

        # 1. Setup and the get the demand from compute system

        # 1.1 Get the operand matrices
        _, ifmap_op_mat = self.op_mat_obj.get_ifmap_matrix()
        _, filter_op_mat = self.op_mat_obj.get_filter_matrix()
        _, ofmap_op_mat = self.op_mat_obj.get_ofmap_matrix()

        self.num_compute = self.topo.get_layer_num_ofmap_px(self.layer_id) \
                           * self.topo.get_layer_window_size(self.layer_id)

        # 1.2 Get the prefetch matrices for both operands
        self.compute_system.set_params(config_obj=self.config,
                                       ifmap_op_mat=ifmap_op_mat,
                                       filter_op_mat=filter_op_mat,
                                       ofmap_op_mat=ofmap_op_mat)

        # 1.3 Get the no compute demand matrices from for 2 operands and the output
        ifmap_prefetch_mat, filter_prefetch_mat = self.compute_system.get_prefetch_matrices()
        ifmap_demand_mat, filter_demand_mat, ofmap_demand_mat = self.compute_system.get_demand_matrices()
        #print('DEBUG: Compute operations done')
        # 2. Setup the memory system and run the demands through it to find any memory bottleneck and generate traces

        # 2.1 Setup the memory system if it was not setup externally
        if not self.memory_system_ready_flag:
            word_size = 1           # bytes, this can be incorporated in the config file
            active_buf_frac = 0.5   # This can be incorporated in the config as well

            ifmap_buf_size_kb, filter_buf_size_kb, ofmap_buf_size_kb = self.config.get_mem_sizes()
            ifmap_buf_size_bytes = 1024 * ifmap_buf_size_kb
            filter_buf_size_bytes = 1024 * filter_buf_size_kb
            ofmap_buf_size_bytes = 1024 * ofmap_buf_size_kb

            ifmap_backing_bw = 1
            filter_backing_bw = 1
            ofmap_backing_bw = 1
            estimate_bandwidth_mode = False
            if self.config.use_user_dram_bandwidth():
                bws = self.config.get_bandwidths_as_list()
                ifmap_backing_bw = bws[0]
                filter_backing_bw = bws[0]
                ofmap_backing_bw = bws[0]

            else:
                dataflow = self.config.get_dataflow()
                arr_row, arr_col = self.config.get_array_dims()
                estimate_bandwidth_mode = True

                # The number 10 elems per cycle is arbitrary
                ifmap_backing_bw = 10
                filter_backing_bw = 10
                ofmap_backing_bw = arr_col

            self.memory_system.set_params(
                    word_size=word_size,
                    ifmap_buf_size_bytes=ifmap_buf_size_bytes,
                    filter_buf_size_bytes=filter_buf_size_bytes,
                    ofmap_buf_size_bytes=ofmap_buf_size_bytes,
                    rd_buf_active_frac=active_buf_frac, wr_buf_active_frac=active_buf_frac,
                    ifmap_backing_buf_bw=ifmap_backing_bw,
                    filter_backing_buf_bw=filter_backing_bw,
                    ofmap_backing_buf_bw=ofmap_backing_bw,
                    verbose=self.verbose,
                    estimate_bandwidth_mode=estimate_bandwidth_mode
            )

        # 2.2 Install the prefetch matrices to the read buffers to finish setup
        if self.config.use_user_dram_bandwidth() :
            self.memory_system.set_read_buf_prefetch_matrices(ifmap_prefetch_mat=ifmap_prefetch_mat,
                                                              filter_prefetch_mat=filter_prefetch_mat)

        # 2.3 Start sending the requests through the memory system until
        # all the OFMAP memory requests have been serviced
        self.memory_system.service_memory_requests(ifmap_demand_mat, filter_demand_mat, ofmap_demand_mat)

        self.runs_ready = True

    # This will write the traces
    def save_traces(self, top_path):
        assert self.params_set_flag, 'Parameters are not set'

        dir_name = top_path + '/layer' + str(self.layer_id)
        if not os.path.isdir(dir_name):
            cmd = 'mkdir ' + dir_name
            os.system(cmd)

        ifmap_sram_filename = dir_name +  '/IFMAP_SRAM_TRACE.csv'
        filter_sram_filename = dir_name + '/FILTER_SRAM_TRACE.csv'
        ofmap_sram_filename = dir_name +  '/OFMAP_SRAM_TRACE.csv'

        ifmap_dram_filename = dir_name +  '/IFMAP_DRAM_TRACE.csv'
        filter_dram_filename = dir_name + '/FILTER_DRAM_TRACE.csv'
        ofmap_dram_filename = dir_name +  '/OFMAP_DRAM_TRACE.csv'

        self.memory_system.print_ifmap_sram_trace(ifmap_sram_filename)
        self.memory_system.print_ifmap_dram_trace(ifmap_dram_filename)
        self.memory_system.print_filter_sram_trace(filter_sram_filename)
        self.memory_system.print_filter_dram_trace(filter_dram_filename)
        self.memory_system.print_ofmap_sram_trace(ofmap_sram_filename)
        self.memory_system.print_ofmap_dram_trace(ofmap_dram_filename)

    #
    def calc_report_data(self):
        assert self.runs_ready, 'Runs are not done yet'

        # Compute report
        self.total_cycles = self.memory_system.get_total_compute_cycles()
        self.stall_cycles = self.memory_system.get_stall_cycles()
        self.overall_util = (self.num_compute * 100) / (self.total_cycles * self.num_mac_unit)
        self.mapping_eff = self.compute_system.get_avg_mapping_efficiency() * 100
        self.compute_util = self.compute_system.get_avg_compute_utilization() * 100

        # BW report
        self.ifmap_sram_reads = self.compute_system.get_ifmap_requests()
        self.filter_sram_reads = self.compute_system.get_filter_requests()
        self.ofmap_sram_writes = self.compute_system.get_ofmap_requests()
        self.avg_ifmap_sram_bw = self.ifmap_sram_reads / self.total_cycles
        self.avg_filter_sram_bw = self.filter_sram_reads / self.total_cycles
        self.avg_ofmap_sram_bw = self.ofmap_sram_writes / self.total_cycles

        # Detail report
        self.ifmap_sram_start_cycle, self.ifmap_sram_stop_cycle \
            = self.memory_system.get_ifmap_sram_start_stop_cycles()

        self.filter_sram_start_cycle, self.filter_sram_stop_cycle \
            = self.memory_system.get_filter_sram_start_stop_cycles()

        self.ofmap_sram_start_cycle, self.ofmap_sram_stop_cycle \
            = self.memory_system.get_ofmap_sram_start_stop_cycles()

        self.ifmap_dram_start_cycle, self.ifmap_dram_stop_cycle, self.ifmap_dram_reads \
            = self.memory_system.get_ifmap_dram_details()

        self.filter_dram_start_cycle, self.filter_dram_stop_cycle, self.filter_dram_reads \
            = self.memory_system.get_filter_dram_details()

        self.ofmap_dram_start_cycle, self.ofmap_dram_stop_cycle, self.ofmap_dram_writes \
            = self.memory_system.get_ofmap_dram_details()

        # BW calc for DRAM access
        self.avg_ifmap_dram_bw = self.ifmap_dram_reads / (self.ifmap_dram_stop_cycle - self.ifmap_dram_start_cycle + 1)
        self.avg_filter_dram_bw = self.filter_dram_reads / (self.filter_dram_stop_cycle - self.filter_dram_start_cycle + 1)
        self.avg_ofmap_dram_bw = self.ofmap_dram_writes / (self.ofmap_dram_stop_cycle - self.ofmap_dram_start_cycle + 1)

        self.report_items_ready = True

    #
    def get_layer_id(self):
        assert self.params_set_flag, 'Parameters are not set yet'
        return self.layer_id

    #
    def get_compute_report_items(self):
        if not self.report_items_ready:
            self.calc_report_data()

        items = [self.total_cycles, self.stall_cycles, self.overall_util, self.mapping_eff, self.compute_util]
        return items

    #
    def get_bandwidth_report_items(self):
        if not self.report_items_ready:
            self.calc_report_data()

        items = [self.avg_ifmap_sram_bw, self.avg_filter_sram_bw, self.avg_ofmap_sram_bw]
        items += [self.avg_ifmap_dram_bw, self.avg_filter_dram_bw, self.avg_ofmap_dram_bw]

        return items

    #
    def get_detail_report_items(self):
        if not self.report_items_ready:
            self.calc_report_data()

        items = [self.ifmap_sram_start_cycle, self.ifmap_sram_stop_cycle, self.ifmap_sram_reads]
        items += [self.filter_sram_start_cycle, self.filter_sram_stop_cycle, self.filter_sram_reads]
        items += [self.ofmap_sram_start_cycle, self.ofmap_sram_stop_cycle, self.ofmap_sram_writes]
        items += [self.ifmap_dram_start_cycle, self.ifmap_dram_stop_cycle, self.ifmap_dram_reads]
        items += [self.filter_dram_start_cycle, self.filter_dram_stop_cycle, self.filter_dram_reads]
        items += [self.ofmap_dram_start_cycle, self.ofmap_dram_stop_cycle, self.ofmap_dram_writes]

        return items
