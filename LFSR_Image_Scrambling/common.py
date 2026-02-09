import numpy as np

def lfsr_generator(seed):
    """
    16-бітний LFSR генератор.
    """
    # Константа для обмеження розрядності
    REGISTER_MASK = 0xFFFF
    
    state = seed & REGISTER_MASK

    while True:
        # Taps for 16-bit Maximal Length Sequence 
        tap_16 = (state >> 15) & 1
        tap_14 = (state >> 13) & 1
        tap_13 = (state >> 12) & 1
        tap_11 = (state >> 10) & 1

        # Обчислення зворотного зв'язку  
        feedback_bit = tap_16 ^ tap_14 ^ tap_13 ^ tap_11

        # Shift Left
        # Накладання маски для емуляції 16-бітної шини
        # Вставка feedback_bit у молодший розряд
        
        state = ((state << 1) & REGISTER_MASK) | feedback_bit

        yield state

def get_permutation_table(seed, num_blocks):
    """
    Формує таблицю перестановок, використовуючи потік з LFSR.
    """
    rng_stream = lfsr_generator(seed)
    
    indices = list(range(num_blocks))
    
    # Fisher-Yates shuffle
    for i in range(num_blocks - 1, 0, -1):
        rand_val = next(rng_stream)
        
        j = rand_val % (i + 1)
        indices[i], indices[j] = indices[j], indices[i]
        
    return indices