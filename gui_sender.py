import tkinter as tk
from tkinter import filedialog, messagebox
import socket
import threading
import os
from datetime import datetime
from des_utils import encrypt_file

class SenderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DES Sender - Client Gửi Dữ Liệu")
        self.root.geometry("660x560")
        self.root.resizable(False, False)
        
        # --- Variables ---
        self.selected_file = None
        self.default_key = "12345678"  # Cùng chung KEY với Receiver
        self.port = 5000
        
        # --- UI Elements ---
        # 1. IP Input
        tk.Label(root, text="IP Máy Nhận (Receiver IP):", font=("Arial", 10)).pack(pady=(20, 5))
        self.ip_entry = tk.Entry(root, width=30, font=("Arial", 12), justify="center")
        self.ip_entry.insert(0, "127.0.0.1")
        self.ip_entry.pack()

        # 2. Key Input
        tk.Label(root, text="Khóa DES (8 ký tự):", font=("Arial", 10)).pack(pady=(12, 5))
        self.key_entry = tk.Entry(root, width=30, font=("Arial", 12), justify="center")
        self.key_entry.insert(0, self.default_key)
        self.key_entry.pack()

        # 3. File Selection
        self.file_label = tk.Label(root, text="Chưa chọn file nào", fg="gray", font=("Arial", 9))
        self.file_label.pack(pady=(20, 5))

        self.file_path_label = tk.Label(
            root,
            text="Đường dẫn: (chưa có)",
            fg="gray",
            font=("Arial", 9),
            wraplength=620,
            justify="left",
        )
        self.file_path_label.pack(pady=(0, 8))
        
        self.btn_select = tk.Button(root, text="📂 Chọn File Dữ Liệu", command=self.select_file, bg="#f0f0f0", font=("Arial", 10, "bold"))
        self.btn_select.pack()

        # 4. Status Display
        self.status_label = tk.Label(root, text="Sẵn sàng...", fg="blue", font=("Arial", 10))
        self.status_label.pack(pady=(20, 5))

        # 5. Send Button
        self.btn_send = tk.Button(root, text="🚀 Mã hóa & Gửi Đi", command=self.start_send_thread, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), width=20, height=2)
        self.btn_send.pack()

        tk.Label(root, text="Nhật ký (có thời gian):", font=("Arial", 10, "bold")).pack(pady=(14, 5))
        log_frame = tk.Frame(root)
        log_frame.pack(fill="both", expand=True, padx=16, pady=(0, 12))
        self.log_text = tk.Text(log_frame, height=10, font=("Consolas", 9), state=tk.DISABLED)
        self.log_text.pack(side=tk.LEFT, fill="both", expand=True)
        log_scroll = tk.Scrollbar(log_frame, command=self.log_text.yview)
        log_scroll.pack(side=tk.RIGHT, fill="y")
        self.log_text.config(yscrollcommand=log_scroll.set)

        self.log("Ứng dụng khởi động. Sẵn sàng gửi dữ liệu.")

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def select_file(self):
        filename = filedialog.askopenfilename(
            title="Chọn file text",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
        )
        if filename:
            self.selected_file = filename
            self.file_label.config(text=f"Đã chọn: {os.path.basename(filename)}", fg="black")
            self.file_path_label.config(text=f"Đường dẫn: {os.path.abspath(filename)}", fg="black")
            self.status_label.config(text="Đã chọn file! Sẵn sàng gửi.", fg="blue")
            self.log(f"Đã chọn file nguồn: {os.path.abspath(filename)}")

    def start_send_thread(self): # Bắt đầu một thread riêng để thực hiện việc mã hóa và gửi file, nhằm tránh làm treo giao diện người dùng trong quá trình này.
        if not self.selected_file:
            self.log("Thiếu file dữ liệu để gửi.")
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn một file dữ liệu để gửi!")
            return
            
        ip = self.ip_entry.get().strip()
        if not ip:
            self.log("Thiếu địa chỉ IP máy nhận.")
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập IP máy nhận!")
            return

        key_text = self.key_entry.get().strip()
        key_bytes = key_text.encode("utf-8")
        if len(key_bytes) != 8:
            self.log("Khóa DES không hợp lệ (không đủ 8 byte).")
            messagebox.showwarning("Khóa không hợp lệ", "Khóa DES phải đúng 8 byte (thường là 8 ký tự ASCII).")
            return
            
        # Vô hiệu hóa nút bấm trong lúc gửi để tránh spam
        self.btn_send.config(state=tk.DISABLED)
        self.btn_select.config(state=tk.DISABLED)
        self.key_entry.config(state=tk.DISABLED)
        self.status_label.config(text="Đang mã hóa...", fg="orange")
        self.log(f"Bắt đầu mã hóa và gửi tới {ip}:{self.port}.")
        
        # Tạo thread riêng để không làm treo giao diện GUI
        threading.Thread(target=self.encrypt_and_send, args=(ip, key_bytes), daemon=True).start()

    def encrypt_and_send(self, ip, key_bytes):
        encrypted_file = os.path.abspath("send.enc")
        
        try:
            # 1. Mã hóa file bằng thư viện DES tự viết (từ des_utils.py -> manual_des.py)
            encrypt_file(self.selected_file, encrypted_file, key_bytes) # truyền vào file gốc, file đích và key để mã hóa. Hàm này sẽ đọc nội dung của file gốc, áp dụng thuật toán DES để mã hóa dữ liệu, và sau đó ghi kết quả mã hóa vào file đích. Nếu quá trình mã hóa thành công, file đích sẽ chứa dữ liệu đã được mã hóa sẵn sàng để gửi đi.
            self.root.after(0, lambda: self.log(f"Mã hóa thành công. File mã hóa: {encrypted_file}"))
            
            # Cập nhật GUI (Cần dùng root.after vì mình đang ở thread khác)
            self.root.after(0, lambda: self.status_label.config(text="Mã hóa xong! Đang kết nối...", fg="orange"))
            
            # 2. Thiết lập socket kết nối và gửi
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(5.0) # Timeout 5 giây nếu không kết nối được
            client.connect((ip, self.port))
            self.root.after(0, lambda: self.log("Kết nối thành công tới máy nhận."))
            
            with open(encrypted_file, "rb") as f:
                data = f.read()
                client.sendall(data)
                self.root.after(0, lambda: self.log(f"Đã gửi {len(data)} bytes dữ liệu mã hóa."))
                
            client.close()
            
            # 3. Phản hồi thành công
            self.root.after(0, self.on_send_success)
            
        except ConnectionRefusedError:
            self.root.after(0, lambda: self.on_send_error("Không thể kết nối! Máy nhận chưa bật receiver.py hoặc sai IP."))
        except socket.timeout:
            self.root.after(0, lambda: self.on_send_error("Kết nối quá hạn! Hãy kiểm tra IP và tường lửa (Firewall)."))
        except Exception as e:
            self.root.after(0, lambda: self.on_send_error(f"Lỗi hệ thống: {str(e)}"))

    def on_send_success(self):
        self.status_label.config(text="Truyền file mã hóa thành công!", fg="green")
        self.log("Gửi file thành công.")
        messagebox.showinfo("Thành công", "Đã gửi tệp tin an toàn đến máy nhận!")
        # Đóng ứng dụng sau khi gửi thành công.
        self.reset_ui()

        # self.root.destroy()

    def on_send_error(self, error_msg):
        self.status_label.config(text="Gửi thất bại!", fg="red")
        self.log(f"Gửi thất bại: {error_msg}")
        messagebox.showerror("Lỗi Gửi Dữ Liệu", error_msg)
        self.reset_ui()

    def reset_ui(self):
        self.btn_send.config(state=tk.NORMAL)
        self.btn_select.config(state=tk.NORMAL)
        self.key_entry.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = SenderApp(root)
    root.mainloop()
