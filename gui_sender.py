import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import socket
import threading
import os
from datetime import datetime
from des_utils import encrypt_file
from des_logging import view_history, get_statistics

class SenderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DES Sender - Client Gửi Dữ Liệu")
        self.root.geometry("700x620")
        self.root.resizable(False, False)
        
        # --- Variables ---
        self.selected_file = None
        self.default_key = "12345678"
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

        # 3. Encryption Mode Selection
        mode_frame = tk.Frame(root)
        mode_frame.pack(pady=(12, 5))
        tk.Label(mode_frame, text="Chế độ mã hóa:", font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 10))
        self.mode_var = tk.StringVar(value="CBC")
        mode_combo = ttk.Combobox(mode_frame, textvariable=self.mode_var, 
                                   values=["CBC", "ECB"], state="readonly", width=15)
        mode_combo.pack(side=tk.LEFT)

        # 4. File Selection
        self.file_label = tk.Label(root, text="Chưa chọn file nào", fg="gray", font=("Arial", 9))
        self.file_label.pack(pady=(15, 5))

        self.file_path_label = tk.Label(
            root,
            text="Đường dẫn: (chưa có)",
            fg="gray",
            font=("Arial", 9),
            wraplength=660,
            justify="left",
        )
        self.file_path_label.pack(pady=(0, 8))
        
        self.btn_select = tk.Button(root, text="📂 Chọn File Dữ Liệu", command=self.select_file, bg="#f0f0f0", font=("Arial", 10, "bold"))
        self.btn_select.pack()

        # 5. Status Display
        self.status_label = tk.Label(root, text="Sẵn sàng...", fg="blue", font=("Arial", 10))
        self.status_label.pack(pady=(15, 5))

        # 6. Button Frame
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=(10, 5))
        
        self.btn_send = tk.Button(btn_frame, text="🚀 Mã hóa & Gửi Đi", command=self.start_send_thread, 
                                   bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), width=16, height=2)
        self.btn_send.pack(side=tk.LEFT, padx=5)
        
        self.btn_history = tk.Button(btn_frame, text="📜 Lịch sử", command=self.show_history,
                                      bg="#2196F3", fg="white", font=("Arial", 10), width=10, height=2)
        self.btn_history.pack(side=tk.LEFT, padx=5)

        tk.Label(root, text="Nhật ký (có thời gian):", font=("Arial", 10, "bold")).pack(pady=(10, 5))
        log_frame = tk.Frame(root)
        log_frame.pack(fill="both", expand=True, padx=16, pady=(0, 12))
        self.log_text = tk.Text(log_frame, height=8, font=("Consolas", 9), state=tk.DISABLED)
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

    def start_send_thread(self):
        """Bắt đầu một thread riêng để thực hiện việc mã hóa và gửi file"""
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
        
        mode = self.mode_var.get()
            
        # Vô hiệu hóa nút bấm trong lúc gửi để tránh spam
        self.btn_send.config(state=tk.DISABLED)
        self.btn_select.config(state=tk.DISABLED)
        self.btn_history.config(state=tk.DISABLED)
        self.key_entry.config(state=tk.DISABLED)
        self.status_label.config(text="Đang mã hóa...", fg="orange")
        self.log(f"Bắt đầu mã hóa (Mode: {mode}) và gửi tới {ip}:{self.port}.")
        
        # Tạo thread riêng để không làm treo giao diện GUI
        threading.Thread(target=self.encrypt_and_send, args=(ip, key_bytes, mode), daemon=True).start()

    def encrypt_and_send(self, ip, key_bytes, mode):
        encrypted_file = os.path.abspath("send.enc")
        
        try:
            # 1. Mã hóa file
            result = encrypt_file(self.selected_file, encrypted_file, key_bytes, mode=mode)
            
            if not result:
                self.root.after(0, lambda: self.on_send_error("Mã hóa file thất bại!"))
                return
            
            self.root.after(0, lambda: self.log(f"✓ Mã hóa thành công. File: {encrypted_file}"))
            
            # Cập nhật GUI
            self.root.after(0, lambda: self.status_label.config(text="Mã hóa xong! Đang kết nối...", fg="orange"))
            
            # 2. Thiết lập socket kết nối và gửi
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(5.0)
            client.connect((ip, self.port))
            self.root.after(0, lambda: self.log("✓ Kết nối thành công tới máy nhận."))
            
            with open(encrypted_file, "rb") as f:
                data = f.read()
                client.sendall(data)
                self.root.after(0, lambda: self.log(f"✓ Đã gửi {len(data)} bytes dữ liệu mã hóa."))
                
            client.close()
            
            # 3. Phản hồi thành công
            self.root.after(0, self.on_send_success)
            
        except ConnectionRefusedError:
            self.root.after(0, lambda: self.on_send_error("Không thể kết nối! Máy nhận chưa bật receiver.py hoặc sai IP."))
        except socket.timeout:
            self.root.after(0, lambda: self.on_send_error("Kết nối quá hạn! Hãy kiểm tra IP và tường lửa."))
        except Exception as e:
            self.root.after(0, lambda: self.on_send_error(f"Lỗi hệ thống: {str(e)}"))

    def on_send_success(self):
        self.status_label.config(text="Truyền file mã hóa thành công!", fg="green")
        self.log("✓ Gửi file thành công.")
        messagebox.showinfo("Thành công", "Đã gửi tệp tin an toàn đến máy nhận!")
        self.reset_ui()

    def on_send_error(self, error_msg):
        self.status_label.config(text="Gửi thất bại!", fg="red")
        self.log(f"✗ Gửi thất bại: {error_msg}")
        messagebox.showerror("Lỗi Gửi Dữ Liệu", error_msg)
        self.reset_ui()

    def reset_ui(self):
        self.btn_send.config(state=tk.NORMAL)
        self.btn_select.config(state=tk.NORMAL)
        self.btn_history.config(state=tk.NORMAL)
        self.key_entry.config(state=tk.NORMAL)

    def show_history(self):
        """Hiển thị lịch sử hoạt động"""
        history = view_history(limit=20)
        stats = get_statistics()
        
        if not history:
            messagebox.showinfo("Lịch sử", "Chưa có lịch sử hoạt động nào.")
            return
        
        # Tạo cửa sổ mới
        hist_win = tk.Toplevel(self.root)
        hist_win.title("Lịch sử hoạt động")
        hist_win.geometry("700x450")
        
        # Thống kê header
        stats_text = f"""Thống kê:  Tổng: {stats['total_operations']} | Mã hóa: {stats['encryptions']} 
Giải mã: {stats['decryptions']} | Thành công: {stats['successful']} | Thất bại: {stats['failed']}
Dữ liệu: {stats['total_data_mb']} MB | Thời gian: {stats['total_time_seconds']}s"""
        
        tk.Label(hist_win, text=stats_text, font=("Consolas", 9), justify=tk.LEFT, bg="#f0f0f0").pack(padx=10, pady=10, fill="x")
        
        # Bảng lịch sử
        text_widget = tk.Text(hist_win, height=18, font=("Consolas", 8))
        text_widget.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        for entry in history:
            timestamp = entry['timestamp'].split('T')[1][:8]
            line = f"[{timestamp}] {entry['action'].upper():8s} {entry['filename']:20s} Mode:{entry['mode']:4s} Size:{entry['file_size_bytes']:8d}B Status:{entry['status']:8s}\n"
            text_widget.insert(tk.END, line)
        
        text_widget.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = SenderApp(root)
    root.mainloop()
