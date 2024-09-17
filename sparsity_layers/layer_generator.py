import random

def generate_row(K, S, array_size, randomize=True):
    # Initialize the row with zeros
    row = [0] * K
    num_blocks = K // array_size

    for block in range(num_blocks):
        block_start = block * array_size
        
        if randomize:
            # Generate S random positions within the block
            ones_positions = random.sample(range(array_size), S)
        else:
            # Sequentially place S ones starting from the beginning of the block
            ones_positions = list(range(S))
        
        for pos in ones_positions:
            row[block_start + pos] = 1

    return row

def generate_matrix(N, K, S_list, array_size, randomize=True):
    matrix = []
    for i in range(N):
        S = S_list[i]  # Get the S value for the current row
        row = generate_row(K, S, array_size, randomize)
        matrix.append(row)
    
    return matrix

def print_matrix(matrix):
    for row in matrix:
        print(row)

def write_matrix_to_file(matrix, filename):
    with open(filename, 'w') as file:
        file.write('[')
        for i, row in enumerate(matrix):
            # Write row with proper formatting
            file.write(f"{row}")
            if i < len(matrix) - 1:
                file.write(",\n ")
        file.write(']')

# Example input values
array_size = 4  # Array size
factor = array_size * 64
factor = 1
N = 3 * factor  # Number of rows
K = 64  # Number of columns
S_list = [4, 1, 1] * factor  # Number of non-zero entries for every 'array_size' elements for each row
randomize = False  # Set to True for randomness, False for fixed pattern

# Generate and print the matrix
matrix = generate_matrix(N, K, S_list, array_size, randomize)
# print_matrix(matrix)

# Write the matrix to a text file
filename = "GEMM_6_basic.txt"
write_matrix_to_file(matrix, filename)
