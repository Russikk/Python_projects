import sys
from typing import List, Dict, Set

# =============================================================================
# ДАНІ ДЛЯ СТАТИСТИЧНОГО АНАЛІЗУ
# =============================================================================

# Наскільки часто літери зустрічаються в англійській мові
# Це допомагає програмі вгадати, який символ найбільш імовірний
CHAR_WEIGHTS: Dict[str, float] = {
    'e': 12.7, 't': 9.1, 'a': 8.2, 'o': 7.5, 'i': 7.0, 'n': 6.7, 's': 6.3, 
    'h': 6.1, 'r': 6.0, 'd': 4.3, 'l': 4.0, 'u': 2.8, 'c': 2.8, 'm': 2.4, 
    'w': 2.4, 'f': 2.2, 'g': 2.0, 'y': 2.0, 'p': 1.9, 'b': 1.5, 'v': 1.0, 
    'k': 0.8, ' ': 20.0  # Пробіл має найвищий пріоритет
}

# Найпопулярніші пари літер (біграми) 
# Допомагають вибрати правильний варіант, коли окремі літери здаються однаково підходящими
COMMON_PAIRS: Set[str] = {
    'th', 'he', 'in', 'er', 'an', 're', 'nd', 'at', 'on', 'nt', 'ha', 'es', 'st', 
    'en', 'ed', 'to', 'it', ' e', ' t', ' a', 's ', 'e ', 'd '
}

# =============================================================================
# ГОЛОВНИЙ МОДУЛЬ ДЕКОДУВАННЯ
# =============================================================================

class XorMessageDecoder:
    """
    Клас для відновлення тексту, якщо декілька повідомлень 
    були зашифровані одним і тим самим ключем.
    """

    def __init__(self, ciphertexts: List[bytearray]):
        self.ciphertexts = ciphertexts
        self.msg_count = len(ciphertexts)
        self.keystream_len = len(ciphertexts[0])
        self.inferred_keystream = bytearray()

    def _evaluate_byte_probability(self, col_index: int, candidate_byte: int) -> float:
        """
        Нараховує бали для конкретного варіанта байта ключа.
        Чим більше балів, тим більше результат схожий на нормальний текст.
        
        Використовує 5 основних перевірок:
        1. Діапазон ASCII: Чи є символ друкованим.
        2. Частота літер: Наскільки типовою є ця буква.
        3. Зв'язок (пари): Чи утворює вона нормальне поєднання з попередньою.
        4. Регістр: Штраф за дивні стрибки (наприклад, з малої на ВЕЛИКУ в слові).
        5. Шум: Штраф за зайві спецсимволи.
        """
        score = 0.0
        
        for j in range(self.msg_count):
            # Пробуємо розшифрувати байт цим варіантом ключа
            decoded_val = self.ciphertexts[j][col_index] ^ candidate_byte
            
            # Перевірка 1: Чи це взагалі символ, який можна надрукувати?
            if not (32 <= decoded_val <= 126):
                return -float('inf')  # Якщо ні — цей ключ неможливий
            
            char = chr(decoded_val)
            low_char = char.lower()
            
            # Перевірка 2: Додаємо бали за "популярність" літери
            score += CHAR_WEIGHTS.get(low_char, 0.1)

            # Перевірка контексту (якщо це не перша колонка)
            if col_index > 0:
                prev_decoded = self.ciphertexts[j][col_index - 1] ^ self.inferred_keystream[col_index - 1]
                prev_char = chr(prev_val := prev_decoded).lower()
                
                # Перевірка 3: Чи утворює ця літера популярну пару з попередньою?
                if (prev_char + low_char) in COMMON_PAIRS:
                    score += 12.0
                
                # Перевірка 4: Чи немає тут помилки регістра (наприклад, 'tHe')?
                # В англійському тексті велика літера після малої — ознака неправильного ключа.
                if (97 <= prev_val <= 122) and (65 <= decoded_val <= 90):
                    score -= 40.0
                    
                # Додана перевірка на дві великі літери поруч
                if (65 <= prev_val <= 90) and (65 <= decoded_val <= 90):
                    score -= 35.0
            
            # Перевірка 5: Чи не забагато спецсимволів (шуму)?
            if not char.isalnum() and char != ' ':
                score -= 15.0
            
            # Додатковий бал за велику літеру на самому початку повідомлення
            if col_index == 0 and (65 <= decoded_val <= 90):
                score += 10.0

        return score

    def decode(self) -> bytearray:
        """Почергово підбирає кожен байт ключа, максимізуючи кількість балів."""
        for i in range(self.keystream_len):
            best_byte = 0
            max_score = -float('inf')
            
            for candidate in range(256):
                current_score = self._evaluate_byte_probability(i, candidate)
                if current_score > max_score:
                    max_score = current_score
                    best_byte = candidate
            
            self.inferred_keystream.append(best_byte)
        
        return self.inferred_keystream

# =============================================================================
# ТЕСТОВИЙ СТЕНД (ПЕРЕВІРКА РОБОТИ)
# =============================================================================

def run_test():
    """Повний цикл: шифрування повідомлень та їх автоматичне відновлення."""
    
    # Оригінальні речення
    plaintexts = [
        "The quick brown fox jumps over the lazy dog  ",
        "Cryptography is the ultimate engineering tool",
        "We are building a test harness for XOR cipher",
        "Data security requires flawless math logic   ",
        "This algorithm will crack the repeated key   ",
        "Python makes byte manipulation very easy now ",
        "Information theory is fascinating to study   ",
        "Let us see how the frequency analysis works  ",
        "Frequency of letters destroys the encryption ",
        "RobberCity hackers made a huge mistake here  "
    ]
    
    # Справжній ключ
    true_key = "SuperSecretEngineeringKey2026_For_CodinGame!!"
    
    # Шифрування (XOR тексту з ключем)
    # Додано % len(true_key), щоб не було IndexError
    cipher_data = [
        bytearray(ord(p[i]) ^ ord(true_key[i % len(true_key)]) for i in range(len(p))) 
        for p in plaintexts
    ]
    
    # Відновлення ключа за допомогою нашого алгоритму
    decoder = XorMessageDecoder(cipher_data)
    recovered_key = decoder.decode()
    
    # Вивід результатів
    print(f"--- ЗВІТ ПРО ДЕКОДУВАННЯ ---")
    print(f"Відновлений ключ: {recovered_key.decode(errors='replace')}")
    print(f"Статус: {'УСПІХ' if recovered_key.decode() == true_key else 'ПОМИЛКА'}")
    print("-" * 30)
    
    print("\n--- РОЗШИФРОВАНІ ТЕКСТИ ---")
    for idx, stream in enumerate(cipher_data):
        decrypted = "".join(chr(b ^ k) for b, k in zip(stream, recovered_key))
        print(f"[{idx+1:02d}] {decrypted}")

if __name__ == "__main__":
    run_test()