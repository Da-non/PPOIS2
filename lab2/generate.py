import xml.dom.minidom as DOM
import random

def save_to_xml(filename, products, category_name):
    """
    Функция для сохранения списка товаров в XML файл
    
    filename - имя файла 
    products - список товаров для сохранения
    category_name - название категории (для вывода в консоль)
    """
    
    # Создаем новый DOM документ
    doc = DOM.Document()
    
    # Создаем корневой элемент <products>
    root = doc.createElement('products')
    doc.appendChild(root)
    
    # Проходим по всем товарам и добавляем их в XML
    for name, manufacturer, unp, quantity, address in products:
        # Создаем элемент <product> для каждого товара
        product_elem = doc.createElement('product')
        
        # Добавляем поле <name>
        name_elem = doc.createElement('name')
        name_elem.appendChild(doc.createTextNode(name))
        product_elem.appendChild(name_elem)
        
        # Добавляем поле <manufacturer>
        manufacturer_elem = doc.createElement('manufacturer')
        manufacturer_elem.appendChild(doc.createTextNode(manufacturer))
        product_elem.appendChild(manufacturer_elem)
        
        # Добавляем поле <unp>
        unp_elem = doc.createElement('unp')
        unp_elem.appendChild(doc.createTextNode(unp))
        product_elem.appendChild(unp_elem)
        
        # Добавляем поле <quantity>
        quantity_elem = doc.createElement('quantity')
        quantity_elem.appendChild(doc.createTextNode(str(quantity)))
        product_elem.appendChild(quantity_elem)
        
        # Добавляем поле <address>
        address_elem = doc.createElement('address')
        address_elem.appendChild(doc.createTextNode(address))
        product_elem.appendChild(address_elem)
        
        # Добавляем готовый <product> в корневой элемент
        root.appendChild(product_elem)
    
    # Сохраняем XML в файл с красивым форматированием
    with open(filename, 'w', encoding='utf-8') as f:
        doc.writexml(f, indent='  ', addindent='  ', newl='\n', encoding='utf-8')
    
    print(f" Создан файл {filename} с {len(products)} записями ({category_name})")

streets = [
    "ул. Ленина",
    "ул. Калинина",
    "ул. Барбоскина",
    "ул. Дрозда",
    "ул. Мазурова",
    "ул. Кожура",
    "ул. Лейма",
    "ул. Кустовая",
    "ул. Гагарина",
    "ул. Пушкина",
    "ул. Советская",
    "ул. Кирова",
    "ул. Орловского",
    "ул. Якуба Коласа",
    "ул. Янки Купалы",
    "пр-т Независимости",
    "пр-т Победителей",
    "ул. Немига",
    "ул. Притыцкого",
    "ул. Сурганова",
    "ул. Богдановича",
    "ул. Веры Хоружей",
    "ул. Красная",
    "ул. Зеленая",
    "ул. Садовая",
    "ул. Широкая",
    "ул. Новая",
    "ул. Заводская",
    "ул. Парковая",
    "ул. Шоссейная"
]

# Номера домов
house_numbers = [2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50]

# Номера складов
warehouses = [
    "склад A1", "склад A2", "склад A3", "склад A4", "склад A5",
    "склад B1", "склад B2", "склад B3", "склад B4", "склад B5",
    "склад C1", "склад C2", "склад C3", "склад C4", "склад C5",
    "склад D1", "склад D2", "склад D3", "склад D4", "склад D5",
    "склад E1", "склад E2", "склад E3", "склад E4", "склад E5"
]

# Дополнительная информация о месте
locations = [
    "ряд 1", "ряд 2", "ряд 3", 
    "стеллаж 1", "стеллаж 2", "стеллаж 3", 
    "секция А", "секция Б", "секция В",
    "ячейка 1", "ячейка 2", "ячейка 3",
    "паллет 1", "паллет 2", "паллет 3"
]

def generate_address():
    """Генерирует случайный адрес с разными улицами"""
    street = random.choice(streets)
    house = random.choice(house_numbers)
    warehouse = random.choice(warehouses)
    location = random.choice(locations)
    return f"{street}, {house}, {warehouse}, {location}"

