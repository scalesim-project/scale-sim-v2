import os
from scalesim.scale_config import scale_config
from scalesim.topology_utils import topologies
from scalesim.simulator import simulator as sim


class scalesim:
    """The top level class for the SCALE-Sim v2 simulator
    Provides methods for setting parameters, running sims, and generating results
    """
    def __init__(self,
                 save_disk_space=False,
                 verbose=True,
                 config='',
                 topology='',
                 input_type_gemm=False):
         """
         Initilize the class object
        :param save_disk_space: Boolean If set, cycle accurate traces will not be save (default: False)
        :param verbose: Boolean If set verbose output will be generated on the console (default: True)
        :param config: Path to the scalesim config file
        :param topology: Path to the scalesim topology file

        :return: None
        """

        # Data structures
        self.config = scale_config()
        self.topo = topologies()

        # File paths
        self.config_file = ''
        self.topology_file = ''

        # Member objects
        #self.runner = r.run_nets()
        self.runner = sim()

        # Flags
        self.save_space = save_disk_space
        self.verbose_flag = verbose
        self.run_done_flag = False
        self.logs_generated_flag = False

        self.set_params(config_filename=config, topology_filename=topology)

    #
    def set_params(self,
                   config_filename='',
                   topology_filename='' ):
        """Set or update the paths to the scalesim input files

        :param config_filename: Name and path to the config file
        :param topology_filename: Name and path to the topology file

        :return: None
        """

        # First check if the user provided a valid topology file
        if not topology_filename == '':
            if not os.path.exists(topology_filename):
                print("ERROR: scalesim.scale.py: Topology file not found")
                print("Input file:" + topology_filename)
                print('Exiting')
                exit()
            else:
                self.topology_file = topology_filename

        if not os.path.exists(config_filename):
            print("ERROR: scalesim.scale.py: Config file not found") 
            print("Input file:" + config_filename)
            print('Exiting')
            exit()
        else: 
            self.config_file = config_filename

        # Parse config first
        self.config.read_conf_file(self.config_file)

        # Take the CLI topology over the one in config
        # If topology is not passed from CLI take the one from config
        if self.topology_file == '':
            self.topology_file = self.config.get_topology_path()
        else:
            self.config.set_topology_file(self.topology_file)

        # Parse the topology
        self.topo.load_arrays(topofile=self.topology_file)

        #num_layers = self.topo.get_num_layers()
        #self.config.scale_memory_maps(num_layers=num_layers)

    #
    def run_scale(self, top_path='.'):
        """Method to initialize the internal simulation objects and run scalesim once

        :param top_path: Path to the directory where generated outputs will be dumped

        :return: None
        """

        self.top_path = top_path
        save_trace = not self.save_space
        self.runner.set_params(
            config_obj=self.config,
            topo_obj=self.topo,
            top_path=self.top_path,
            verbosity=self.verbose_flag,
            save_trace=save_trace
        )
        self.run_once()

    def run_once(self):
        """Method to run the simulation once with preset config and topology objects

        :return: None
        """

        if self.verbose_flag:
            self.print_run_configs()

        self.runner.run()
        self.run_done_flag = True

        self.logs_generated_flag = True

        if self.verbose_flag:
            print("************ SCALE SIM Run Complete ****************")

    #
    def print_run_configs(self):
        """Method to print the banner of input parameters for verbose scalesim runs

        :return: None
        """

        df_string = "Output Stationary"
        df = self.config.get_dataflow()

        if df == 'ws':
            df_string = "Weight Stationary"
        elif df == 'is':
            df_string = "Input Stationary"

        print("====================================================")
        print("******************* SCALE SIM **********************")
        print("====================================================")

        arr_h, arr_w = self.config.get_array_dims()
        print("Array Size: \t" + str(arr_h) + "x" + str(arr_w))

        ifmap_kb, filter_kb, ofmap_kb = self.config.get_mem_sizes()
        print("SRAM IFMAP (kB): \t" + str(ifmap_kb))
        print("SRAM Filter (kB): \t" + str(filter_kb))
        print("SRAM OFMAP (kB): \t" + str(ofmap_kb))
        print("Dataflow: \t" + df_string)
        print("CSV file path: \t" + self.config.get_topology_path())

        if self.config.use_user_dram_bandwidth():
            print("Bandwidth: \t" + self.config.get_bandwidths_as_string())
            print('Working in USE USER BANDWIDTH mode.')
        else:
            print('Working in ESTIMATE BANDWIDTH mode.')

        print("====================================================")

    #
    def get_total_cycles(self):
        """Method to get the total cycles (stalls + compute) for the workload once the simulation is completed

        :return: Total cycles
        """
        me = 'scale.' + 'get_total_cycles()'
        if not self.run_done_flag:
            message = 'ERROR: ' + me
            message += ' : Cannot determine cycles. Run the simulation first'
            print(message)
            return

        return self.runner.get_total_cycles()
