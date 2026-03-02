class ProductModel:
    """Модель данных для работы с товарами"""
    
    def __init__(self):
        self.products: List[Product] = []
        self.current_page = 0
        self.items_per_page = 10
        
    def add_product(self, product: Product):
        """Добавление товара"""
        self.products.append(product)
        
    def update_product(self, index: int, product: Product):
        """Обновление товара"""
        if 0 <= index < len(self.products):
            self.products[index] = product
            
    def delete_product(self, index: int):
        """Удаление товара по индексу"""
        if 0 <= index < len(self.products):
            del self.products[index]
            
    def delete_by_conditions(self, conditions: Dict) -> int:
        """Удаление товаров по условиям"""
        to_delete = []
        for i, product in enumerate(self.products):
            if self._matches_conditions(product, conditions):
                to_delete.append(i)
        
        # Удаляем с конца, чтобы не сбивать индексы
        for i in reversed(to_delete):
            del self.products[i]
            
        return len(to_delete)
    
    def search(self, conditions: Dict) -> List[Product]:
        """Поиск товаров по условиям"""
        return [p for p in self.products if self._matches_conditions(p, conditions)]
    
    def _matches_conditions(self, product: Product, conditions: Dict) -> bool:
        """Проверка соответствия товара условиям"""
        matches = []
        
        # Условие по названию товара или количеству
        if 'name_or_quantity' in conditions:
            cond = conditions['name_or_quantity']
            if cond.get('name'):
                matches.append(cond['name'].lower() in product.name.lower())
            if cond.get('quantity') is not None:
                matches.append(product.quantity == cond['quantity'])
                
        # Условие по производителю или УНП
        if 'manufacturer_or_unp' in conditions:
            cond = conditions['manufacturer_or_unp']
            if cond.get('manufacturer'):
                matches.append(cond['manufacturer'].lower() in product.manufacturer.lower())
            if cond.get('unp'):
                matches.append(cond['unp'] == product.unp)
                
        return any(matches) if matches else True
    
    def save_to_xml(self, filename: str):
        """Сохранение данных в XML (DOM парсер)"""
        doc = DOM.Document()
        root = doc.createElement('products')
        doc.appendChild(root)
        
        for product in self.products:
            product_elem = doc.createElement('product')
            
            name = doc.createElement('name')
            name.appendChild(doc.createTextNode(product.name))
            product_elem.appendChild(name)
            
            manufacturer = doc.createElement('manufacturer')
            manufacturer.appendChild(doc.createTextNode(product.manufacturer))
            product_elem.appendChild(manufacturer)
            
            unp = doc.createElement('unp')
            unp.appendChild(doc.createTextNode(product.unp))
            product_elem.appendChild(unp)
            
            quantity = doc.createElement('quantity')
            quantity.appendChild(doc.createTextNode(str(product.quantity)))
            product_elem.appendChild(quantity)
            
            address = doc.createElement('address')
            address.appendChild(doc.createTextNode(product.address))
            product_elem.appendChild(address)
            
            root.appendChild(product_elem)
            
        with open(filename, 'w', encoding='utf-8') as f:
            doc.writexml(f, indent='  ', addindent='  ', newl='\n', encoding='utf-8')
    
    def load_from_xml(self, filename: str):
        """Загрузка данных из XML (SAX парсер)"""
        handler = ProductXMLHandler()
        parser = xml.sax.make_parser()
        parser.setContentHandler(handler)
        parser.parse(filename)
        self.products = handler.products
