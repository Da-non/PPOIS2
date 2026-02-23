class Recipient(Person):
    """Получатель посылки"""
    
    def __init__(self, name: str, phone: str, email: str):
        """Инициализация получателя"""
        super().__init__(name, phone, email)
    
    def __str__(self) -> str:
        return f"Получатель: {self.name}"
