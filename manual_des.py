import os
import struct
import random

# BẢNG HOÁN VỊ - PERMUTATION TABLES
# Các bảng dưới đây định nghĩa thứ tự sắp xếp lại các bit trong quá trình mã hóa

# Initial Permutation (IP) - Hoán vị ban đầu
# Sắp xếp lại 64 bit dữ liệu ban đầu
# Ví dụ: bit thứ 58 của dữ liệu gốc → vị trí 1 của kết quả
IP = [
    58, 50, 42, 34, 26, 18, 10, 2,
    60, 52, 44, 36, 28, 20, 12, 4,
    62, 54, 46, 38, 30, 22, 14, 6,
    64, 56, 48, 40, 32, 24, 16, 8,
    57, 49, 41, 33, 25, 17, 9,  1,
    59, 51, 43, 35, 27, 19, 11, 3,
    61, 53, 45, 37, 29, 21, 13, 5,
    63, 55, 47, 39, 31, 23, 15, 7
]
# Sau khi hoán vị chuỗi thì sẽ chia đôi thành 2 nửa: Left (L) và Right (R), mỗi nửa 32 bit. Các vòng mã hóa sẽ chỉ xử lý nửa phải (R) và sau đó hoán đổi với nửa trái (L) sau mỗi vòng. Hoán vị ban đầu giúp tăng cường tính bảo mật bằng cách làm rối loạn dữ liệu trước khi bắt đầu quá trình mã hóa chính.
# Final Permutation (IP^-1) - Hoán vị cuối cùng (nghịch đảo IP)
# Hoàn nguyên lại thứ tự các bit sau 16 vòng mã hóa
FP = [
    40, 8, 48, 16, 56, 24, 64, 32,
    39, 7, 47, 15, 55, 23, 63, 31,
    38, 6, 46, 14, 54, 22, 62, 30,
    37, 5, 45, 13, 53, 21, 61, 29,
    36, 4, 44, 12, 52, 20, 60, 28,
    35, 3, 43, 11, 51, 19, 59, 27,
    34, 2, 42, 10, 50, 18, 58, 26,
    33, 1, 41, 9,  49, 17, 57, 25
]

# Expansion (E) - Mở rộng từ 32 bit thành 48 bit  
# Nhân đôi một số bit để phục vụ XOR với subkey 48-bit
E = [
    32, 1,  2,  3,  4,  5,
    4,  5,  6,  7,  8,  9,
    8,  9,  10, 11, 12, 13,
    12, 13, 14, 15, 16, 17,
    16, 17, 18, 19, 20, 21,
    20, 21, 22, 23, 24, 25,
    24, 25, 26, 27, 28, 29,
    28, 29, 30, 31, 32, 1
]

# Permutation (P) - Hoán vị sau S-box
# Sắp xếp lại 32 bit kết quả từ S-box 
P = [
    16, 7,  20, 21,
    29, 12, 28, 17,
    1,  15, 23, 26,
    5,  18, 31, 10,
    2,  8,  24, 14,
    32, 27, 3,  9,
    19, 13, 30, 6,
    22, 11, 4,  25
]

# Permuted Choice 1 (PC1) - Chọn hoán vị 1 (tạo khóa)
# Rút ra 56 bit từ 64 bit khóa ban đầu (bỏ các bit parity)
# bỏ các bit thứ 8, 16, 24, 32, 40, 48, 56, 64 (các bit này thường được sử dụng làm bit parity và không tham gia vào quá trình mã hóa chính)
PC1 = [
    57, 49, 41, 33, 25, 17, 9,
    1,  58, 50, 42, 34, 26, 18,
    10, 2,  59, 51, 43, 35, 27,
    19, 11, 3,  60, 52, 44, 36,
    63, 55, 47, 39, 31, 23, 15,
    7,  62, 54, 46, 38, 30, 22,
    14, 6,  61, 53, 45, 37, 29,
    21, 13, 5,  28, 20, 12, 4
]

