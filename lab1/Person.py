class Person:
    """Базовый класс для отправителя и получателя"""
    
    def __init__(self, name: str, phone: str, email: str):
        """
        Инициализация персоны
        
        Args:
            name: Имя
            phone: Телефон
            email: Email
            
        Raises:
            ValidationError: Если данные не проходят валидацию
        """
        if not Validator.validate_name(name):
            raise ValidationError(
                "Имя должно содержать минимум 2 символа и только буквы, пробелы или дефис (без цифр)"
            )
        
        if not Validator.validate_phone(phone):
            raise ValidationError(
                "Неверный формат телефона. Используйте +375 и код оператора (24,25,29,33,44). "
                "Пример: +375291234567"
            )
        
        if not Validator.validate_email(email):
            raise ValidationError(
                "Неверный формат email. Пример: name@domain.by"
            )
        
        self.name = name.strip()
        self.phone = Validator.normalize_phone(phone)
        self.email = email.strip().lower()
        self.id = self._generate_id()
    
    def _generate_id(self) -> str:
        """Генерация уникального идентификатора"""
        data = f"{self.name}{self.phone}{self.email}".encode()
        return hashlib.md5(data).hexdigest()[:10]
    
    def __str__(self) -> str:
        return f"{self.name}"
