import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Optional
from model import Product

class ProductDialog:
    """Диалог добавления/редактирования товара"""
    
    def __init__(self, parent, product: Optional[Product] = None):
        self.result = None
        self.product = product or Product('', '', '', 0, '')
        
        # Создание окна - УВЕЛИЧЕННЫЙ РАЗМЕР
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Товар" if not product else "Редактирование товара")
        self.dialog.geometry("550x500")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        
        # Центрируем окно
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
        
    def setup_ui(self):
        """Настройка интерфейса диалога"""
        main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Название товара
        tk.Label(main_frame, text="Название товара:*", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_entry = tk.Entry(main_frame, width=45, font=('Arial', 10))
        self.name_entry.insert(0, self.product.name)
        self.name_entry.grid(row=0, column=1, pady=5)
        
        # Производитель
        tk.Label(main_frame, text="Производитель:*", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.manufacturer_entry = tk.Entry(main_frame, width=45, font=('Arial', 10))
        self.manufacturer_entry.insert(0, self.product.manufacturer)
        self.manufacturer_entry.grid(row=1, column=1, pady=5)
        
        # УНП (с проверкой)
        tk.Label(main_frame, text="УНП производителя:*", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=5)
        unp_frame = tk.Frame(main_frame)
        unp_frame.grid(row=2, column=1, pady=5, sticky=tk.W)
        
        self.unp_entry = tk.Entry(unp_frame, width=30, font=('Arial', 10))
        self.unp_entry.insert(0, self.product.unp)
        self.unp_entry.pack(side=tk.LEFT)
        
        self.unp_status = tk.Label(unp_frame, text="", font=('Arial', 9), width=25, anchor=tk.W)
        self.unp_status.pack(side=tk.LEFT, padx=10)
        
        # Привязка проверки УНП
        self.unp_entry.bind('<KeyRelease>', self.validate_unp)
        
        # Количество
        tk.Label(main_frame, text="Количество на складе:*", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.quantity_spin = tk.Spinbox(main_frame, from_=0, to=10000, width=43, font=('Arial', 10))
        self.quantity_spin.delete(0, tk.END)
        self.quantity_spin.insert(0, str(self.product.quantity))
        self.quantity_spin.grid(row=3, column=1, pady=5)
        
        # Адрес склада
        tk.Label(main_frame, text="Адрес склада:*", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky=tk.W, pady=5)
        self.address_entry = tk.Entry(main_frame, width=45, font=('Arial', 10))
        self.address_entry.insert(0, self.product.address)
        self.address_entry.grid(row=4, column=1, pady=5)
        
        # Подсказка об обязательных полях
        tk.Label(main_frame, text="* - обязательные поля", font=('Arial', 8, 'italic'), fg='gray').grid(row=5, column=0, columnspan=2, pady=10)
        
        # Кнопки
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        tk.Button(button_frame, text="OK", command=self.ok_clicked, width=12,
                 bg='#4CAF50', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Отмена", command=self.cancel_clicked, width=12,
                 bg='#f44336', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=10)
        
        # Привязка Enter и Escape
        self.dialog.bind('<Return>', lambda e: self.ok_clicked())
        self.dialog.bind('<Escape>', lambda e: self.cancel_clicked())
        
    def validate_unp(self, event=None):
        """Проверка УНП (9 цифр)"""
        unp = self.unp_entry.get().strip()
        
        if not unp:
            self.unp_status.config(text="", fg='black')
            return False
        elif not unp.isdigit():
            self.unp_status.config(text="❌ Только цифры!", fg='red')
            return False
        elif len(unp) != 9:
            self.unp_status.config(text=f"❌ Должно быть 9 цифр (сейчас {len(unp)})", fg='red')
            return False
        else:
            self.unp_status.config(text="✅ OK", fg='green')
            return True
        
    def ok_clicked(self):
        """Обработка нажатия OK с проверкой всех полей"""
        # Проверка на пустые поля
        errors = []
        
        name = self.name_entry.get().strip()
        if not name:
            errors.append("Название товара")
            
        manufacturer = self.manufacturer_entry.get().strip()
        if not manufacturer:
            errors.append("Производитель")
            
        address = self.address_entry.get().strip()
        if not address:
            errors.append("Адрес склада")
        
        # Проверка количества
        try:
            quantity = int(self.quantity_spin.get())
        except ValueError:
            errors.append("Количество (должно быть числом)")
            quantity = 0
        
        # Проверка УНП
        unp = self.unp_entry.get().strip()
        if not unp:
            errors.append("УНП")
        elif not unp.isdigit():
            errors.append("УНП (только цифры)")
        elif len(unp) != 9:
            errors.append(f"УНП (должно быть 9 цифр, сейчас {len(unp)})")
            
        # Если есть ошибки, показываем сообщение
        if errors:
            error_msg = "Заполните правильно следующие поля:\n• " + "\n• ".join(errors)
            messagebox.showerror("Ошибка ввода", error_msg, parent=self.dialog)
            return
            
        self.result = Product(
            name=name,
            manufacturer=manufacturer,
            unp=unp,
            quantity=quantity,
            address=address
        )
        self.dialog.destroy()
        
    def cancel_clicked(self):
        """Обработка нажатия Отмена"""
        self.result = None
        self.dialog.destroy()
        
    def show(self) -> Optional[Product]:
        """Показать диалог и вернуть результат"""
        self.dialog.wait_window()
        return self.result