# ФАЙЛ 1: КОМПЬЮТЕРНАЯ ТЕХНИКА - 50 записей

computer_products = []
computer_products.append(("Ноутбук Lenovo IdeaPad 3 15ITL6", "Lenovo", "100000001", 15, generate_address()))
computer_products.append(("Ноутбук ASUS ROG Strix G15", "ASUS", "100000002", 8, generate_address()))
computer_products.append(("Ноутбук HP Pavilion 15-eg0000", "HP", "100000003", 12, generate_address()))
computer_products.append(("Ноутбук Dell XPS 13 9310", "Dell", "100000004", 5, generate_address()))
computer_products.append(("Ноутбук Acer Aspire 5 A515", "Acer", "100000005", 20, generate_address()))
computer_products.append(("Ноутбук MSI Modern 14", "MSI", "100000006", 7, generate_address()))
computer_products.append(("Ноутбук Huawei MateBook D15", "Huawei", "100000007", 10, generate_address()))
computer_products.append(("Ноутбук Apple MacBook Air M1", "Apple", "100000008", 6, generate_address()))
computer_products.append(("Ноутбук Microsoft Surface Laptop 4", "Microsoft", "100000009", 4, generate_address()))
computer_products.append(("Ноутбук Razer Blade 15", "Razer", "100000010", 3, generate_address()))
computer_products.append(("Ноутбук Xiaomi Mi Notebook Pro", "Xiaomi", "100000011", 9, generate_address()))
computer_products.append(("Ноутбук ASUS TUF Gaming F15", "ASUS", "100000012", 11, generate_address()))
computer_products.append(("Ноутбук Lenovo ThinkPad X1 Carbon", "Lenovo", "100000013", 7, generate_address()))
computer_products.append(("Ноутбук HP EliteBook 840", "HP", "100000014", 5, generate_address()))
computer_products.append(("Ноутбук Dell Latitude 7430", "Dell", "100000015", 4, generate_address()))
computer_products.append(("Монитор Dell UltraSharp U2723QE", "Dell", "200000001", 12, generate_address()))
computer_products.append(("Монитор Samsung Odyssey G7", "Samsung", "200000002", 8, generate_address()))
computer_products.append(("Монитор LG 27GN950-B", "LG", "200000003", 5, generate_address()))
computer_products.append(("Монитор ASUS ROG Swift PG279Q", "ASUS", "200000004", 4, generate_address()))
computer_products.append(("Монитор Acer Predator XB273U", "Acer", "200000005", 6, generate_address()))
computer_products.append(("Монитор BenQ PD3220U", "BenQ", "200000006", 3, generate_address()))
computer_products.append(("Монитор Philips 346B1C", "Philips", "200000007", 7, generate_address()))
computer_products.append(("Монитор ViewSonic VP3881", "ViewSonic", "200000008", 4, generate_address()))
computer_products.append(("Монитор Iiyama ProLite", "Iiyama", "200000009", 9, generate_address()))
computer_products.append(("Монитор AOC U34E2M", "AOC", "200000010", 11, generate_address()))
computer_products.append(("Клавиатура Logitech MX Mechanical", "Logitech", "300000001", 35, generate_address()))
computer_products.append(("Клавиатура Razer BlackWidow V3", "Razer", "300000002", 28, generate_address()))
computer_products.append(("Клавиатура Corsair K70 RGB", "Corsair", "300000003", 19, generate_address()))
computer_products.append(("Клавиатура Keychron K2", "Keychron", "300000004", 22, generate_address()))
computer_products.append(("Клавиатура Ducky One 2", "Ducky", "300000005", 16, generate_address()))
computer_products.append(("Клавиатура HyperX Alloy Origins", "HyperX", "300000006", 31, generate_address()))
computer_products.append(("Клавиатура SteelSeries Apex Pro", "SteelSeries", "300000007", 14, generate_address()))
computer_products.append(("Клавиатура Logitech G915", "Logitech", "300000008", 17, generate_address()))
computer_products.append(("Клавиатура Apple Magic Keyboard", "Apple", "300000009", 12, generate_address()))
computer_products.append(("Клавиатура Microsoft Designer", "Microsoft", "300000010", 25, generate_address()))
computer_products.append(("Мышь Logitech MX Master 3S", "Logitech", "400000001", 45, generate_address()))
computer_products.append(("Мышь Razer DeathAdder V2", "Razer", "400000002", 52, generate_address()))
computer_products.append(("Мышь SteelSeries Rival 600", "SteelSeries", "400000003", 31, generate_address()))
computer_products.append(("Мышь Corsair Dark Core", "Corsair", "400000004", 27, generate_address()))
computer_products.append(("Мышь Logitech G502 Hero", "Logitech", "400000005", 38, generate_address()))
computer_products.append(("Мышь ASUS ROG Gladius", "ASUS", "400000006", 23, generate_address()))
computer_products.append(("Мышь HyperX Pulsefire", "HyperX", "400000007", 34, generate_address()))
computer_products.append(("Мышь Apple Magic Mouse", "Apple", "400000008", 19, generate_address()))
computer_products.append(("Мышь Microsoft Arc Mouse", "Microsoft", "400000009", 16, generate_address()))
computer_products.append(("Мышь Zowie EC2", "Zowie", "400000010", 21, generate_address()))
computer_products.append(("Видеокарта MSI RTX 4080", "MSI", "500000001", 3, generate_address()))
computer_products.append(("Видеокарта ASUS RTX 4070 Ti", "ASUS", "500000002", 5, generate_address()))
computer_products.append(("Процессор Intel Core i9-13900K", "Intel", "500000003", 12, generate_address()))
computer_products.append(("Процессор AMD Ryzen 9 7950X", "AMD", "500000004", 10, generate_address()))
computer_products.append(("Оперативная память Corsair 32GB", "Corsair", "500000005", 25, generate_address()))

