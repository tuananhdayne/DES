import os
import time
from manual_des import ManualDES
from des_logging import log_message, log_operation

BLOCK_SIZE = 8
# random iV cho CBC mode
def get_random_bytes(num_bytes: int) -> bytes:
    # Sử dụng os.urandom thay vì Crypto.Random
    return os.urandom(num_bytes)

def encrypt_file(input_file, output_file, key, mode='CBC'):
    """
    Mã hóa file sử dụng DES
    
    Args:
        input_file: đường dẫn file gốc
        output_file: đường dẫn file mã hóa
        key: khóa DES (8 bytes)
        mode: chế độ mã hóa ('CBC' hoặc 'ECB')
    """
    start_time = time.time()
    
    try:
        # Log bắt đầu
        log_message(f"🔒 Bắt đầu mã hóa: {os.path.basename(input_file)} (Mode: {mode})")
        
        # Đọc file
        with open(input_file, "rb") as f:
            data = f.read()
        
        file_size = len(data)
        log_message(f"   Kích thước file: {file_size} bytes")
        
        # Tạo IV nếu CBC mode
        iv = get_random_bytes(8) if mode == 'CBC' else None
        
        # Mã hóa
        cipher = ManualDES(key, mode=mode, iv=iv)
        encrypted_data = cipher.encrypt(data)
        
        log_message(f"   Dữ liệu mã hóa: {len(encrypted_data)} bytes")
        
        # Ghi file - Format: [1 byte mode] + [8 bytes IV if CBC] + [encrypted data]
        with open(output_file, "wb") as f:
            mode_byte = bytes([1 if mode == 'CBC' else 0])
            f.write(mode_byte)
            
            if mode == 'CBC':
                f.write(iv)
            
            f.write(encrypted_data)
        
        duration = time.time() - start_time
        
        # Log thành công
        log_message(f"✅ Mã hóa thành công! Thời gian: {duration:.3f}s")
        log_operation("encrypt", os.path.basename(input_file), mode, file_size, duration, "success")
        
        return True
        
    except Exception as e:
        duration = time.time() - start_time
        error_msg = f"❌ Lỗi mã hóa: {str(e)}"
        log_message(error_msg)
        log_operation("encrypt", os.path.basename(input_file), mode, 0, duration, "failed", str(e))
        return False


def decrypt_file(input_file, output_file, key):
    """
    Giải mã file DES
    
    Args:
        input_file: đường dẫn file mã hóa
        output_file: đường dẫn file sau giải mã
        key: khóa DES (8 bytes)
    
    Returns: True nếu thành công, False nếu thất bại
    """
    start_time = time.time()
    
    try:
        # Đọc file
        with open(input_file, "rb") as f:
            data = f.read()
        
        if len(data) < 1:
            raise ValueError("File mã hóa rỗng hoặc không hợp lệ")
        
        # Đọc mode byte
        mode_byte = data[0]
        if mode_byte not in (0, 1):
            raise ValueError("File mã hóa không hợp lệ (mode byte không đúng)")

        mode = 'CBC' if mode_byte == 1 else 'ECB'
        
        log_message(f"🔓 Bắt đầu giải mã: {os.path.basename(input_file)} (Mode: {mode})")
        
        offset = 1
        iv = None
        
        # Đọc IV nếu CBC mode
        if mode == 'CBC':
            if len(data) < 9:
                raise ValueError("File mã hóa không đủ IV bytes")
            iv = data[1:9]
            offset = 9
            log_message(f"   IV được đọc từ file")
        
        ciphertext = data[offset:]
        if len(ciphertext) == 0:
            raise ValueError("File mã hóa không có dữ liệu ciphertext")
        if len(ciphertext) % BLOCK_SIZE != 0:
            raise ValueError("Ciphertext không hợp lệ (không chia hết cho 8 bytes)")

        file_size = len(ciphertext)
        log_message(f"   Kích thước dữ liệu mã hóa: {file_size} bytes")
        
        # Giải mã
        cipher = ManualDES(key, mode=mode, iv=iv)
        decrypted_data = cipher.decrypt(ciphertext)
        
        # Ghi file
        with open(output_file, "wb") as f:
            f.write(decrypted_data)
#tính thời gian thực hiện        
        duration = time.time() - start_time
        
        # Log thành công
        log_message(f"✅ Giải mã thành công! Thời gian: {duration:.3f}s")
        log_message(f"   File giải mã: {len(decrypted_data)} bytes")
        log_operation("decrypt", os.path.basename(input_file), mode, file_size, duration, "success")
        
        return True
        
    except Exception as e:
        duration = time.time() - start_time
        error_msg = f"❌ Lỗi giải mã: {str(e)}"
        log_message(error_msg)
        log_operation("decrypt", os.path.basename(input_file), "unknown", 0, duration, "failed", str(e))
        return False