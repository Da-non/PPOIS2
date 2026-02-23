class Parcel:
    """Почтовое отправление"""
    
    _existing_trackings: Set[str] = set()
    TRACKING_PREFIXES = ["ABC", "XYZ", "TRK", "PKG", "BOX", "SHP", "DLV", "POS"]
    
    def __init__(self, 
                 sender: Sender,
                 recipient: Recipient,
                 size: ParcelSize,
                 description: str = ""):
        """
        Инициализация посылки с автоматической генерацией трек-номера
        
        Args:
            sender: Отправитель
            recipient: Получатель
            size: Размер
            description: Описание (без цифр)
            
        Raises:
            ValidationError: Если описание содержит цифры
        """
        if not sender or not recipient:
            raise ValidationError("Отправитель и получатель обязательны")
        
        # Проверка описания на наличие цифр
        if not Validator.validate_description(description):
            raise ValidationError("Описание посылки не должно содержать цифр")
        
        self.tracking_number = self._generate_unique_tracking()
        self.sender = sender
        self.recipient = recipient
        self.size = size
        self.description = description.strip()
        self.status = ParcelStatus.CREATED
        self.created_at = datetime.now()
        self.placed_at: Optional[datetime] = None
        self.delivered_at: Optional[datetime] = None
        self.locker_number: Optional[int] = None
        self.storage_days = 3
        self.storage_until: Optional[datetime] = None
    
    @classmethod
    def _generate_unique_tracking(cls) -> str:
        """Генерация уникального трек-номера"""
        while True:
            prefix = random.choice(cls.TRACKING_PREFIXES)
            numbers = ''.join([str(random.randint(0, 9)) for _ in range(10)])
            tracking = f"{prefix}{numbers}"
            
            if tracking not in cls._existing_trackings:
                cls._existing_trackings.add(tracking)
                return tracking
    
    def place_in_locker(self, locker_number: int):
        """Размещение в ячейке"""
        self.status = ParcelStatus.IN_POSTOMAT
        self.placed_at = datetime.now()
        self.locker_number = locker_number
        self.storage_until = datetime.now() + timedelta(days=self.storage_days)
    
    def deliver(self):
        """Получение посылки"""
        self.status = ParcelStatus.DELIVERED
        self.delivered_at = datetime.now()
    
    def is_expired(self) -> bool:
        """Проверка на просрочку"""
        if not self.storage_until:
            return False
        return datetime.now() > self.storage_until
    
    def get_info(self) -> Dict:
        """Получение информации о посылке"""
        return {
            "tracking": self.tracking_number,
            "sender": str(self.sender),
            "recipient": str(self.recipient),
            "size": self.size.value,
            "description": self.description,
            "status": self.status.value,
            "created": self.created_at.strftime("%d.%m.%Y %H:%M"),
            "locker": self.locker_number,
            "storage_until": self.storage_until.strftime("%d.%m.%Y") if self.storage_until else None
        }
    
    def __str__(self) -> str:
        return f"Посылка {self.tracking_number} [{self.size.value}] - {self.status.value}"

