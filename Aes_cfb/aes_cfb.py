import os
import logging
from typing import Optional
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# Налаштування логування для професійного виводу в консоль
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class AesCfbCodec:
    """
    Клас для симетричного шифрування та розшифрування даних за алгоритмом AES у режимі CFB.
    
    Режим CFB (Cipher Feedback) перетворює блочний шифр на потоковий, 
    що дозволяє шифрувати дані без необхідності їх доповнення (padding).
    """

    def __init__(self, key: Optional[bytes] = None, iv: Optional[bytes] = None) -> None:
        """
        Ініціалізує криптографічний модуль.

        Args:
            key (bytes, optional): Ключ шифрування (16, 24 або 32 байти). 
                                   Якщо не передано, генерується автоматично (32 байти для AES-256).
            iv (bytes, optional): Вектор ініціалізації (рівно 16 байтів). 
                                  Якщо не передано, генерується автоматично.

        Raises:
            ValueError: Якщо довжина ключа або IV не відповідає стандарту AES.
        """
        # Інкапсуляція атрибутів (захист від прямого редагування)
        self._key: bytes = key or os.urandom(32)
        self._iv: bytes = iv or os.urandom(16)
        
        self._validate_parameters()

    def _validate_parameters(self) -> None:
        """Внутрішній метод для валідації криптографічних параметрів."""
        if len(self._key) not in (16, 24, 32):
            raise ValueError(f"Неприпустима довжина ключа: {len(self._key)} байт. Очікується 16, 24 або 32.")
        if len(self._iv) != 16:
            raise ValueError(f"Неприпустима довжина IV: {len(self._iv)} байт. Очікується рівно 16 байт.")

    def encrypt(self, plaintext: str) -> bytes:
        """
        Зашифровує відкритий текст у криптограму.

        Args:
            plaintext (str): Текст, який потрібно приховати.

        Returns:
            bytes: Зашифрований потік даних.
        """
        cipher = Cipher(
            algorithms.AES(self._key), 
            modes.CFB(self._iv), 
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Перетворюємо рядок у байти, шифруємо і закриваємо потік
        return encryptor.update(plaintext.encode('utf-8')) + encryptor.finalize()

    def decrypt(self, ciphertext: bytes) -> str:
        """
        Розшифровує криптограму назад у відкритий текст.

        Args:
            ciphertext (bytes): Зашифровані дані.

        Returns:
            str: Відновлений оригінальний текст.
        """
        cipher = Cipher(
            algorithms.AES(self._key), 
            modes.CFB(self._iv), 
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        # Розшифровуємо байти і конвертуємо їх назад у рядок
        decrypted_bytes = decryptor.update(ciphertext) + decryptor.finalize()
        return decrypted_bytes.decode('utf-8')


def run_testbench() -> None:
    """Запускає ізольований цикл тестування для перевірки цілісності алгоритму."""
    logging.info("=== Запуск Testbench: AES-256 (Mode: CFB) ===")
    
    target_payload = "Top secret engineering payload data: X-7890."
    logging.info(f"[ORIGINAL]  '{target_payload}'")
    
    try:
        # 1. Ініціалізація з автоматичною генерацією стійких ключів
        codec = AesCfbCodec()
        
        # 2. Зашифрування
        encrypted_data = codec.encrypt(target_payload)
        logging.info(f"[ENCRYPTED] {encrypted_data.hex().upper()}")
        
        # 3. Розшифрування
        decrypted_text = codec.decrypt(encrypted_data)
        logging.info(f"[DECRYPTED] '{decrypted_text}'")
        
        # 4. Автоматична верифікація результатів
        assert target_payload == decrypted_text, "Критична помилка: Розбіжність даних!"
        logging.info("[STATUS]  Транзакція успішна. Цілісність даних підтверджено.")
        
    except AssertionError as err:
        logging.error(f"[FAILED]  Помилка валідації: {err}")
    except Exception as err:
        logging.critical(f"[FATAL]  Внутрішня помилка обробки: {err}")


if __name__ == "__main__":
    run_testbench()