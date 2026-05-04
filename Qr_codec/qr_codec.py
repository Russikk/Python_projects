import sys
from typing import List, Iterator, Tuple

class QRCodeV1Codec:
    """
    Клас кодування та декодування QR-коду (Версія 1, 21x21).
    Реалізує просторове перетворення потоку даних.
    """
    SIZE = 21
    TIMING_PATTERN_IDX = 6
    MODE_BYTE_ASCII = "0100"

    @staticmethod
    def _is_reserved(row: int, col: int) -> bool:
        """Визначає, чи належить координата до службової зони."""
        # Пошукові візерунки (включно з порожньою рамкою-сепаратором)
        if row <= 8 and col <= 8: return True      # Top-Left
        if row <= 8 and col >= 13: return True     # Top-Right
        if row >= 13 and col <= 8: return True     # Bottom-Left
        
        # Лінії синхронізації
        if row == QRCodeV1Codec.TIMING_PATTERN_IDX or col == QRCodeV1Codec.TIMING_PATTERN_IDX: 
            return True
            
        return False

    @staticmethod
    def _zigzag_path() -> Iterator[Tuple[int, int]]:
        """
        Генератор просторової маршрутизації. 
        Повертає координати (row, col) тільки для інформаційних модулів, оминаючи службові зони.
        """
        col = QRCodeV1Codec.SIZE - 1
        row = QRCodeV1Codec.SIZE - 1
        direction = -1

        while col > 0:
            if col == QRCodeV1Codec.TIMING_PATTERN_IDX:
                col -= 1

            for c in (col, col - 1):
                if not QRCodeV1Codec._is_reserved(row, c):
                    yield row, c

            row += direction
            if row < 0 or row >= QRCodeV1Codec.SIZE:
                direction *= -1
                row += direction
                col -= 2

    @classmethod
    def encode(cls, text: str) -> List[List[int]]:
        """Формує 2D матрицю QR-коду з вхідного тексту."""
        grid = [[0 for _ in range(cls.SIZE)] for _ in range(cls.SIZE)]

        # 1. Заповнення службових зон (для коректної візуалізації меж)
        for r in range(cls.SIZE):
            for c in range(cls.SIZE):
                if cls._is_reserved(r, c):
                    grid[r][c] = 1

        # 2. Формування бітового потоку: [Режим 4 біти] + [Довжина 8 біт] + [Дані]
        header = f"{cls.MODE_BYTE_ASCII}{len(text):08b}"
        payload = "".join(f"{ord(char):08b}" for char in text)
        bit_stream = header + payload

        # 3. Маршрутизація даних у просторі матриці через ітератор
        stream_iterator = iter(bit_stream)
        for r, c in cls._zigzag_path():
            try:
                grid[r][c] = int(next(stream_iterator))
            except StopIteration:
                grid[r][c] = 0  # Заповнення нулями після вичерпання корисного навантаження

        return grid

    @classmethod
    def decode(cls, grid: List[List[int]]) -> str:
        """Парсить 2D матрицю QR-коду та екстрагує закодований текст."""
        # 1. Зчитування бітів за генератором маршруту
        data_bits = [str(grid[r][c]) for r, c in cls._zigzag_path()]
        raw_stream = "".join(data_bits)

        if len(raw_stream) < 12:
            raise ValueError("Потік даних занадто короткий для валідного пакету.")

        # 2. Розбір заголовка (Парсинг протоколу)
        mode = raw_stream[0:4]
        if mode != cls.MODE_BYTE_ASCII:
            raise ValueError(f"Непідтримуваний режим кодування. Очікувався {cls.MODE_BYTE_ASCII}, отримано {mode}.")

        msg_length = int(raw_stream[4:12], 2)
        
        # 3. Екстракція корисного навантаження
        decoded_chars = []
        current_idx = 12
        
        for _ in range(msg_length):
            if current_idx + 8 > len(raw_stream):
                raise ValueError("Обрив потоку: заявлена довжина повідомлення перевищує фактичну.")
            
            byte_str = raw_stream[current_idx : current_idx + 8]
            decoded_chars.append(chr(int(byte_str, 2)))
            current_idx += 8

        return "".join(decoded_chars)

    @classmethod
    def print_matrix(cls, grid: List[List[int]]) -> None:
        """Виводить матрицю в термінал у зручному для візуального аналізу вигляді."""
        for row in grid:
            print("".join("██" if bit else "░░" for bit in row))


if __name__ == "__main__":
    # ==========================================
    # Testbench: Валідація алгоритму
    # ==========================================
    TARGET_PAYLOAD = "Warrior"
    
    print(f"[VERIFICATION] Старт циклу транзакції. Payload: '{TARGET_PAYLOAD}'\n")
    
    try:
        # Етап 1: Формування stimulus data (Кодування)
        matrix_under_test = QRCodeV1Codec.encode(TARGET_PAYLOAD)
        print("[STATUS] Матриця згенерована:")
        QRCodeV1Codec.print_matrix(matrix_under_test)
        
        # Етап 2: Зчитування та обробка (Декодування)
        recovered_data = QRCodeV1Codec.decode(matrix_under_test)
        print(f"\n[STATUS] Дані відновлено: '{recovered_data}'")
        
        # Етап 3: Assertions
        assert recovered_data == TARGET_PAYLOAD, "Невідповідність між переданими та отриманими даними."
        print("\n[PASSED] Функціональне покриття підтверджено. Транзакція успішна.")
        
    except AssertionError as e:
        print(f"\n[FAILED] Помилка верифікації: {e}", file=sys.stderr)
    except Exception as e:
        print(f"\n[FATAL] Внутрішня помилка обробки: {e}", file=sys.stderr)