import math
import numpy as np
from tqdm import tqdm

from scalesim.topology_utils import topologies as topoutil
from scalesim.layout_utils import layouts as layoututil
from scalesim.scale_config import scale_config as cfg


# This class defines data types for operand matrices
class operand_matrix(object):
    def __init__(self):
        # Objects from outer container classes
        self.config = cfg()
        self.topoutil = topoutil()
        self.layoututil = layoututil()

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
                   layoututil_obj,
                   layer_id=0,
                   ):

        self.config = config_obj
        self.topoutil = topoutil_obj
        self.layoututil = layoututil_obj
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

    def get_ifmap_prefetch_matrix_custom_layout(self):
        """
            Default ifmap layout:
            for x in X:
              for y in Y:
                for c in C:
            "X->Y->C"
            Under which, the address should be calculated as

            ifmap_px_addr = internal_address + offset
        """
        #                          X, Y, C
        #ifmap_intraline_factor = [2, 2, 16] # A given fixed dimension order
        #ifmap_intraline_order  = [0, 1, 2] # A given fixed dimension order
        #ifmap_interline_order  = [1+3, 2+3, 0+3] # A given fixed dimension order
        ifmap_intraline_factor = self.layoututil.get_layer_ifmap_intraline_factor()
        ifmap_intraline_order = self.layoututil.get_layer_ifmap_intraline_order()
        ifmap_interline_order = self.layoututil.get_layer_ifmap_interline_order()
        
        # Sanity Checking
        assert np.prod(ifmap_intraline_factor) == int(self.config.get_bandwidths_as_string())

        ifmap_overall_data = np.arange(self.ifmap_rows * self.ifmap_cols * self.num_input_channels)
        
        # Reshape each dimension of ifmap to be a different index.
        ifmap_overall_data = ifmap_overall_data.reshape(self.ifmap_rows, self.ifmap_cols, self.num_input_channels)
        num_x_t = math.ceil(self.ifmap_rows / ifmap_intraline_factor[0])
        padding_x = num_x_t * ifmap_intraline_factor[0] - self.ifmap_rows
        num_y_t = math.ceil(self.ifmap_cols / ifmap_intraline_factor[1])
        padding_y = num_y_t * ifmap_intraline_factor[1] - self.ifmap_cols
        num_c_t = math.ceil(self.num_input_channels / ifmap_intraline_factor[2])
        padding_c = num_c_t * ifmap_intraline_factor[2] - self.num_input_channels
        x_t = ifmap_intraline_factor[0]
        y_t = ifmap_intraline_factor[1]
        c_t = ifmap_intraline_factor[2]

        ifmap_overall_data_pad = np.pad(ifmap_overall_data, [(0, padding_x), (0, padding_y), (0, padding_c)], 'constant', constant_values=-1)
        # Note that: padded -1 will be removed in read_buffer/prepare_hashed_buffer, so won't waste on-chip memory.
        
        # Factorize each dimension of ifmap to be interline (row) and intraline (col).
        assert ifmap_overall_data_pad.shape[0] % ifmap_intraline_factor[0] == 0, (f"dimension X must be full divisible by"
             f" intraline factorization; post-padding X:{ifmap_overall_data_pad.shape[0]}, factor:{ifmap_intraline_factor[0]}")
        assert ifmap_overall_data_pad.shape[1] % ifmap_intraline_factor[1] == 0, (f"dimension Y must be full divisible by"
             f" intraline factorization; post-padding Y:{ifmap_overall_data_pad.shape[1]} factor:{ifmap_intraline_factor[1]}")
        assert ifmap_overall_data_pad.shape[2] % ifmap_intraline_factor[2] == 0, (f"dimension C must be full divisible by" 
             f" intraline factorization; post-padding C:{ifmap_overall_data_pad.shape[2]}, factor:{ifmap_intraline_factor[2]}")
        
        """
            x_t = ifmap_intraline_factor[1]
            y_t = ifmap_intraline_factor[2]
            c_t = ifmap_intraline_factor[3]
            
            for x_1 in range(X, x_t):
              for x_2 in range(x_t):
                for y_1 in range(Y, y1):
                  for y_2 in range(y1):
                    for c_1 in range(C, c_t):
                      for c_2 in range(c_t):
                        # Address specification.
                        # x = x_2 + x_1 * x_t
                        # y = y_2 + y_1 * y_t
                        # c = c_2 + c_1 * c1
        """
        ifmap_overall_data_pad = ifmap_overall_data_pad.reshape(num_x_t, x_t, num_y_t, y_t, num_c_t, c_t)
        
        # Transpose two separate interline dimension order and intraline dimension order.
        ifmap_overall_data_pad = np.transpose(ifmap_overall_data_pad, (0,2,4,1,3,5))

        # Transpose data layout to force a specific order.
        ifmap_overall_data_pad = np.transpose(ifmap_overall_data_pad, 
           (ifmap_interline_order[0], ifmap_interline_order[1], ifmap_interline_order[2], 
            ifmap_intraline_order[0], ifmap_intraline_order[1], ifmap_intraline_order[2]))

        print(f"finalized shape = {ifmap_overall_data_pad.shape}")
        return ifmap_overall_data_pad.reshape(1,-1)
        
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
        ret_mat = self.filter_addr_matrix[start_row: end_row, start_col: end_col]
        return 0, ret_mat

    def get_filter_matrix(self):
        return self.get_filter_matrix_part()


    def get_filter_prefetch_matrix_custom_layout(self):
        """
            Default filter layout:
            for k in K:
              for c in C:
                for r in R:
                  for s in S:
            "K->C->R->S"
            Under which, the address should be calculated as

            internal_address = j * filter_row * filter_col * channel + i
            j:  the kernel index 
        """
        #                            K, C, R, S
        # filter_intraline_factor = [4,16, 1, 1] # A given fixed dimension order
        # filter_intraline_order  = [3, 2, 1, 0] # A given fixed dimension order
        # filter_interline_order  = [0+4, 1+4, 2+4, 3+4] # A given fixed dimension order
        filter_intraline_factor = self.layoututil.get_layer_filter_intraline_factor()
        filter_intraline_order  = self.layoututil.get_layer_filter_intraline_order()
        filter_interline_order  = self.layoututil.get_layer_filter_interline_order()


        # Sanity Checking
        assert np.prod(filter_intraline_factor) == int(self.config.get_bandwidths_as_string())

        filter_overall_data = np.arange(self.filter_rows * self.filter_cols * self.num_input_channels * self.num_filters) + self.filter_offset
        
        # Reshape each dimension of filter to be a different index.
        filter_overall_data = filter_overall_data.reshape(self.num_filters, self.num_input_channels, self.filter_rows, self.filter_cols)
        num_k_t = math.ceil(self.num_filters / filter_intraline_factor[0])
        padding_k = num_k_t * filter_intraline_factor[0] - self.num_filters
        num_c_t = math.ceil(self.num_input_channels / filter_intraline_factor[1])
        padding_c = num_c_t * filter_intraline_factor[1] - self.num_input_channels
        num_r_t = math.ceil(self.filter_rows / filter_intraline_factor[2])
        padding_r = num_r_t * filter_intraline_factor[2] - self.filter_rows
        num_s_t = math.ceil(self.filter_cols / filter_intraline_factor[3])
        padding_s = num_s_t * filter_intraline_factor[3] - self.filter_cols
        k_t = filter_intraline_factor[0]
        c_t = filter_intraline_factor[1]
        r_t = filter_intraline_factor[2]
        s_t = filter_intraline_factor[3]

        filter_overall_data_pad = np.pad(filter_overall_data, [(0, padding_k), (0, padding_c), (0, padding_r), (0, padding_s)], 'constant', constant_values=-1)
        # Note that: padded -1 will be removed in read_buffer/prepare_hashed_buffer, so won't waste on-chip memory.
        
        # Factorize each dimension of filter to be interline (row) and intraline (col).
        assert filter_overall_data_pad.shape[0] % filter_intraline_factor[0] == 0, (f"dimension K must be full divisible by"
             f" intraline factorization; post-padding K:{filter_overall_data_pad.shape[0]}, factor:{filter_intraline_factor[0]}")
        assert filter_overall_data_pad.shape[1] % filter_intraline_factor[1] == 0, (f"dimension C must be full divisible by"
             f" intraline factorization; post-padding C:{filter_overall_data_pad.shape[1]} factor:{filter_intraline_factor[1]}")
        assert filter_overall_data_pad.shape[2] % filter_intraline_factor[2] == 0, (f"dimension R must be full divisible by" 
             f" intraline factorization; post-padding R:{filter_overall_data_pad.shape[2]}, factor:{filter_intraline_factor[2]}")
        assert filter_overall_data_pad.shape[3] % filter_intraline_factor[3] == 0, (f"dimension S must be full divisible by" 
             f" intraline factorization; post-padding S:{filter_overall_data_pad.shape[2]}, factor:{filter_intraline_factor[2]}")
        
        """
            k_t = filter_intraline_factor[0]
            c_t = filter_intraline_factor[1]
            r_t = filter_intraline_factor[2]
            s_t = filter_intraline_factor[3]

            for k_1 in range(K, k_t):
              for k_2 in range(k_t):
                for c_1 in range(C, c_t):
                  for c_2 in range(c_t):
                    for r_1 in range(R, r_t):
                      for r_2 in range(r_t):
                        for s_1 in range(S, s_t):
                          for s_2 in range(s_t):
                            # Address specification.
                            # k = k_2 + k_1 * k_t
                            # c = c_2 + c_1 * c_t
                            # r = r_2 + r_1 * r1
                            # s = s_2 + s_1 * s1
        """
        filter_overall_data_pad = filter_overall_data_pad.reshape(num_k_t, k_t, num_c_t, c_t, num_r_t, r_t, num_s_t, s_t)
        
        # Transpose two separate interline dimension order and intraline dimension order.
        filter_overall_data_pad = np.transpose(filter_overall_data_pad, (0,2,4,6,1,3,5,7))

        # Transpose data layout to force a specific order.
        filter_overall_data_pad = np.transpose(filter_overall_data_pad, 
           (filter_interline_order[0], filter_interline_order[1], filter_interline_order[2], filter_interline_order[3], 
            filter_intraline_order[0]+4, filter_intraline_order[1]+4, filter_intraline_order[2]+4, filter_intraline_order[3]+4))

        print(f"finalized filter.shape = {filter_overall_data_pad.shape}")
        return filter_overall_data_pad.reshape(1,-1)
    
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
    layout = layoututil()
    lid = 3
    topology_file = "../../topologies/conv_nets/test.csv"
    layout_file = "../../layouts/conv_nets/test.csv"
    tutil.load_arrays(topofile=topology_file)
    layout.load_arrays(layoutfile=layout_file)
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

        ifmap_intraline_factor = layout.get_layer_ifmap_intraline_factor(layer_id=i)
        ifmap_intraline_order = layout.get_layer_ifmap_intraline_order(layer_id=i)
        ifmap_interline_order = layout.get_layer_ifmap_interline_order(layer_id=i)

        filter_intraline_factor = layout.get_layer_filter_intraline_factor(layer_id=i)
        filter_intraline_order = layout.get_layer_filter_intraline_order(layer_id=i)
        filter_interline_order = layout.get_layer_filter_interline_order(layer_id=i)

        print(f"ifmap_intraline_factor={ifmap_intraline_factor}")
        print(f"ifmap_intraline_order={ifmap_intraline_order}")
        print(f"ifmap_interline_order={ifmap_interline_order}")
        print(f"filter_intraline_factor={filter_intraline_factor}")
        print(f"filter_intraline_order={filter_intraline_order}")
        print(f"filter_interline_order={filter_interline_order}")