# Permuted Choice 2 (PC2) - Chọn hoán vị 2 (tạo subkey)
# Rút ra 48 bit từ 56 bit khóa để tạo subkey cho mỗi vòng
# bỏ các bit thứ 9, 18, 22, 25, 35, 38, 43, 54 (các bit này không được sử dụng trong quá trình tạo subkey và thường được loại bỏ để giảm độ dài khóa từ 56 bit xuống còn 48 bit cho mỗi subkey)
PC2 = [
    14, 17, 11, 24, 1,  5,
    3,  28, 15, 6,  21, 10,
    23, 19, 12, 4,  26, 8,
    16, 7,  27, 20, 13, 2,
    41, 52, 31, 37, 47, 55,
    30, 40, 51, 45, 33, 48,
    44, 49, 39, 56, 34, 53,
    46, 42, 50, 36, 29, 32
]

# SHIFT_SCHEDULE - Lịch trình dịch trái để tạo subkey
# Số lần dịch trái cho mỗi vòng (16 vòng tổng cộng)
SHIFT_SCHEDULE = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]

# S-BOX - Bảng thay thế (S-box 1 đến S-box 8)
# 8 bảng thay thế để biến đổi 48 bit thành 32 bit
# Mỗi bảng nhận 6 bit và xuất 4 bit
S_BOX = [
    [
        [14, 4,  13, 1,  2,  15, 11, 8,  3,  10, 6,  12, 5,  9,  0,  7],
        [0,  15, 7,  4,  14, 2,  13, 1,  10, 6,  12, 11, 9,  5,  3,  8],
        [4,  1,  14, 8,  13, 6,  2,  11, 15, 12, 9,  7,  3,  10, 5,  0],
        [15, 12, 8,  2,  4,  9,  1,  7,  5,  11, 3,  14, 10, 0,  6,  13]
    ],
    [
        [15, 1,  8,  14, 6,  11, 3,  4,  9,  7,  2,  13, 12, 0,  5,  10],
        [3,  13, 4,  7,  15, 2,  8,  14, 12, 0,  1,  10, 6,  9,  11, 5],
        [0,  14, 7,  11, 10, 4,  13, 1,  5,  8,  12, 6,  9,  3,  2,  15],
        [13, 8,  10, 1,  3,  15, 4,  2,  11, 6,  7,  12, 0,  5,  14, 9]
    ],
    [
        [10, 0,  9,  14, 6,  3,  15, 5,  1,  13, 12, 7,  11, 4,  2,  8],
        [13, 7,  0,  9,  3,  4,  6,  10, 2,  8,  5,  14, 12, 11, 15, 1],
        [13, 6,  4,  9,  8,  15, 3,  0,  11, 1,  2,  12, 5,  10, 14, 7],
        [1,  10, 13, 0,  6,  9,  8,  7,  4,  15, 14, 3,  11, 5,  2,  12]
    ],
    [
        [7,  13, 14, 3,  0,  6,  9,  10, 1,  2,  8,  5,  11, 12, 4,  15],
        [13, 8,  11, 5,  6,  15, 0,  3,  4,  7,  2,  12, 1,  10, 14, 9],
        [10, 6,  9,  0,  12, 11, 7,  13, 15, 1,  3,  14, 5,  2,  8,  4],
        [3,  15, 0,  6,  10, 1,  13, 8,  9,  4,  5,  11, 12, 7,  2,  14]
    ],
    [
        [2,  12, 4,  1,  7,  10, 11, 6,  8,  5,  3,  15, 13, 0,  14, 9],
        [14, 11, 2,  12, 4,  7,  13, 1,  5,  0,  15, 10, 3,  9,  8,  6],
        [4,  2,  1,  11, 10, 13, 7,  8,  15, 9,  12, 5,  6,  3,  0,  14],
        [11, 8,  12, 7,  1,  14, 2,  13, 6,  15, 0,  9,  10, 4,  5,  3]
    ],
    [
        [12, 1,  10, 15, 9,  2,  6,  8,  0,  13, 3,  4,  14, 7,  5,  11],
        [10, 15, 4,  2,  7,  12, 9,  5,  6,  1,  13, 14, 0,  11, 3,  8],
        [9,  14, 15, 5,  2,  8,  12, 3,  7,  0,  4,  10, 1,  13, 11, 6],
        [4,  3,  2,  12, 9,  5,  15, 10, 11, 14, 1,  7,  6,  0,  8,  13]
    ],
    [
        [4,  11, 2,  14, 15, 0,  8,  13, 3,  12, 9,  7,  5,  10, 6,  1],
        [13, 0,  11, 7,  4,  9,  1,  10, 14, 3,  5,  12, 2,  15, 8,  6],
        [1,  4,  11, 13, 12, 3,  7,  14, 10, 15, 6,  8,  0,  5,  9,  2],
        [6,  11, 13, 8,  1,  4,  10, 7,  9,  5,  0,  15, 14, 2,  3,  12]
    ],
    [
        [13, 2,  8,  4,  6,  15, 11, 1,  10, 9,  3,  14, 5,  0,  12, 7],
        [1,  15, 13, 8,  10, 3,  7,  4,  12, 5,  6,  11, 0,  14, 9,  2],
        [7,  11, 4,  1,  9,  12, 14, 2,  0,  6,  10, 13, 15, 3,  5,  8],
        [2,  1,  14, 7,  4,  10, 8,  13, 15, 12, 9,  0,  3,  5,  6,  11]
    ]
]