# ФАЙЛ 2: ОБУВЬ (КЕДЫ И ДРУГАЯ ОБУВЬ) - 50 записей

shoes_products = []
shoes_products.append(("Кеды Converse Chuck Taylor All Star", "Converse", "600000001", 45, generate_address()))
shoes_products.append(("Кеды Vans Old Skool", "Vans", "600000002", 38, generate_address()))
shoes_products.append(("Кроссовки Nike Air Force 1", "Nike", "600000003", 52, generate_address()))
shoes_products.append(("Кроссовки Adidas Superstar", "Adidas", "600000004", 47, generate_address()))
shoes_products.append(("Кеды Puma Suede Classic", "Puma", "600000005", 31, generate_address()))
shoes_products.append(("Кроссовки New Balance 574", "New Balance", "600000006", 29, generate_address()))
shoes_products.append(("Кеды Reebok Club C 85", "Reebok", "600000007", 34, generate_address()))
shoes_products.append(("Кроссовки Asics Gel-Lyte III", "Asics", "600000008", 23, generate_address()))
shoes_products.append(("Кеды Fila Disruptor", "Fila", "600000009", 27, generate_address()))
shoes_products.append(("Кроссовки Saucony Jazz Original", "Saucony", "600000010", 19, generate_address()))
shoes_products.append(("Кеды Nike SB Dunk Low", "Nike", "600000011", 16, generate_address()))
shoes_products.append(("Кроссовки Adidas NMD R1", "Adidas", "600000012", 22, generate_address()))
shoes_products.append(("Кеды Vans Authentic", "Vans", "600000013", 41, generate_address()))
shoes_products.append(("Кроссовки Puma RS-X", "Puma", "600000014", 28, generate_address()))
shoes_products.append(("Кеды Converse Run Star Hike", "Converse", "600000015", 33, generate_address()))
shoes_products.append(("Кроссовки Reebok Classic Leather", "Reebok", "600000016", 37, generate_address()))
shoes_products.append(("Кеды New Balance 327", "New Balance", "600000017", 25, generate_address()))
shoes_products.append(("Кроссовки Nike Air Max 90", "Nike", "600000018", 42, generate_address()))
shoes_products.append(("Кеды Adidas Stan Smith", "Adidas", "600000019", 39, generate_address()))
shoes_products.append(("Кроссовки Asics Gel-Kayano 14", "Asics", "600000020", 18, generate_address()))
shoes_products.append(("Кеды Puma Cali", "Puma", "600000021", 26, generate_address()))
shoes_products.append(("Кроссовки Fila Ray Tracer", "Fila", "600000022", 21, generate_address()))
shoes_products.append(("Кеды Vans Sk8-Hi", "Vans", "600000023", 32, generate_address()))
shoes_products.append(("Кроссовки New Balance 990v5", "New Balance", "600000024", 15, generate_address()))
shoes_products.append(("Кеды Converse Chuck 70", "Converse", "600000025", 44, generate_address()))
shoes_products.append(("Ботинки Timberland 6-Inch Premium", "Timberland", "600000026", 18, generate_address()))
shoes_products.append(("Ботинки Dr. Martens 1460", "Dr. Martens", "600000027", 22, generate_address()))
shoes_products.append(("Полуботинки Clarks Desert Boot", "Clarks", "600000028", 16, generate_address()))
shoes_products.append(("Ботинки Caterpillar Colorado", "Caterpillar", "600000029", 14, generate_address()))
shoes_products.append(("Полуботинки ECCO Soft 7", "ECCO", "600000030", 19, generate_address()))
shoes_products.append(("Ботинки Red Wing Iron Ranger", "Red Wing", "600000031", 8, generate_address()))
shoes_products.append(("Полуботинки Geox Nebula", "Geox", "600000032", 23, generate_address()))
shoes_products.append(("Ботинки The North Face Back-to-Berkeley", "The North Face", "600000033", 11, generate_address()))
shoes_products.append(("Полуботинки Skechers Memory Foam", "Skechers", "600000034", 37, generate_address()))
shoes_products.append(("Ботинки Columbia Newton Ridge", "Columbia", "600000035", 13, generate_address()))
shoes_products.append(("Туфли мужские классические", "Baldinini", "600000036", 12, generate_address()))
shoes_products.append(("Лоферы женские на каблуке", "Tamaris", "600000037", 24, generate_address()))
shoes_products.append(("Туфли женские лодочки", "Ralf Ringer", "600000038", 31, generate_address()))
shoes_products.append(("Лоферы мужские с кисточками", "Hugo Boss", "600000039", 9, generate_address()))
shoes_products.append(("Туфли офисные женские", "ECCO", "600000040", 17, generate_address()))
shoes_products.append(("Лоферы на платформе", "Vagabond", "600000041", 21, generate_address()))
shoes_products.append(("Туфли мужские замшевые", "Loake", "600000042", 7, generate_address()))
shoes_products.append(("Лоферы с цепочкой", "Guess", "600000043", 15, generate_address()))
shoes_products.append(("Сандалии мужские кожаные", "Birkenstock", "600000044", 26, generate_address()))
shoes_products.append(("Шлепанцы пляжные резиновые", "Havaianas", "600000045", 58, generate_address()))
shoes_products.append(("Сандалии женские на платформе", "Teva", "600000046", 33, generate_address()))
shoes_products.append(("Шлепанцы домашние", "Crocs", "600000047", 42, generate_address()))
shoes_products.append(("Сандалии спортивные", "Keen", "600000048", 19, generate_address()))
shoes_products.append(("Шлепанцы с ремешком", "Adidas", "600000049", 37, generate_address()))
shoes_products.append(("Сабо женские", "Crocs", "600000050", 28, generate_address()))
print("="*60)
print("ГЕНЕРАЦИЯ XML ФАЙЛОВ С ТОВАРАМИ")
print("="*60)
save_to_xml("computers_50.xml", computer_products, "компьютерная техника")
save_to_xml("shoes_50.xml", shoes_products, "обувь (кеды, кроссовки и др.)")
print("\n" + "="*60)
print(" ВСЕ ФАЙЛЫ УСПЕШНО СОЗДАНЫ!")
print("="*60)
print("\nСозданные файлы:")
print("   computers_50.xml - 50 записей (компьютерная техника)")
print("   shoes_50.xml - 50 записей (обувь, включая кеды)")
print("\nКак использовать:")
print("1. Запустите программу: python main.py")
print("2. Нажмите кнопку 'Загрузить'")
print("3. Выберите один из созданных файлов")
print("4. Просматривайте записи (5 страниц по 10 записей)")
