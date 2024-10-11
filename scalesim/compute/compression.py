import numpy as np

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

    def compress_to_ellpack_block(self, matrix, filter_op_mat):
        # Each entry of the original matrix requires 1 word size
        # Each entry in filter_op_mat will require 2 bits of metadata
        original_rows, original_cols = matrix.shape
        new_rows, new_cols = filter_op_mat.shape

        original_storage = original_rows * original_cols # Units: Words
        metadata_storage = ((new_rows * new_cols) * 2) / 32 # Units: Words (considering 1 word = 4 bytes = 32 bits)
        new_storage = (new_rows * new_cols) + metadata_storage # Units: Words (considering 1 word = 4 bytes = 32 bits)

        return original_storage, new_storage, metadata_storage

    def csr_to_blocked_ellpack_indices(self, indices, indptr, max_cols):
        num_rows = len(indptr) - 1
        ellpack_indices = np.zeros((num_rows, max_cols), dtype=int) - 1
        latency = 1

        for i in range(num_rows):
            row_start = indptr[i]
            row_end = indptr[i + 1]
            row_indices = indices[row_start:row_end]

            for j in range(min(len(row_indices), max_cols)):
                ellpack_indices[i, row_indices[j]] = row_indices[j] % 4

        return ellpack_indices, latency

    def csc_to_blocked_ellpack_indices(self, indices, indptr, max_rows):
        num_cols = len(indptr) - 1
        ellpack_indices = np.zeros((max_rows, num_cols), dtype=int) - 1
        latency = 1

        for j in range(num_cols):
            col_start = indptr[j]
            col_end = indptr[j + 1]
            col_indices = indices[col_start:col_end]

            for i in range(min(len(col_indices), max_rows)):
                ellpack_indices[col_indices[i], j] = col_indices[i] % 4

        return ellpack_indices, latency

    def sparse_to_blocked_ellpack_indices(self, sparse_matrix, max_elements_per_row):
        num_rows, num_cols = sparse_matrix.shape
        latency = 0

        ellpack_indices = -np.ones((num_rows, max_elements_per_row), dtype=int)

        for i in range(num_rows):
            row_indices = []

            for j in range(num_cols):
                if sparse_matrix[i, j] != 0:
                    row_indices.append(j)

            row_indices = row_indices[:max_elements_per_row]
            ellpack_indices[i, row_indices] = row_indices 

        return ellpack_indices, latency

    def get_csr_storage(self, matrix):
        data, col_id, row_ptr, original_storage, new_storage, metadata_storage = self.compress_to_csr(matrix)
        return original_storage, new_storage, metadata_storage

    def get_csc_storage(self, matrix):
        data, row_id, col_ptr, original_storage, new_storage, metadata_storage = self.compress_to_csc(matrix)
        return original_storage, new_storage, metadata_storage

    def get_ellpack_block_storage(self, matrix, filter_op_mat):
        original_storage, new_storage, metadata_storage = self.compress_to_ellpack_block(matrix, filter_op_mat)
        return original_storage, new_storage, metadata_storage

    def get_csr_extra_cycles(self, matrix):
        data, _id, _ptr, original_storage, new_storage = self.compress_to_csr(matrix)
        ellpack_mat, delay = self.csr_to_blocked_ellpack_indices(_id, _ptr, matrix.shape[1])
        return ellpack_mat, delay

    def get_csc_extra_cycles(self, matrix):
        data, _id, _ptr, original_storage, new_storage = self.compress_to_csc(matrix)
        ellpack_mat, delay = self.csc_to_blocked_ellpack_indices(_id, _ptr, matrix.shape[0])
        return ellpack_mat, delay

    def get_ellpack_block_extra_cycles(self, matrix):
        ellpack_mat, delay = self.sparse_to_blocked_ellpack_indices(matrix, matrix.shape[1])
        return ellpack_mat, delay
    
