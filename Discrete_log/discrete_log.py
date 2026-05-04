import math
import sys
from typing import Optional

class DiscreteLogSolver:
    """
    Клас-солвер для криптографічної задачі дискретного логарифма (DLP).
    Розв'язує рівняння виду: g^x ≡ h (mod p).
    """

    @staticmethod
    def baby_step_giant_step(g: int, h: int, p: int) -> Optional[int]:
        """
        Реалізація алгоритму Шенкса (Baby-step Giant-step) для прискореного пошуку ключа.
        Використовує компроміс між часом і пам'яттю (Time-Memory Trade-off), 
        знижуючи обчислювальну складність з O(p) до O(√p).

        Аргументи:
            g (int): Генератор (основа).
            h (int): Публічний ключ (результат).
            p (int): Простий модуль.

        Повертає:
            Optional[int]: Знайдений секретний ключ (x) або None, якщо розв'язку не існує.
        """
        # Оптимальний розмір блоку (n) дорівнює найближчому цілому кореню з модуля
        n = math.isqrt(p) + 1

        # ==========================================
        # "Малі кроки" (Побудова Lookup Table)
        # ==========================================
        # Хешуємо значення g^j mod p для всіх 0 <= j < n.
        # Вимагає O(√p) пам'яті, але забезпечує пошук за O(1).
        value_table = {pow(g, j, p): j for j in range(n)}

        # ==========================================
        # Розрахунок множника для "Великих кроків"
        # ==========================================
        # c = g^(-n) mod p. 
        # У Python 3.8+ pow(base, exp, mod) підтримує від'ємні експоненти 
        # для автоматичного пошуку модульного оберненого елемента.
        try:
            c = pow(g, -n, p)
        except ValueError:
            # Виникає, якщо g та p не є взаємно простими (p не є простим числом)
            raise ValueError("Генератор та модуль не є взаємно простими, оберненого елемента не існує.")

        # ==========================================
        # "Великі кроки" (Пошук колізій)
        # ==========================================
        # Шукаємо збіг між h * g^(-i*n) mod p та кешованими значеннями
        current = h
        for i in range(n):
            if current in value_table:
                # Колізію знайдено: x = i * n + j
                return i * n + value_table[current]
            
            # Наступний крок: current = (current * c) mod p
            current = (current * c) % p

        # Якщо цикл завершився без колізій
        return None

if __name__ == "__main__":
    # ==========================================
    # Testbench: Валідація алгоритму
    # ==========================================
    # Тестовий вектор: 5^x ≡ 18 (mod 23)
    TEST_G = 5
    TEST_H = 18
    TEST_P = 23
    EXPECTED_X = 14 # Заздалегідь відома правильна відповідь для перевірки

    print(f"[VERIFICATION] Старт пошуку x для рівняння: {TEST_G}^x ≡ {TEST_H} (mod {TEST_P})")
    
    try:
        # Запуск алгоритму
        secret_x = DiscreteLogSolver.baby_step_giant_step(TEST_G, TEST_H, TEST_P)
        
        if secret_x is not None:
            print(f"[STATUS] Знайдено потенційний ключ: x = {secret_x}")
            
            # Перевірка математичної коректності (Verification Assertion)
            actual_h = pow(TEST_G, secret_x, TEST_P)
            assert actual_h == TEST_H, f"Помилка валідації: {TEST_G}^{secret_x} mod {TEST_P} = {actual_h}, очікувалося {TEST_H}"
            
            print(f"[PASSED] Криптографічну цілісність підтверджено. Транзакція успішна.")
        else:
            print("[FAILED] Розв'язку в заданому полі не існує.", file=sys.stderr)
            
    except Exception as e:
        print(f"[FATAL] Внутрішня помилка: {e}", file=sys.stderr)