import sys
import time
import numpy as np
import scipy
import matplotlib.pyplot as plt
import time
from scipy.ndimage import label

class DmdPattern():
    def __init__(self, pattern:str, sequence:str, width: int, height: int, modes: int, grayscale: int =255):
        """""
        A class to generate mask patterns.  
        :param pattern: The type of sampling method.  Options are: Hadamard, 
        :param sequence: The ordering of the masks.  Options are: Natural 'N', Walsh 'W', Cake Cutting 'CC', Inverse Cake Cutting 'ICC'
            Russian Doll 'RD', Total Variation 'TV', Total Gradient Ascending 'TG'
        :param width: The width of each mask.  Set to: 16, 32, 64, 128, 256, 512
        :param height: The height of each mask.  Set to: 16, 32, 64, 128, 256, 512
        :param modes: The number of modes sampled. 
        :param grayscale: Grayscale of the image (ranges from 1 to 255)
        """""
        self.pattern = pattern
        self.sequence = sequence
        self.width = width 
        self.height = height 
        self.size = width * height # width = height in current applications
        self.modes = modes
        self.grayscale = grayscale

    def execute(self):
        # type: list [np.array] data type:float64

        def conjugate(pattern):
            pattern = (pattern==0).astype(int).astype(np.uint8)
            return pattern
        if self.pattern == "h": # Hadamard Sampling
            temp = hadamard(self.size)
            positive = []
            if self.sequence == 'N': # Natural ordering
                hadamard_matrix = temp.astype(np.uint8)
                for i in range(self.size):
                    test = hadamard_matrix[i].reshape(int(self.width), int(self.height))
                    rotated = np.rot90(test)
                    positive.append(rotated)
                negative = [conjugate(pattern) for pattern in positive]

                positive = three_dimension(positive)
                negative = three_dimension(negative)
                positive = [(pattern.astype(np.uint8) *255) for pattern in positive]
                negative = [(pattern.astype(np.uint8) *255) for pattern in negative]

                if self.modes == 1:
                    return positive, negative
                if self.modes == 6:
                    positive_combined = []
                    negative_combined = []
                    for i in range(self.size):
                        positive_combined.append(np.tile(positive[i], (2, 3)))
                        negative_combined.append(np.tile(negative[i], (2,3)))
                    
                   
                    return positive_combined, negative_combined

            
            if self.sequence == 'W': # Walsh sequency ordering
                hadamard_matrix = sequency(temp)
                for i in range(self.size):
                    test = hadamard_matrix[i].reshape(int(self.width), int(self.height))
                    rotated = np.rot90(test)
                    positive.append(rotated)
                negative = [conjugate(pattern) for pattern in positive]

                positive = three_dimension(positive)
                negative = three_dimension(negative)
                positive = [(pattern.astype(np.uint8) *255) for pattern in positive]
                negative = [(pattern.astype(np.uint8) *255) for pattern in negative]

                if self.modes == 1:
                    return positive, negative
                if self.modes == 6:
                    positive_combined = []
                    negative_combined = []
                    for i in range(self.size):
                        positive_combined.append(np.tile(positive[i], (2, 3)))
                        negative_combined.append(np.tile(negative[i], (2,3)))
                return positive_combined, negative_combined
            
            if self.sequence == 'CC':
                hadamard_matrix = cake_cutting_order(temp)
                for i in range(self.size):
                    test = hadamard_matrix[i].reshape(int(self.width), int(self.height))
                    positive.append(test)
                negative = [conjugate(pattern) for pattern in positive]

                positive = three_dimension(positive)
                negative = three_dimension(negative)
                positive = [(pattern.astype(np.uint8) *255) for pattern in positive]
                negative = [(pattern.astype(np.uint8) *255) for pattern in negative]

                if self.modes == 1:
                    return positive, negative
                if self.modes == 6:
                    positive_combined = []
                    negative_combined = []
                    for i in range(self.size):
                        positive_combined.append(np.tile(positive[i], (2, 3)))
                        negative_combined.append(np.tile(negative[i], (2,3)))
                return positive_combined, negative_combined

            if self.sequence == 'ICC':
                hadamard_matrix = cake_cutting_order(temp)
                for i in range(self.size):
                    test = hadamard_matrix[i].reshape(int(self.width), int(self.height))
                    positive.append(test)
                positive = reverse(positive)
                negative = [conjugate(pattern) for pattern in positive]

                positive = three_dimension(positive)
                negative = three_dimension(negative)
                positive = [(pattern.astype(np.uint8) *255) for pattern in positive]
                negative = [(pattern.astype(np.uint8) *255) for pattern in negative]

                if self.modes == 1:
                    return positive, negative
                if self.modes == 6:
                    positive_combined = []
                    negative_combined = []
                    for i in range(self.size):
                        positive_combined.append(np.tile(positive[i], (2, 3)))
                        negative_combined.append(np.tile(negative[i], (2,3)))
                return positive_combined, negative_combined
            
            if self.sequence == 'RD':
                negative = [conjugate(pattern) for pattern in positive]
                return positive, negative
            if self.sequence == 'TV':
                negative = [conjugate(pattern) for pattern in positive]
                return positive, negative
            if self.sequence == 'TG':
                negative = [conjugate(pattern) for pattern in positive]
                return positive, negative