# ============================================================================
# CoreDES - Lõi của thuật toán DES
# ============================================================================
class CoreDES:
    """Lớp thực hiện mã hóa/giải mã từng khối 8 bytes bằng DES"""
    
    def __init__(self, key: bytes):
        """Khởi tạo DES với khóa 8 bytes (64 bits)
        Args:
            key: Khóa 64-bit (8 bytes). Thực tế chỉ sử dụng 56 bits (8 bits parity)
        Raises:
            ValueError: Nếu khóa không phải 8 bytes
        """
        if len(key) != 8:
            raise ValueError("Key must be exactly 8 bytes.")
        # Tạo 16 subkeys (mỗi cái 48 bits) từ khóa gốc
        self.subkeys = self._generate_subkeys(self._bytes_to_bits(key)) 

    def _bytes_to_bits(self, data: bytes) -> list:
        """Chuyển đổi bytes thành danh sách các bit (0 và 1)
        Ví dụ: b'\x05' → [0,0,0,0,0,1,0,1]
        """
        bits = []
        for byte in data:
            bits.extend([int(b) for b in f"{byte:08b}"])
        return bits

    def _bits_to_bytes(self, bits: list) -> bytes:
        """Chuyển đổi danh sách bit thành bytes
        Ví dụ: [0,0,0,0,0,1,0,1] → b'\x05'
        """
        byte_list = []
        for i in range(0, len(bits), 8):
            byte_val = int("".join(str(b) for b in bits[i:i+8]), 2)
            byte_list.append(byte_val)
        return bytes(byte_list)
