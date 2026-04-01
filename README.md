# DES

Triển khai thuật toán mã hóa **DES** (Data Encryption Standard) bằng Python.

---

## Tổng quan

DES là thuật toán mã hóa đối xứng theo khối (block cipher) với:
- Kích thước khối: **64 bit** (8 byte)
- Kích thước khóa: **64 bit** (8 byte, trong đó 8 bit là parity)
- Số vòng Feistel: **16**

---

## Cấu trúc file

| File | Mô tả |
|------|-------|
| `des.py` | Triển khai đầy đủ DES (mã hóa & giải mã) |
| `test_des.py` | Kiểm thử với các vector chuẩn NIST |

---

## Sử dụng

### Từ dòng lệnh

```bash
# Mã hóa (encrypt)
python des.py encrypt <plaintext_hex> <key_hex>

# Giải mã (decrypt)
python des.py decrypt <ciphertext_hex> <key_hex>
```

**Ví dụ:**

```bash
$ python des.py encrypt 0123456789ABCDEF 133457799BBCDFF1
Ciphertext: 85e813540f0ab405

$ python des.py decrypt 85E813540F0AB405 133457799BBCDFF1
Plaintext:  0123456789abcdef
```

### Từ Python

```python
from des import des_encrypt, des_decrypt

key        = bytes.fromhex("133457799BBCDFF1")
plaintext  = bytes.fromhex("0123456789ABCDEF")

ciphertext = des_encrypt(plaintext, key)
print(ciphertext.hex())   # 85e813540f0ab405

recovered  = des_decrypt(ciphertext, key)
print(recovered.hex())    # 0123456789abcdef
```

---

## Kiểm thử

```bash
python -m unittest test_des -v
```
