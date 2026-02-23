class TestPersonFull(unittest.TestCase):
    """Полные тесты классов персон"""
    
    def setUp(self):
        self.name = "Иван Петров"
        self.phone = "+375291234567"
        self.email = "ivan@example.com"
        self.address = "ул. Ленина, 10"
    
    def test_person_creation(self):
        """Тест создания персоны"""
        person = Person(self.name, self.phone, self.email)
        self.assertEqual(person.name, self.name)
        self.assertEqual(person.phone, self.phone)
        self.assertEqual(person.email, self.email)
        self.assertEqual(len(person.id), 10)
        
        # Тест строкового представления
        self.assertEqual(str(person), self.name)
    
    def test_person_normalization(self):
        """Тест нормализации данных"""
        person = Person("  Иван Петров  ", "8 029 123-45-67", "  IVAN@EXAMPLE.COM  ")
        self.assertEqual(person.name, "Иван Петров")
        self.assertEqual(person.phone, "+375291234567")
        self.assertEqual(person.email, "ivan@example.com")
    
    def test_person_id_generation(self):
        """Тест генерации ID"""
        p1 = Person(self.name, self.phone, self.email)
        p2 = Person(self.name, self.phone, self.email)
        p3 = Person("Другой", self.phone, self.email)
        
        self.assertEqual(p1.id, p2.id)
        self.assertNotEqual(p1.id, p3.id)
    
    def test_person_id_uniqueness(self):
        """Тест уникальности ID для разных данных"""
        p1 = Person("Иван", "+375291234567", "ivan@ex.com")
        p2 = Person("Петр", "+375291234567", "ivan@ex.com")
        p3 = Person("Иван", "+375331234567", "ivan@ex.com")
        
        self.assertNotEqual(p1.id, p2.id)
        self.assertNotEqual(p1.id, p3.id)
    
    def test_person_validation_errors(self):
        """Тест ошибок валидации"""
        with self.assertRaises(ValidationError):
            Person("123", self.phone, self.email)
        with self.assertRaises(ValidationError):
            Person(self.name, "123", self.email)
        with self.assertRaises(ValidationError):
            Person(self.name, self.phone, "invalid")
    
    def test_sender_creation(self):
        """Тест создания отправителя"""
        sender = Sender(self.name, self.phone, self.email, self.address)
        self.assertEqual(sender.address, self.address)
        self.assertIn("Отправитель", str(sender))
        self.assertIn(self.name, str(sender))
    
    def test_sender_invalid_address(self):
        """Тест невалидного адреса отправителя"""
        with self.assertRaises(ValidationError):
            Sender(self.name, self.phone, self.email, "ул")
    
    def test_recipient_creation(self):
        """Тест создания получателя"""
        recipient = Recipient(self.name, self.phone, self.email)
        self.assertIn("Получатель", str(recipient))
        self.assertIn(self.name, str(recipient))

