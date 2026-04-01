# Giai thich thuat toan DES trong project

Tai lieu nay mo ta thuat toan dua tren code trong manual_des.py va des_utils.py.

## 1) Tong quan kien truc

Project chia thanh 3 lop logic:

1. Lop xu ly khoi DES (CoreDES trong manual_des.py)
2. Lop mode CBC + padding (ManualDES trong manual_des.py)
3. Lop ma hoa/giai ma file (encrypt_file, decrypt_file trong des_utils.py)

Luong tong quat:

1. Ben gui doc file goc
2. Them padding PKCS7
3. Tao IV ngau nhien 8 byte
4. Ma hoa CBC bang DES thu cong
5. Ghi file ma hoa: IV + ciphertext
6. Ben nhan doc file ma hoa, tach IV
7. Giai ma CBC
8. Bo padding de lay plaintext goc

## 2) CoreDES: ma hoa 1 khoi 8 byte

DES xu ly theo khoi 64 bit (8 byte).

### 2.1 Chuyen doi du lieu

- _bytes_to_bits: bytes -> danh sach bit
- _bits_to_bytes: danh sach bit -> bytes

### 2.2 Hoan vi va XOR

- _permute: hoan vi theo bang (IP, FP, E, P, PC1, PC2)
- _xor: XOR tung bit
- _left_shift: dich vong trai cho C, D khi tao subkey

### 2.3 Sinh 16 subkey

Ham _generate_subkeys thuc hien:

1. PC1: 64 bit key -> 56 bit (bo 8 parity bit)
2. Tach thanh C va D, moi nua 28 bit
3. Dung SHIFT_SCHEDULE de dich trai C, D qua 16 vong
4. Gop C + D, roi PC2 de lay 48 bit
5. Thu duoc 16 subkey, moi subkey 48 bit

### 2.4 Ham Feistel

Ham _feistel_function(right, subkey):

1. E: mo rong Right 32 bit -> 48 bit
2. XOR voi subkey 48 bit
3. Chia 8 cum, moi cum 6 bit
4. Qua 8 S-box: 6 bit -> 4 bit
5. Gop lai thanh 32 bit
6. P permutation de tron bit

### 2.5 16 vong DES trong process_block

1. IP tren block 64 bit
2. Tach Left, Right (32 + 32)
3. Neu decrypt thi dao nguoc thu tu subkey
4. Lap 16 vong:
   - f = Feistel(Right, subkey)
   - new_right = Left XOR f
   - Left = Right
   - Right = new_right
5. Swap cuoi: Right + Left
6. FP de ra block ket qua

Tinh doi xung cua DES nam o cho: giai ma dung cung cong thuc, chi dao thu tu subkey.

## 3) ManualDES: CBC va padding

CoreDES chi xu ly 1 khoi 8 byte. ManualDES them kha nang xu ly data dai bat ky.

### 3.1 Padding PKCS7

- pad_pkcs7: bo sung n byte co gia tri n de du do dai boi cua 8
- unpad_pkcs7: bo cac byte padding o cuoi sau giai ma

### 3.2 CBC mode khi ma hoa

Moi block plaintext P_i:

1. X_i = P_i XOR C_{i-1}
2. C_i = DES_encrypt(X_i)

Trong do C_0 = IV.

Code tuong ung o ManualDES.encrypt:

1. prev = IV
2. block = block XOR prev
3. enc_block = des.process_block(block, False)
4. prev = enc_block

### 3.3 CBC mode khi giai ma

Moi block ciphertext C_i:

1. X_i = DES_decrypt(C_i)
2. P_i = X_i XOR C_{i-1}

Trong do C_0 = IV.

Code tuong ung o ManualDES.decrypt:

1. dec_block = des.process_block(block, True)
2. dec_block = dec_block XOR prev
3. prev = block (ciphertext goc cua vong hien tai)

## 4) des_utils.py: ma hoa/giai ma file

### 4.1 encrypt_file

1. Tao IV ngau nhien 8 byte (os.urandom)
2. Doc toan bo input_file (binary)
3. Ma hoa bang ManualDES(mode='CBC', iv=IV)
4. Ghi output_file theo format:
   - 8 byte dau: IV
   - phan sau: ciphertext

### 4.2 decrypt_file

1. Doc file ma hoa
2. Tach 8 byte dau lam IV
3. Phan con lai la ciphertext
4. Giai ma CBC
5. Ghi plaintext ra output_file

## 5) Vi sao khoa 12345670 va 12345671 van co the giai ma dung?

Ly do nam o co che parity cua DES key:

1. DES nhan key 64 bit nhung chi dung 56 bit hieu luc
2. 8 bit con lai la parity bit (moi byte 1 bit)
3. PC1 trong code loai bo 8 parity bit nay

Voi cap byte cuoi:

- '0' = 0x30 = 00110000
- '1' = 0x31 = 00110001

Khac nhau o bit thap nhat (thuong la parity bit theo quy uoc DES), nen sau PC1 hai key co the tro thanh cung 56 bit hieu luc. Khi subkey giong nhau thi ciphertext va ket qua giai ma van dung.

Noi ngan gon: khac parity bit khong lam doi effective key cua DES.

## 6) Ghi chu bao mat

1. DES 56-bit da yeu theo tieu chuan hien dai
2. Neu dung thuc te nen chuyen sang AES-GCM hoac it nhat 3DES/AES-CBC + xac thuc
3. Dang CBC hien tai chua co MAC, nen co nguy co bi sua du lieu ma khong bi phat hien

## 7) Ket luan

Code cua ban da dung luong DES-CBC co IV va PKCS7:

1. CoreDES xu ly dung cau truc Feistel 16 vong
2. ManualDES them CBC de ma hoa du lieu dai
3. des_utils quan ly file va format luu IV + ciphertext

Vi vay, day la mot mo phong DES hoc thuat rat ro rang cho muc dich hoc tap va bao cao.
