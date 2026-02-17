ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def pass_through_rotors_forward(char, rotors):
    """
    Прямий каскад: пропускає символ через масив роторів зліва направо (R1 -> R2 -> R3).
    """
    current_char = char
    for rotor_wiring in rotors:
        # Знаходимо індекс поточного символу в стандартному алфавіті
        pin_in = ALPHABET.index(current_char)
        # Знімаємо сигнал з виходу ротора
        current_char = rotor_wiring[pin_in]
        
    return current_char

def pass_through_rotors_backward(char, rotors):
    """
    Зворотний каскад: пропускає символ через ротори справа наліво (R3 -> R2 -> R1).
    """
    current_char = char
    # reversed(rotors) гарантує, що ми почнемо з останнього ротора
    for rotor_wiring in reversed(rotors):
        # Шукаємо, на якому піні ротора з'явився цей сигнал
        pin_in = rotor_wiring.index(current_char)
        # Повертаємо символ стандарту
        current_char = ALPHABET[pin_in]
        
    return current_char

def encode_enigma(plaintext, start_shift, rotors):
    """Повний цикл шифрування"""
    ciphertext = ""
    for i, char in enumerate(plaintext):
        # Динамічний зсув Цезаря (Препроцесинг)
        p_idx = ALPHABET.index(char)
        shifted_idx = (p_idx + start_shift + i) % 26
        shifted_char = ALPHABET[shifted_idx]
        
        # Каскад роторів (LUT)
        encoded_char = pass_through_rotors_forward(shifted_char, rotors)
        ciphertext += encoded_char
        
    return ciphertext

def decode_enigma(ciphertext, start_shift, rotors):
    """Повний цикл дешифрування"""
    plaintext = ""
    for i, char in enumerate(ciphertext):
        # Зворотний каскад роторів
        shifted_char = pass_through_rotors_backward(char, rotors)
        
        # Зворотний зсув Цезаря (Постпроцесинг)
        c_idx = ALPHABET.index(shifted_char)
        original_idx = (c_idx - start_shift - i) % 26
        plaintext += ALPHABET[original_idx]
        
    return plaintext

# === Тестування алгоритму ===
if __name__ == "__main__":
    # Набір роторів з прикладу CodinGame
    ROTOR_1 = "BDFHJLCPRTXVZNYEIWGAKMUSQO"
    ROTOR_2 = "AJDKSIRUXBLHWTMCQGZNPYFVOE"
    ROTOR_3 = "EKMFLGDQVZNTOWYHXUSPAIBRCJ"
    
    my_rotors = [ROTOR_1, ROTOR_2, ROTOR_3]
    shift_n = 4
    
    original_msg = "AWEATHER"
    
    print(f"Оригінал: {original_msg}")
    
    # Шифруємо
    encrypted_msg = encode_enigma(original_msg, shift_n, my_rotors)
    print(f"ENCODE:   {encrypted_msg}")
    
    # Розшифровуємо
    decrypted_msg = decode_enigma(encrypted_msg, shift_n, my_rotors)
    print(f"DECODE:   {decrypted_msg}")
    
    assert original_msg == decrypted_msg, "Система порушена: втрата даних при дешифруванні!"