# hàm để hoán vị 1 khối theo thứ tự bảng 
    def _permute(self, block: list, table: list) -> list: 
        """Thực hiện hoán vị theo bảng permutation
        Args:
            block: Danh sách bit cần hoán vị
            table: Bảng hoán vị (các chỉ mục từ 1)
        Returns:
            Danh sách bit sau hoán vị
        """
        return [block[i - 1] for i in table]

    def _left_shift(self, bits: list, num_shifts: int) -> list:
        """Dịch trái danh sách bit một số vị trí
        Ví dụ: [1,2,3,4,5] dịch 2 → [3,4,5,1,2]
        """
        return bits[num_shifts:] + bits[:num_shifts]

    def _xor(self, bits1: list, bits2: list) -> list:  #khác 1 giống 0
        """Thực hiện phép XOR theo từng bit
        Ví dụ: [1,0,1] XOR [1,1,0] → [0,1,1]
        """
        return [b1 ^ b2 for b1, b2 in zip(bits1, bits2)]

    def _generate_subkeys(self, key_bits: list) -> list:  
        """Tạo 16 subkey từ khóa 64-bit
        Quá trình: Hoán vị PC1 → Chia 28+28 → Dịch trái → Hoán vị PC2 (16 lần)
        Returns: Danh sách 16 subkey (mỗi cái 48 bits)
        """
        # Hoán vị PC1: 64 bits → 56 bits (bỏ bit parity)
        key_56 = self._permute(key_bits, PC1)
        # Chia thành 2 nửa: C và D (28 bits mỗi nửa)
        c, d = key_56[:28], key_56[28:]
        
        subkeys = []
        # Tạo 16 subkey cho 16 vòng DES
        for shifts in SHIFT_SCHEDULE:
            # Dịch trái C và D
            c = self._left_shift(c, shifts)
            d = self._left_shift(d, shifts)
            # Nối C và D lại
            cd = c + d
            # Hoán vị PC2: 56 bits → 48 bits
            subkey = self._permute(cd, PC2)
            subkeys.append(subkey) 
        return subkeys   # danh sách 16 subkey, mỗi subkey là một danh sách 48 bit (0 và 1)

    def _feistel_function(self, right: list, subkey: list) -> list:
        """Hàm Feistel: Mã hóa nửa phải 32 bits
        Quá trình: Mở rộng → XOR → S-box → Hoán vị
        Args:
            right: 32 bits nửa phải
            subkey: 48 bits khóa con
        Returns: 32 bits sau khi qua hàm Feistel
        """
        # Bước 1: Mở rộng 32 → 48 bits
        expanded_right = self._permute(right, E)
        
        # Bước 2: XOR với subkey
        xored = self._xor(expanded_right, subkey)
        
        # Bước 3: Đưa qua 8 S-box (mỗi S-box: 6 bits → 4 bits)
        sbox_out = []
        for i in range(8):
            chunk = xored[i * 6:(i + 1) * 6]  # Lấy 6 bits cho S-box thứ i
            # Tính hàng: bit 0 và bit 5
            row = (chunk[0] << 1) + chunk[5]
            # Tính cột: bit 1,2,3,4
            col = (chunk[1] << 3) + (chunk[2] << 2) + (chunk[3] << 1) + chunk[4]
            # Tra bảng S-box và lấy giá trị 4 bits
            val = S_BOX[i][row][col]
            sbox_out.extend([int(b) for b in f"{val:04b}"])
        
        # Bước 4: Hoán vị kết quả
        return self._permute(sbox_out, P)

    def process_block(self, block: bytes, decrypt=False) -> bytes:
        """Mã hóa hoặc giải mã một khối 8 bytes (64 bits)
        Args:
            block: 8 bytes dữ liệu cần xử lý
            decrypt: True để giải mã, False để mã hóa
        Returns: 8 bytes dữ liệu sau khi xử lý
        """
        # Bước 1: Chuyển bytes → bits
        bits = self._bytes_to_bits(block)
        
        # Bước 2: Hoán vị ban đầu (IP)
        bits = self._permute(bits, IP)
        left, right = bits[:32], bits[32:]
        
        # Bước 3: Chọn subkeys (giải mã dùng subkeys ngược)  lấy khóa ở trên
        # nếu mã hóa thì lấy từ cuối đến đầu, nếu giải mã thì lấy từ đầu đến cuối. Điều này là do quá trình mã hóa và giải mã trong DES sử dụng cùng một thuật toán nhưng với thứ tự subkey ngược lại. Khi mã hóa, subkey đầu tiên được sử dụng trong vòng đầu tiên, subkey thứ hai trong vòng thứ hai, và cứ tiếp tục như vậy. Ngược lại, khi giải mã, subkey cuối cùng được sử dụng trong vòng đầu tiên, subkey kế cuối trong vòng thứ hai, và cứ tiếp tục như vậy cho đến khi sử dụng subkey đầu tiên ở vòng cuối cùng.
        keys = self.subkeys[::-1] if decrypt else self.subkeys 
        
        # Bước 4: 16 vòng Feistel
        for subkey in keys:
            f_res = self._feistel_function(right, subkey)
            new_right = self._xor(left, f_res)  # XOR left với kết quả hàm Feistel
            left = right                        # Swap
            right = new_right
        # sau 16 vòng, left và right đã được hoán đổi 16 lần, nhưng chúng ta cần swap lại một lần cuối để khôi phục đúng vị trí ban đầu của chúng trước khi áp dụng hoán vị cuối cùng (FP). Điều này là do trong mỗi vòng, chúng ta đã thực hiện swap giữa left và right, nên sau 16 vòng, chúng ta cần swap lại một lần nữa để đảm bảo rằng left và right ở đúng vị trí của chúng trước khi áp dụng hoán vị cuối cùng. Nếu không swap lại, kết quả sẽ bị đảo ngược so với mong đợi.
        # Bước 5: Hoán vị cuối cùng (IP inverse)
        final_bits = right + left  # Swap lần cuối
        final_bits = self._permute(final_bits, FP)
        
        # Bước 6: Chuyển bits → bytes
        return self._bits_to_bytes(final_bits)

# ============================================================================
# HỘI TRỢ CHỨC NĂNG - HELPER FUNCTIONS
# ============================================================================

def xor_bytes(b1: bytes, b2: bytes) -> bytes: # thực hiện phép XOR giữa hai chuỗi byte
    """Thực hiện phép XOR từng byte
    Ví dụ: b'A' XOR b'B' → b'\x03' (0x41 XOR 0x42 = 0x03)
    """
    return bytes(a ^ b for a, b in zip(b1, b2))

