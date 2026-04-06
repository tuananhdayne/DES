import os
import socket
import threading
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

from des_utils import decrypt_file
from des_logging import view_history, get_statistics


class ReceiverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DES Receiver - Client Nhan Du Lieu")
        self.root.geometry("760x640")
        self.root.resizable(False, False)

        self.server_socket = None
        self.is_listening = False

        tk.Label(root, text="IP Lang Nghe:", font=("Arial", 10)).pack(pady=(15, 5))
        self.host_entry = tk.Entry(root, width=32, font=("Arial", 12), justify="center")
        self.host_entry.insert(0, "0.0.0.0")
        self.host_entry.pack()

        tk.Label(root, text="Port:", font=("Arial", 10)).pack(pady=(10, 5))
        self.port_entry = tk.Entry(root, width=32, font=("Arial", 12), justify="center")
        self.port_entry.insert(0, "5000")
        self.port_entry.pack()

        tk.Label(root, text="Khoa DES (8 ky tu):", font=("Arial", 10)).pack(pady=(10, 5))
        self.key_entry = tk.Entry(root, width=32, font=("Arial", 12), justify="center")
        self.key_entry.insert(0, "12345678")
        self.key_entry.pack()

        tk.Label(root, text="Duong dan file ma hoa nhan duoc:", font=("Arial", 10)).pack(pady=(12, 5))
        encrypted_wrap = tk.Frame(root)
        encrypted_wrap.pack()
        self.encrypted_entry = tk.Entry(encrypted_wrap, width=52, font=("Arial", 10))
        self.encrypted_entry.insert(0, "received.enc")
        self.encrypted_entry.pack(side=tk.LEFT, padx=(0, 8))
        tk.Button(encrypted_wrap, text="Chon", command=self.choose_encrypted_path).pack(side=tk.LEFT)

        self.encrypted_path_label = tk.Label(
            root,
            text="Duong dan day du file ma hoa: (chua co)",
            fg="gray",
            font=("Arial", 9),
            wraplength=720,
            justify="left",
        )
        self.encrypted_path_label.pack(pady=(2, 8))

        tk.Label(root, text="Duong dan file sau giai ma:", font=("Arial", 10)).pack(pady=(12, 5))
        decrypted_wrap = tk.Frame(root)
        decrypted_wrap.pack()
        self.decrypted_entry = tk.Entry(decrypted_wrap, width=52, font=("Arial", 10))
        self.decrypted_entry.insert(0, "received_decrypted.txt")
        self.decrypted_entry.pack(side=tk.LEFT, padx=(0, 8))
        tk.Button(decrypted_wrap, text="Chon", command=self.choose_decrypted_path).pack(side=tk.LEFT)

        self.decrypted_path_label = tk.Label(
            root,
            text="Duong dan day du file giai ma: (chua co)",
            fg="gray",
            font=("Arial", 9),
            wraplength=720,
            justify="left",
        )
        self.decrypted_path_label.pack(pady=(2, 8))

        self.status_label = tk.Label(root, text="San sang...", fg="blue", font=("Arial", 10))
        self.status_label.pack(pady=(16, 6))

        tk.Label(root, text="Nhat ky (co thoi gian):", font=("Arial", 10, "bold")).pack(pady=(8, 5))
        log_frame = tk.Frame(root)
        log_frame.pack(fill="both", expand=True, padx=16, pady=(0, 10))
        self.log_text = tk.Text(log_frame, height=10, font=("Consolas", 9), state=tk.DISABLED)
        self.log_text.pack(side=tk.LEFT, fill="both", expand=True)
        log_scroll = tk.Scrollbar(log_frame, command=self.log_text.yview)
        log_scroll.pack(side=tk.RIGHT, fill="y")
        self.log_text.config(yscrollcommand=log_scroll.set)

        button_wrap = tk.Frame(root)
        button_wrap.pack()
        self.btn_start = tk.Button(
            button_wrap,
            text="Bắt Đầu Nhận",
            command=self.start_listen,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 11, "bold"),
            width=14,
            height=2,
        )
        self.btn_start.pack(side=tk.LEFT, padx=8)

        self.btn_stop = tk.Button(
            button_wrap,
            text="Dừng",
            command=self.stop_listen,
            bg="#c0392b",
            fg="white",
            font=("Arial", 11, "bold"),
            width=10,
            height=2,
            state=tk.DISABLED,
        )
        self.btn_stop.pack(side=tk.LEFT, padx=8)

        self.btn_history = tk.Button(
            button_wrap,
            text="📜 Lịch sử",
            command=self.show_history,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10),
            width=10,
            height=2
        )
        self.btn_history.pack(side=tk.LEFT, padx=8)

        self.encrypted_entry.bind("<KeyRelease>", lambda _event: self.refresh_path_preview())
        self.decrypted_entry.bind("<KeyRelease>", lambda _event: self.refresh_path_preview())

        self.refresh_path_preview()
        self.log("Ung dung khoi dong. San sang nhan du lieu.")

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def refresh_path_preview(self):
        encrypted_abs = os.path.abspath(self.encrypted_entry.get().strip() or "received.enc")
        decrypted_abs = os.path.abspath(self.decrypted_entry.get().strip() or "received_decrypted.txt")
        self.encrypted_path_label.config(text=f"Duong dan day du file ma hoa: {encrypted_abs}", fg="black")
        self.decrypted_path_label.config(text=f"Duong dan day du file giai ma: {decrypted_abs}", fg="black")

    def choose_encrypted_path(self):
        path = filedialog.asksaveasfilename(
            title="Chon noi luu file ma hoa",
            defaultextension=".enc",
            filetypes=(("Encrypted files", "*.enc"), ("All files", "*.*")),
        )
        if path:
            self.encrypted_entry.delete(0, tk.END)
            self.encrypted_entry.insert(0, path)
            self.refresh_path_preview()
            self.log(f"Da chon duong dan luu file ma hoa: {os.path.abspath(path)}")

    def choose_decrypted_path(self):
        path = filedialog.asksaveasfilename(
            title="Chon noi luu file giai ma",
            defaultextension=".txt",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*")),
        )
        if path:
            self.decrypted_entry.delete(0, tk.END)
            self.decrypted_entry.insert(0, path)
            self.refresh_path_preview()
            self.log(f"Da chon duong dan luu file giai ma: {os.path.abspath(path)}")

    def start_listen(self):
        if self.is_listening:
            return

        host = self.host_entry.get().strip()
        if not host:
            self.log("Thieu IP lang nghe.")
            messagebox.showwarning("Thieu thong tin", "Vui long nhap IP lang nghe.")
            return

        try:
            port = int(self.port_entry.get().strip())
            if port < 1 or port > 65535:
                raise ValueError
        except ValueError:
            self.log("Port khong hop le.")
            messagebox.showwarning("Port khong hop le", "Port phai la so tu 1 den 65535.")
            return

        key_text = self.key_entry.get().strip()
        key_bytes = key_text.encode("utf-8")
        if len(key_bytes) != 8:
            self.log("Khoa DES khong hop le (khong du 8 byte).")
            messagebox.showwarning("Khoa khong hop le", "Khoa DES phai dung 8 byte (thuong la 8 ky tu ASCII).")
            return

        encrypted_file = self.encrypted_entry.get().strip()
        decrypted_file = self.decrypted_entry.get().strip()
        if not encrypted_file or not decrypted_file:
            self.log("Thieu duong dan file nhan/giai ma.")
            messagebox.showwarning("Thieu duong dan", "Vui long nhap duong dan file nhan va file giai ma.")
            return

        encrypted_file = os.path.abspath(encrypted_file)
        decrypted_file = os.path.abspath(decrypted_file)
        self.encrypted_entry.delete(0, tk.END)
        self.encrypted_entry.insert(0, encrypted_file)
        self.decrypted_entry.delete(0, tk.END)
        self.decrypted_entry.insert(0, decrypted_file)
        self.refresh_path_preview()

        self.lock_controls_for_listening()
        self.status_label.config(text=f"Dang lang nghe tai {host}:{port}...", fg="orange")
        self.log(f"Bat dau lang nghe tai {host}:{port}.")
        self.log(f"File ma hoa se luu tai: {encrypted_file}")
        self.log(f"File giai ma se luu tai: {decrypted_file}")
        self.is_listening = True

        threading.Thread(
            target=self.receive_and_decrypt,
            args=(host, port, key_bytes, encrypted_file, decrypted_file),
            daemon=True,
        ).start()

    def receive_and_decrypt(self, host, port, key_bytes, encrypted_file, decrypted_file):
        conn = None
        try:
            encrypted_dir = os.path.dirname(encrypted_file)
            decrypted_dir = os.path.dirname(decrypted_file)
            if encrypted_dir:
                os.makedirs(encrypted_dir, exist_ok=True)
            if decrypted_dir:
                os.makedirs(decrypted_dir, exist_ok=True)

            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((host, port))
            self.server_socket.listen(1)

            self.root.after(0, lambda: self.status_label.config(text="Dang cho ket noi tu may gui...", fg="orange"))
            self.root.after(0, lambda: self.log("Dang cho ket noi tu may gui..."))

            conn, addr = self.server_socket.accept()
            self.root.after(0, lambda: self.status_label.config(text=f"Da ket noi tu {addr[0]}. Dang nhan file...", fg="orange"))
            self.root.after(0, lambda: self.log(f"Da ket noi tu {addr[0]}:{addr[1]}."))

            total_bytes = 0
            with open(encrypted_file, "wb") as f:
                while True:
                    data = conn.recv(4096)
                    if not data:
                        break
                    f.write(data)
                    total_bytes += len(data)

            self.root.after(0, lambda: self.log(f"Nhan xong {total_bytes} bytes du lieu ma hoa."))

            decrypt_ok = decrypt_file(encrypted_file, decrypted_file, key_bytes)
            if not decrypt_ok:
                self.root.after(0, lambda: self.on_receive_error("Giai ma that bai. Kiem tra khoa DES va noi dung file ma hoa."))
                return

            self.root.after(0, lambda: self.log("Giai ma thanh cong."))

            # Lấy thời gian giải mã từ lịch sử để hiển thị trên GUI
            history = view_history(limit=1)
            if history:
                last_entry = history[-1]
                if last_entry.get("action") == "decrypt" and last_entry.get("status") == "success":
                    duration = last_entry.get("duration_seconds")
                    if duration is not None:
                        self.root.after(0, lambda d=duration: self.log(f"Thoi gian giai ma: {d:.3f}s"))

            self.root.after(
                0,
                lambda: self.on_receive_success(
                    encrypted_file,
                    decrypted_file,
                ),
            )
        except OSError as e:
            if self.is_listening:
                self.root.after(0, lambda: self.on_receive_error(f"Loi ket noi: {e}"))
        except Exception as e:
            self.root.after(0, lambda: self.on_receive_error(f"Loi he thong: {e}"))
        finally:
            if conn:
                conn.close()
            self.close_server_socket()

    def on_receive_success(self, encrypted_file, decrypted_file):
        self.status_label.config(text="Nhan va giai ma thanh cong!", fg="green")
        self.log(f"Hoan tat. File ma hoa: {encrypted_file}")
        self.log(f"Hoan tat. File giai ma: {decrypted_file}")
        messagebox.showinfo(
            "Thanh cong",
            f"Da luu file ma hoa tai:\n{encrypted_file}\n\nDa giai ma ra:\n{decrypted_file}",
        )
        self.unlock_controls_after_listening()

    def on_receive_error(self, msg):
        self.status_label.config(text="Nhan that bai!", fg="red")
        self.log(f"Nhan that bai: {msg}")
        messagebox.showerror("Loi Nhan Du Lieu", msg)
        self.unlock_controls_after_listening()

    def stop_listen(self):
        if not self.is_listening:
            return

        self.is_listening = False
        self.close_server_socket()
        self.status_label.config(text="Da dung lang nghe.", fg="blue")
        self.log("Da dung lang nghe.")
        self.unlock_controls_after_listening()

    def lock_controls_for_listening(self):
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.host_entry.config(state=tk.DISABLED)
        self.port_entry.config(state=tk.DISABLED)
        self.key_entry.config(state=tk.DISABLED)
        self.encrypted_entry.config(state=tk.DISABLED)
        self.decrypted_entry.config(state=tk.DISABLED)

    def unlock_controls_after_listening(self):
        self.is_listening = False
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.host_entry.config(state=tk.NORMAL)
        self.port_entry.config(state=tk.NORMAL)
        self.key_entry.config(state=tk.NORMAL)
        self.encrypted_entry.config(state=tk.NORMAL)
        self.decrypted_entry.config(state=tk.NORMAL)

    def close_server_socket(self):
        if self.server_socket:
            try:
                self.server_socket.close()
            except OSError:
                pass
            self.server_socket = None

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

    def on_close(self):
        self.stop_listen()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ReceiverApp(root)
    root.mainloop()
