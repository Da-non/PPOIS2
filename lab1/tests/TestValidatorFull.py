class TestValidatorFull(unittest.TestCase):
    """Полные тесты валидатора"""
    
    def test_validate_phone(self):
        """Полный тест валидации телефона"""
        # Валидные
        valid = [
            "+375291234567", "80291234567", "375291234567", "8291234567",
            "+375 29 123-45-67", "8 029 1234567", "8-029-123-45-67",
            "+375441234567", "+375251234567", "+375331234567", "+375241234567"
        ]
        for phone in valid:
            self.assertTrue(Validator.validate_phone(phone), f"Failed for {phone}")
        
        # Невалидные
        invalid = [
            "", "12345", "+3752912345", "+37529123456789",
            "80501234567", "abc", "8 55 1234567",
        ]
        for phone in invalid:
            self.assertFalse(Validator.validate_phone(phone), f"Failed for {phone}")
    
    def test_validate_phone_all_operators(self):
        """Тест всех допустимых кодов операторов"""
        operators = ["24", "25", "29", "33", "44"]
        for op in operators:
            phone = f"+375{op}1234567"
            self.assertTrue(Validator.validate_phone(phone), f"Failed for operator {op}")
    
    def test_validate_email(self):
        """Полный тест валидации email"""
        valid = [
            "user@example.com", "user.name@example.by", "user+filter@ex.com",
            "user@subdomain.example.com", "UPPERCASE@EXAMPLE.COM",
            "first.last@example.com", "user@example.co.uk", "user+test@example.com"
        ]
        for email in valid:
            self.assertTrue(Validator.validate_email(email), f"Failed for {email}")
        
        invalid = [
            "", "user", "user@", "@example.com", "user@.com",
            "user@com", "user@example.", "user@exam ple.com",
            ".user@example.com", "user@example..com"
        ]
        for email in invalid:
            self.assertFalse(Validator.validate_email(email), f"Failed for {email}")
    
    def test_validate_name(self):
        """Полный тест валидации имени"""
        valid = ["Иван", "Иван Петров", "Иван-Петр", "John Doe", "Анна-Мария"]
        for name in valid:
            self.assertTrue(Validator.validate_name(name), f"Failed for {name}")
        
        invalid = ["", "А", "Иван123", "123", "Иван@", "Иван_Петров", "  "]
        for name in invalid:
            self.assertFalse(Validator.validate_name(name), f"Failed for {name}")
    
    def test_validate_description(self):
        """Полный тест валидации описания"""
        valid = ["", "Книги", "Одежда, обувь", "Документы!", "Хрупкий груз - стекло"]
        for desc in valid:
            self.assertTrue(Validator.validate_description(desc), f"Failed for {desc}")
        
        invalid = ["Товар №123", "123", "Книги 5 шт", "Артикул 4567"]
        for desc in invalid:
            self.assertFalse(Validator.validate_description(desc), f"Failed for {desc}")
    
    def test_validate_address(self):
        """Полный тест валидации адреса"""
        valid = [
            "ул. Ленина, д. 1", "пр. Независимости, 10", "Минск, ул. Пушкина",
            "д. Боровляны, ул. Центральная, 5"
        ]
        for addr in valid:
            self.assertTrue(Validator.validate_address(addr), f"Failed for {addr}")
        
        invalid = ["", "ул", "12345", "дом", "  "]
        for addr in invalid:
            self.assertFalse(Validator.validate_address(addr), f"Failed for {addr}")
    
    def test_validate_tracking(self):
        """Полный тест валидации трек-номера"""
        valid = [
            "ABC12345", "XYZ1234567890", "PKG123456", "BOX123456789012345",
            "TRK123456", "DLV123456789", "POS1234567"
        ]
        for track in valid:
            self.assertTrue(Validator.validate_tracking(track), f"Failed for {track}")
        
        invalid = [
            "", "abc12345", "AB12345", "ABC123", "ABC" + "1"*20,
            "12345678", "ABC!2345", "ABC 1234", None
        ]
        for track in invalid:
            self.assertFalse(Validator.validate_tracking(track), f"Failed for {track}")
    
    def test_normalize_phone(self):
        """Тест нормализации телефона"""
        test_cases = [
            ("+375291234567", "+375291234567"),
            ("80291234567", "+375291234567"),
            ("375291234567", "+375291234567"),
            ("8291234567", "+375291234567"),
            ("8 029 123-45-67", "+375291234567"),
            ("8-029-123-45-67", "+375291234567"),
        ]
        for inp, expected in test_cases:
            self.assertEqual(Validator.normalize_phone(inp), expected, f"Failed for {inp}")
