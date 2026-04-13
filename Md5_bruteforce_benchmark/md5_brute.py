import hashlib
import time
import sys
from typing import Optional, List

# =============================================================================
# КОНФІГУРАЦІЯ СИСТЕМИ
# =============================================================================

# Цільовий хеш для дешифрування
TARGET_HASH: str = "827ccb0eea8a706c4c34a16891f84e7b"
# Довжина PIN-коду для базової атаки
TARGET_PIN_LENGTH: int = 5
# Кількість ітерацій для профілювання апаратної частини
BENCHMARK_ITERATIONS: int = 1_000_000

# =============================================================================
# УТИЛІТИ (ДОПОМІЖНІ ФУНКЦІЇ)
# =============================================================================

def format_time_duration(seconds: float) -> str:
    """
    Конвертує час у секундах в інженерний читабельний формат.
    """
    if seconds < 60:
        return f"{seconds:.3f} сек"
    if seconds < 3600:
        return f"{seconds / 60:.2f} хв"
    if seconds < 86400:
        return f"{seconds / 3600:.2f} год"
    if seconds < 31_536_000:
        return f"{seconds / 86400:.2f} днів"
    
    return f"{seconds / 31_536_000:.2f} років"

def generate_md5(input_string: str) -> str:
    """
    Генерує MD5-хеш для заданого рядка.
    """
    return hashlib.md5(input_string.encode('utf-8')).hexdigest()

# =============================================================================
# АТАКА ПОВНИМ ПЕРЕБОРОМ (BRUTE FORCE)
# =============================================================================

def execute_brute_force_attack(target_hash: str, pin_length: int) -> Optional[str]:
    """
    Виконує атаку методом вичерпання простору ключів для цифрового PIN-коду.
    
    Args:
        target_hash: MD5 хеш, який необхідно зламати.
        pin_length: Довжина очікуваного PIN-коду.
        
    Returns:
        Знайдений PIN-код у вигляді рядка або None, якщо збігів не знайдено.
    """
    print(f"--- ЕТАП 1: Практичний злам {pin_length}-значного PIN-коду ---")
    print(f"Цільовий хеш: {target_hash}")
    print("Ініціалізація перебору...")
    
    keyspace_size = 10 ** pin_length
    start_time = time.time()
    
    for i in range(keyspace_size):
        # Динамічне форматування рядка із заповненням нулями зліва (наприклад, "00042")
        candidate_pin = f"{i:0{pin_length}d}"
        
        if generate_md5(candidate_pin) == target_hash:
            execution_time_ms = (time.time() - start_time) * 1000
            
            print(f"[УСПІХ] Компрометація успішна. PIN-код: {candidate_pin}")
            print(f"Час виконання: {execution_time_ms:.2f} мс\n")
            return candidate_pin
            
    print("[ПОМИЛКА] Простір ключів вичерпано. Збігів не знайдено.\n")
    return None

# =============================================================================
# ПРОФІЛЮВАННЯ ТА ЕКСТРАПОЛЯЦІЯ (BENCHMARK)
# =============================================================================

def calculate_hardware_throughput(iterations: int) -> float:
    """
    Вимірює пропускну здатність процесора для алгоритму MD5.
    
    Returns:
        Швидкість обчислення (хешів за секунду).
    """
    start_time = time.time()
    for i in range(iterations):
        # Оптимізований виклик без додаткового форматування для чистоти тесту
        hashlib.md5(b"000000").hexdigest()
    elapsed_time = time.time() - start_time
    
    return iterations / elapsed_time

def run_cryptanalytic_benchmark() -> None:
    """
    Виконує стрес-тест системи та розраховує прогнозований час злому 
    для паролів різної довжини на основі отриманої пропускної здатності.
    """
    print("--- ЕТАП 2: Профілювання обладнання та екстраполяція ---")
    print(f"Генерація масиву з {BENCHMARK_ITERATIONS:,} хешів для визначення швидкості...")
    
    throughput_hps = calculate_hardware_throughput(BENCHMARK_ITERATIONS)
    print(f"Пропускна здатність системи: {throughput_hps:,.0f} хешів/сек.\n")
    
    print("--- Прогноз криптографічної стійкості (Цифрові PIN-коди) ---")
    print(f"{'Довжина':<10} | {'Простір ключів (варіантів)':<28} | {'Розрахунковий час злому'}")
    print("-" * 75)
    
    password_lengths: List[int] = [5, 6, 8, 10, 12, 16]
    
    for length in password_lengths:
        combinations = 10 ** length
        seconds_required = combinations / throughput_hps
        formatted_time = format_time_duration(seconds_required)
        
        print(f"{length:<10} | {combinations:<28,} | {formatted_time}")

# =============================================================================
# ТОЧКА ВХОДУ (MAIN ENTRY)
# =============================================================================

if __name__ == "__main__":
    try:
        # Фаза 1: Демонстрація вразливості
        execute_brute_force_attack(TARGET_HASH, TARGET_PIN_LENGTH)
        
        # Фаза 2: Аналіз складності
        run_cryptanalytic_benchmark()
        
    except KeyboardInterrupt:
        print("\n[СИСТЕМА] Виконання перервано користувачем.")
        sys.exit(0)