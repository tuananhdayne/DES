import os
from manual_des import ManualDES

BLOCK_SIZE = 8

def get_random_bytes(num_bytes: int) -> bytes:
    # Sử dụng os.urandom thay vì Crypto.Random
    return os.urandom(num_bytes)

def encrypt_file(input_file, output_file, key): #mã hóa file gửi đi 
    iv = get_random_bytes(8)
    # Khởi tạo thuật toán DES thủ công
    cipher = ManualDES(key, mode='CBC', iv=iv)   # Tạo một instance của lớp ManualDES với key đã cho, chế độ CBC, và IV ngẫu nhiên. Instance này sẽ được sử dụng để mã hóa dữ liệu từ file gốc. Chế độ CBC yêu cầu một IV để đảm bảo rằng cùng một plaintext sẽ tạo ra các ciphertext khác nhau mỗi khi được mã hóa, tăng cường tính bảo mật của quá trình mã hóa.

    with open(input_file, "rb") as f: #đọc file gốc ở chế độ nhị phân ("rb") để đảm bảo rằng dữ liệu được đọc chính xác mà không bị thay đổi do các vấn đề về mã hóa ký tự. Dữ liệu đọc được sẽ được lưu vào biến data, sau đó sẽ được mã hóa bằng thuật toán DES thủ công và ghi vào file đích. Nếu quá trình mã hóa thành công, file đích sẽ chứa dữ liệu đã được mã hóa sẵn sàng để gửi đi.
        data = f.read()

    # Mã hóa dữ liệu (đã tự động đệm PKCS7 bên trong hàm encrypt)
    encrypted_data = cipher.encrypt(data) 

    with open(output_file, "wb") as f:  # ghi vào file đích ở chế độ nhị phân ("wb") để đảm bảo rằng dữ liệu được ghi chính xác mà không bị thay đổi do các vấn đề về mã hóa ký tự. Trong file đích, IV sẽ được ghi vào 8 bytes đầu tiên, sau đó là dữ liệu mã hóa. Điều này cho phép máy nhận biết được IV cần thiết để giải mã dữ liệu khi nhận được file này.
        # Ghi IV vào 8 bytes đầu tiên, sau đó là dữ liệu mã hóa
        f.write(iv + encrypted_data)

    print("Ma hoa thanh cong:", output_file)


def decrypt_file(input_file, output_file, key):  # Giải mã file đã mã hóa. Hàm này sẽ đọc dữ liệu mã hóa từ file, tách IV ra khỏi phần đầu của dữ liệu, sau đó sử dụng thuật toán DES thủ công để giải mã phần còn lại của dữ liệu. Kết quả giải mã sẽ được ghi vào một file mới. Nếu quá trình giải mã thành công, nội dung của file output_file sẽ là bản gốc của dữ liệu trước khi được mã hóa.
    with open(input_file, "rb") as f:
        data = f.read()

    # Lấy 8 bytes đầu làm IV
    iv = data[:8]
    ciphertext = data[8:]

    cipher = ManualDES(key, mode='CBC', iv=iv)
    
    # Giải mã và loại bỏ đệm padding
    decrypted_data = cipher.decrypt(ciphertext)

    with open(output_file, "wb") as f:
        f.write(decrypted_data)

    print("Giai ma thanh cong:", output_file)