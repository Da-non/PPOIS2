class DeleteDialog:
    """Диалог удаления товаров по условиям с предварительным просмотром"""
    def __init__(self, parent, model):
        self.parent = parent
        self.model = model
        self.result = None
        self.current_page = 0
        self.items_per_page = 10
        self.all_products = model.products  # Прямая ссылка на список в модели
        self.search_results = []
        self.product_indices = {}  # Словарь: индекс в search_results -> индекс в модели
        
        # Создание окна
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Удаление товаров по условиям")
        self.dialog.geometry("1000x750")
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
        # Основной фрейм с прокруткой
        main_canvas = tk.Canvas(self.dialog)
        scrollbar = ttk.Scrollbar(self.dialog, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Предупреждение
        warning_frame = tk.Frame(scrollable_frame, bg='#ffebee', bd=2, relief=tk.RIDGE)
        warning_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        tk.Label(warning_frame, text="⚠️ ВНИМАНИЕ! Удаление необратимо! ⚠️",
                fg='red', font=('Arial', 12, 'bold'), bg='#ffebee').pack(pady=5)
        
        # Группа условий удаления
        conditions_frame = tk.LabelFrame(scrollable_frame, text="Условия для поиска удаляемых записей", 
                                         padx=10, pady=10, font=('Arial', 10, 'bold'))
        conditions_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # По названию товара или количеству
        name_quantity_frame = tk.LabelFrame(conditions_frame, text="По названию товара или количеству", font=('Arial', 9))
        name_quantity_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(name_quantity_frame, text="Название: ", font=('Arial', 9)).grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.name_or_quantity_name = tk.Entry(name_quantity_frame, width=40, font=('Arial', 9))
        self.name_or_quantity_name.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.name_or_quantity_name.bind('<KeyRelease>', lambda e: self.apply_filter())
        
        tk.Label(name_quantity_frame, text="Количество: ", font=('Arial', 9)).grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.name_or_quantity_quantity = tk.Entry(name_quantity_frame, width=15, font=('Arial', 9))
        self.name_or_quantity_quantity.delete(0, tk.END)
        self.name_or_quantity_quantity.insert(0, "")
        self.name_or_quantity_quantity.grid(row=0, column=3, padx=5, pady=5, sticky='w')
        self.name_or_quantity_quantity.bind('<KeyRelease>', lambda e: self.apply_filter())
        
        # По производителю или УНП
        manufacturer_frame = tk.LabelFrame(conditions_frame, text="По производителю или УНП", font=('Arial', 9))
        manufacturer_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(manufacturer_frame, text="Производитель: ", font=('Arial', 9)).grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.manufacturer_or_unp_manufacturer = tk.Entry(manufacturer_frame, width=40, font=('Arial', 9))
        self.manufacturer_or_unp_manufacturer.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.manufacturer_or_unp_manufacturer.bind('<KeyRelease>', lambda e: self.apply_filter())
        
        tk.Label(manufacturer_frame, text="УНП: ", font=('Arial', 9)).grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.manufacturer_or_unp_unp = tk.Entry(manufacturer_frame, width=20, font=('Arial', 9))
        self.manufacturer_or_unp_unp.grid(row=0, column=3, padx=5, pady=5, sticky='w')
        self.manufacturer_or_unp_unp.bind('<KeyRelease>', lambda e: self.apply_filter())
        
        # Поиск по адресу
        address_frame = tk.LabelFrame(conditions_frame, text="По адресу склада", font=('Arial', 9))
        address_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(address_frame, text="Адрес: ", font=('Arial', 9)).grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.address_entry = tk.Entry(address_frame, width=85, font=('Arial', 9))
        self.address_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.address_entry.bind('<KeyRelease>', lambda e: self.apply_filter())
        
        # Кнопки управления
        button_frame = tk.Frame(conditions_frame)
        button_frame.pack(pady=10)
        
        self.reset_btn = tk.Button(button_frame, text="🔄 Сбросить условия", 
                                   command=self.reset_filters, bg='#FF9800', fg='white', 
                                   font=('Arial', 9, 'bold'), width=20)
        self.reset_btn.pack(side=tk.LEFT, padx=5)
        
        # Информация о найденных записях
        info_frame = tk.Frame(scrollable_frame, bg='#e8f5e8', bd=1, relief=tk.SUNKEN)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(info_frame, text="📋 Найденные записи для удаления: ", 
                font=('Arial', 10, 'bold'), bg='#e8f5e8').pack(side=tk.LEFT, padx=10, pady=5)
        
        self.found_count_label = tk.Label(info_frame, text="0 записей", 
                                         font=('Arial', 10, 'bold'), fg='#4CAF50', bg='#e8f5e8')
        self.found_count_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Таблица результатов
        table_frame = tk.Frame(scrollable_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ("name", "manufacturer", "unp", "quantity", "address")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12, selectmode="extended")
        
        self.tree.heading("name", text="Название товара")
        self.tree.heading("manufacturer", text="Производитель")
        self.tree.heading("unp", text="УНП")
        self.tree.heading("quantity", text="Количество")
        self.tree.heading("address", text="Адрес склада")
        
        self.tree.column("name", width=250)
        self.tree.column("manufacturer", width=150)
        self.tree.column("unp", width=100)
        self.tree.column("quantity", width=80)
        self.tree.column("address", width=350)
        
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Пагинация (как в главном окне)
        pagination_frame = tk.Frame(scrollable_frame)
        pagination_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.first_btn = tk.Button(pagination_frame, text="<<", command=self.first_page, width=3)
        self.first_btn.pack(side=tk.LEFT, padx=2)
        
        self.prev_btn = tk.Button(pagination_frame, text="<", command=self.prev_page, width=3)
        self.prev_btn.pack(side=tk.LEFT, padx=2)
        
        self.page_label = tk.Label(pagination_frame, text="Страница: 0/0", font=('Arial', 9, 'bold'))
        self.page_label.pack(side=tk.LEFT, padx=10)
        
        self.next_btn = tk.Button(pagination_frame, text=">", command=self.next_page, width=3)
        self.next_btn.pack(side=tk.LEFT, padx=2)
        
        self.last_btn = tk.Button(pagination_frame, text=">>", command=self.last_page, width=3)
        self.last_btn.pack(side=tk.LEFT, padx=2)
        
        tk.Label(pagination_frame, text="Записей на странице: ").pack(side=tk.LEFT, padx=(20, 5))
        
        self.items_per_page_var = tk.StringVar(value="10")
        self.items_per_page_combo = ttk.Combobox(pagination_frame, textvariable=self.items_per_page_var,
                                                 values=["5", "10", "20", "50"], width=5, state="readonly")
        self.items_per_page_combo.pack(side=tk.LEFT)
        self.items_per_page_combo.bind('<<ComboboxSelected>>', self.change_items_per_page)
        
        # Кнопки выбора
        selection_frame = tk.Frame(scrollable_frame)
        selection_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(selection_frame, text="Выберите записи для удаления (кликните по строкам, можно выбрать несколько): ", 
                font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=5)
        
        tk.Button(selection_frame, text="✓ Выбрать все", command=self.select_all, 
                 bg='#9C27B0', fg='white', font=('Arial', 9, 'bold'), width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(selection_frame, text="✗ Снять все", command=self.deselect_all, 
                 bg='#9C27B0', fg='white', font=('Arial', 9, 'bold'), width=12).pack(side=tk.LEFT, padx=5)
        
        # ГЛАВНАЯ КНОПКА УДАЛЕНИЯ
        delete_button_frame = tk.Frame(scrollable_frame)
        delete_button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.delete_btn = tk.Button(delete_button_frame, 
                                     text="🗑️ УДАЛИТЬ ВЫБРАННЫЕ ЗАПИСИ 🗑️", 
                                    command=self.delete_selected, 
                                    bg='#f44336', 
                                    fg='white',
                                     font=('Arial', 14, 'bold'), 
                                    height=2,
                                    cursor="hand2")
        self.delete_btn.pack(fill=tk.X)
        
        # Кнопка закрытия
        close_frame = tk.Frame(scrollable_frame)
        close_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(close_frame, text="Закрыть", command=self.dialog.destroy,
                 bg='#607d8b', fg='white', font=('Arial', 10, 'bold'), width=15).pack()
        
        # Привязка Escape
        self.dialog.bind('<Escape>', lambda e: self.dialog.destroy())
        
        # Подсказка
        status_frame = tk.Frame(scrollable_frame, bg='#fff3e0', bd=1, relief=tk.SUNKEN)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(status_frame, text="💡 Подсказка: Сначала найдите записи по условиям, затем выделите нужные строки (кликните по ним), после чего нажмите красную кнопку для удаления",
                font=('Arial', 8), fg='#ff6f00', bg='#fff3e0').pack(pady=3)
        
    def reset_filters(self):
        """Сброс всех фильтров"""
        self.name_or_quantity_name.delete(0, tk.END)
        self.name_or_quantity_quantity.delete(0, tk.END)
        self.manufacturer_or_unp_manufacturer.delete(0, tk.END)
        self.manufacturer_or_unp_unp.delete(0, tk.END)
        self.address_entry.delete(0, tk.END)
        
        # Очищаем результаты
        self.search_results = []
        self.product_indices = {}
        self.current_page = 0
        self.update_table()
        self.found_count_label.config(text="0 записей")
        
    def apply_filter(self):
        """Применение фильтра для поиска записей для удаления (автопоиск)"""
        # Берем актуальные данные из модели
        self.all_products = self.model.products
        filtered = []
        self.product_indices = {}  # Очищаем маппинг индексов
        
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
            self.product_indices = {}
            self.current_page = 0
            self.update_table()
            self.found_count_label.config(text="0 записей")
            return
        
        # Проходим по всем продуктам с их индексами
        for idx, product in enumerate(self.model.products):
            match = True
            
            # Применяем фильтр по названию (частичное совпадение)
            if name_value and name_value not in product.name.lower():
                match = False
            
            # Применяем фильтр по количеству (частичное совпадение)
            if match and quantity_value:
                try:
                    quantity = int(quantity_value)
                    if product.quantity != quantity:
                        match = False
                except ValueError:
                    # Если введено не число, ищем по частичному совпадению
                    if quantity_value not in str(product.quantity):
                        match = False
            
            # Применяем фильтр по производителю (частичное совпадение)
            if match and manufacturer_value and manufacturer_value not in product.manufacturer.lower():
                match = False
            
            # Применяем фильтр по УНП (частичное совпадение)
            if match and unp_value and unp_value not in product.unp:
                match = False
                
            # Применяем фильтр по адресу (частичное совпадение)
            if match and address_value and address_value not in product.address.lower():
                match = False
            
            if match:
                filtered.append(product)
                # Сохраняем индекс продукта в модели
                self.product_indices[len(filtered) - 1] = idx
        
        # Обновляем результаты - сохраняем ВСЕ найденные записи
        self.search_results = filtered
        self.current_page = 0  # Сбрасываем на первую страницу
        self.update_table()  # Обновляем таблицу (она сама разобьет на страницы)
        self.found_count_label.config(text=f"{len(self.search_results)} записей")
        
    def update_table(self):
        """Обновление таблицы с результатами (с пагинацией)"""
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Очищаем маппинг для текущей страницы
        self.page_product_indices = {}
        
        # Если нет результатов, показываем пустую таблицу
        if not self.search_results:
            self.page_label.config(text="Страница: 0/0")
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
        for local_idx, product in enumerate(page_results):
            global_idx = start + local_idx
            original_model_idx = self.product_indices.get(global_idx, -1)
            
            item_id = self.tree.insert("", tk.END, values=(
                product.name,
                product.manufacturer,
                product.unp,
                product.quantity,
                product.address
            ))
            # Сохраняем связь между item_id и индексом в модели
            self.page_product_indices[item_id] = original_model_idx
         
        # Обновляем информацию о пагинации
        self.page_label.config(text=f"Страница: {self.current_page + 1}/{total_pages}")
        
        # Обновляем состояние кнопок
        self.first_btn.config(state=tk.NORMAL if self.current_page > 0 else tk.DISABLED)
        self.prev_btn.config(state=tk.NORMAL if self.current_page > 0 else tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL if self.current_page < total_pages - 1 else tk.DISABLED)
        self.last_btn.config(state=tk.NORMAL if self.current_page < total_pages - 1 else tk.DISABLED)
        
    def select_all(self):
        """Выбрать все записи на текущей странице"""
        for item in self.tree.get_children():
            self.tree.selection_add(item)
        count = len(self.tree.selection())
        if count > 0:
            self.dialog.title(f"Удаление товаров - выбрано {count} записей")
            
    def deselect_all(self):
        """Снять выделение со всех записей"""
        self.tree.selection_remove(self.tree.selection())
        self.dialog.title("Удаление товаров по условиям")
        
    def delete_selected(self):
        """Удаление выбранных записей"""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning(
                "Нет выбранных записей", 
                "Сначала найдите записи по условиям, затем выделите нужные строки (кликните по ним), после чего нажмите кнопку удаления.",
                parent=self.dialog
            )
            return
        
        # Получаем индексы продуктов в модели для удаления
        indices_to_delete = []
        for item_id in selected_items:
            model_idx = self.page_product_indices.get(item_id)
            if model_idx is not None and model_idx >= 0:
                indices_to_delete.append(model_idx)
        
        if not indices_to_delete:
            messagebox.showwarning(
                "Ошибка",
                "Не удалось определить индексы товаров для удаления. Попробуйте найти записи заново.",
                parent=self.dialog
            )
            return
        
        # Показываем информацию о том, что будет удалено
        preview_products = [self.model.products[i] for i in indices_to_delete if i < len(self.model.products)]
        preview = "\n".join([f"• {p.name} ({p.manufacturer})" for p in preview_products[:10]])
        if len(preview_products) > 10:
            preview += f"\n• ... и еще {len(preview_products) - 10} записей"
            
        result = messagebox.askyesno(
            "Подтверждение удаления",
            f"Вы действительно хотите удалить {len(indices_to_delete)} записей?\n\n{preview}",
            parent=self.dialog
        )

        if result:
            # Возвращаем индексы для удаления (отсортированные в обратном порядке)
            self.result = sorted(list(set(indices_to_delete)), reverse=True)
            self.dialog.destroy()

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
        """Показать диалог и вернуть список индексов для удаления"""
        self.dialog.wait_window()
        return self.result
