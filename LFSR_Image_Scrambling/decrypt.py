import cv2
import numpy as np
import sys
from common import get_permutation_table

SEED_KEY = 44257   
GRID = (40, 30)
INPUT_FILE = "encrypted_image.png"
OUTPUT_FILE = "restored_image.jpg"

def decrypt_image():
    img = cv2.imread(INPUT_FILE)
    if img is None:
        print(f"Помилка: Не знайдено файл {INPUT_FILE}")
        sys.exit(1)

    h, w, _ = img.shape
    rows, cols = GRID
    num_blocks = rows * cols
    bh = h // rows
    bw = w // cols

    # Генеруємо ту ж саму таблицю, що і при шифруванні
    forward_perm_table = get_permutation_table(SEED_KEY, num_blocks)
    
    # Створюємо зворотну карту
    inverse_table = [0] * num_blocks
    for dest_pos, src_pos in enumerate(forward_perm_table):
        inverse_table[dest_pos] = src_pos
        

    restored_img = np.zeros_like(img)
    print(f"Дешифрування з ключем {SEED_KEY}...")

    for i in range(num_blocks):

        target_idx = i 
             
        scrambled_idx = i
        original_idx = forward_perm_table[i] 

        restored_block_idx = forward_perm_table[i]
        
        r_row = restored_block_idx // cols
        r_col = restored_block_idx % cols
        
        # Координати джерела (в Encrypted) - це просто i
        s_row = i // cols
        s_col = i % cols
        
        # Пікселі цільові (куди пишемо - у відновлене)
        y1, y2 = r_row * bh, (r_row + 1) * bh
        x1, x2 = r_col * bw, (r_col + 1) * bw
        
        # Пікселі джерела (звідки беремо - із зашифрованого)
        sy1, sy2 = s_row * bh, (s_row + 1) * bh
        sx1, sx2 = s_col * bw, (s_col + 1) * bw
        
        restored_img[y1:y2, x1:x2] = img[sy1:sy2, sx1:sx2]

    cv2.imwrite(OUTPUT_FILE, restored_img)
    print(f"Готово! Відновлене зображення збережено як {OUTPUT_FILE}")

if __name__ == "__main__":
    decrypt_image()