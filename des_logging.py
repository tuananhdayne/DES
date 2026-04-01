import os
import json
from datetime import datetime

LOG_FILE = "des_operations.log"
LOG_JSON = "des_history.json"

def init_logging():
    """Khởi tạo file log"""
    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, 'w').close()
    if not os.path.exists(LOG_JSON):
        with open(LOG_JSON, 'w') as f:
            json.dump([], f)

def log_message(message: str):
    """Ghi thông báo vào log"""
    init_logging()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}"
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_line + '\n')
    
    print(log_line)

def log_operation(action: str, filename: str, mode: str, file_size: int, 
                  duration: float, status: str = "success", details: str = ""):
    """Ghi thông tin vận hành chi tiết vào JSON"""
    init_logging()
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,  # 'encrypt' hoặc 'decrypt'
        "filename": filename,
        "mode": mode,  # 'CBC' hoặc 'ECB'
        "file_size_bytes": file_size,
        "duration_seconds": round(duration, 3),
        "status": status,
        "details": details
    }
    
    # Đọc history cũ
    history = []
    try:
        with open(LOG_JSON, 'r', encoding='utf-8') as f:
            history = json.load(f)
    except:
        history = []
    
    # Thêm entry mới
    history.append(log_entry)
    
    # Ghi lại
    with open(LOG_JSON, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def get_statistics():
    """Lấy thống kê"""
    init_logging()
    
    try:
        with open(LOG_JSON, 'r', encoding='utf-8') as f:
            history = json.load(f)
    except:
        history = []
    
    encrypts = [h for h in history if h['action'] == 'encrypt']
    decrypts = [h for h in history if h['action'] == 'decrypt']
    successful = [h for h in history if h['status'] == 'success']
    
    total_size = sum(h.get('file_size_bytes', 0) for h in history)
    total_time = sum(h.get('duration_seconds', 0) for h in history)
    
    return {
        "total_operations": len(history),
        "encryptions": len(encrypts),
        "decryptions": len(decrypts),
        "successful": len(successful),
        "failed": len(history) - len(successful),
        "total_data_mb": round(total_size / (1024*1024), 2),
        "total_time_seconds": round(total_time, 2)
    }

def view_history(limit=20):
    """Xem lịch sử"""
    init_logging()
    
    try:
        with open(LOG_JSON, 'r', encoding='utf-8') as f:
            history = json.load(f)
    except:
        history = []
    
    return history[-limit:]