def pad_pkcs7(data: bytes, block_size: int = 8) -> bytes:  #thêm padding PKCS7 để độ dài dữ liệu là bội số của block_size
    """Thêm padding PKCS7 để độ dài dữ liệu là bội số của block_size
    Ví dụ: b'Hello' + 3 bytes padding(\x03) → b'Hello\x03\x03\x03'
    """
    pad_len = block_size - (len(data) % block_size)
    return data + bytes([pad_len] * pad_len)

def unpad_pkcs7(data: bytes) -> bytes:   #gỡ bỏ padding PKCS7
    """Loại bỏ padding PKCS7
    Ví dụ: b'Hello\x03\x03\x03' → b'Hello'
    """
    if not data:
        raise ValueError("Dữ liệu rỗng, không thể bỏ padding")

    pad_len = data[-1]

    # PKCS7 với block size 8: pad_len phải trong khoảng 1..8
    if pad_len < 1 or pad_len > 8:
        raise ValueError("Padding không hợp lệ (sai khóa hoặc dữ liệu hỏng)")

    # Toàn bộ pad bytes cuối phải cùng giá trị pad_len
    if data[-pad_len:] != bytes([pad_len] * pad_len):
        raise ValueError("Padding không hợp lệ (sai khóa hoặc dữ liệu hỏng)")

    return data[:-pad_len]

# ============================================================================
# ManualDES - Giao diện mã hóa toàn bộ dữ liệu
# ============================================================================
class ManualDES:
    """Lớp để mã hóa/giải mã dữ liệu với chế độ CBC
    Xử lý dữ liệu có độ dài bất kỳ, tự động thêm padding
    """
    
    def __init__(self, key: bytes, mode='CBC', iv=None):
        """Khởi tạo ManualDES
        Args:
            key: Khóa 8 bytes (64-bit)
            mode: Chế độ mã hóa ('CBC' hoặc 'ECB'). Mặc định: 'CBC'
            iv: Initialization Vector (8 bytes), dùng cho CBC mode
        """
        self.des = CoreDES(key)
        self.mode = mode
        self.iv = iv

    def encrypt(self, data: bytes) -> bytes:
        """Mã hóa dữ liệu có độ dài bất kỳ
        Args:
            data: Dữ liệu cần mã hóa (bytes)
        Returns: Dữ liệu đã mã hóa (bytes)
        """
        # Bước 1: Thêm padding PKCS7
        data = pad_pkcs7(data)
        
        out = []
        prev = self.iv  # Bắt đầu với IV (hoặc None nếu ECB)
        
        # Bước 2: Mã hóa từng khối 8 bytes
        for i in range(0, len(data), 8):
            block = data[i:i+8]
            
            # CBC mode: XOR khối hiện tại với khối mã hóa trước đó
            if self.mode == 'CBC':
                block = xor_bytes(block, prev)
            
            # Mã hóa khối bằng DES
            enc_block = self.des.process_block(block, False)
            out.append(enc_block)
            
            # Lưu khối mã hóa để dùng trong lần lặp tiếp theo (CBC)
            prev = enc_block
        
        # Bước 3: Nối tất cả các khối mã hóa
        return b"".join(out)

    def decrypt(self, data: bytes) -> bytes:
        """Giải mã dữ liệu đã mã hóa
        Args:
            data: Dữ liệu đã mã hóa (bytes), độ dài phải là bội số 8
        Returns: Dữ liệu gốc trước khi mã hóa (bytes)
        """
        out = []
        prev = self.iv  # Bắt đầu với IV
        
        # Bước 1: Giải mã từng khối 8 bytes
        for i in range(0, len(data), 8):
            block = data[i:i+8]
            # Giải mã khối bằng DES (decrypt=True)
            dec_block = self.des.process_block(block, True)
            
            # CBC mode: XOR với khối mã hóa trước đó để lấy lại plaintext
            if self.mode == 'CBC':
                dec_block = xor_bytes(dec_block, prev)
            
            out.append(dec_block)
            # Lưu khối mã hóa gốc (không phải dec_block) cho lần tiếp theo
            prev = block
        
        # Bước 2: Nối tất cả khối và loại bỏ padding
        return unpad_pkcs7(b"".join(out))
