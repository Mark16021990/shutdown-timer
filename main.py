import customtkinter as ctk
import subprocess
import threading
import time
import os
import sys

# Функция для получения правильного пути к ресурсам
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class SimpleShutdownTimer(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Настройка окна
        self.title("⚡ Таймер выключения")
        self.geometry("640x480")
        self.resizable(False, False)
        
        # Настройка темы
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")  # Используем встроенную тему
        
        # Переменные
        self.time_left = 0
        self.timer_running = False
        
        # Создание виджетов
        self.create_widgets()
        
    def create_widgets(self):
        # Основной фрейм
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Заголовок
        title_label = ctk.CTkLabel(main_frame, text="Таймер выключения", 
                                 font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=10)
        
        # Поля ввода времени
        time_frame = ctk.CTkFrame(main_frame)
        time_frame.pack(pady=10)
        
        ctk.CTkLabel(time_frame, text="Часы:").grid(row=0, column=0, padx=5)
        self.hours_entry = ctk.CTkEntry(time_frame, width=50)
        self.hours_entry.grid(row=0, column=1, padx=5)
        self.hours_entry.insert(0, "0")
        
        ctk.CTkLabel(time_frame, text="Минуты:").grid(row=0, column=2, padx=5)
        self.minutes_entry = ctk.CTkEntry(time_frame, width=50)
        self.minutes_entry.grid(row=0, column=3, padx=5)
        self.minutes_entry.insert(0, "0")
        
        ctk.CTkLabel(time_frame, text="Секунды:").grid(row=0, column=4, padx=5)
        self.seconds_entry = ctk.CTkEntry(time_frame, width=50)
        self.seconds_entry.grid(row=0, column=5, padx=5)
        self.seconds_entry.insert(0, "0")
        
        # Кнопки управления
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(pady=10)
        
        self.start_button = ctk.CTkButton(button_frame, text="Старт", 
                                        command=self.start_timer)
        self.start_button.pack(side="left", padx=5)
        
        self.stop_button = ctk.CTkButton(button_frame, text="Стоп", 
                                       command=self.stop_timer, state="disabled")
        self.stop_button.pack(side="left", padx=5)
        
        # Дисплей таймера
        self.timer_label = ctk.CTkLabel(main_frame, text="00:00:00", 
                                      font=ctk.CTkFont(size=24))
        self.timer_label.pack(pady=10)
        
        # Статус
        self.status_label = ctk.CTkLabel(main_frame, text="Готов к работе")
        self.status_label.pack(pady=5)
        
        # Быстрые действия
        action_frame = ctk.CTkFrame(main_frame)
        action_frame.pack(pady=10)
        
        ctk.CTkButton(action_frame, text="Выключить сейчас", 
                     command=self.shutdown_now).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="Перезагрузить", 
                     command=self.restart_computer).pack(side="left", padx=5)
    
    def start_timer(self):
        try:
            hours = int(self.hours_entry.get() or 0)
            minutes = int(self.minutes_entry.get() or 0)
            seconds = int(self.seconds_entry.get() or 0)
            
            total_seconds = hours * 3600 + minutes * 60 + seconds
            
            if total_seconds <= 0:
                self.status_label.configure(text="Введите время больше 0")
                return
                
            self.time_left = total_seconds
            self.timer_running = True
            
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            self.status_label.configure(text="Таймер запущен")
            
            # Запуск таймера
            self.timer_thread = threading.Thread(target=self.run_timer)
            self.timer_thread.daemon = True
            self.timer_thread.start()
            
        except ValueError:
            self.status_label.configure(text="Ошибка: введите числа")
    
    def stop_timer(self):
        self.timer_running = False
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.status_label.configure(text="Таймер остановлен")
    
    def run_timer(self):
        while self.time_left > 0 and self.timer_running:
            hours = self.time_left // 3600
            minutes = (self.time_left % 3600) // 60
            seconds = self.time_left % 60
            
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            self.timer_label.configure(text=time_str)
            
            time.sleep(1)
            self.time_left -= 1
        
        if self.time_left <= 0 and self.timer_running:
            self.shutdown_computer()
    
    def shutdown_computer(self):
        try:
            subprocess.run(["shutdown", "/s", "/t", "0"])
            self.status_label.configure(text="Компьютер выключается...")
        except Exception as e:
            self.status_label.configure(text=f"Ошибка выключения: {e}")
    
    def shutdown_now(self):
        """Немедленное выключение"""
        try:
            subprocess.run(["shutdown", "/s", "/t", "1"])
            self.status_label.configure(text="Немедленное выключение...")
        except Exception as e:
            self.status_label.configure(text=f"Ошибка: {e}")
    
    def restart_computer(self):
        """Перезагрузка компьютера"""
        try:
            subprocess.run(["shutdown", "/r", "/t", "1"])
            self.status_label.configure(text="Перезагрузка компьютера...")
        except Exception as e:
            self.status_label.configure(text=f"Ошибка: {e}")
    
    def on_closing(self):
        """Обработчик закрытия окна"""
        self.timer_running = False
        self.destroy()

if __name__ == "__main__":
    app = SimpleShutdownTimer()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()