import random
from typing import List, Tuple, Optional


# Countdown numbers game constants
LARGE_NUMBERS = [25, 50, 75, 100]
SMALL_NUMBERS = [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10]
MIN_TARGET = 101
MAX_TARGET = 999


def generate_random_countdown_numbers() -> Tuple[List[int], int]:
    """
    Generate random numbers following Countdown TV show rules.
    Uses 1-2 large numbers (most common choice) with random selection.
        
    Returns:
        Tuple of (6 numbers, target)
    """
    # Randomly choose between 1-2 large numbers (most popular choices)
    num_large = random.choice([1, 2])
    
    # Select large numbers (without replacement)
    large_selected = random.sample(LARGE_NUMBERS, num_large)
    
    # Select small numbers (with replacement from the pool)
    num_small = 6 - num_large
    small_selected = random.choices(SMALL_NUMBERS, k=num_small)
    
    # Combine and shuffle
    numbers = large_selected + small_selected
    random.shuffle(numbers)
    
    # Generate random target
    target = random.randint(MIN_TARGET, MAX_TARGET)
    
    return numbers, target


def get_countdown_selection_options() -> List[Tuple[int, str]]:
    """
    Get available selection options for the dropdown.
    
    Returns:
        List of (num_large, description) tuples
    """
    return [
        (0, "0 large, 6 small"),
        (1, "1 large, 5 small (most popular)"),
        (2, "2 large, 4 small (best odds)"),
        (3, "3 large, 3 small"),
        (4, "4 large, 2 small")
    ]