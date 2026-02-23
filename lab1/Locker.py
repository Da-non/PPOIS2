class Locker:
    """Ячейка почтомата"""
    
    def __init__(self, number: int, size: ParcelSize):
        """
        Инициализация ячейки
        
        Args:
            number: Номер ячейки
            size: Размер ячейки
        """
        self.number = number
        self.size = size
        self.is_occupied = False
        self.is_functional = True
        self.current_parcel: Optional[Parcel] = None
        self.last_maintenance: Optional[datetime] = None
    
    def open(self) -> bool:
        """Открытие ячейки"""
        if not self.is_functional:
            raise LockerError(f"Ячейка {self.number} неисправна")
        return True
    
    def close(self) -> bool:
        """Закрытие ячейки"""
        return True
    
    def put_parcel(self, parcel: Parcel) -> bool:
        """Помещение посылки в ячейку"""
        if not self.is_functional:
            raise LockerError(f"Ячейка {self.number} неисправна")
        
        if self.is_occupied:
            raise LockerError(f"Ячейка {self.number} уже занята")
        
        size_order = {ParcelSize.SMALL: 1, ParcelSize.MEDIUM: 2, ParcelSize.LARGE: 3}
        if size_order[parcel.size] > size_order[self.size]:
            raise LockerError(f"Посылка слишком большая для ячейки {self.number}")
        
        self.is_occupied = True
        self.current_parcel = parcel
        parcel.place_in_locker(self.number)
        return True
    
    def take_parcel(self) -> Parcel:
        """Извлечение посылки из ячейки"""
        if not self.is_functional:
            raise LockerError(f"Ячейка {self.number} неисправна")
        
        if not self.is_occupied:
            raise LockerError(f"Ячейка {self.number} пуста")
        
        parcel = self.current_parcel
        self.is_occupied = False
        self.current_parcel = None
        return parcel
    
    def repair(self) -> bool:
        """Ремонт ячейки"""
        self.is_functional = True
        self.last_maintenance = datetime.now()
        return True
    
    def get_info(self) -> Dict:
        """Информация о ячейке"""
        return {
            "number": self.number,
            "size": self.size.value,
            "occupied": self.is_occupied,
            "functional": self.is_functional,
            "parcel": self.current_parcel.tracking_number if self.current_parcel else None,
            "last_maintenance": self.last_maintenance.strftime("%d.%m.%Y") if self.last_maintenance else None
        }
    
    def __str__(self) -> str:
        status = "занята" if self.is_occupied else "свободна"
        functional = "исправна" if self.is_functional else "неисправна"
        return f"Ячейка {self.number} [{self.size.value}] {status} ({functional})"
