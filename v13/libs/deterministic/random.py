"""
deterministic/random.py - Deterministic Random Functions for QFS V13

Provides deterministic alternatives to random.random(), random.randint(), etc.
Uses a linear congruential generator (LCG) with fixed seed for reproducibility.
"""

from typing import List, Any
import hashlib

# Global state for deterministic PRNG
# Using LCG parameters from glibc for consistency
_prng_state = 1234567890

def det_random() -> float:
    """
    Deterministic alternative to random.random().
    
    Uses a linear congruential generator (LCG) for deterministic pseudo-random numbers.
    This replaces random.random() calls to maintain Zero-Simulation compliance.
    
    Returns:
        float: A deterministic pseudo-random float in the range [0.0, 1.0)
    """
    global _prng_state
    _prng_state = (_prng_state * 1103515245 + 12345) & 0x7fffffff
    return _prng_state / 2147483648.0

def det_randint(a: int, b: int) -> int:
    """
    Deterministic alternative to random.randint().
    
    Returns a deterministic integer in the range [a, b].
    
    Args:
        a: Lower bound (inclusive)
        b: Upper bound (inclusive)
        
    Returns:
        int: A deterministic random integer in the range [a, b]
    """
    if a > b:
        raise ValueError("randint: a must be <= b")
    range_size = b - a + 1
    random_float = det_random()
    return a + int(random_float * range_size)

def det_choice(seq: List[Any]) -> Any:
    """
    Deterministic alternative to random.choice().
    
    Returns a deterministic choice from a sequence.
    
    Args:
        seq: Sequence to choose from
        
    Returns:
        Any: A deterministic choice from the sequence
    """
    if not seq:
        raise IndexError("Cannot choose from an empty sequence")
    index = det_randint(0, len(seq) - 1)
    return seq[index]

def det_choices(seq: List[Any], k: int = 1) -> List[Any]:
    """
    Deterministic alternative to random.choices().
    
    Returns deterministic choices from a sequence.
    
    Args:
        seq: Sequence to choose from
        k: Number of choices to make
        
    Returns:
        List[Any]: A list of deterministic choices from the sequence
    """
    if not seq:
        raise IndexError("Cannot choose from an empty sequence")
    return [det_choice(seq) for _ in range(k)]

def det_uniform(a: float, b: float) -> float:
    """
    Deterministic alternative to random.uniform().
    
    Returns a deterministic float in the range [a, b).
    
    Args:
        a: Lower bound (inclusive)
        b: Upper bound (exclusive)
        
    Returns:
        float: A deterministic random float in the range [a, b)
    """
    if a > b:
        raise ValueError("uniform: a must be <= b")
    return a + (b - a) * det_random()

def det_seed(seed_value: int) -> None:
    """
    Seed the deterministic PRNG.
    
    Sets the global PRNG state to ensure reproducible sequences.
    
    Args:
        seed_value: The seed value to use
    """
    global _prng_state
    _prng_state = seed_value & 0x7fffffff

def det_getstate() -> int:
    """
    Get the current state of the deterministic PRNG.
    
    Returns:
        int: The current PRNG state
    """
    global _prng_state
    return _prng_state

def det_setstate(state: int) -> None:
    """
    Set the state of the deterministic PRNG.
    
    Args:
        state: The PRNG state to set
    """
    global _prng_state
    _prng_state = state & 0x7fffffff

def det_shuffle(seq: List[Any]) -> None:
    """
    Deterministic alternative to random.shuffle().
    
    Shuffles a sequence in place using deterministic randomization.
    
    Args:
        seq: Sequence to shuffle in place
    """
    for i in range(len(seq) - 1, 0, -1):
        j = det_randint(0, i)
        seq[i], seq[j] = seq[j], seq[i]

def det_sample(seq: List[Any], k: int) -> List[Any]:
    """
    Deterministic alternative to random.sample().
    
    Returns a deterministic sample of k unique elements from a sequence.
    
    Args:
        seq: Sequence to sample from
        k: Number of elements to sample
        
    Returns:
        List[Any]: A list of k unique elements sampled from the sequence
    """
    if k > len(seq):
        raise ValueError("Sample larger than population")
    if k < 0:
        raise ValueError("Negative sample size")
    
    # Create a copy to avoid modifying the original
    pool = list(seq)
    result = []
    
    for i in range(k):
        j = det_randint(0, len(pool) - 1)
        result.append(pool[j])
        pool.pop(j)
    
    return result