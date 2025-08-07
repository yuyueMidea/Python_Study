import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import threading
import time

class ReminderApp:
    def __init__(self, root):
        self.root = root
        root.title("桌面提示器")
        root.geometry("400x300")
        
        # 设置提醒时间
        tk.Label(root, text="提醒时间 (HH:MM:SS)").pack(pady=5)
        self.time_entry = tk.Entry(root, font=('Arial', 14))
        self.time_entry.pack(pady=5)
        self.time_entry.insert(0, datetime.now().strftime("%H:%M:%S"))
        
        # 提醒内容
        tk.Label(root, text="提醒内容").pack(pady=5)
        self.message_entry = tk.Text(root, height=5, font=('Arial', 12))
        self.message_entry.pack(pady=5, fill=tk.X, padx=10)
        self.message_entry.insert("1.0", "该做某事了！")
        
        # 设置提醒按钮
        self.set_button = tk.Button(root, text="设置提醒", command=self.set_reminder)
        self.set_button.pack(pady=10)
        
        # 状态标签
        self.status_label = tk.Label(root, text="", fg="blue")
        self.status_label.pack(pady=5)
        
        # 存储提醒线程
        self.reminder_thread = None
        self.running = False
    
    def set_reminder(self):
        # 获取用户输入
        time_str = self.time_entry.get()
        message = self.message_entry.get("1.0", tk.END).strip()
        
        try:
            # 验证时间格式
            reminder_time = datetime.strptime(time_str, "%H:%M:%S").time()
            current_time = datetime.now().time()
            
            # 计算时间差（秒）
            time_diff = (reminder_time.hour - current_time.hour) * 3600 + \
                       (reminder_time.minute - current_time.minute) * 60 + \
                       (reminder_time.second - current_time.second)
            
            if time_diff <= 0:
                messagebox.showwarning("提示", "设置的时间已过去，请设置未来的时间")
                return
            
            # 更新状态
            self.status_label.config(text=f"提醒已设置: {time_str} - {message}")
            
            # 如果已有线程在运行，先停止
            if self.reminder_thread and self.running:
                self.running = False
                self.reminder_thread.join()
            
            # 启动新线程
            self.running = True
            self.reminder_thread = threading.Thread(
                target=self.wait_and_remind,
                args=(time_diff, message),
                daemon=True
            )
            self.reminder_thread.start()
            
        except ValueError:
            messagebox.showerror("错误", "时间格式不正确，请使用 HH:MM:SS 格式")
    
    def wait_and_remind(self, seconds, message):
        # 等待指定秒数
        for _ in range(seconds):
            if not self.running:
                return
            time.sleep(1)
        
        if self.running:
            # 在主线程中显示提醒
            self.root.after(0, lambda: self.show_reminder(message))
    
    def show_reminder(self, message):
        # 创建提醒窗口
        reminder_window = tk.Toplevel(self.root)
        reminder_window.title("提醒！")
        reminder_window.geometry("300x150")
        reminder_window.attributes('-topmost', True)  # 置顶窗口
        
        # 提醒内容
        tk.Label(reminder_window, text=message, font=('Arial', 14), wraplength=250).pack(pady=20)
        
        # 确认按钮
        tk.Button(
            reminder_window, 
            text="知道了", 
            command=reminder_window.destroy,
            width=10
        ).pack(pady=10)
        
        # 播放提示音（系统默认提示音）
        reminder_window.bell()
        
        # 更新状态
        self.status_label.config(text="提醒已触发")

if __name__ == "__main__":
    root = tk.Tk()
    app = ReminderApp(root)
    root.mainloop()
