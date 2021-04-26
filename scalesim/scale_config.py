import configparser as cp
import os
import sys

from scalesim.memory_map import memory_map


class scale_config:
    def __init__(self):
        self.run_name = "scale_run"
        # Anand: ISSUE #2. Patch
        self.use_user_bandwidth = False

        self.array_rows = 4
        self.array_cols = 4
        self.ifmap_sz_kb = 256
        self.filter_sz_kb = 256
        self.ofmap_sz_kb = 128
        self.df = 'ws'
        self.ifmap_offset = 0
        self.filter_offset = 10000000
        self.ofmap_offset = 20000000
        self.topofile = ""
        self.bandwidths = []
        self.memory_banks = 1
        self.memory_map = memory_map()

        self.valid_conf_flag = False

        self.valid_df_list = ['os', 'ws', 'is']

    #
    def read_conf_file(self, conf_file_in):

        me = 'scale_config.' + 'read_conf_file()'

        config = cp.ConfigParser()
        config.read(conf_file_in)

        section = 'general'
        self.run_name = config.get(section, 'run_name')

        # Anand: ISSUE #2. Patch
        section = 'run_presets'
        bw_mode_string = config.get(section, 'InterfaceBandwidth')
        if bw_mode_string == 'USER':
            self.use_user_bandwidth = True
        elif bw_mode_string == 'CALC':
            self.use_user_bandwidth = False
        else:
            message = 'ERROR: ' + me
            message += 'Use either USER or CALC in InterfaceBandwidth feild. Aborting!'
            return

        section = 'architecture_presets'
        self.array_rows = int(config.get(section, 'ArrayHeight'))
        self.array_cols = int(config.get(section, 'ArrayWidth'))
        self.ifmap_sz_kb = int(config.get(section, 'ifmapsramszkB'))
        self.filter_sz_kb = int(config.get(section, 'filtersramszkB'))
        self.ofmap_sz_kb = int(config.get(section, 'ofmapsramszkB'))
        self.ifmap_offset = int(config.get(section, 'IfmapOffset'))
        self.filter_offset = int(config.get(section, 'FilterOffset'))
        self.ofmap_offset = int(config.get(section, 'OfmapOffset'))
        self.df = config.get(section, 'Dataflow')
        self.memory_banks = int(config.get(section, 'MemoryBanks').strip())

        # Anand: ISSUE #2. Patch
        if self.use_user_bandwidth:
            self.bandwidths = [int(x.strip())
                               for x in config.get(section, 'Bandwidth').strip().split(',')]

            # Anand: ISSUE #12. Fix
            assert self.memory_banks == len(self.bandwidths), \
                'In USER mode bandwidths for each memory bank is a required input'

        if self.df not in self.valid_df_list:
            print("WARNING: Invalid dataflow")

        # Anand: Added the memory bank check to avoid stray errors
        if self.memory_banks > 1:
            section = 'memory_map_files'
            if not os.path.exists(config.get(section, 'MemoryMapIfmap')):
                print("Ifmap file does not exist")
                sys.exit(-1)
            ifmap_mem_map_file = config.get(section, 'MemoryMapIfmap')

            if not os.path.exists(config.get(section, 'MemoryMapFilter')):
                print("Filter file does not exist")
                sys.exit(-1)
            filter_mem_map_file = config.get(section, 'MemoryMapFilter')

            if not os.path.exists(config.get(section, 'MemoryMapOfmap')):
                print("Ofmap file does not exist")
                sys.exit(-1)

            ofmap_mem_map_file = config.get(section, 'MemoryMapOfmap')

            self.memory_map.set_params(num_banks=self.memory_banks,
                                       ifmap_map_file=ifmap_mem_map_file,
                                       filter_map_file=filter_mem_map_file,
                                       ofmap_map_file=ofmap_mem_map_file
                                       )
        elif self.memory_banks == 1:
            self.memory_map.set_single_bank_params( filter_offset=self.filter_offset,
                                                    ofmap_offset=self.ofmap_offset)

        if config.has_section('network_presets'):  # Read network_presets
            self.topofile = config.get(section, 'TopologyCsvLoc').split('"')[1]

        self.valid_conf_flag = True

    #
    def update_from_list(self, conf_list):
        if not len(conf_list) > 11:
            print("ERROR: scale_config.update_from_list: "
                  "Incompatible number of elements in the list")

        self.run_name = conf_list[0]
        self.array_rows = int(conf_list[1])
        self.array_cols = int(conf_list[2])
        self.ifmap_sz_kb = int(conf_list[3])
        self.filter_sz_kb = int(conf_list[4])
        self.ofmap_sz_kb = int(conf_list[5])
        self.ifmap_offset = int(conf_list[6])
        self.filter_offset = int(conf_list[7])
        self.ofmap_offset = int(conf_list[8])
        self.df = conf_list[9]
        bw_mode_string = str(conf_list[10])

        assert bw_mode_string in ['CALC', 'USER'], 'Invalid mode of operation'
        if bw_mode_string == "USER":
            assert not len(conf_list) < 12, 'The user bandwidth needs to be provided'
            self.bandwidths = conf_list[11]
            self.use_user_bandwidth = True
        elif bw_mode_string == 'CALC':
            self.use_user_bandwidth = False

        if len(conf_list) > 12:
            self.memory_banks = conf_list[12]
        else:
            self.memory_banks = 1

        if bw_mode_string == "USER":
            assert len(self.bandwidths) == self.memory_banks, 'Bandwidths and num banks dont match'

        if self.memory_banks > 1:
            assert not len(conf_list) < 14, 'Memory maps should be provided'
            self.memory_map = conf_list[13]

            assert len(self.memory_map) == self.memory_banks, 'Each bank should have an unique map'

        if len(conf_list) == 15:
            self.topofile = conf_list[14]

        self.valid_conf_flag = True

    #
    def write_conf_file(self, conf_file_out):
        if not self.valid_conf_flag:
            print('ERROR: scale_config.write_conf_file: No valid config loaded')
            return

        config = cp.ConfigParser()

        section = 'general'
        config.add_section(section)
        config.set(section, 'run_name', str(self.run_name))

        section = 'architecture_presets'
        config.add_section(section)
        config.set(section, 'ArrayHeight', str(self.array_rows))
        config.set(section, 'ArrayWidth', str(self.array_cols))

        config.set(section, 'ifmapsramszkB', str(self.ifmap_sz_kb))
        config.set(section, 'filtersramszkB', str(self.filter_sz_kb))
        config.set(section, 'ofmapsramszkB', str(self.ofmap_sz_kb))

        config.set(section, 'IfmapOffset', str(self.ifmap_offset))
        config.set(section, 'FilterOffset', str(self.filter_offset))
        config.set(section, 'OfmapOffset', str(self.ofmap_offset))

        config.set(section, 'Dataflow', str(self.df))
        config.set(section, 'Bandwidth', ','.join([str(x) for x in self.bandwidths]))
        config.set(section, 'MemoryBanks', str(self.memory_banks))

        section = 'network_presets'
        config.add_section(section)
        topofile = '"' + self.topofile + '"'
        config.set(section, 'TopologyCsvLoc', str(topofile))

        with open(conf_file_out, 'w') as configfile:
            config.write(configfile)

    #
    def scale_memory_maps(self, num_layers=1):
        me = 'scale_config.' + 'scale_memory_maps'

        if not self.valid_conf_flag:
            message = 'ERROR: ' + me
            message += ': Config needs to be read/set first'
            print(message)
            return

        if self.memory_banks == 1:
            self.memory_map.scale_single_bank_params(num_layers=num_layers)

    #
    def set_arr_dims(self, rows=1, cols=1):
        self.array_rows = rows
        self.array_cols = cols

    #
    def set_dataflow(self, dataflow='os'):
        self.df = dataflow

    #
    def set_buffer_sizes_kb(self, ifmap_size_kb=1, filter_size_kb=1, ofmap_size_kb=1):
        self.ifmap_sz_kb = ifmap_size_kb
        self.filter_sz_kb = filter_size_kb
        self.ofmap_sz_kb = ofmap_size_kb

    #
    def set_topology_file(self, topofile=''):
        self.topofile = topofile

    #
    def set_offsets(self,
                    ifmap_offset=0,
                    filter_offset=10000000,
                    ofmap_offset=20000000
                    ):
        self.ifmap_offset = ifmap_offset
        self.filter_offset = filter_offset
        self.ifmap_offset = ofmap_offset
        self.valid_conf_flag = True

    #
    def force_valid(self):
        self.valid_conf_flag = True

    #
    def set_bw_mode_to_calc(self):
        self.use_user_bandwidth = False

    #
    def use_user_dram_bandwidth(self):
        if not self.valid_conf_flag:
            me = 'scale_config.' + 'use_user_dram_bandwidth()'
            message = 'ERROR: ' + me + ': Configuration is not valid'
            print(message)
            return

        return self.use_user_bandwidth

    #
    def get_conf_as_list(self):
        out_list = []

        if not self.valid_conf_flag:
            print("ERROR: scale_config.get_conf_as_list: Configuration is not valid")
            return

        out_list.append(str(self.run_name))

        out_list.append(str(self.array_rows))
        out_list.append(str(self.array_cols))

        out_list.append(str(self.ifmap_sz_kb))
        out_list.append(str(self.filter_sz_kb))
        out_list.append(str(self.ofmap_sz_kb))

        out_list.append(str(self.ifmap_offset))
        out_list.append(str(self.filter_offset))
        out_list.append(str(self.ofmap_offset))

        out_list.append(str(self.df))
        out_list.append(str(self.topofile))
        out_list.append(str(self.memory_banks))

        # Note: This will just show the memory location of the object.
        #       Making this visible to the user is necessary so that no errors are committed
        out_list.append(str(self.memory_map))

        return out_list

    def get_run_name(self):
        if not self.valid_conf_flag:
            print("ERROR: scale_config.get_run_name() : Config data is not valid")
            return

        return self.run_name

    def get_topology_path(self):
        if not self.valid_conf_flag:
            print("ERROR: scale_config.get_topology_path() : Config data is not valid")
            return
        return self.topofile

    def get_topology_name(self):
        if not self.valid_conf_flag:
            print("ERROR: scale_config.get_topology_name() : Config data is not valid")
            return

        name = self.topofile.split('/')[-1].strip()
        name = name.split('.')[0]

        return name

    def get_dataflow(self):
        if self.valid_conf_flag:
            return self.df

    def get_array_dims(self):
        if self.valid_conf_flag:
            return self.array_rows, self.array_cols

    def get_mem_sizes(self):
        me = 'scale_config.' + 'get_mem_sizes()'

        if not self.valid_conf_flag:
            message = 'ERROR: ' + me
            message += 'Config is not valid. Not returning any values'
            return

        return self.ifmap_sz_kb, self.filter_sz_kb, self.ofmap_sz_kb

    def get_offsets(self):
        if self.valid_conf_flag:
            return self.ifmap_offset, self.filter_offset, self.ofmap_offset

    def get_bandwidths_as_string(self):
        if self.valid_conf_flag:
            return ','.join([str(x) for x in self.bandwidths])

    def get_mem_banks(self):
        if self.valid_conf_flag:
            return self.memory_banks

    def get_mem_map_obj(self):
        if self.valid_conf_flag:
            return self.memory_map

    def get_bandwidths_as_list(self):
        if self.valid_conf_flag:
            return self.bandwidths

    def get_min_dram_bandwidth(self):
        if not self.use_user_dram_bandwidth():
            me = 'scale_config.' + 'get_min_dram_bandwidth()'
            message = 'ERROR: ' + me + ': No user bandwidth provided'
            print(message)
        else:
            return min(self.bandwidths)

    # FIX ISSUE #14
    @staticmethod
    def get_default_conf_as_list():
        dummy_obj = scale_config()
        dummy_obj.force_valid()
        out_list = dummy_obj.get_conf_as_list()
        return out_list
