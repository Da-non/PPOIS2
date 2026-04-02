class SearchDialog:
    """Диалог поиска товаров с автоматической фильтрацией"""
    
    def __init__(self, parent, model):
        self.parent = parent
        self.model = model
        self.result = None
        self.current_page = 0
        self.items_per_page = 10
        # Прямая ссылка на список товаров в модели
        self.all_products = model.products
        # Изначально результаты пустые
        self.search_results = []
        
        # Создание окна
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Поиск товаров")
        self.dialog.geometry("950x750")  # Увеличил размер окна
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        
        # Центрируем окно
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
        
        # Показываем пустую таблицу при открытии
        self.update_table()
        
    def setup_ui(self):
        """Настройка интерфейса диалога"""
        # Основной контейнер
        main_container = tk.Frame(self.dialog)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Создаем Canvas с прокруткой для всего содержимого
        canvas = tk.Canvas(main_container)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Теперь все элементы добавляем в scrollable_frame
        main_frame = scrollable_frame
        
        # Группа условий поиска
        conditions_frame = tk.LabelFrame(main_frame, text="Условия поиска (фильтр)", padx=10, pady=10, font=('Arial', 10, 'bold'))
        conditions_frame.pack(fill=tk.X, pady=(0, 10), padx=10)
        
        # По названию товара или количеству
        name_quantity_frame = tk.LabelFrame(conditions_frame, text="По названию товара или количеству", font=('Arial', 9))
        name_quantity_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(name_quantity_frame, text="Название:", font=('Arial', 9)).grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.name_or_quantity_name = tk.Entry(name_quantity_frame, width=40, font=('Arial', 9))
        self.name_or_quantity_name.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.name_or_quantity_name.bind('<KeyRelease>', lambda e: self.apply_filter())
        
        tk.Label(name_quantity_frame, text="Количество:", font=('Arial', 9)).grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.name_or_quantity_quantity = tk.Entry(name_quantity_frame, width=15, font=('Arial', 9))
        self.name_or_quantity_quantity.insert(0, "")
        self.name_or_quantity_quantity.grid(row=0, column=3, padx=5, pady=5, sticky='w')
        self.name_or_quantity_quantity.bind('<KeyRelease>', lambda e: self.apply_filter())
        
        # По производителю или УНП
        manufacturer_frame = tk.LabelFrame(conditions_frame, text="По производителю или УНП", font=('Arial', 9))
        manufacturer_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(manufacturer_frame, text="Производитель:", font=('Arial', 9)).grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.manufacturer_or_unp_manufacturer = tk.Entry(manufacturer_frame, width=40, font=('Arial', 9))
        self.manufacturer_or_unp_manufacturer.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.manufacturer_or_unp_manufacturer.bind('<KeyRelease>', lambda e: self.apply_filter())
        
        tk.Label(manufacturer_frame, text="УНП:", font=('Arial', 9)).grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.manufacturer_or_unp_unp = tk.Entry(manufacturer_frame, width=20, font=('Arial', 9))
        self.manufacturer_or_unp_unp.grid(row=0, column=3, padx=5, pady=5, sticky='w')
        self.manufacturer_or_unp_unp.bind('<KeyRelease>', lambda e: self.apply_filter())
        
        # Поиск по адресу
        address_frame = tk.LabelFrame(conditions_frame, text="По адресу склада", font=('Arial', 9))
        address_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(address_frame, text="Адрес:", font=('Arial', 9)).grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.address_entry = tk.Entry(address_frame, width=85, font=('Arial', 9))
        self.address_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.address_entry.bind('<KeyRelease>', lambda e: self.apply_filter())
        
        # Кнопка сброса
        reset_btn = tk.Button(conditions_frame, text="🔄 Сбросить все фильтры", 
                              command=self.reset_filters, bg='#FF9800', fg='white', font=('Arial', 9, 'bold'))
        reset_btn.pack(pady=5)
        
        # Таблица результатов
        table_frame = tk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10), padx=10)
        
        columns = ("name", "manufacturer", "unp", "quantity", "address")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        
        self.tree.heading("name", text="Название")
        self.tree.heading("manufacturer", text="Производитель")
        self.tree.heading("unp", text="УНП")
        self.tree.heading("quantity", text="Количество")
        self.tree.heading("address", text="Адрес")
        
        self.tree.column("name", width=220)
        self.tree.column("manufacturer", width=150)
        self.tree.column("unp", width=100)
        self.tree.column("quantity", width=80)
        self.tree.column("address", width=320)
        
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # ========== ПАГИНАЦИЯ - СДЕЛАЕМ ЯРКОЙ И ЗАМЕТНОЙ ==========
        pagination_frame = tk.Frame(main_frame, bg='#e0e0e0', bd=2, relief=tk.RIDGE, height=60)
        pagination_frame.pack(fill=tk.X, pady=10, padx=10)
        pagination_frame.pack_propagate(False)
        
        # Центральный фрейм для кнопок
        center_frame = tk.Frame(pagination_frame, bg='#e0e0e0')
        center_frame.pack(expand=True)
        
        # Кнопки пагинации
        self.first_btn = tk.Button(center_frame, text="⏮ Первая", command=self.first_page, 
                                   bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'), width=10)
        self.first_btn.pack(side=tk.LEFT, padx=5)
        
        self.prev_btn = tk.Button(center_frame, text="◀ Пред.", command=self.prev_page,
                                  bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'), width=10)
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        
        self.page_label = tk.Label(center_frame, text="Страница: 0/0", 
                                   bg='#e0e0e0', fg='#2c3e50', font=('Arial', 12, 'bold'), width=15)
        self.page_label.pack(side=tk.LEFT, padx=10)
        
        self.next_btn = tk.Button(center_frame, text="След. ▶", command=self.next_page,
                                  bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'), width=10)
        self.next_btn.pack(side=tk.LEFT, padx=5)
        
        self.last_btn = tk.Button(center_frame, text="Последняя ⏭", command=self.last_page,
                                  bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'), width=10)
        self.last_btn.pack(side=tk.LEFT, padx=5)
        
        # Нижняя панель с настройками
        settings_frame = tk.Frame(main_frame, bg='#f5f5f5', bd=1, relief=tk.SUNKEN)
        settings_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        left_settings = tk.Frame(settings_frame, bg='#f5f5f5')
        left_settings.pack(side=tk.LEFT, padx=10, pady=5)
        
        tk.Label(left_settings, text="Записей на странице:", bg='#f5f5f5', font=('Arial', 9)).pack(side=tk.LEFT)
        
        self.items_per_page_var = tk.StringVar(value="10")
        self.items_per_page_combo = ttk.Combobox(left_settings, textvariable=self.items_per_page_var,
                                                 values=["5", "10", "20", "50"], width=5, state="readonly")
        self.items_per_page_combo.pack(side=tk.LEFT, padx=5)
        self.items_per_page_combo.bind('<<ComboboxSelected>>', self.change_items_per_page)
        
        right_settings = tk.Frame(settings_frame, bg='#f5f5f5')
        right_settings.pack(side=tk.RIGHT, padx=10, pady=5)
        
        self.total_label = tk.Label(right_settings, text="Всего записей: 0", 
                                    bg='#f5f5f5', fg='#2c3e50', font=('Arial', 10, 'bold'))
        self.total_label.pack(side=tk.RIGHT)
        
        # Кнопка закрытия
        close_frame = tk.Frame(main_frame)
        close_frame.pack(fill=tk.X, pady=10, padx=10)
        tk.Button(close_frame, text="Закрыть", command=self.dialog.destroy,
                 bg='#607d8b', fg='white', font=('Arial', 11, 'bold'), width=15).pack()
        
        # Привязка Escape
        self.dialog.bind('<Escape>', lambda e: self.dialog.destroy())
        
    def reset_filters(self):
        """Сброс всех фильтров"""
        self.name_or_quantity_name.delete(0, tk.END)
        self.name_or_quantity_quantity.delete(0, tk.END)
        self.manufacturer_or_unp_manufacturer.delete(0, tk.END)
        self.manufacturer_or_unp_unp.delete(0, tk.END)
        self.address_entry.delete(0, tk.END)
        
        # Очищаем результаты поиска
        self.search_results = []
        self.current_page = 0
        self.update_table()
        self.dialog.title("Поиск товаров")
        
    def apply_filter(self):
        """Применение фильтра при каждом изменении полей (автопоиск)"""
        # Берем актуальные данные из модели
        self.all_products = self.model.products
        filtered = self.all_products.copy()
        
        # Получаем значения полей
        name_value = self.name_or_quantity_name.get().strip().lower()
        quantity_value = self.name_or_quantity_quantity.get().strip()
        manufacturer_value = self.manufacturer_or_unp_manufacturer.get().strip().lower()
        unp_value = self.manufacturer_or_unp_unp.get().strip()
        address_value = self.address_entry.get().strip().lower()
        
        # Проверяем, есть ли хоть какой-то критерий поиска
        has_search_criteria = any([
            name_value,
            quantity_value,
            manufacturer_value,
            unp_value,
            address_value
        ])
        
        # Если нет критериев поиска, показываем пустой результат
        if not has_search_criteria:
            self.search_results = []
            self.current_page = 0
            self.update_table()
            self.dialog.title("Поиск товаров")
            return
        
        # Применяем фильтр по названию (частичное совпадение)
        if name_value:
            filtered = [p for p in filtered if name_value in p.name.lower()]
        
        # Применяем фильтр по количеству (точное совпадение или частичное)
        if quantity_value:
            try:
                quantity = int(quantity_value)
                filtered = [p for p in filtered if p.quantity == quantity]
            except ValueError:
                # Если введено не число, ищем по частичному совпадению с числом как строкой
                filtered = [p for p in filtered if quantity_value in str(p.quantity)]
        
        # Применяем фильтр по производителю (частичное совпадение)
        if manufacturer_value:
            filtered = [p for p in filtered if manufacturer_value in p.manufacturer.lower()]
        
        # Применяем фильтр по УНП (частичное совпадение)
        if unp_value:
            filtered = [p for p in filtered if unp_value in p.unp]
            
        # Применяем фильтр по адресу (частичное совпадение)
        if address_value:
            filtered = [p for p in filtered if address_value in p.address.lower()]
        
        # Обновляем результаты - сохраняем ВСЕ найденные записи
        self.search_results = filtered
        self.current_page = 0  # Сбрасываем на первую страницу
        self.update_table()  # Обновляем таблицу (она сама разобьет на страницы)
        
        # Обновляем заголовок окна
        found_count = len(self.search_results)
        if found_count > 0:
            self.dialog.title(f"Поиск товаров - найдено: {found_count}")
        else:
            self.dialog.title("Поиск товаров - ничего не найдено")
        
    def update_table(self):
        """Обновление таблицы с результатами (с пагинацией)"""
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Если нет результатов, показываем пустую таблицу
        if not self.search_results:
            self.page_label.config(text="Страница: 0/0")
            self.total_label.config(text="Всего записей: 0")
            self.first_btn.config(state=tk.DISABLED)
            self.prev_btn.config(state=tk.DISABLED)
            self.next_btn.config(state=tk.DISABLED)
            self.last_btn.config(state=tk.DISABLED)
            return
        
        # Вычисляем общее количество записей и страниц
        total_items = len(self.search_results)
        total_pages = (total_items + self.items_per_page - 1) // self.items_per_page
        
        # Корректируем текущую страницу, если она выходит за пределы
        if self.current_page >= total_pages:
            self.current_page = total_pages - 1
            if self.current_page < 0:
                self.current_page = 0
            
        # Получаем записи для текущей страницы
        start = self.current_page * self.items_per_page
        end = min(start + self.items_per_page, total_items)
        page_results = self.search_results[start:end]
        
        # Заполняем таблицу
        for product in page_results:
            self.tree.insert("", tk.END, values=(
                product.name,
                product.manufacturer,
                product.unp,
                product.quantity,
                product.address
            ))
            
        # Обновляем информацию о пагинации
        self.page_label.config(text=f"Страница: {self.current_page + 1} / {total_pages}")
        self.total_label.config(text=f"Всего записей: {total_items}")
        
        # Обновляем состояние кнопок
        self.first_btn.config(state=tk.NORMAL if self.current_page > 0 else tk.DISABLED)
        self.prev_btn.config(state=tk.NORMAL if self.current_page > 0 else tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL if self.current_page < total_pages - 1 else tk.DISABLED)
        self.last_btn.config(state=tk.NORMAL if self.current_page < total_pages - 1 else tk.DISABLED)
        
    def first_page(self):
        self.current_page = 0
        self.update_table()
        
    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_table()
            
    def next_page(self):
        if self.search_results:
            total_pages = (len(self.search_results) + self.items_per_page - 1) // self.items_per_page
            if self.current_page < total_pages - 1:
                self.current_page += 1
                self.update_table()
            
    def last_page(self):
        if self.search_results:
            total_pages = (len(self.search_results) + self.items_per_page - 1) // self.items_per_page
            self.current_page = max(0, total_pages - 1)
            self.update_table()
        
    def change_items_per_page(self, event):
        self.items_per_page = int(self.items_per_page_var.get())
        self.current_page = 0
        self.update_table()
        
    def show(self):
        """Показать диалог"""
        self.dialog.wait_window()
