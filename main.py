import customtkinter as ctk
import subprocess
import threading
import time
from datetime import datetime, timedelta
import os
import sys
import math
from PIL import Image, ImageTk
import json
from CTkMessagebox import CTkMessagebox

class AdvancedShutdownTimer(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Настройка окна
        self.title("⚡ Power Control Pro")
        self.geometry("800x900")
        self.resizable(True, True)
        self.minsize(700, 800)
        
        # Настройка темы
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("assets/theme.json")
        
        # Переменные
        self.time_left = 0
        self.timer_running = False
        self.scheduled_time = None
        self.animation_running = False
        
        # Загрузка изображений
        self.load_images()
        
        # Создание виджетов
        self.create_widgets()
        self.setup_layout()
        
        # Запуск анимации
        self.animate_clock()
        
    def load_images(self):
        """Загрузка изображений для интерфейса"""
        try:
            # Создаем папку assets если её нет
            if not os.path.exists("assets"):
                os.makedirs("assets")
                
            # Иконки (можно заменить на свои)
            self.icons = {
                "shutdown": self.create_icon("🔌", "#E74C3C"),
                "restart": self.create_icon("🔄", "#3498DB"),
                "sleep": self.create_icon("💤", "#9B59B6"),
                "timer": self.create_icon("⏰", "#F39C12"),
                "schedule": self.create_icon("📅", "#2ECC71"),
                "settings": self.create_icon("⚙️", "#95A5A6"),
            }
            
        except Exception as e:
            print(f"Ошибка загрузки изображений: {e}")
    
    def create_icon(self, emoji, color):
        """Создание иконки из эмодзи"""
        from PIL import Image, ImageDraw, ImageFont
        try:
            # Создаем изображение
            img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
            d = ImageDraw.Draw(img)
            
            # Рисуем круг
            d.ellipse([0, 0, 64, 64], fill=color)
            
            # Добавляем эмодзи
            try:
                font = ImageFont.truetype("seguiemj.ttf", 32)
            except:
                font = ImageFont.load_default()
            
            d.text((16, 16), emoji, font=font, embedded_color=True)
            
            return ctk.CTkImage(light_image=img, dark_image=img, size=(64, 64))
            
        except Exception as e:
            print(f"Ошибка создания иконки: {e}")
            return None
    
    def create_widgets(self):
        # ===== ВКЛАДКИ =====
        self.tabview = ctk.CTkTabview(self)
        self.tab1 = self.tabview.add("⏰ Таймер")
        self.tab2 = self.tabview.add("📅 Расписание")
        self.tab3 = self.tabview.add("⚡ Действия")
        self.tab4 = self.tabview.add("📊 Статистика")
        self.tab5 = self.tabview.add("⚙️ Настройки")
        
        # ===== ВКЛАДКА ТАЙМЕР =====
        # Анимированный циферблат
        self.clock_frame = ctk.CTkFrame(self.tab1, height=300)
        self.clock_canvas = ctk.CTkCanvas(self.clock_frame, bg="#2B2B2B", highlightthickness=0)
        self.clock_canvas.pack(fill="both", expand=True)
        
        # Поля ввода времени
        self.time_input_frame = ctk.CTkFrame(self.tab1)
        
        self.create_time_input(self.time_input_frame, "Часы", 0, 23, "hours")
        self.create_time_input(self.time_input_frame, "Минуты", 0, 59, "minutes")
        self.create_time_input(self.time_input_frame, "Секунды", 0, 59, "seconds")
        
        # Кнопки управления
        self.control_frame = ctk.CTkFrame(self.tab1)
        self.start_btn = ctk.CTkButton(self.control_frame, text="▶️ Запуск", 
                                     command=self.start_timer, fg_color="#27AE60")
        self.stop_btn = ctk.CTkButton(self.control_frame, text="⏹️ Стоп", 
                                    command=self.stop_timer, fg_color="#E74C3C", state="disabled")
        self.pause_btn = ctk.CTkButton(self.control_frame, text="⏸️ Пауза", 
                                     command=self.pause_timer, fg_color="#F39C12", state="disabled")
        
        # ===== ВКЛАДКА РАСПИСАНИЕ =====
        self.calendar_frame = ctk.CTkFrame(self.tab2)
        
        # Выбор даты и времени
        self.date_picker = ctk.CTkEntry(self.calendar_frame, placeholder_text="Выберите дату")
        self.time_picker = ctk.CTkEntry(self.calendar_frame, placeholder_text="Выберите время")
        
        # Предустановки
        self.presets_frame = ctk.CTkFrame(self.tab2)
        self.create_presets()
        
        # ===== ВКЛАДКА ДЕЙСТВИЯ =====
        self.actions_grid = ctk.CTkFrame(self.tab3)
        
        # Создаем кнопки действий
        actions = [
            ("🔌 Выключить", self.shutdown_now, "#E74C3C"),
            ("🔄 Перезагрузить", self.restart_computer, "#3498DB"),
            ("💤 Сон", self.sleep_computer, "#9B59B6"),
            ("⚡ Гибернация", self.hibernate_computer, "#8E44AD"),
            ("🔒 Выход", self.logoff_computer, "#F39C12"),
            ("🚫 Отмена", self.cancel_shutdown, "#95A5A6")
        ]
        
        for i, (text, command, color) in enumerate(actions):
            btn = ctk.CTkButton(self.actions_grid, text=text, command=command, 
                              fg_color=color, height=80, width=180,
                              font=ctk.CTkFont(size=16, weight="bold"))
            btn.grid(row=i//2, column=i%2, padx=10, pady=10)
        
        # ===== ВКЛАДКА СТАТИСТИКА =====
        self.stats_frame = ctk.CTkFrame(self.tab4)
        
        # График статистики
        self.stats_canvas = ctk.CTkCanvas(self.stats_frame, bg="#2B2B2B", height=300)
        self.stats_canvas.pack(fill="both", expand=True, padx=20, pady=20)
        
        # ===== ВКЛАДКА НАСТРОЙКИ =====
        self.settings_frame = ctk.CTkFrame(self.tab5)
        
        # Настройки темы
        self.theme_label = ctk.CTkLabel(self.settings_frame, text="Тема:")
        self.theme_var = ctk.StringVar(value="Dark")
        self.theme_option = ctk.CTkOptionMenu(self.settings_frame, values=["Dark", "Light", "System"],
                                            variable=self.theme_var, command=self.change_theme)
        
        # Настройки уведомлений
        self.notify_var = ctk.BooleanVar(value=True)
        self.notify_check = ctk.CTkCheckBox(self.settings_frame, text="Включить уведомления",
                                          variable=self.notify_var)
        
        # Настройки звука
        self.sound_var = ctk.BooleanVar(value=True)
        self.sound_check = ctk.CTkCheckBox(self.settings_frame, text="Включить звук",
                                         variable=self.sound_var)
        
        # ===== СТАТУС БАР =====
        self.status_bar = ctk.CTkFrame(self, height=30)
        self.status_label = ctk.CTkLabel(self.status_bar, text="Готов к работе")
        self.progress_bar = ctk.CTkProgressBar(self.status_bar, width=200, height=10)
        
    def create_time_input(self, parent, label, min_val, max_val, var_name):
        """Создание поля ввода времени"""
        frame = ctk.CTkFrame(parent)
        lbl = ctk.CTkLabel(frame, text=label)
        entry = ctk.CTkEntry(frame, width=60)
        setattr(self, f"{var_name}_entry", entry)
        
        # Кнопки +/-
        btn_frame = ctk.CTkFrame(frame)
        plus_btn = ctk.CTkButton(btn_frame, text="+", width=30, 
                               command=lambda: self.adjust_time(var_name, 1, max_val))
        minus_btn = ctk.CTkButton(btn_frame, text="-", width=30,
                                command=lambda: self.adjust_time(var_name, -1, min_val))
        
        lbl.pack()
        entry.pack(pady=5)
        plus_btn.pack(side="left")
        minus_btn.pack(side="right")
        btn_frame.pack()
        frame.pack(side="left", padx=10)
        
    def create_presets(self):
        """Создание предустановок времени"""
        presets = [
            ("5 минут", 5),
            ("15 минут", 15),
            ("30 минут", 30),
            ("1 час", 60),
            ("2 часа", 120),
            ("4 часа", 240)
        ]
        
        for text, minutes in presets:
            btn = ctk.CTkButton(self.presets_frame, text=text,
                              command=lambda m=minutes: self.set_preset_time(m))
            btn.pack(side="left", padx=5)
    
    def setup_layout(self):
        # Размещение вкладок
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Вкладка таймер
        self.clock_frame.pack(fill="x", padx=20, pady=20)
        self.time_input_frame.pack(pady=20)
        self.control_frame.pack(pady=20)
        self.start_btn.pack(side="left", padx=10)
        self.stop_btn.pack(side="left", padx=10)
        self.pause_btn.pack(side="left", padx=10)
        
        # Вкладка расписание
        self.calendar_frame.pack(pady=20)
        self.date_picker.pack(pady=10)
        self.time_picker.pack(pady=10)
        self.presets_frame.pack(pady=20)
        
        # Вкладка действия
        self.actions_grid.pack(pady=20)
        
        # Вкладка статистика
        self.stats_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Вкладка настройки
        self.settings_frame.pack(pady=20)
        self.theme_label.pack(pady=10)
        self.theme_option.pack(pady=10)
        self.notify_check.pack(pady=10)
        self.sound_check.pack(pady=10)
        
        # Статус бар
        self.status_bar.pack(fill="x", side="bottom")
        self.status_label.pack(side="left", padx=10)
        self.progress_bar.pack(side="right", padx=10)
        self.progress_bar.set(0)
    
    def animate_clock(self):
        """Анимация циферблата"""
        if self.animation_running:
            self.after_cancel(self.animation_id)
        
        self.animation_running = True
        self.draw_clock()
        self.animation_id = self.after(1000, self.animate_clock)
    
    def draw_clock(self):
        """Отрисовка анимированного циферблата"""
        try:
            width = self.clock_canvas.winfo_width()
            height = self.clock_canvas.winfo_height()
            
            if width <= 1 or height <= 1:
                return
                
            self.clock_canvas.delete("all")
            
            # Рисуем циферблат
            center_x, center_y = width // 2, height // 2
            radius = min(center_x, center_y) - 20
            
            # Внешний круг
            self.clock_canvas.create_oval(center_x - radius, center_y - radius,
                                        center_x + radius, center_y + radius,
                                        outline="#3498DB", width=3)
            
            # Если таймер запущен, рисуем прогресс
            if self.timer_running and self.total_time > 0:
                progress = 1 - (self.time_left / self.total_time)
                angle = progress * 360
                
                # Рисуем дугу прогресса
                self.clock_canvas.create_arc(center_x - radius, center_y - radius,
                                           center_x + radius, center_y + radius,
                                           start=90, extent=-angle, outline="#2ECC71", width=5,
                                           style="arc")
            
            # Рисуем цифры
            for i in range(12):
                angle = math.radians(i * 30 - 90)
                x = center_x + (radius - 20) * math.cos(angle)
                y = center_y + (radius - 20) * math.sin(angle)
                self.clock_canvas.create_text(x, y, text=str(i if i > 0 else 12), 
                                            fill="white", font=("Arial", 12, "bold"))
            
            # Отображаем оставшееся время
            if self.timer_running:
                hours = self.time_left // 3600
                minutes = (self.time_left % 3600) // 60
                seconds = self.time_left % 60
                
                time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                self.clock_canvas.create_text(center_x, center_y, text=time_str,
                                            fill="white", font=("Arial", 24, "bold"))
                
        except Exception as e:
            print(f"Ошибка отрисовки часов: {e}")
    
    def adjust_time(self, field, delta, limit):
        """Изменение значения времени"""
        entry = getattr(self, f"{field}_entry")
        try:
            value = int(entry.get() or 0) + delta
            value = max(0, min(limit, value))
            entry.delete(0, "end")
            entry.insert(0, str(value))
        except ValueError:
            entry.delete(0, "end")
            entry.insert(0, "0")
    
    def set_preset_time(self, minutes):
        """Установка предустановленного времени"""
        hours = minutes // 60
        minutes = minutes % 60
        
        self.hours_entry.delete(0, "end")
        self.hours_entry.insert(0, str(hours))
        
        self.minutes_entry.delete(0, "end")
        self.minutes_entry.insert(0, str(minutes))
        
        self.seconds_entry.delete(0, "end")
        self.seconds_entry.insert(0, "0")
    
    def start_timer(self):
        try:
            hours = int(self.hours_entry.get() or 0)
            minutes = int(self.minutes_entry.get() or 0)
            seconds = int(self.seconds_entry.get() or 0)
            
            total_seconds = hours * 3600 + minutes * 60 + seconds
            
            if total_seconds <= 0:
                self.show_message("Ошибка", "Введите время больше 0")
                return
                
            self.time_left = total_seconds
            self.total_time = total_seconds
            self.timer_running = True
            
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            self.pause_btn.configure(state="normal")
            self.update_status("Таймер запущен", "green")
            
            # Запуск таймера
            self.timer_thread = threading.Thread(target=self.run_timer)
            self.timer_thread.daemon = True
            self.timer_thread.start()
            
        except ValueError:
            self.show_message("Ошибка", "Введите корректные числа")
    
    def pause_timer(self):
        """Пауза/возобновление таймера"""
        if self.timer_running:
            self.timer_running = False
            self.pause_btn.configure(text="▶️ Возобновить")
            self.update_status("Таймер на паузе", "orange")
        else:
            self.timer_running = True
            self.pause_btn.configure(text="⏸️ Пауза")
            self.update_status("Таймер возобновлен", "green")
            
            # Запуск таймера
            self.timer_thread = threading.Thread(target=self.run_timer)
            self.timer_thread.daemon = True
            self.timer_thread.start()
    
    def stop_timer(self):
        self.timer_running = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.pause_btn.configure(state="disabled")
        self.pause_btn.configure(text="⏸️ Пауза")
        self.update_status("Таймер остановлен", "orange")
        self.progress_bar.set(0)
    
    def run_timer(self):
        while self.time_left > 0 and self.timer_running:
            # Обновление прогресс бара
            progress = 1 - (self.time_left / self.total_time)
            self.progress_bar.set(progress)
            
            time.sleep(1)
            if self.timer_running:
                self.time_left -= 1
        
        if self.time_left <= 0 and self.timer_running:
            self.shutdown_computer()
    
    def shutdown_computer(self):
        try:
            self.update_status("Выключение компьютера...", "red")
            subprocess.run(["shutdown", "/s", "/t", "0"])
        except Exception as e:
            self.show_message("Ошибка", f"Не удалось выключить компьютер: {e}")
    
    def restart_computer(self):
        try:
            self.update_status("Перезагрузка компьютера...", "blue")
            subprocess.run(["shutdown", "/r", "/t", "0"])
        except Exception as e:
            self.show_message("Ошибка", f"Не удалось перезагрузить компьютер: {e}")
    
    def sleep_computer(self):
        try:
            self.update_status("Переход в режим сна...", "purple")
            subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"])
        except Exception as e:
            self.show_message("Ошибка", f"Не удалось перевести компьютер в сон: {e}")
    
    def hibernate_computer(self):
        try:
            self.update_status("Переход в режим гибернации...", "purple")
            subprocess.run(["shutdown", "/h"])
        except Exception as e:
            self.show_message("Ошибка", f"Не удалось перевести компьютер в гибернацию: {e}")
    
    def logoff_computer(self):
        try:
            self.update_status("Выход из системы...", "orange")
            subprocess.run(["shutdown", "/l"])
        except Exception as e:
            self.show_message("Ошибка", f"Не удалось выйти из системы: {e}")
    
    def cancel_shutdown(self):
        try:
            subprocess.run(["shutdown", "/a"])
            self.update_status("Выключение отменено", "green")
            self.show_message("Успех", "Запланированное выключение отменено")
        except Exception as e:
            self.show_message("Ошибка", f"Не удалось отменить выключение: {e}")
    
    def update_status(self, message, color="white"):
        """Обновление статусной строки"""
        self.status_label.configure(text=message, text_color=color)
    
    def show_message(self, title, message):
        """Показать сообщение"""
        CTkMessagebox(title=title, message=message)
    
    def change_theme(self, choice):
        """Изменение темы приложения"""
        ctk.set_appearance_mode(choice)
    
    def on_closing(self):
        """Обработчик закрытия окна"""
        self.animation_running = False
        if self.timer_running:
            self.stop_timer()
        self.destroy()

if __name__ == "__main__":
    app = AdvancedShutdownTimer()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()