def three_dimension(pattern):
    def inner_loop(two_dimension_pattern):
        return two_dimension_pattern.T[:,:,np.newaxis]
    return list(map(inner_loop, pattern))      
def hadamard(size):
    """"
    Generate a hadamard matrix of the appropriate size
    """
    print(size)
    
    
    hadamard_matrix = scipy.linalg.hadamard(size)
    hadamard_matrix = (hadamard_matrix == 1).astype(int)
     
    return hadamard_matrix

def sequency(matrix):
    """
    Reorder the rows of a given Hadamard matrix according to the sequency order.
    """
    n = matrix.shape[0]
    
    # Generate sequency order array
    sequency_order = [bin(i).count('1') for i in range(n)]

    # Sort rows of the Hadamard matrix based on sequency order
    sequency_ordered_hadamard = matrix[np.argsort(sequency_order)]

    return sequency_ordered_hadamard

def dfs(matrix, visited, row, col):
    """
    Depth-first search to identify connected regions within the reshaped "cake".
    """
    n_rows, n_cols = matrix.shape
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    stack = [(row, col)]
    visited[row][col] = True

    while stack:
        current_row, current_col = stack.pop()

        for d_row, d_col in directions:
            new_row, new_col = current_row + d_row, current_col + d_col
            if 0 <= new_row < n_rows and 0 <= new_col < n_cols and matrix[new_row][new_col] == matrix[current_row][current_col] and not visited[new_row][new_col]:
                stack.append((new_row, new_col))
                visited[new_row][new_col] = True

def count_connected_regions(matrix):
    """
    Count the number of connected regions in a reshaped "cake".
    """
    n_rows, n_cols = matrix.shape
    visited = np.zeros((n_rows, n_cols), dtype=bool)
    count = 0

    for i in range(n_rows):
        for j in range(n_cols):
            if not visited[i][j]:
                dfs(matrix, visited, i, j)
                count += 1

    return count

def cake_cutting_order(hadamard_matrix):
    """
    Reorder the rows of a Hadamard matrix according to the number of connected regions (piece number).
    """
    n = hadamard_matrix.shape[0]
    reshaped_cakes = []

    # Reshape each row of the Hadamard matrix into a matrix of pixels
    for row in hadamard_matrix:
        reshaped_cake = row.reshape(int(np.sqrt(n)), -1)
        reshaped_cakes.append(reshaped_cake)

    # Count the number of connected regions in each reshaped "cake"
    piece_numbers = [count_connected_regions(cake) for cake in reshaped_cakes]

    # Sort the rows of the Hadamard matrix based on the number of connected regions
    cake_ordered_hadamard = hadamard_matrix[np.argsort(piece_numbers)]

    return cake_ordered_hadamard

def reverse(matrix):
    reversed = matrix[::-1]
    return reversed

def plot_pixel(image_matrix):

    fig,ax = plt.subplots() 
    im = ax.imshow(image_matrix, cmap='gray') # Display the image
    ax.set_axis_off()
    # Show the plot
    plt.show()

"""""
positive, negative= DmdPattern("h","CC", 2, 2, 1, 255).execute()

print(positive[0])
print(negative[0])

for i in range(16):
   plot_pixel(positive[i])

"""""
