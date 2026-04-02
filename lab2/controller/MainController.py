from model import ProductModel, Product
from view import MainWindow
from dialogs import ProductDialog, SearchDialog, DeleteDialog

class MainController:
    """Контроллер главного окна для tkinter"""
    
    def __init__(self, root):
        self.model = ProductModel()
        self.view = MainWindow(root)
        
        # Устанавливаем callback функции
        self.view.set_callbacks(
            add_cb=self.add_product,
            edit_cb=self.edit_product,
            delete_cb=self.delete_product,
            search_cb=self.open_search_dialog,
            delete_cond_cb=self.open_delete_dialog,
            save_cb=self.save_data,
            load_cb=self.load_data,
            page_change_cb=self.change_page
        )
        
        # Загружаем тестовые данные для демонстрации
        self.load_sample_data()
        self.refresh_view()
        
    def load_sample_data(self):
        """Загрузка тестовых данных для демонстрации"""
        sample_products = [
            Product("Ноутбук Lenovo IdeaPad", "Lenovo", "123456789", 15, "ул. Ленина, 10, склад 1"),
            Product("Смартфон Samsung Galaxy", "Samsung", "987654321", 23, "ул. Ленина, 10, склад 2"),
            Product("Монитор Dell UltraSharp", "Dell", "456789123", 8, "ул. Ленина, 10, склад 1"),
            Product("Клавиатура Logitech", "Logitech", "789123456", 42, "ул. Ленина, 10, склад 3"),
            Product("Мышь беспроводная", "Logitech", "789123457", 37, "ул. Ленина, 10, склад 3"),
            Product("Принтер HP LaserJet", "HP", "321654987", 5, "ул. Ленина, 10, склад 2"),
            Product("Внешний жесткий диск", "Western Digital", "147258369", 12, "ул. Ленина, 10, склад 1"),
            Product("Флешка USB 64GB", "SanDisk", "369258147", 56, "ул. Ленина, 10, склад 3"),
            Product("Наушники Sony", "Sony", "951753852", 19, "ул. Ленина, 10, склад 2"),
            Product("Веб-камера Logitech", "Logitech", "789123458", 9, "ул. Ленина, 10, склад 3"),
            Product("Планшет Samsung", "Samsung", "987654322", 7, "ул. Ленина, 10, склад 2"),
            Product("Роутер TP-Link", "TP-Link", "654321987", 14, "ул. Ленина, 10, склад 1"),
            Product("Сетевой фильтр", "APC", "852963741", 31, "ул. Ленина, 10, склад 3"),
            Product("Кабель HDMI 2м", "Belkin", "741852963", 84, "ул. Ленина, 10, склад 3"),
            Product("Адаптер питания", "Apple", "159753852", 11, "ул. Ленина, 10, склад 2")
        ]
        
        for product in sample_products:
            self.model.add_product(product)
            
    def refresh_view(self):
        """Обновление отображения данных"""
        start = self.model.current_page * self.model.items_per_page
        end = start + self.model.items_per_page
        page_products = self.model.products[start:end]
        self.view.update_table(
            page_products,
            self.model.current_page,
            len(self.model.products)
        )
        
    def add_product(self):
        """Добавление нового товара"""
        dialog = ProductDialog(self.view.root)
        product = dialog.show()
        if product:
            self.model.add_product(product)
            self.refresh_view()
            self.view.update_status(f"Товар '{product.name}' добавлен")
            
    def edit_product(self, index):
        """Редактирование товара"""
        # Получаем товар из текущей страницы
        global_index = self.model.current_page * self.model.items_per_page + index
        if global_index < len(self.model.products):
            product = self.model.products[global_index]
            dialog = ProductDialog(self.view.root, product)
            updated_product = dialog.show()
            if updated_product:
                self.model.update_product(global_index, updated_product)
                self.refresh_view()
                self.view.update_status(f"Товар '{updated_product.name}' обновлен")
                
    def delete_product(self, index):
        """Удаление товара"""
        global_index = self.model.current_page * self.model.items_per_page + index
        if global_index < len(self.model.products):
            product = self.model.products[global_index]
            if self.view.confirm_deletion(1):
                self.model.delete_product(global_index)
                # Корректируем текущую страницу после удаления
                self._adjust_page_after_deletion()
                self.refresh_view()
                self.view.update_status(f"Товар '{product.name}' удален")
                
    def _adjust_page_after_deletion(self):
        """Корректировка текущей страницы после удаления"""
        total_pages = (len(self.model.products) + self.model.items_per_page - 1) // self.model.items_per_page
        if self.model.current_page >= total_pages and self.model.current_page > 0:
            self.model.current_page = total_pages - 1
            if self.model.current_page < 0:
                self.model.current_page = 0
                
    def open_search_dialog(self):
        """Открытие диалога поиска"""
        dialog = SearchDialog(self.view.root, self.model)
        dialog.show()
        
    def open_delete_dialog(self):
        """Открытие диалога удаления с предварительным просмотром"""
        dialog = DeleteDialog(self.view.root, self.model)
        indices_to_delete = dialog.show()
    
        if indices_to_delete and len(indices_to_delete) > 0:
            # Удаляем товары по индексам (уже отсортированы в обратном порядке)
            deleted_count = 0
            deleted_products = []
            
            for idx in indices_to_delete:
                if 0 <= idx < len(self.model.products):
                    deleted_products.append(self.model.products[idx].name)
                    self.model.delete_product(idx)
                    deleted_count += 1
            
            # Показываем сообщение о результате
            if deleted_count > 0:
                self.view.show_message(
                    "Удаление завершено", 
                    f"✅ Успешно удалено {deleted_count} записей"
                )
                # Корректируем текущую страницу после удаления
                self._adjust_page_after_deletion()
                self.refresh_view()
                self.view.update_status(f"Удалено {deleted_count} записей")
            else:
                self.view.show_message("Ошибка", "Не удалось удалить выбранные записи")
                
    def save_data(self, filename):
        """Сохранение данных в файл"""
        if not filename:
            filename = self.view.get_save_filename()
            
        if filename:
            try:
                self.model.save_to_xml(filename)
                self.view.show_message("Сохранение", "Данные успешно сохранены")
                self.view.update_status(f"Данные сохранены в {filename}")
            except Exception as e:
                self.view.show_message("Ошибка", f"Ошибка при сохранении: {str(e)}")
                
    def load_data(self, filename):
        """Загрузка данных из файла"""
        if not filename:
            filename = self.view.get_load_filename()
            
        if filename:
            try:
                self.model.load_from_xml(filename)
                self.model.current_page = 0
                self.refresh_view()
                self.view.show_message("Загрузка", "Данные успешно загружены")
                self.view.update_status(f"Данные загружены из {filename}")
            except Exception as e:
                self.view.show_message("Ошибка", f"Ошибка при загрузке: {str(e)}")
                
    def change_page(self, page):
        """Смена страницы"""
        total_pages = (len(self.model.products) + self.model.items_per_page - 1) // self.model.items_per_page
        if 0 <= page < total_pages:
            self.model.current_page = page
            self.refresh_view()
