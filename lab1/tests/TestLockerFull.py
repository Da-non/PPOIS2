class TestLockerFull(unittest.TestCase):
    """Полные тесты ячейки"""
    
    def setUp(self):
        self.locker = Locker(1, ParcelSize.MEDIUM)
        self.sender = Sender("Иван", "+375291234567", "ivan@ex.com", "ул. Ленина")
        self.recipient = Recipient("Петр", "+375331234567", "petr@ex.com")
    
    def test_locker_creation(self):
        """Тест создания ячейки"""
        self.assertEqual(self.locker.number, 1)
        self.assertEqual(self.locker.size, ParcelSize.MEDIUM)
        self.assertFalse(self.locker.is_occupied)
        self.assertTrue(self.locker.is_functional)
        self.assertIsNone(self.locker.current_parcel)
        self.assertIsNone(self.locker.last_maintenance)
    
    def test_open_close(self):
        """Тест открытия/закрытия"""
        self.assertTrue(self.locker.open())
        self.assertTrue(self.locker.close())
        
        # Неисправная ячейка
        self.locker.is_functional = False
        with self.assertRaises(LockerError):
            self.locker.open()
    
    def test_put_parcel(self):
        """Тест размещения посылки"""
        # Маленькая в среднюю
        parcel = Parcel(self.sender, self.recipient, ParcelSize.SMALL)
        self.assertTrue(self.locker.put_parcel(parcel))
        self.assertTrue(self.locker.is_occupied)
        self.assertEqual(self.locker.current_parcel, parcel)
        self.assertEqual(parcel.locker_number, 1)
        self.assertEqual(parcel.status, ParcelStatus.IN_POSTOMAT)
    
    def test_put_parcel_same_size(self):
        """Тест размещения посылки такого же размера"""
        parcel = Parcel(self.sender, self.recipient, ParcelSize.MEDIUM)
        self.assertTrue(self.locker.put_parcel(parcel))
        self.assertTrue(self.locker.is_occupied)
    
    def test_put_parcel_too_big(self):
        """Тест слишком большой посылки"""
        parcel = Parcel(self.sender, self.recipient, ParcelSize.LARGE)
        with self.assertRaises(LockerError) as ctx:
            self.locker.put_parcel(parcel)
        self.assertIn("слишком большая", str(ctx.exception))
    
    def test_put_parcel_occupied(self):
        """Тест размещения в занятую ячейку"""
        parcel1 = Parcel(self.sender, self.recipient, ParcelSize.SMALL)
        parcel2 = Parcel(self.sender, self.recipient, ParcelSize.SMALL)
        
        self.locker.put_parcel(parcel1)
        with self.assertRaises(LockerError) as ctx:
            self.locker.put_parcel(parcel2)
        self.assertIn("уже занята", str(ctx.exception))
    
    def test_put_parcel_broken(self):
        """Тест размещения в неисправную ячейку"""
        self.locker.is_functional = False
        parcel = Parcel(self.sender, self.recipient, ParcelSize.SMALL)
        with self.assertRaises(LockerError) as ctx:
            self.locker.put_parcel(parcel)
        self.assertIn("неисправна", str(ctx.exception))
    
    def test_take_parcel(self):
        """Тест извлечения посылки"""
        parcel = Parcel(self.sender, self.recipient, ParcelSize.SMALL)
        self.locker.put_parcel(parcel)
        
        taken = self.locker.take_parcel()
        self.assertEqual(taken, parcel)
        self.assertFalse(self.locker.is_occupied)
        self.assertIsNone(self.locker.current_parcel)
    
    def test_take_parcel_empty(self):
        """Тест извлечения из пустой ячейки"""
        with self.assertRaises(LockerError) as ctx:
            self.locker.take_parcel()
        self.assertIn("пуста", str(ctx.exception))
    
    def test_take_parcel_broken(self):
        """Тест извлечения из неисправной ячейки"""
        self.locker.is_functional = False
        with self.assertRaises(LockerError) as ctx:
            self.locker.take_parcel()
        self.assertIn("неисправна", str(ctx.exception))
    
    def test_repair(self):
        """Тест ремонта"""
        self.locker.is_functional = False
        self.locker.last_maintenance = None
        
        self.assertTrue(self.locker.repair())
        self.assertTrue(self.locker.is_functional)
        self.assertIsNotNone(self.locker.last_maintenance)
    
    def test_repair_with_date(self):
        """Тест ремонта с установкой даты"""
        locker = Locker(2, ParcelSize.SMALL)
        locker.is_functional = False
        locker.last_maintenance = None
        
        locker.repair()
        self.assertTrue(locker.is_functional)
        self.assertIsNotNone(locker.last_maintenance)
    
    def test_get_info(self):
        """Тест получения информации"""
        # Пустая
        info = self.locker.get_info()
        self.assertEqual(info["number"], 1)
        self.assertEqual(info["size"], "M")
        self.assertFalse(info["occupied"])
        self.assertTrue(info["functional"])
        self.assertIsNone(info["parcel"])
        self.assertIsNone(info["last_maintenance"])
        
        # С посылкой
        parcel = Parcel(self.sender, self.recipient, ParcelSize.SMALL)
        self.locker.put_parcel(parcel)
        info = self.locker.get_info()
        self.assertTrue(info["occupied"])
        self.assertEqual(info["parcel"], parcel.tracking_number)
    
    def test_get_info_with_maintenance(self):
        """Тест получения информации о ячейке с датой обслуживания"""
        locker = Locker(5, ParcelSize.LARGE)
        locker.last_maintenance = datetime(2024, 1, 15, 10, 30)
        
        info = locker.get_info()
        self.assertEqual(info["last_maintenance"], "15.01.2024")
    
    def test_str(self):
        """Тест строкового представления"""
        cases = [
            (False, True, "свободна (исправна)"),
            (True, True, "занята (исправна)"),
            (True, False, "занята (неисправна)"),
            (False, False, "свободна (неисправна)")
        ]
        for occupied, functional, expected in cases:
            self.locker.is_occupied = occupied
            self.locker.is_functional = functional
            self.assertIn(expected, str(self.locker))

