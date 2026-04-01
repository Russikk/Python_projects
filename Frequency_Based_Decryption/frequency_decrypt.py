import string

# Відновлена таблиця частот англійської мови (у відсотках)
ENGLISH_FREQUENCIES = {
    'A': 8.08, 'B': 1.67, 'C': 3.18, 'D': 3.99, 'E': 12.56, 'F': 2.17,
    'G': 1.80, 'H': 5.27, 'I': 7.24, 'J': 0.14, 'K': 0.63, 'L': 4.04,
    'M': 2.60, 'N': 7.38, 'O': 7.47, 'P': 1.91, 'Q': 0.09, 'R': 6.42,
    'S': 6.59, 'T': 9.15, 'U': 2.79, 'V': 1.00, 'W': 1.89, 'X': 0.21,
    'Y': 1.65, 'Z': 0.07
}

def shift_char(char, shift_amount):
    """
    Зсуває один символ зі збереженням регістру.
    Неалфавітні символи повертаються без змін.
    """
    if not char.isalpha():
        return char
    
    # Визначаємо базовий ASCII код залежно від регістру
    base = ord('A') if char.isupper() else ord('a')
    
    # Виконуємо зсув у межах кільцевого буфера 0-25
    shifted_ascii = (ord(char) - base + shift_amount) % 26 + base
    return chr(shifted_ascii)

def calculate_chi_squared(text):
    """
    Розраховує метрику Хі-квадрат для тексту порівняно з еталоном англійської мови.
    """
    # Рахуємо фактичну кількість кожної літери (ігноруючи регістр)
    letter_counts = {char: 0 for char in string.ascii_uppercase}
    total_letters = 0
    
    for char in text.upper():
        if char in letter_counts:
            letter_counts[char] += 1
            total_letters += 1
            
    # Якщо текст не містить літер, повертаємо нескінченність
    if total_letters == 0:
        return float('inf')
        
    chi_squared_stat = 0
    for char, expected_percent in ENGLISH_FREQUENCIES.items():
        expected_count = total_letters * (expected_percent / 100)
        observed_count = letter_counts[char]
        
        # Запобігаємо діленню на нуль (хоча в еталоні нулів немає)
        if expected_count > 0:
            chi_squared_stat += ((observed_count - expected_count) ** 2) / expected_count
            
    return chi_squared_stat

def decode_message(ciphertext):
    """
    Головна функція зламу. Перебирає 26 варіантів зсуву і повертає текст з найменшим відхиленням.
    """
    best_shift = 0
    min_chi_squared = float('inf')
    best_plaintext = ""
    
    # Перевіряємо всі можливі варіанти зсуву для розшифрування
    for shift in range(26):
        # Дешифруємо текст поточним зсувом (віднімаємо shift, що еквівалентно додаванню (26 - shift))
        current_attempt = "".join(shift_char(c, -shift) for c in ciphertext)
        
        # Оцінюємо статистичну близькість до англійської мови
        chi_sq = calculate_chi_squared(current_attempt)
        
        if chi_sq < min_chi_squared:
            min_chi_squared = chi_sq
            best_shift = shift
            best_plaintext = current_attempt
            
    return best_shift, best_plaintext

# === Блок тестування ===
if __name__ == "__main__":
    # Тестове повідомлення (зашифровано зсувом +7)
    encoded_text = "Aol zljyla ishn pz opkklu bukly aol old jvmmll zovw! 123"
    
    print(f"Зашифрований текст: {encoded_text}\n")
    
    found_shift, decoded_text = decode_message(encoded_text)
    
    print(f"Знайдений зсув: {found_shift}")
    print(f"Розшифрований текст: {decoded_text}")