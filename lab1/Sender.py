class Sender(Person):
    """Отправитель посылки"""
    
    def __init__(self, name: str, phone: str, email: str, address: str):
        """
        Инициализация отправителя
        
        Args:
            name: Имя
            phone: Телефон
            email: Email
            address: Адрес отправителя
        """
        super().__init__(name, phone, email)
        
        if not Validator.validate_address(address):
            raise ValidationError(
                "Адрес должен содержать минимум 5 символов и не состоять только из цифр"
            )
        
        self.address = address.strip()
    
    def __str__(self) -> str:
        return f"Отправитель: {self.name}, адрес: {self.address}"

