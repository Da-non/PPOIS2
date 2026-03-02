import xml.dom.minidom as DOM
import xml.sax
from typing import List, Dict
from dataclasses import dataclass, asdict

@dataclass
class Product:
    """Класс записи о товаре"""
    name: str
    manufacturer: str
    unp: str  # УНП производителя
    quantity: int  # Количество на складе
    address: str  # Адрес склада
    
    def to_dict(self):
        return asdict(self)
