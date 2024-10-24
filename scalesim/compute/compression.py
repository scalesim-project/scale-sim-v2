import numpy as np
import math

class compression:
    def compress_to_csr(self, matrix):
        rows, cols = matrix.shape
        data = []
        col_id = []
        row_ptr = [0]

        for i in range(rows):
            # Find non-zero elements in current row
            non_zero_indices = np.nonzero(matrix[i])[0]
            data.extend(matrix[i, non_zero_indices])
            col_id.extend(non_zero_indices)
            row_ptr.append(len(data))  # Update starting index for next row

        original_storage = rows * cols
        new_storage = (2 * len(col_id)) + len(row_ptr)
        metadata_storage = len(col_id) + len(row_ptr)

        return np.array(data), np.array(col_id), np.array(row_ptr), original_storage, new_storage, metadata_storage

    def compress_to_csc(self, matrix):
        rows, cols = matrix.shape
        data = []
        row_id = []
        col_ptr = [0] * (cols + 1)

        for j in range(cols):
            # Find non-zero elements in current column
            non_zero_indices = np.nonzero(matrix[:, j])[0]
            data.extend(matrix[non_zero_indices, j])
            row_id.extend(non_zero_indices)
            col_ptr[j + 1] = len(data)  # Update starting index for next column

        original_storage = rows * cols
        new_storage = (2 * len(row_id)) + len(col_ptr)
        metadata_storage = len(row_id) + len(col_ptr)

        return np.array(data), np.array(row_id), np.array(col_ptr), original_storage, new_storage, metadata_storage

    def compress_to_ellpack_block(self, matrix, filter_op_mat, sparsity_M):
        # Each entry of the original matrix requires 1 word size
        # Each entry in filter_op_mat will require 2 bits of metadata
        original_rows, original_cols = matrix.shape
        new_rows, new_cols = filter_op_mat.shape

        original_storage = original_rows * original_cols # Units: Words
        metadata_storage = ((new_rows * new_cols) * math.ceil(math.log2(sparsity_M))) / 32 # Units: Words (considering 1 word = 4 bytes = 32 bits)
        new_storage = (new_rows * new_cols) + metadata_storage # Units: Words (considering 1 word = 4 bytes = 32 bits)

        return original_storage, new_storage, metadata_storage

    def get_csr_storage(self, matrix):
        data, col_id, row_ptr, original_storage, new_storage, metadata_storage = self.compress_to_csr(matrix)
        return original_storage, new_storage, metadata_storage

    def get_csc_storage(self, matrix):
        data, row_id, col_ptr, original_storage, new_storage, metadata_storage = self.compress_to_csc(matrix)
        return original_storage, new_storage, metadata_storage

    def get_ellpack_block_storage(self, matrix, filter_op_mat, sparsity_M):
        original_storage, new_storage, metadata_storage = self.compress_to_ellpack_block(matrix, filter_op_mat, sparsity_M)
        return original_storage, new_storage, metadata_storage
    
