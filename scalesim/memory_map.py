import sys


class memory_map:
    def __init__(self):

        self.num_mappings = 1
        self.num_banks = 1

        # 2-D list: Num_layers x Num_banks
        self.ifmap_map_list = []
        self.filter_map_list = []
        self.ofmap_map_list = []

        # Flags
        self.map_data_valid = False

    #
    def set_single_bank_params(self, filter_offset=10000000, ofmap_offset=20000000):
        self.num_banks = 1
        self.num_mappings = 1

        self.ifmap_map_list = [filter_offset]
        self.filter_map_list = [ofmap_offset]
        self.ofmap_map_list = [sys.maxsize]

        self.map_data_valid = True

    #
    def scale_single_bank_params(self, num_layers=1):
        me = 'memory_map.' + 'scale_single_bank_params()'

        if not self.map_data_valid:
            message = 'ERROR: ' + me
            message += ' : Initial single bank params need to be set first'
            print(message)
            return

        prev_ifmap_map_list = self.ifmap_map_list
        prev_filter_map_list = self.filter_map_list
        prev_ofmap_map_list = self.ofmap_map_list

        self.ifmap_map_list = prev_ifmap_map_list * num_layers
        self.filter_map_list = prev_filter_map_list * num_layers
        self.ofmap_map_list = prev_ofmap_map_list * num_layers

        self.num_mappings = num_layers

    #
    def set_params(self, num_banks=1, ifmap_map_file='', filter_map_file='', ofmap_map_file=''):
        success = 0

        if num_banks > 0:
            self.num_banks = num_banks
            success += 1
        else:
            print('Error')

        if not ifmap_map_file == '':
            success += self.read_ifmap_mapping_from_file(ifmap_map_file)
        else:
            print('Error')

        if not ofmap_map_file == '':
            success += self.read_ofmap_mapping_from_file(ofmap_map_file)
        else:
            print('Error')

        if not filter_map_file == '':
            success += self.read_filter_mapping_from_file(ifmap_map_file)
        else:
            print('Error')

        if success == 4:
            self.num_mappings = min(len(self.ifmap_map_list), len(self.filter_map_list), len(self.ofmap_map_list))      # Min is used for safety, all the three should be of same len
            self.map_data_valid = True

    #
    def read_ifmap_mapping_from_file(self, filename = ''):
        try:
            f = open(filename,'r')

            for row in f:
                elems = [int(x.strip()) for x in row.strip().split(',')]
                self.ifmap_map_list.append(elems[self.num_banks])

            return 1

        except:
            print('Unable to read ifmap mapping from ' + filename)
            return 0

    #
    def read_filter_mapping_from_file(self, filename=''):
        try:
            f = open(filename, 'r')

            for row in f:
                elems = [int(x.strip()) for x in row.strip().split(',')]
                self.filter_map_list.append(elems[:self.num_banks])

            return 1

        except:
            print('Unable to read filter mapping from ' + filename)
            return 0

    #
    def read_ofmap_mapping_from_file(self, filename=''):
        try:
            f = open(filename, 'r')

            for row in f:
                elems = [int(x.strip()) for x in row.strip().split(',')]
                self.ofmap_map_list.append(elems[:self.num_banks])

            return 1

        except:
            print('Unable to read ofmap mapping from ' + filename)
            return 0

    #
    def get_ifmap_mapping(self, layer_id=0):
        me = 'memory_map.' + 'get_ifmap_mapping'

        if not self.map_data_valid:
            message = 'ERROR: ' + me
            message += ' : Mapping not valid'
            print(message)
            return

        if not layer_id < self.num_mappings:
            message = 'ERROR: ' + me
            message += ' : No associated mapping for this layer'
            print(message)
            return

        # Ensure that we are sending a list out
        if len([self.ifmap_map_list[layer_id]]) == 1:
            return [self.ifmap_map_list[layer_id]]
        else:
            return self.ifmap_map_list[layer_id]

    #
    def get_filter_mapping(self, layer_id=0):
        me = 'memory_map.' + 'get_filter_mapping'

        if not self.map_data_valid:
            message = 'ERROR: ' + me
            message += ' : Mapping not valid'
            print(message)
            return

        if not layer_id < self.num_mappings:
            message = 'ERROR: ' + me
            message += ' : No associated mapping for this layer'
            print(message)
            return

        # Ensure that we are sending a list out
        if len([self.filter_map_list[layer_id]]) == 1:
            return [self.filter_map_list[layer_id]]
        else:
            return self.filter_map_list[layer_id]

    #
    def get_ofmap_mapping(self, layer_id=0):
        me = 'memory_map.' + 'get_ofmap_mapping'

        if not self.map_data_valid:
            message = 'ERROR: ' + me
            message += ' : Mapping not valid'
            print(message)
            return

        if not layer_id < self.num_mappings:
            message = 'ERROR: ' + me
            message += ' : No associated mapping for this layer'
            print(message)
            return


        # Ensure that we are sending a list out
        if len([self.ofmap_map_list[layer_id]]) == 1:
            return [self.ofmap_map_list[layer_id]]
        else:
            return self.ofmap_map_list[layer_id]
