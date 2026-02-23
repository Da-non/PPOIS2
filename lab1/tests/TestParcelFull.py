class TestParcelFull(unittest.TestCase):
    """Полные тесты посылки"""
    
    def setUp(self):
        self.sender = Sender("Иван", "+375291234567", "ivan@ex.com", "ул. Ленина")
        self.recipient = Recipient("Петр", "+375331234567", "petr@ex.com")
        Parcel._existing_trackings.clear()
    
    def test_parcel_creation(self):
        """Тест создания посылки"""
        parcel = Parcel(self.sender, self.recipient, ParcelSize.MEDIUM, "Книги")
        self.assertIsNotNone(parcel.tracking_number)
        self.assertEqual(parcel.sender, self.sender)
        self.assertEqual(parcel.recipient, self.recipient)
        self.assertEqual(parcel.size, ParcelSize.MEDIUM)
        self.assertEqual(parcel.description, "Книги")
        self.assertEqual(parcel.status, ParcelStatus.CREATED)
        self.assertEqual(parcel.storage_days, 3)
        
        # Тест без описания
        parcel2 = Parcel(self.sender, self.recipient, ParcelSize.SMALL)
        self.assertEqual(parcel2.description, "")
    
    def test_parcel_validation(self):
        """Тест валидации посылки"""
        with self.assertRaises(ValidationError):
            Parcel(None, self.recipient, ParcelSize.SMALL)
        with self.assertRaises(ValidationError):
            Parcel(self.sender, None, ParcelSize.SMALL)
        with self.assertRaises(ValidationError):
            Parcel(self.sender, self.recipient, ParcelSize.SMALL, "Книги 5 шт")
    
    def test_tracking_generation(self):
        """Тест генерации трек-номера"""
        prefixes = set()
        for _ in range(20):
            parcel = Parcel(self.sender, self.recipient, ParcelSize.SMALL)
            self.assertTrue(Validator.validate_tracking(parcel.tracking_number))
            prefixes.add(parcel.tracking_number[:3])
            self.assertIn(parcel.tracking_number[:3], Parcel.TRACKING_PREFIXES)
        
        self.assertGreater(len(prefixes), 1)
    
    def test_tracking_uniqueness(self):
        """Тест уникальности трек-номеров"""
        parcels = [Parcel(self.sender, self.recipient, ParcelSize.SMALL) for _ in range(50)]
        trackings = [p.tracking_number for p in parcels]
        self.assertEqual(len(trackings), len(set(trackings)))
        self.assertEqual(len(Parcel._existing_trackings), 50)
    
    def test_tracking_generation_all_prefixes(self):
        """Тест генерации всех возможных префиксов"""
        Parcel._existing_trackings.clear()
        prefixes = set()
        
        for _ in range(50):
            p = Parcel(self.sender, self.recipient, ParcelSize.SMALL)
            prefixes.add(p.tracking_number[:3])
        
        # Проверяем, что сгенерировались разные префиксы
        self.assertGreater(len(prefixes), 1)
    
    def test_place_in_locker(self):
        """Тест размещения в ячейке"""
        parcel = Parcel(self.sender, self.recipient, ParcelSize.SMALL)
        parcel.place_in_locker(5)
        
        self.assertEqual(parcel.status, ParcelStatus.IN_POSTOMAT)
        self.assertEqual(parcel.locker_number, 5)
        self.assertIsNotNone(parcel.placed_at)
        self.assertIsNotNone(parcel.storage_until)
        
        expected = parcel.placed_at + timedelta(days=3)
        self.assertEqual(parcel.storage_until.date(), expected.date())
    
    def test_deliver(self):
        """Тест получения"""
        parcel = Parcel(self.sender, self.recipient, ParcelSize.SMALL)
        parcel.deliver()
        
        self.assertEqual(parcel.status, ParcelStatus.DELIVERED)
        self.assertIsNotNone(parcel.delivered_at)
    
    def test_is_expired(self):
        """Тест проверки просрочки"""
        parcel = Parcel(self.sender, self.recipient, ParcelSize.SMALL)
        
        # Не размещена
        self.assertFalse(parcel.is_expired())
        
        # Размещена, не просрочена
        parcel.place_in_locker(5)
        self.assertFalse(parcel.is_expired())
        
        # Просрочена
        parcel.storage_until = datetime.now() - timedelta(days=1)
        self.assertTrue(parcel.is_expired())
        
        # Точно в момент истечения
        parcel.storage_until = datetime.now()
        self.assertFalse(parcel.is_expired())
        
        # Без storage_until
        parcel.storage_until = None
        self.assertFalse(parcel.is_expired())
    
    def test_get_info(self):
        """Тест получения информации"""
        parcel = Parcel(self.sender, self.recipient, ParcelSize.MEDIUM, "Книги")
        
        info = parcel.get_info()
        self.assertEqual(info["tracking"], parcel.tracking_number)
        self.assertEqual(info["size"], "M")
        self.assertEqual(info["status"], "создана")
        self.assertIsNone(info["locker"])
        
        parcel.place_in_locker(5)
        info = parcel.get_info()
        self.assertEqual(info["locker"], 5)
        self.assertIsNotNone(info["storage_until"])
    
    def test_str(self):
        """Тест строкового представления"""
        parcel = Parcel(self.sender, self.recipient, ParcelSize.SMALL)
        expected = f"Посылка {parcel.tracking_number} [S] - создана"
        self.assertEqual(str(parcel), expected)

