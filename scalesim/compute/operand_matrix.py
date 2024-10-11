import math
import numpy as np
from tqdm import tqdm

from scalesim.topology_utils import topologies as topoutil
from scalesim.scale_config import scale_config as cfg


# This class defines data types for operand matrices
class operand_matrix(object):
    def __init__(self):
        # Objects from outer container classes
        self.config = cfg()
        self.topoutil = topoutil()

        # Layer hyper parameters
        self.layer_id = 0
        self.ifmap_rows, self.ifmap_cols = 1, 1
        self.filter_rows, self.filter_cols = 1, 1
        self.num_input_channels, self.num_filters = 1, 1
        self.row_stride, self.col_stride = 1, 1
        self.batch_size = 1

        #  Derived hyper parameters
        self.ofmap_px_per_filt, self.conv_window_size = 1, 1
        self.ofmap_rows, self.ofmap_cols = 1, 1

        # Offsets
        self.ifmap_offset, self.filter_offset, self.ofmap_offset = 0, 10000000, 20000000
        self.matrix_offset_arr = [0, 10000000, 20000000]

        # Address matrices
        self.ifmap_addr_matrix = np.ones((self.ofmap_px_per_filt, self.conv_window_size), dtype=int)
        self.filter_addr_matrix = np.ones((self.conv_window_size, self.num_filters), dtype=int)
        self.ofmap_addr_matrix = np.ones((self.ofmap_px_per_filt, self.num_filters), dtype=int)

        # Flags
        self.params_set_flag = False
        self.matrices_ready_flag = False

    #
    def set_params(self,
                   config_obj,
                   topoutil_obj,
                   layer_id=0,
                   ):

        self.config = config_obj
        self.topoutil = topoutil_obj
        self.layer_id = layer_id

        # TODO: Marked for cleanup
        #my_name = 'operand_matrix.set_params(): '
        #err_prefix = 'Error: ' + my_name
        #
        #if (not len(layer_hyper_param_arr) == 7 and not len(layer_hyper_param_arr) == 8
        #        and not len(layer_hyper_param_arr) == 9) or (not len(layer_calc_hyper_param_arr) == 4) \
        #        or (not len(self.matrix_offset_arr) == 3):
        #    message = err_prefix + 'Invalid arguments. Exiting.'
        #    print(message)
        #    return -1

        self.ifmap_rows, self.ifmap_cols = self.topoutil.get_layer_ifmap_dims(self.layer_id)
        self.filter_rows, self.filter_cols = self.topoutil.get_layer_filter_dims(self.layer_id)
        self.num_input_channels = self.topoutil.get_layer_num_channels(self.layer_id)
        self.num_filters = self.topoutil.get_layer_num_filters(self.layer_id)
        self.row_stride, self.col_stride = self.topoutil.get_layer_strides(self.layer_id)
        # TODO: Marked for cleanup
        #self.row_stride = layer_hyper_param_arr[6]
        #if len(layer_hyper_param_arr) == 8:
        #    self.col_stride = layer_hyper_param_arr[7]

        # TODO: Anand
        # TODO: Next release
        # TODO: Add an option for batching
        self.batch_size = 1

        # TODO: Marked for cleanup
        #if len(layer_hyper_param_arr) == 9:
        #    self.batch_size = layer_hyper_param_arr[8]

        # Assign the calculated hyper parameters
        self.ofmap_rows, self.ofmap_cols = self.topoutil.get_layer_ofmap_dims(self.layer_id)
        self.ofmap_rows = int(self.ofmap_rows)
        self.ofmap_cols = int(self.ofmap_cols)
        self.ofmap_px_per_filt = int(self.ofmap_rows * self.ofmap_cols)
        self.conv_window_size = int(self.topoutil.get_layer_window_size(self.layer_id))

        # Assign the offsets
        self.ifmap_offset, self.filter_offset, self.ofmap_offset \
            = self.config.get_offsets()

        # Address matrices: This is needed to take into account the updated dimensions
        self.ifmap_addr_matrix = np.ones((self.ofmap_px_per_filt * self.batch_size, self.conv_window_size), dtype='>i4')
        self.filter_addr_matrix = np.ones((self.conv_window_size, self.num_filters), dtype='>i4')
        self.ofmap_addr_matrix = np.ones((self.ofmap_px_per_filt, self.num_filters), dtype='>i4')
        self.params_set_flag = True

        # TODO: This should be called from top level
        # TODO: Implement get() function for getting the matrix
        # TODO: Marked for cleanup
        # Return 0 if operand matrix generation is successful
        #self.create_operand_matrices()
        #if self.matrices_ready_flag:
        #    return True, self.ifmap_addr_matrix, self.filter_addr_matrix, self.ofmap_addr_matrix
        #else:
        #    message = err_prefix + 'Address Matrices not created. Exiting!'
        #    print(message)
        #    return False, None, None, None

    # top level function to create the operand matrices
    def create_operand_matrices(self):
        my_name = 'operand_matrix.create_operand_matrices(): '
        err_prefix = 'Error: ' + my_name

        if not self.params_set_flag:
            message = err_prefix + 'Parameters not set yet. Run set_params(). Exiting'
            print(message)
            return -1

        retcode_1 = self.create_ifmap_matrix()
        retcode_2 = self.create_filter_matrix()
        retcode_3 = self.create_ofmap_matrix()

        retcode = retcode_1 + retcode_2 + retcode_3
        if retcode == 0:
            self.matrices_ready_flag = True

        return retcode

    # creates the ifmap operand
    def create_ifmap_matrix(self):
        my_name = 'operand_matrix.create_ifmap_matrix(): '
        err_prefix = 'Error: ' + my_name

        if not self.params_set_flag:
            message = err_prefix + 'Parameters not set yet. Run set_params(). Exiting'
            print(message)
            return -1

        row_indices = np.arange(self.batch_size * self.ofmap_px_per_filt)
        col_indices = np.arange(self.conv_window_size)
        # Create 2D index arrays using meshgrid
        i, j = np.meshgrid(row_indices, col_indices, indexing='ij')

        # Call calc_ifmap_elem_addr_numpy with 2D index arrays
        self.ifmap_addr_matrix = self.calc_ifmap_elem_addr(i, j)

        # print(self.ifmap_addr_matrix)

        if self.config.sparsity_support:
            temp_matrix = self.ifmap_addr_matrix[:,0:int(self.ifmap_addr_matrix.shape[1]/2)]
            self.ifmap_addr_matrix = temp_matrix

        if False:
            ifmap_matrix_1 = []
            ifmap_matrix_2 = []
            # for i in range(0, len(self.ifmap_addr_matrix), self.config.array_rows):

            # print(len(self.ifmap_addr_matrix[0]))

            for ifmap_row in self.ifmap_addr_matrix:
                for i in range(0, len(ifmap_row), self.config.array_rows*2):
                    start_idx = i
                    end_idx = min(start_idx+self.config.array_rows, len(ifmap_row))
                    ifmap_matrix_1.append(ifmap_row[start_idx:end_idx])

                    i = i + self.config.array_rows
                    start_idx = i
                    end_idx = min(start_idx+self.config.array_rows, len(ifmap_row))
                    ifmap_matrix_2.append(ifmap_row[start_idx:end_idx])                

            ifmap_matrix_1 = np.array(ifmap_matrix_1)
            ifmap_matrix_2 = np.array(ifmap_matrix_2)

            if len(ifmap_matrix_1) == 0:
                ifmap_matrix_1 = np.zeros((1, self.config.array_rows))
            else:
                for matrix_row_index , matrix_row in enumerate(ifmap_matrix_1):
                    if len(matrix_row) < self.config.array_rows:
                        matrix_row_new = np.concatenate((matrix_row, np.zeros(self.config.array_rows - len(matrix_row))))
                        ifmap_matrix_1[matrix_row_index] = matrix_row_new

            for matrix_row_index , matrix_row in enumerate(ifmap_matrix_2):
                if len(matrix_row) == 0:
                    ifmap_matrix_2 = np.zeros((1, self.config.array_rows))
                elif len(matrix_row) < self.config.array_rows:
                    matrix_row_new = np.concatenate((matrix_row, np.zeros(self.config.array_rows - len(matrix_row))))
                    ifmap_matrix_2[matrix_row_index] = matrix_row_new

            # print("Ifmap 1")
            # print(ifmap_matrix_1)
            # print("Ifmap 2")
            # print(ifmap_matrix_2)

            ifmap_matrix = ifmap_matrix_1 + ifmap_matrix_2
            print("IFMAP MATRIX NCBS before")
            print(ifmap_matrix)
            ifmap_matrix = np.reshape(ifmap_matrix, (1, ifmap_matrix.shape[0] * ifmap_matrix.shape[1]))

            print("IFMAP MATRIX NCBS")
            print(ifmap_matrix)

            self.ifmap_addr_matrix = ifmap_matrix

        # print(row_indices)
        # print(col_indices)
        # print(i)
        # print(j)
        # print(self.ifmap_addr_matrix)

        return 0

    # logic to translate ifmap into matrix fed into systolic array MACs
    def calc_ifmap_elem_addr(self, i, j):
        offset = self.ifmap_offset
        ifmap_rows = self.ifmap_rows
        ifmap_cols = self.ifmap_cols
        filter_col = self.filter_cols
        r_stride = self.row_stride
        c_stride = self.col_stride
        Ew = self.ofmap_cols
        channel = self.num_input_channels

        ofmap_row, ofmap_col = np.divmod(i, Ew)
        i_row, i_col = ofmap_row * r_stride, ofmap_col * c_stride
        window_addr = (i_row * ifmap_cols + i_col) * channel

        c_row, k = np.divmod(j, filter_col * channel)
        c_col, c_ch = np.divmod(k, channel)

        valid_indices = np.logical_and(c_row + i_row < ifmap_rows, c_col + i_col < ifmap_cols)
        ifmap_px_addr = np.full(i.shape, -1)
        if valid_indices.any():
            internal_address = (c_row[valid_indices] * ifmap_cols + c_col[valid_indices]) * channel + c_ch[valid_indices]
            ifmap_px_addr[valid_indices] = internal_address + window_addr[valid_indices] + offset

        return ifmap_px_addr

    # creates the ofmap operand
    def create_ofmap_matrix(self):
        my_name = 'operand_matrix.create_ofmap_matrix(): '
        err_prefix = 'Error: ' + my_name
        if not self.params_set_flag:
            message = err_prefix + 'Parameters not set yet. Run set_params(). Exiting'
            print(message)
            return -1
        
        row_indices = np.expand_dims(np.arange(self.ofmap_px_per_filt), axis=1)
        if self.config.sparsity_support:
            _, col_indices = np.unique(np.array(self.filter_addr_matrix[0]), return_inverse=True)
        else:
            col_indices = np.arange(self.num_filters)

        self.ofmap_addr_matrix = self.calc_ofmap_elem_addr(row_indices, col_indices)

        return 0

    # logic to translate ofmap into matrix resulting systolic array MACs
    def calc_ofmap_elem_addr(self, i, j):
        offset = self.ofmap_offset
        num_filt = self.num_filters
        internal_address = num_filt * i + j
        ofmap_px_addr = internal_address + offset
        return ofmap_px_addr

    # creates the filter operand
    def create_filter_matrix(self):
        my_name = 'operand_matrix.create_filter_matrix(): '
        err_prefix = 'Error: ' + my_name
        if not self.params_set_flag:
            message = err_prefix + 'Parameters not set yet. Run set_params(). Exiting'
            print(message)
            return -1

        row_indices = np.expand_dims(np.arange(self.conv_window_size), axis=1)
        col_indices = np.arange(self.num_filters)

        self.filter_addr_matrix = self.calc_filter_elem_addr(row_indices, col_indices)

        if self.config.sparsity_support == True:
            sparse_array = self.topoutil.topo_arrays[self.layer_id][-1].T
            sparse_array = np.reshape(sparse_array, self.filter_addr_matrix.shape)
            self.sparse_filter_array = sparse_array
            self.filter_addr_matrix = np.multiply(self.filter_addr_matrix, sparse_array)
            self.filter_addr_matrix = self.filter_addr_matrix.T
            sparse_filter_matrix = []   
            num_arr_cols = 0
            for iter in range(0, len(col_indices)):
                array = self.filter_addr_matrix[iter][0:8]
                array = [i for i in array if i != 0]
                if(len(array) == 4):
                    sparse_filter_matrix.append(array)
                    num_arr_cols+=1
                elif(len(array) == 2):
                    temp = []
                    temp.append(array[0])
                    temp.append(-1)
                    temp.append(array[1])
                    temp.append(-1)
                    sparse_filter_matrix.append(temp)
                    num_arr_cols+=1
                elif(len(array) == 8):
                    sparse_filter_matrix.append(array[0:4])
                    sparse_filter_matrix.append(array[0:4])
                
            sparse_filter_matrix = np.array(sparse_filter_matrix).T
            self.filter_addr_matrix = sparse_filter_matrix

            num_chunks = len(row_indices)//8
            for _ in range(1, num_chunks):
                self.filter_addr_matrix = np.concatenate((self.filter_addr_matrix, sparse_filter_matrix))

        return 0

    # logic to translate filter into matrix fed into systolic array MACs
    def calc_filter_elem_addr(self, i, j):
        offset = self.filter_offset
        filter_row = self.filter_rows
        filter_col = self.filter_cols
        channel = self.num_input_channels
        internal_address = j * filter_row * filter_col * channel + i
        filter_px_addr = internal_address + offset
        return filter_px_addr

    # function to get a part or the full ifmap operand
    def get_ifmap_matrix_part(self, start_row=0, num_rows=-1, start_col=0,
                              num_cols=-1):
        if num_rows == -1:
            num_rows = self.ofmap_px_per_filt
        if num_cols == -1:
            num_cols = self.conv_window_size
        my_name = 'operand_matrix.get_ifmap_matrix_part(): '
        err_prefix = 'Error: ' + my_name
        if not self.matrices_ready_flag:
            if self.params_set_flag:
                self.create_operand_matrices()
            else:
                message = err_prefix + ": Parameters not set yet. Run set_params(). Exiting!"
                print(message)
                return -1, np.zeros((1, 1))
        if (start_row + num_rows) > self.ofmap_px_per_filt or (start_col + num_cols) > self.conv_window_size:
            message = err_prefix + ": Illegal arguments. Exiting!"
            print(message)
            return -2, np.zeros((1, 1))

        # Anand: ISSUE #3. Patch
        #end_row = start_row + num_rows + 1
        #end_col = start_col + num_cols + 1
        #ret_mat = self.ifmap_addr_matrix[start_row: end_row][start_col: end_col]
        end_row = start_row + num_rows
        end_col = start_col + num_cols
        ret_mat = self.ifmap_addr_matrix[start_row: end_row, start_col: end_col]
        return 0, ret_mat

    def get_ifmap_matrix(self):
        return self.get_ifmap_matrix_part()

    # function to get a part or the full filter operand
    def get_filter_matrix_part(self, start_row=0, num_rows=-1, start_col=0,
                               num_cols=-1):

        if num_rows == -1:
            num_rows = self.conv_window_size
        if num_cols == -1:
            num_cols = self.num_filters

        my_name = 'operand_matrix.get_filter_matrix_part(): '
        err_prefix = 'Error: ' + my_name
        if not self.matrices_ready_flag:
            if self.params_set_flag:
                self.create_operand_matrices()
            else:
                message = err_prefix + ": Parameters not set yet. Run set_params(). Exiting!"
                print(message)
                return -1, np.zeros((1, 1))
        if (start_row + num_rows) > self.conv_window_size or (start_col + num_cols) > self.num_filters:
            message = err_prefix + ": Illegal arguments. Exiting!"
            print(message)
            return -2, np.zeros((1, 1))

        # Anand: ISSUE #3. FIX
        #end_row = start_row + num_rows + 1
        #end_col = start_col + num_cols + 1
        end_row = start_row + num_rows
        end_col = start_col + num_cols

        # Anand: ISSUE #3. FIX
        #ret_mat = self.filter_addr_matrix[start_row: end_row][start_col: end_col]
        # ret_mat = self.filter_addr_matrix[start_row: end_row, start_col: end_col]
        if self.config.sparsity_support == True:
            ret_mat = self.filter_addr_matrix
        else:
            ret_mat = self.filter_addr_matrix[start_row: end_row, start_col: end_col]

        return 0, ret_mat

    def get_filter_matrix(self):
        return self.get_filter_matrix_part()

    # function to get a part or the full ofmap operand
    def get_ofmap_matrix_part(self, start_row=0, num_rows=-1, start_col=0,
                               num_cols=-1):

        # Since we cannot pass self as an argument in the member functions
        # This is an alternate way of making the matrix dimensions as defaults
        if num_rows == -1:
            num_rows = self.ofmap_px_per_filt
        if num_cols == -1:
            num_cols = self.num_filters
        my_name = 'operand_matrix.get_ofmap_matrix_part(): '
        err_prefix = 'Error: ' + my_name
        if not self.matrices_ready_flag:
            if self.params_set_flag:
                self.create_operand_matrices()
            else:
                message = err_prefix + ": Parameters not set yet. Run set_params(). Exiting!"
                print(message)
                return -1, np.zeros((1, 1))
        if (start_row + num_rows) > self.ofmap_px_per_filt or (start_col + num_cols) > self.num_filters:
            message = err_prefix + ": Illegal arguments. Exiting!"
            print(message)
            return -2, np.zeros((1, 1))

        # Anand: ISSUE #3. Patch
        #end_row = start_row + num_rows + 1
        #end_col = start_col + num_cols + 1
        #ret_mat = self.filter_addr_matrix[start_row: end_row][start_col: end_col]
        end_row = start_row + num_rows
        end_col = start_col + num_cols
        # Anand: ISSUE #7. Patch
        #ret_mat = self.filter_addr_matrix[start_row: end_row, start_col: end_col]
        if self.config.sparsity_support == True:
            ret_mat =self.ofmap_addr_matrix
        else:
            ret_mat = self.ofmap_addr_matrix[start_row: end_row, start_col: end_col]

        return 0, ret_mat

    def get_ofmap_matrix(self):
        return self.get_ofmap_matrix_part()

    def get_all_operand_matrix(self):
        if not self.matrices_ready_flag:
            me = 'operand_matrix.' + 'get_all_operand_matrix()'
            message = 'ERROR:' + me + ': Matrices not ready or matrix gen failed'
            print(message)
            return

        return self.ifmap_addr_matrix, \
               self.filter_addr_matrix, \
               self.ofmap_addr_matrix


if __name__ == '__main__':
    opmat = operand_matrix()
    tutil = topoutil()
    lid = 3
    topology_file = "../../topologies/mlperf/test.csv"
    tutil.load_arrays(topofile=topology_file)
    for i in range(tutil.get_num_layers()):
        layer_param_arr = tutil.get_layer_params(layer_id=i)
        ofmap_dims = tutil.get_layer_ofmap_dims(layer_id=i)
        ofmap_px_filt = tutil.get_layer_num_ofmap_px(layer_id=i) / tutil.get_layer_num_filters(layer_id=i)
        conv_window_size = tutil.get_layer_window_size(layer_id=i)
        layer_calc_hyper_param_arr = [ofmap_dims[0], ofmap_dims[1], ofmap_px_filt, conv_window_size]
        config_arr = [512, 512, 256, 8, 8]
        #[matrix_set, ifmap_addr_matrix, filter_addr_matrix, ofmap_addr_matrix] \
        #    = opmat.set_params(layer_hyper_param_arr=layer_param_arr[1:],
        #                       layer_calc_hyper_param_arr=layer_calc_hyper_param_arr,
        #                       offset_list=[0, 1000000, 2000000])
