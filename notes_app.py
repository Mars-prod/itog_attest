import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
import os
from datetime import datetime

class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Password Generator")
        self.root.geometry("750x700")
        self.root.resizable(False, False)
        
        # История паролей
        self.history_file = "password_history.json"
        self.history = self.load_history()
        
        # Настройка интерфейса
        self.setup_ui()
        
        # Генерация пароля по умолчанию
        self.generate_password()
    
    def setup_ui(self):
        # Заголовок
        title_label = tk.Label(
            self.root, 
            text="Генератор случайных паролей", 
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=10)
        
        # Фрейм для настроек
        settings_frame = tk.LabelFrame(self.root, text="Настройки пароля", padx=10, pady=10)
        settings_frame.pack(padx=20, pady=10, fill="x")
        
        # Длина пароля
        length_frame = tk.Frame(settings_frame)
        length_frame.pack(fill="x", pady=5)
        
        tk.Label(length_frame, text="Длина пароля:", font=("Arial", 10)).pack(side="left")
        
        self.length_value = tk.IntVar(value=12)
        self.length_slider = tk.Scale(
            length_frame,
            from_=4,
            to=32,
            orient="horizontal",
            variable=self.length_value,
            command=self.update_length_label
        )
        self.length_slider.pack(side="left", padx=(10, 5), fill="x", expand=True)
        
        self.length_label = tk.Label(length_frame, text="12", width=4)
        self.length_label.pack(side="left")
        
        # Чекбоксы
        self.use_lowercase = tk.BooleanVar(value=True)
        self.use_uppercase = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=True)
        
        checkboxes_frame = tk.Frame(settings_frame)
        checkboxes_frame.pack(pady=10)
        
        tk.Checkbutton(
            checkboxes_frame, 
            text="Буквы (a-z)", 
            variable=self.use_lowercase,
            command=self.validate_checkboxes
        ).pack(side="left", padx=5)
        
        tk.Checkbutton(
            checkboxes_frame, 
            text="Буквы (A-Z)", 
            variable=self.use_uppercase,
            command=self.validate_checkboxes
        ).pack(side="left", padx=5)
        
        tk.Checkbutton(
            checkboxes_frame, 
            text="Цифры (0-9)", 
            variable=self.use_digits,
            command=self.validate_checkboxes
        ).pack(side="left", padx=5)
        
        tk.Checkbutton(
            checkboxes_frame, 
            text="Спецсимволы", 
            variable=self.use_symbols,
            command=self.validate_checkboxes
        ).pack(side="left", padx=5)
        
        # Кнопка генерации
        self.generate_btn = tk.Button(
            settings_frame,
            text="Сгенерировать пароль",
            command=self.generate_password,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=5
        )
        self.generate_btn.pack(pady=10)
        
        # Фрейм для отображения пароля
        password_frame = tk.LabelFrame(self.root, text="Сгенерированный пароль", padx=10, pady=10)
        password_frame.pack(padx=20, pady=10, fill="x")
        
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(
            password_frame,
            textvariable=self.password_var,
            font=("Courier", 14),
            state="readonly",
            justify="center"
        )
        self.password_entry.pack(fill="x", pady=5)
        
        # Кнопка копирования
        self.copy_btn = tk.Button(
            password_frame,
            text="Копировать в буфер обмена",
            command=self.copy_to_clipboard,
            bg="#2196F3",
            fg="white",
            padx=20,
            pady=5
        )
        self.copy_btn.pack(pady=5)
        
        # История
        history_frame = tk.LabelFrame(self.root, text="История паролей", padx=10, pady=10)
        history_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        # Таблица истории
        columns = ("Дата", "Пароль", "Длина", "Настройки")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=8)
        
        # Настройка колонок
        for col in columns:
            self.history_tree.heading(col, text=col)
        
        self.history_tree.column("Дата", width=150)
        self.history_tree.column("Пароль", width=180)
        self.history_tree.column("Длина", width=50)
        self.history_tree.column("Настройки", width=200)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Кнопка очистки истории - размещаем ПОД таблицей
        self.clear_btn = tk.Button(
            history_frame,
            text="ОЧИСТИТЬ ИСТОРИЮ",
            command=self.clear_history,
            bg="#f44336",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=8
        )
        self.clear_btn.pack(pady=(10, 5))
        
        # Отображение истории
        self.update_history_display()
    
    def update_length_label(self, value):
        self.length_label.config(text=str(int(float(value))))
    
    def validate_checkboxes(self):
        """Проверка, что выбран хотя бы один тип символов"""
        if not (self.use_lowercase.get() or self.use_uppercase.get() or 
                self.use_digits.get() or self.use_symbols.get()):
            messagebox.showwarning(
                "Предупреждение", 
                "Должен быть выбран хотя бы один тип символов!"
            )
            if not self.use_lowercase.get():
                self.use_lowercase.set(True)
    
    def generate_password(self):
        """Генерация пароля"""
        length = self.length_slider.get()
        
        # Проверка длины
        if length < 4:
            messagebox.showerror("Ошибка", "Длина пароля должна быть минимум 4 символа!")
            return
        if length > 32:
            messagebox.showerror("Ошибка", "Длина пароля не может превышать 32 символа!")
            return
        
        # Формирование набора символов
        chars = ""
        if self.use_lowercase.get():
            chars += string.ascii_lowercase
        if self.use_uppercase.get():
            chars += string.ascii_uppercase
        if self.use_digits.get():
            chars += string.digits
        if self.use_symbols.get():
            chars += string.punctuation
        
        if not chars:
            messagebox.showerror("Ошибка", "Не выбран ни один тип символов!")
            return
        
        # Генерация пароля
        password = ''.join(random.choice(chars) for _ in range(length))
        self.password_var.set(password)
        
        # Сохранение в историю
        self.save_to_history(password, length, self.get_selected_options())
    
    def get_selected_options(self):
        """Получение строки с выбранными опциями"""
        options = []
        if self.use_lowercase.get():
            options.append("a-z")
        if self.use_uppercase.get():
            options.append("A-Z")
        if self.use_digits.get():
            options.append("0-9")
        if self.use_symbols.get():
            options.append("sym")
        return ", ".join(options)
    
    def save_to_history(self, password, length, options):
        """Сохранение пароля в историю"""
        entry = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "password": password,
            "length": length,
            "options": options
        }
        self.history.append(entry)
        
        # Ограничение истории 50 записями
        if len(self.history) > 50:
            self.history = self.history[-50:]
        
        self.save_history()
        self.update_history_display()
    
    def update_history_display(self):
        """Обновление отображения истории"""
        # Очистка текущих записей
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Добавление записей
        for entry in reversed(self.history):
            self.history_tree.insert("", "end", values=(
                entry["date"],
                entry["password"],
                entry["length"],
                entry["options"]
            ))
    
    def copy_to_clipboard(self):
        """Копирование пароля в буфер обмена"""
        password = self.password_var.get()
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена!")
        else:
            messagebox.showwarning("Предупреждение", "Нет пароля для копирования!")
    
    def clear_history(self):
        """Очистка истории"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.history = []
            self.save_history()
            self.update_history_display()
            messagebox.showinfo("Успех", "История очищена!")
    
    def save_history(self):
        """Сохранение истории в JSON"""
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения истории: {e}")
    
    def load_history(self):
        """Загрузка истории из JSON"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Ошибка загрузки истории: {e}")
                return []
        return []

def main():
    root = tk.Tk()
    app = PasswordGenerator(root)
    root.mainloop()

if __name__ == "__main__":
    main()