def encode(text: str) -> str:
    """
    Кодує текст, перетворюючи кожен символ у 8-бітне представлення,
    де кожен біт повторюється тричі.
    """
    # Перетворюємо кожен символ у байт (ASCII), а байт - у 8 біт
    # '08b' гарантує, що ми завжди маємо 8 біт, заповнених нулями зліва
    bits = "".join(format(ord(char), '08b') for char in text)
    
    # Потроюємо кожен біт для забезпечення завадостійкості
    encoded_bits = "".join(bit * 3 for bit in bits)
    
    return encoded_bits


def decode(bits: str) -> str:
    """
    Декодує потік бітів, використовуючи мажоритарну логіку для виправлення помилок,
    і повертає початковий текст.
    """
    # Розбиваємо вхідний потік на трійки (тріади)
    triplets = [bits[i:i+3] for i in range(0, len(bits), 3)]
    
    # Мажоритарне голосування для кожної трійки
    # Якщо в трійці більше одиниць ніж нулів - вважаємо біт одиницею
    corrected_bits = ""
    for triplet in triplets:
        if triplet.count('1') > 1:
            corrected_bits += '1'
        else:
            corrected_bits += '0'
    
    # Розбиваємо відновлені біти на байти (блоки по 8)
    bytes_list = [corrected_bits[i:i+8] for i in range(0, len(corrected_bits), 8)]
    
    # Конвертуємо кожен байт назад у символ ASCII
    decoded_text = "".join(chr(int(byte_str, 2)) for byte_str in bytes_list)
    
    return decoded_text

# --- ПРИКЛАД ВИКОРИСТАННЯ ТА ТЕСТУВАННЯ ---
if __name__ == "__main__":
    original_text = "A"
    print(f"Оригінальний текст: {original_text}")
    
    # Етап кодування
    encoded = encode(original_text)
    print(f"Закодовані біти (надмірність 3x): {encoded}")
    
    # Імітація завади в каналі (змінимо один біт у першій трійці)
    # Наприклад, замість '000' зробимо '100'
    noisy_bits = "100" + encoded[3:]
    print(f"Біти із завадою (перший біт інвертовано): {noisy_bits}")
    
    # Етап декодування
    decoded = decode(noisy_bits)
    print(f"Відновлений текст: {decoded}")