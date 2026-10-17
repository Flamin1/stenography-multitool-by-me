import os
from PIL import Image

# Константы для шифратора
blank = '.'
knalb = '∫'

crypt = str.maketrans({
    'a': '✞', 'b': 'q', 'c': '♩', 'd': '~', 'e': '☞', 'f': blank,
    'g': '>', 'h': '+', 'i': knalb, 'j': '*', 'k': '=', 'l': '^',
    'm': '3', 'n': '{', 'o': '|', 'p': '∞', 'q': 'у', 'r': '&',
    's': '←', 't': '♨', 'u': '☂', 'v': '☃', 'w': 'ゾ'
})

decode = str.maketrans({
    '✞': 'a', 'q': 'b', '♩': 'c', '~': 'd', '☞': 'e', blank: 'f',  
    '>': 'g', '+': 'h', knalb: 'i', '*': 'j', '=': 'k', '^': 'l', 
    '3': 'm', '{': 'n', '|': 'o', '∞': 'p', 'у': 'q', '&': 'r', 
    '←': 's', '♨': 't', '☂': 'u', '☃': 'v', 'ゾ': 'w'
})

def encode_lsb(image_path, secret_text, output_path):
    try:
        img = Image.open(image_path)
    except Exception as e:
        print(f"Ошибка открытия файла: {e}")
        return False

    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    data_bytes = secret_text.encode('utf-8')
    data_len = len(data_bytes)
    
    payload = data_len.to_bytes(4, 'big') + data_bytes
    bits = ''.join(format(byte, '08b') for byte in payload)
    
    width, height = img.size
    max_bits = width * height * 3
    
    if len(bits) > max_bits:
        print("Ошибка: Текст слишком большой для этой картинки!")
        return False
    
    pixels = list(img.getdata())
    new_pixels = []
    bit_idx = 0
    
    for pixel in pixels:
        r, g, b = pixel
        channels = [r, g, b]
        new_channels = []
        for ch in channels:
            if bit_idx < len(bits):
                ch = (ch & ~1) | int(bits[bit_idx])
                bit_idx += 1
            new_channels.append(ch)
        new_pixels.append(tuple(new_channels))
    
    encoded_img = Image.new('RGB', (width, height))
    encoded_img.putdata(new_pixels)
    encoded_img.save(output_path, 'PNG')
    return True

def decode_lsb(image_path):
    try:
        img = Image.open(image_path)
    except Exception as e:
        print(f"Ошибка открытия файла: {e}")
        return None

    if img.mode != 'RGB':
        img = img.convert('RGB')
        
    pixels = list(img.getdata())
    bits = []
    
    for pixel in pixels:
        for ch in pixel:
            bits.append(str(ch & 1))
            
    bits_str = ''.join(bits)
    
    length_bits = bits_str[:32]
    data_len = int(length_bits, 2)
    
    start_idx = 32
    end_idx = 32 + (data_len * 8)
    data_bits = bits_str[start_idx:end_idx]
    
    byte_array = bytearray()
    for i in range(0, len(data_bits), 8):
        byte_array.append(int(data_bits[i:i+8], 2))
        
    return byte_array.decode('utf-8', errors='ignore')


# Основная логика меню
print("1.encrypt", "\n2.decode", "\n3.LSB paste", "\n4.LSB get")
a = int(input("Выберите действие (1-4): "))

if a == 1:
    b = input("your text here: ")
    print("result:", b.translate(crypt), sep='')

elif a == 2:
    b = input("your text here: ")
    print("result:", b.translate(decode), sep='')

elif a == 3:
    # Запрашиваем текст и сразу шифруем его вашим шифратором
    b = input("your text here: ")
    encrypted_text = b.translate(crypt)
    
    img_path = input("Введите путь к исходной картинке: ").strip("'\" ")
    out_path = input("Введите имя для новой картинки (например, res.png): ").strip("'\" ")
    
    print("Кодирование и внедрение...")
    if encode_lsb(img_path, encrypted_text, out_path):
        print(f"Успешно! Картинка сохранена как: {out_path}")

elif a == 4:
    img_path = input("Введите путь к картинке со скрытым текстом: ").strip("'\" ")
    
    print("Извлечение данных...")
    hidden_text = decode_lsb(img_path)
    
    if hidden_text:
        # Переводим извлеченные символы обратно в нормальный текст
        decrypted_text = hidden_text.translate(decode)
        print("\nИзвлеченный шифр:", hidden_text)
        print("Результат расшифровки:", decrypted_text)
