from itertools import product
import numpy as np

def generate_composite(z_vector, p_vector, z, n):
    """
    Generate a list of composite diagrams based on the allowed z and p values.

    Args:
        z_vector (np.ndarray): Possible values for z (transmutation steps).
        p_vector (np.ndarray): Possible values for p (propagation steps).
        z (int): Maximum allowed number of transmutations.
        n (int): Number of legs (steps in the diagram).

    Returns:
        np.ndarray: Array of valid composite diagrams.
    """
    composite = []
    
    # Create the Cartesian product of n z_vectors and (n-1) p_vectors
    cartesian_product = product(*([z_vector] * n), *([p_vector] * (n - 1)))
    
    for values in cartesian_product:
        # Split the tuple into z_values and p_values
        z_values = values[:n]
        p_values = values[n:]
        
        # Build the sequence of intermediate values
        intermediates = [1, 1 + z_values[0]]  # Start with a = 1 + alpha
        for i in range(1, n):
            intermediates.append(intermediates[-1] + p_values[i - 1])
            intermediates.append(intermediates[-1] + z_values[i])
        
        # Apply constraints:
        # - Final intermediate value must be zero
        # - Total transmutations <= z
        # - All intermediate values must be non-negative
        if (
            intermediates[-1] == 0 and
            sum(abs(x) for x in z_values) <= z and
            all(x >= 0 for x in intermediates)
        ):
            composite.append([
                [intermediates[2*i], intermediates[2*i + 1]] for i in range(n)
            ])

    return np.asarray(composite)

def coefficient_calc(dummy_array):    
    """
    Calculate the coefficient for a given diagram.

    Args:
        dummy_array (np.ndarray): Array representing a diagram.

    Returns:
        int: Calculated coefficient.
    """
    temp_pair = np.array([0, 0])
    coefficient = 1
    for i in range(len(dummy_array)):
        pair_difference = dummy_array[i][0] - temp_pair[1]
        if pair_difference > 0:
            coefficient *= dummy_array[i][0]
        temp_pair = dummy_array[i]
    return coefficient

def flavour_output(test_array):
    """
    Generate a string representation of a diagram with its flavour and coefficient.

    Args:
        test_array (np.ndarray): Array representing a diagram.

    Returns:
        str: String encoding the diagram's structure and coefficient.
    """
    max_time = len(test_array)
    diag_dictionary = {1: "straight", -1: "wiggle"}
    full_flavour_array = []
    flavour = 1
    for array in test_array:
        sub_flavour_array = [diag_dictionary[flavour]]
        if array[0] - array[1] == 0:
            sub_flavour_array.append(diag_dictionary[flavour])
        for _ in range(array[0] - array[1]):
            flavour *= -1
            sub_flavour_array.append(diag_dictionary[flavour])
        phrase = (
            ''.join(sub_flavour_array) +
            f"[{array[0]},{array[1]},t{max_time},t{max_time-1}]"
        )
        max_time -= 1
        full_flavour_array.append(phrase)
    output_string = (
        f"{coefficient_calc(test_array)}*" +
        '*'.join(full_flavour_array)
    )
    return output_string

# --- Parameters ---
z = 2  # Maximum allowed number of transmutations
n = 6  # Number of legs in the diagram
z_vector = np.arange(-z, 1)  # Allowed z values: [-2, -1, 0]
p_vector = np.array([-1, 1]) # Allowed p values

# --- Generate all valid diagrams ---
composite = generate_composite(z_vector, p_vector, z, n)

print(composite)
print("Total number of diagrams:", len(composite))

# --- Convert diagrams to string representations ---
diagrams_text = [flavour_output(i) for i in composite]

# --- Prepare Mathematica command outputs ---
mathematica_diagram_definitions = []
mathematica_threederivs_command = []
mathematica_fivederivs_command = []
mathematica_threederivs_command_cumulative = []
mathematica_fivederivs_command_cumulative = []

for idx, i in enumerate(composite):
    mathematica_diagram_definitions.append(
        f"term{idx+1}[t6_, t5_, t4_, t3_, t2_, t1_] = Limit[" +
        flavour_output(i) +
        ", t0 -> -Infinity, Assumptions -> {{k > 0, alpha > 0}}]"
    )
    mathematica_threederivs_command.append(
        f"FullSimplify[threeDerivs[term{idx+1}]]"
    )
    mathematica_fivederivs_command.append(
        f"FullSimplify[fiveDerivs[term{idx+1}]]"
    )
    mathematica_threederivs_command_cumulative.append(
        f"FullSimplify[threeDerivs[term{idx+1}]+%]"
    )
    mathematica_fivederivs_command_cumulative.append(
        f"FullSimplify[fiveDerivs[term{idx+1}]+%]"
    )

# --- Write results to files ---
output_dir = '/home/jacob/Documents/imperial/non_markov_epr/diagrams/output/'

with open(output_dir + 'six_legs.txt', 'w') as f:
    for line in diagrams_text:
        f.write(f"{line}\n")

with open(output_dir + 'six_legs_summed.txt', 'w') as f:
    f.write('+'.join(diagrams_text))

with open(output_dir + 'mathematica_diagrams.txt', 'w') as f:
    for line in mathematica_diagram_definitions:
        f.write(f"{line}\n")

with open(output_dir + 'threederivs_command.txt', 'w') as f:
    for line in mathematica_threederivs_command:
        f.write(f"{line}\n")

with open(output_dir + 'fivederivs_command.txt', 'w') as f:
    for line in mathematica_fivederivs_command:
        f.write(f"{line}\n")

with open(output_dir + 'threederivs_command_cumulative.txt', 'w') as f:
    for line in mathematica_threederivs_command_cumulative:
        f.write(f"{line}\n")

with open(output_dir + 'fivederivs_command_cumulative.txt', 'w') as f:
    for line in mathematica_fivederivs_command_cumulative:
        f.write(f"{line}\n")
