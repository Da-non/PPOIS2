import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List, Callable
from model import Product

class MainWindow:
    """Главное окно приложения на tkinter """
    
    def __init__(self, root):
        self.root = root
        self.root.title("Учет товаров на складе")
        self.root.geometry("1000x600")
        self.bg_color = '#e8f5e9'  
        self.root.configure(bg=self.bg_color)
        self.current_page = 0
        self.items_per_page = 10
        self.products = []
        self.total_items = 0
        
        # Callback функции для связи с контроллером
        self.add_callback = None
        self.edit_callback = None
        self.delete_callback = None
        self.search_callback = None
        self.delete_cond_callback = None
        self.save_callback = None
        self.load_callback = None
        self.page_change_callback = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.create_menu()
        self.create_toolbar()
        self.create_main_area()
        self.create_statusbar()
        
    def create_menu(self):
        """Создание меню"""
        menubar = tk.Menu(self.root, bg='#a5d6a7', fg='#1b5e20')  # Мятный цвет меню
        self.root.config(menu=menubar)
        
        # Меню Файл
        file_menu = tk.Menu(menubar, tearoff=0, bg='#c8e6c9', fg='#1b5e20')
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Сохранить", command=self.on_save, accelerator="Ctrl+S")
        file_menu.add_command(label="Загрузить", command=self.on_load, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit, accelerator="Ctrl+Q")
        
        # Меню Записи
        records_menu = tk.Menu(menubar, tearoff=0, bg='#c8e6c9', fg='#1b5e20')
        menubar.add_cascade(label="Записи", menu=records_menu)
        records_menu.add_command(label="Добавить", command=self.on_add, accelerator="Ctrl+A")
        records_menu.add_command(label="Редактировать", command=self.on_edit, accelerator="Ctrl+E")
        records_menu.add_command(label="Удалить", command=self.on_delete, accelerator="Del")
        
        # Меню Поиск
        search_menu = tk.Menu(menubar, tearoff=0, bg='#c8e6c9', fg='#1b5e20')
        menubar.add_cascade(label="Поиск", menu=search_menu)
        search_menu.add_command(label="Найти", command=self.on_search, accelerator="Ctrl+F")
        search_menu.add_command(label="Удалить по условиям", command=self.on_delete_conditions, accelerator="Ctrl+D")
        
        # Привязка горячих клавиш
        self.root.bind('<Control-s>', lambda e: self.on_save())
        self.root.bind('<Control-o>', lambda e: self.on_load())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        self.root.bind('<Control-a>', lambda e: self.on_add())
        self.root.bind('<Control-e>', lambda e: self.on_edit())
        self.root.bind('<Delete>', lambda e: self.on_delete())
        self.root.bind('<Control-f>', lambda e: self.on_search())
        self.root.bind('<Control-d>', lambda e: self.on_delete_conditions())
        
    def create_toolbar(self):
        """Создание панели инструментов в нежно-зеленых тонах"""
        toolbar = tk.Frame(self.root, bd=1, relief=tk.RAISED, bg='#a5d6a7')  # Мятный цвет
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # Стиль для кнопок
        button_style = {
            'bg': '#81c784',  # Светло-зеленый
            'fg': '#1b5e20',  # Темно-зеленый текст
            'font': ('Arial', 10, 'bold'),
            'padx': 10,
            'pady': 5,
            'relief': tk.RAISED,
            'bd': 2
        }
        
        # Кнопки на панели инструментов
        tk.Button(toolbar, text="💾 Сохранить", command=self.on_save, **button_style).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(toolbar, text="📂 Загрузить", command=self.on_load, **button_style).pack(side=tk.LEFT, padx=2, pady=2)
        
        # Разделитель
        tk.Frame(toolbar, width=2, bg='#66bb6a').pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=2)
        
        tk.Button(toolbar, text="➕ Добавить", command=self.on_add, **button_style).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(toolbar, text="✏️ Редактировать", command=self.on_edit, **button_style).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(toolbar, text="🗑️ Удалить", command=self.on_delete, **button_style).pack(side=tk.LEFT, padx=2, pady=2)
        
        # Разделитель
        tk.Frame(toolbar, width=2, bg='#66bb6a').pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=2)
        
        tk.Button(toolbar, text="🔍 Найти", command=self.on_search, **button_style).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(toolbar, text="🗑️ Удалить по условиям", command=self.on_delete_conditions, **button_style).pack(side=tk.LEFT, padx=2, pady=2)
        
    def create_main_area(self):
        """Создание основной области с таблицей """
        main_frame = tk.Frame(self.root, bg='#e8f5e9')  
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Стиль для таблицы
        style = ttk.Style()
        style.theme_use("default")
        
        # Настройка заголовков таблицы
        style.configure("Treeview.Heading", 
                        background="#66bb6a", 
                        foreground="white", 
                        font=('Arial', 10, 'bold'),
                        relief="raised")
        
        # Настройка строк таблицы
        style.configure("Treeview", 
                        background="#f1f8e9",  
                        foreground="#1b5e20",  
                        rowheight=25,
                        fieldbackground="#f1f8e9",
                        font=('Arial', 9))
        
        # Выделение выбранной строки
        style.map('Treeview', 
                  background=[('selected', '#a5d6a7')],  
                  foreground=[('selected', '#1b5e20')])
        
        # Создаем таблицу
        columns = ("name", "manufacturer", "unp", "quantity", "address")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", selectmode="browse")
        
        # Заголовки колонок
        self.tree.heading("name", text="Название товара")
        self.tree.heading("manufacturer", text="Производитель")
        self.tree.heading("unp", text="УНП")
        self.tree.heading("quantity", text="Количество")
        self.tree.heading("address", text="Адрес склада")
        
        # Настройка ширины колонок
        self.tree.column("name", width=200)
        self.tree.column("manufacturer", width=150)
        self.tree.column("unp", width=100)
        self.tree.column("quantity", width=100)
        self.tree.column("address", width=250)
        
        # Полосы прокрутки
        v_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Размещение таблицы и скроллбаров
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Двойной клик для редактирования
        self.tree.bind('<Double-1>', lambda e: self.on_edit())
        
        # Панель пагинации в нежно-зеленых тонах
        pagination_frame = tk.Frame(self.root, bg='#c8e6c9', height=40)  # Светло-зеленый
        pagination_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Стиль для кнопок пагинации
        page_button_style = {
            'bg': '#81c784',
            'fg': '#1b5e20',
            'font': ('Arial', 9, 'bold'),
            'width': 3,
            'relief': tk.RAISED,
            'bd': 1
        }
        
        # Кнопки навигации
        self.first_btn = tk.Button(pagination_frame, text="<<", command=self.on_first_page, **page_button_style)
        self.first_btn.pack(side=tk.LEFT, padx=2, pady=5)
        
        self.prev_btn = tk.Button(pagination_frame, text="<", command=self.on_prev_page, **page_button_style)
        self.prev_btn.pack(side=tk.LEFT, padx=2, pady=5)
        
        # Информация о странице
        self.page_label = tk.Label(pagination_frame, text="Страница: 0/0", 
                                   bg='#c8e6c9', fg='#1b5e20', font=('Arial', 10, 'bold'))
        self.page_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.next_btn = tk.Button(pagination_frame, text=">", command=self.on_next_page, **page_button_style)
        self.next_btn.pack(side=tk.LEFT, padx=2, pady=5)
        
        self.last_btn = tk.Button(pagination_frame, text=">>", command=self.on_last_page, **page_button_style)
        self.last_btn.pack(side=tk.LEFT, padx=2, pady=5)
        
        # Выбор количества записей на странице
        tk.Label(pagination_frame, text="Записей на странице:", 
                bg='#c8e6c9', fg='#1b5e20', font=('Arial', 9)).pack(side=tk.LEFT, padx=(20, 5))
        
        self.items_per_page_var = tk.StringVar(value="10")
        self.items_per_page_combo = ttk.Combobox(pagination_frame, textvariable=self.items_per_page_var,
                                                 values=["5", "10", "20", "50"], width=5, state="readonly")
        self.items_per_page_combo.pack(side=tk.LEFT)
        self.items_per_page_combo.bind('<<ComboboxSelected>>', self.on_items_per_page_change)
        
        # Информация о записях
        self.total_label = tk.Label(pagination_frame, text="Всего записей: 0",
                                   bg='#c8e6c9', fg='#1b5e20', font=('Arial', 9, 'bold'))
        self.total_label.pack(side=tk.RIGHT, padx=10)
        
    def create_statusbar(self):
        """Создание строки состояния в нежно-зеленых тонах"""
        self.statusbar = tk.Label(
            self.root, 
            text="Готов к работе", 
            bd=1, 
            relief=tk.SUNKEN, 
            anchor=tk.W,
            bg='#66bb6a',  # Средне-зеленый
            fg='white',
            font=('Arial', 9, 'bold')
        )
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def set_callbacks(self, add_cb, edit_cb, delete_cb, search_cb, delete_cond_cb, save_cb, load_cb, page_change_cb):
        """Установка callback функций"""
        self.add_callback = add_cb
        self.edit_callback = edit_cb
        self.delete_callback = delete_cb
        self.search_callback = search_cb
        self.delete_cond_callback = delete_cond_cb
        self.save_callback = save_cb
        self.load_callback = load_cb
        self.page_change_callback = page_change_cb
        
    def on_add(self):
        if self.add_callback:
            self.add_callback()
            
    def on_edit(self):
        selected = self.tree.selection()
        if selected:
            index = self.tree.index(selected[0])
            if self.edit_callback:
                self.edit_callback(index)
        else:
            messagebox.showinfo("Информация", "Выберите товар для редактирования")
            
    def on_delete(self):
        selected = self.tree.selection()
        if selected:
            index = self.tree.index(selected[0])
            if self.delete_callback:
                self.delete_callback(index)
        else:
            messagebox.showinfo("Информация", "Выберите товар для удаления")
            
    def on_search(self):
        if self.search_callback:
            self.search_callback()
            
    def on_delete_conditions(self):
        if self.delete_cond_callback:
            self.delete_cond_callback()
            
    def on_save(self):
        if self.save_callback:
            self.save_callback("")
            
    def on_load(self):
        if self.load_callback:
            self.load_callback("")
            
    def on_first_page(self):
        if self.page_change_callback:
            self.page_change_callback(0)
            
    def on_prev_page(self):
        if self.current_page > 0 and self.page_change_callback:
            self.page_change_callback(self.current_page - 1)
            
    def on_next_page(self):
        if self.page_change_callback:
            self.page_change_callback(self.current_page + 1)
            
    def on_last_page(self):
        total_pages = (self.total_items + self.items_per_page - 1) // self.items_per_page
        if self.page_change_callback:
            self.page_change_callback(total_pages - 1)
            
    def on_items_per_page_change(self, event):
        self.items_per_page = int(self.items_per_page_var.get())
        if self.page_change_callback:
            self.page_change_callback(0)
            
    def update_table(self, products, current_page, total_items):
        """Обновление таблицы с данными"""
        self.products = products
        self.current_page = current_page
        self.total_items = total_items
        
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Добавляем новые данные
        for product in products:
            self.tree.insert("", tk.END, values=(
                product.name,
                product.manufacturer,
                product.unp,
                product.quantity,
                product.address
            ))
            
        # Обновляем информацию о пагинации
        total_pages = (total_items + self.items_per_page - 1) // self.items_per_page
        self.page_label.config(text=f"Страница: {current_page + 1}/{max(1, total_pages)}")
        self.total_label.config(text=f"Всего записей: {total_items}")
        
        # Обновляем состояние кнопок
        self.first_btn.config(state=tk.NORMAL if current_page > 0 else tk.DISABLED)
        self.prev_btn.config(state=tk.NORMAL if current_page > 0 else tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL if current_page < total_pages - 1 else tk.DISABLED)
        self.last_btn.config(state=tk.NORMAL if current_page < total_pages - 1 else tk.DISABLED)
        
    def get_selected_row(self) -> int:
        """Получение индекса выбранной строки"""
        selected = self.tree.selection()
        if selected:
            return self.tree.index(selected[0])
        return -1
        
    def show_message(self, title: str, message: str):
        """Показ сообщения пользователю"""
        messagebox.showinfo(title, message)
        
    def confirm_deletion(self, count: int) -> bool:
        """Подтверждение удаления"""
        return messagebox.askyesno("Подтверждение удаления", 
                                   f"Будет удалено {count} записей. Продолжить?")
        
    def get_save_filename(self) -> str:
        """Получение имени файла для сохранения"""
        return filedialog.asksaveasfilename(defaultextension=".xml", 
                                            filetypes=[("XML files", "*.xml")])
        
    def get_load_filename(self) -> str:
        """Получение имени файла для загрузки"""
        return filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
        
    def update_status(self, message: str):
        """Обновление строки состояния"""
        self.statusbar.config(text=message)
