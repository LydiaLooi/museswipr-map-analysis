import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

def plot_difficulty_to_jumps_per_second(mu=12.5, lower_sigma_val=10.667, upper_sigma_val=14, std_dev=None):
    """
    Plots a 'DifficultyToJumpsPerSecond' curve based on the 'PlayerProportionToJumpsPerSecond' bell curve.
    
    Parameters:
    mu (float): The mean of the 'PlayerProportionToJumpsPerSecond' bell curve (default 12.5)
    lower_sigma_val (float): The value at the lower spectrum of the bell curve (default 10.667)
    upper_sigma_val (float): The value at the upper spectrum of the bell curve (default 14)
    std_dev (float): A standard deviation parameter. If not provided, it will be calculated based on the given values.
    
    Returns:
    None
    """

    # Calculate the standard deviation if not provided
    if std_dev is None:
        std_dev = (upper_sigma_val - lower_sigma_val) / 2

    # Create a normal distribution with the given mean and standard deviation
    player_proportion_distribution = stats.norm(loc=mu, scale=std_dev)

    # Define the difficulties and the corresponding player proportions
    difficulties = [1, 3, 10]
    proportions = [0.9, 0.5, 0.05]

    # Calculate the jumps per second required for each difficulty
    jumps_per_second_required = [player_proportion_distribution.ppf(p) for p in proportions]

    # Plot the DifficultyToJumpsPerSecond curve
    plt.plot(jumps_per_second_required, difficulties, marker='o')
    plt.xlabel('Jumps Per Second')
    plt.ylabel('Difficulty (0-10)')
    plt.title('DifficultyToJumpsPerSecond')
    plt.grid(True)
    plt.show()

# Example usage
plot_difficulty_to_jumps_per_second()
