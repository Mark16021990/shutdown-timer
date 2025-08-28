import customtkinter as ctk
import subprocess
import threading
import time
from datetime import datetime, timedelta
import os
from PIL import Image, ImageTk
import sys

class AdvancedShutdownTimer(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Настройка окна
        self.title("⚡ Таймер выключения PRO")
        self.geometry("600x700")
        self.resizable(True, True)
        self.minsize(500, 600)
        
        # Настройка темы
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        # Переменные
        self.time_left = 0
        self.timer_running = False
        self.scheduled_time = None
        
        # Создание виджетов
        self.create_widgets()
        self.setup_layout()
        
    def create_widgets(self):
        # ===== ЗАГОЛОВОК =====
        self.header_frame = ctk.CTkFrame(self, corner_radius=15)
        self.title_label = ctk.CTkLabel(self.header_frame, 
                                      text="⚡ ТАЙМЕР ВЫКЛЮЧЕНИЯ", 
                                      font=ctk.CTkFont(size=24, weight="bold", family="Arial"))
        self.subtitle_label = ctk.CTkLabel(self.header_frame, 
                                         text="Умное управление питанием вашего компьютера",
                                         font=ctk.CTkFont(size=14),
                                         text_color="gray")
        
        # ===== БЫСТРЫЕ ДЕЙСТВИЯ =====
        self.quick_actions_frame = ctk.CTkFrame(self, corner_radius=15)
        self.quick_actions_label = ctk.CTkLabel(self.quick_actions_frame, 
                                              text="⚡ Быстрые действия",
                                              font=ctk.CTkFont(size=16, weight="bold"))
        
        # Кнопки быстрых действий
        self.shutdown_now_btn = ctk.CTkButton(self.quick_actions_frame, 
                                            text="🚀 Выключить сейчас", 
                                            command=self.shutdown_now,
                                            fg_color="#E74C3C",
                                            hover_color="#C0392B")
        
        self.restart_btn = ctk.CTkButton(self.quick_actions_frame, 
                                       text="🔄 Перезагрузить", 
                                       command=self.restart_computer,
                                       fg_color="#3498DB",
                                       hover_color="#2980B9")
        
        self.sleep_btn = ctk.CTkButton(self.quick_actions_frame, 
                                     text="💤 Сон", 
                                     command=self.sleep_computer,
                                     fg_color="#9B59B6",
                                     hover_color="#8E44AD")
        
        # ===== ТАЙМЕР =====
        self.timer_frame = ctk.CTkFrame(self, corner_radius=15)
        self.timer_label = ctk.CTkLabel(self.timer_frame, 
                                      text="⏰ Установите время",
                                      font=ctk.CTkFont(size=16, weight="bold"))
        
        # Поля ввода времени
        self.time_input_frame = ctk.CTkFrame(self.timer_frame)
        
        self.hours_label = ctk.CTkLabel(self.time_input_frame, text="Часы:")
        self.hours_entry = ctk.CTkEntry(self.time_input_frame, width=60, placeholder_text="0")
        self.hours_entry.insert(0, "0")
        
        self.minutes_label = ctk.CTkLabel(self.time_input_frame, text="Минуты:")
        self.minutes_entry = ctk.CTkEntry(self.time_input_frame, width=60, placeholder_text="0")
        self.minutes_entry.insert(0, "0")
        
        self.seconds_label = ctk.CTkLabel(self.time_input_frame, text="Секунды:")
        self.seconds_entry = ctk.CTkEntry(self.time_input_frame, width=60, placeholder_text="0")
        self.seconds_entry.insert(0, "0")
        
        # Кнопки управления таймером
        self.control_buttons_frame = ctk.CTkFrame(self.timer_frame)
        
        self.start_button = ctk.CTkButton(self.control_buttons_frame, 
                                        text="▶️ Старт", 
                                        command=self.start_timer,
                                        fg_color="#27AE60",
                                        hover_color="#229954")
        
        self.stop_button = ctk.CTkButton(self.control_buttons_frame, 
                                       text="⏹️ Стоп", 
                                       command=self.stop_timer,
                                       fg_color="#E74C3C",
                                       hover_color="#C0392B",
                                       state="disabled")
        
        # Дисплей таймера
        self.timer_display = ctk.CTkLabel(self.timer_frame, 
                                        text="00:00:00", 
                                        font=ctk.CTkFont(size=48, weight="bold"),
                                        text_color="#2ECC71")
        
        # ===== РАСПИСАНИЕ =====
        self.schedule_frame = ctk.CTkFrame(self, corner_radius=15)
        self.schedule_label = ctk.CTkLabel(self.schedule_frame, 
                                         text="📅 Запланировать на время",
                                         font=ctk.CTkFont(size=16, weight="bold"))
        
        self.datetime_frame = ctk.CTkFrame(self.schedule_frame)
        
        self.date_label = ctk.CTkLabel(self.datetime_frame, text="Дата:")
        self.date_entry = ctk.CTkEntry(self.datetime_frame, width=100, placeholder_text="ГГГГ-ММ-ДД")
        
        self.time_label = ctk.CTkLabel(self.datetime_frame, text="Время:")
        self.time_entry = ctk.CTkEntry(self.datetime_frame, width=100, placeholder_text="ЧЧ:ММ")
        
        self.schedule_button = ctk.CTkButton(self.schedule_frame, 
                                           text="📅 Запланировать", 
                                           command=self.schedule_shutdown)
        
        # ===== СТАТУС И ЛОГИ =====
        self.status_frame = ctk.CTkFrame(self, corner_radius=15)
        self.status_label = ctk.CTkLabel(self.status_frame, 
                                       text="📊 Статус: Готов к работе",
                                       font=ctk.CTkFont(size=14))
        
        self.log_text = ctk.CTkTextbox(self.status_frame, height=100, width=400)
        self.log_text.insert("1.0", "=== Лог событий ===\n")
        self.log_text.configure(state="disabled")
        
        # ===== ПРОГРЕСС БАР =====
        self.progress_frame = ctk.CTkFrame(self, corner_radius=15)
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, width=400)
        self.progress_bar.set(0)
        self.progress_label = ctk.CTkLabel(self.progress_frame, text="0%")
        
    def setup_layout(self):
        # Заголовок
        self.header_frame.pack(pady=20, padx=20, fill="x")
        self.title_label.pack(pady=(15, 5))
        self.subtitle_label.pack(pady=(0, 15))
        
        # Быстрые действия
        self.quick_actions_frame.pack(pady=10, padx=20, fill="x")
        self.quick_actions_label.pack(pady=10)
        
        quick_btn_frame = ctk.CTkFrame(self.quick_actions_frame)
        quick_btn_frame.pack(pady=10)
        
        self.shutdown_now_btn.pack(side="left", padx=5, pady=5)
        self.restart_btn.pack(side="left", padx=5, pady=5)
        self.sleep_btn.pack(side="left", padx=5, pady=5)
        
        # Таймер
        self.timer_frame.pack(pady=10, padx=20, fill="x")
        self.timer_label.pack(pady=10)
        
        # Поля ввода времени
        self.time_input_frame.pack(pady=10)
        self.hours_label.grid(row=0, column=0, padx=5, pady=5)
        self.hours_entry.grid(row=0, column=1, padx=5, pady=5)
        self.minutes_label.grid(row=0, column=2, padx=5, pady=5)
        self.minutes_entry.grid(row=0, column=3, padx=5, pady=5)
        self.seconds_label.grid(row=0, column=4, padx=5, pady=5)
        self.seconds_entry.grid(row=0, column=5, padx=5, pady=5)
        
        # Кнопки управления
        self.control_buttons_frame.pack(pady=10)
        self.start_button.pack(side="left", padx=10)
        self.stop_button.pack(side="left", padx=10)
        
        # Дисплей таймера
        self.timer_display.pack(pady=20)
        
        # Расписание
        self.schedule_frame.pack(pady=10, padx=20, fill="x")
        self.schedule_label.pack(pady=10)
        
        self.datetime_frame.pack(pady=10)
        self.date_label.grid(row=0, column=0, padx=5, pady=5)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.time_label.grid(row=0, column=2, padx=5, pady=5)
        self.time_entry.grid(row=0, column=3, padx=5, pady=5)
        
        self.schedule_button.pack(pady=10)
        
        # Статус и логи
        self.status_frame.pack(pady=10, padx=20, fill="both", expand=True)
        self.status_label.pack(pady=10)
        self.log_text.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Прогресс бар
        self.progress_frame.pack(pady=10, padx=20, fill="x")
        self.progress_bar.pack(pady=10)
        self.progress_label.pack(pady=5)
        
    def log_message(self, message):
        """Добавление сообщения в лог"""
        self.log_text.configure(state="normal")
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")
        
    def update_status(self, message, color="white"):
        """Обновление статуса"""
        self.status_label.configure(text=f"📊 Статус: {message}", text_color=color)
        
    def start_timer(self):
        try:
            hours = int(self.hours_entry.get() or 0)
            minutes = int(self.minutes_entry.get() or 0)
            seconds = int(self.seconds_entry.get() or 0)
            
            total_seconds = hours * 3600 + minutes * 60 + seconds
            
            if total_seconds <= 0:
                self.update_status("Введите время больше 0", "red")
                return
                
            self.time_left = total_seconds
            self.total_time = total_seconds
            self.timer_running = True
            
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            self.update_status("Таймер запущен", "green")
            self.log_message(f"Таймер запущен: {hours}ч {minutes}м {seconds}с")
            
            # Запуск таймера
            self.timer_thread = threading.Thread(target=self.run_timer)
            self.timer_thread.daemon = True
            self.timer_thread.start()
            
        except ValueError:
            self.update_status("Ошибка: введите числа", "red")
            
    def stop_timer(self):
        self.timer_running = False
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.update_status("Таймер остановлен", "orange")
        self.log_message("Таймер остановлен")
        self.progress_bar.set(0)
        self.progress_label.configure(text="0%")
        
    def run_timer(self):
        while self.time_left > 0 and self.timer_running:
            hours = self.time_left // 3600
            minutes = (self.time_left % 3600) // 60
            seconds = self.time_left % 60
            
            # Обновление дисплея
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            self.timer_display.configure(text=time_str)
            
            # Обновление прогресс бара
            progress = 1 - (self.time_left / self.total_time)
            self.progress_bar.set(progress)
            self.progress_label.configure(text=f"{int(progress * 100)}%")
            
            time.sleep(1)
            self.time_left -= 1
        
        if self.time_left <= 0 and self.timer_running:
            self.log_message("Время вышло! Выключаем компьютер...")
            self.shutdown_computer()
            
    def shutdown_computer(self):
        try:
            subprocess.run(["shutdown", "/s", "/t", "0"])
            self.log_message("Компьютер выключается...")
        except Exception as e:
            self.log_message(f"Ошибка выключения: {e}")
            
    def shutdown_now(self):
        """Немедленное выключение"""
        self.log_message("Немедленное выключение...")
        try:
            subprocess.run(["shutdown", "/s", "/t", "1"])
        except Exception as e:
            self.log_message(f"Ошибка: {e}")
            
    def restart_computer(self):
        """Перезагрузка компьютера"""
        self.log_message("Перезагрузка компьютера...")
        try:
            subprocess.run(["shutdown", "/r", "/t", "1"])
        except Exception as e:
            self.log_message(f"Ошибка: {e}")
            
    def sleep_computer(self):
        """Режим сна"""
        self.log_message("Переход в режим сна...")
        try:
            subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"])
        except Exception as e:
            self.log_message(f"Ошибка: {e}")
            
    def schedule_shutdown(self):
        """Запланировать выключение на определенное время"""
        try:
            date_str = self.date_entry.get()
            time_str = self.time_entry.get()
            
            if not date_str or not time_str:
                self.update_status("Введите дату и время", "red")
                return
                
            scheduled_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            now = datetime.now()
            
            if scheduled_datetime <= now:
                self.update_status("Введите будущее время", "red")
                return
                
            delta = scheduled_datetime - now
            seconds = int(delta.total_seconds())
            
            subprocess.run(["shutdown", "/s", "/t", str(seconds)])
            
            self.log_message(f"Выключение запланировано на {scheduled_datetime}")
            self.update_status("Выключение запланировано", "green")
            
        except ValueError:
            self.update_status("Неверный формат даты/времени", "red")
        except Exception as e:
            self.log_message(f"Ошибка планирования: {e}")
            
    def on_closing(self):
        """Обработчик закрытия окна"""
        if self.timer_running:
            self.stop_timer()
        self.destroy()

if __name__ == "__main__":
    app = AdvancedShutdownTimer()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()