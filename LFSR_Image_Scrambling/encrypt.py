import cv2
import numpy as np
import sys
from common import get_permutation_table

SEED_KEY = 44257    
GRID = (40, 30)  # Сітка розбиття: (рядки, стовпці)
INPUT_FILE = "input.jpg"
OUTPUT_FILE = "encrypted_image.png"

def encrypt_image():
    img = cv2.imread(INPUT_FILE)
    if img is None:
        print(f"Помилка: Не знайдено файл {INPUT_FILE}")
        sys.exit(1)

    h, w, _ = img.shape
    rows, cols = GRID
    num_blocks = rows * cols
    
    # Розміри блоку
    bh = h // rows
    bw = w // cols

    # Отримання таблиці перестановок
    perm_table = get_permutation_table(SEED_KEY, num_blocks)
    
    encrypted_img = np.zeros_like(img)

    print(f"Шифрування з ключем {SEED_KEY}...")

    # Перемішування
    for dest_idx in range(num_blocks):
        # Куди вставляємо (поточна позиція в зашифрованому)
        dest_row = dest_idx // cols
        dest_col = dest_idx % cols
        
        # Звідки беремо (позиція в оригіналі)
        src_idx = perm_table[dest_idx]
        src_row = src_idx // cols
        src_col = src_idx % cols
        
        # Координати пікселів
        y1, y2 = dest_row * bh, (dest_row + 1) * bh
        x1, x2 = dest_col * bw, (dest_col + 1) * bw
        
        sy1, sy2 = src_row * bh, (src_row + 1) * bh
        sx1, sx2 = src_col * bw, (src_col + 1) * bw
        
        # Копіювання блоку
        encrypted_img[y1:y2, x1:x2] = img[sy1:sy2, sx1:sx2]

    cv2.imwrite(OUTPUT_FILE, encrypted_img)
    print(f"Готово! Зашифроване зображення збережено як {OUTPUT_FILE}")

if __name__ == "__main__":
    encrypt_image()




