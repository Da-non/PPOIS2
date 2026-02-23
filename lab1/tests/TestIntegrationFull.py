class TestIntegrationFull(unittest.TestCase):
    """Интеграционные тесты"""
    
    def setUp(self):
        self.postomat = Postomat("PM001", "ул. Тест", total_lockers=3)
        self.sender = Sender("Иван", "+375291234567", "ivan@ex.com", "ул. Ленина")
        self.recipient = Recipient("Петр", "+375331234567", "petr@ex.com")
        Parcel._existing_trackings.clear()
    
    def test_full_lifecycle(self):
        """Тест полного жизненного цикла"""
        # Создание
        parcel = Parcel(self.sender, self.recipient, ParcelSize.SMALL, "Книги")
        
        # Отправка
        success, _ = self.postomat.send_parcel(parcel, "user1")
        self.assertTrue(success)
        self.assertIn(parcel.tracking_number, self.postomat.parcels)
        
        # Проверка размещения
        locker = self.postomat.lockers[parcel.locker_number - 1]
        self.assertTrue(locker.is_occupied)
        self.assertEqual(locker.current_parcel, parcel)
        
        # Получение
        success, _, received = self.postomat.receive_parcel(
            parcel.tracking_number, self.recipient, "user1"
        )
        self.assertTrue(success)
        self.assertEqual(received.status, ParcelStatus.DELIVERED)
        
        # Проверка освобождения
        self.assertFalse(locker.is_occupied)
        self.assertNotIn(parcel.tracking_number, self.postomat.parcels)
    
    def test_multiple_parcels(self):
        """Тест нескольких посылок (без цифр в описании)"""
        parcels = []
        descriptions = ["Книги", "Одежда", "Обувь"]
        for i in range(3):
            p = Parcel(self.sender, self.recipient, ParcelSize.SMALL, descriptions[i])
            self.postomat.send_parcel(p, "user1")
            parcels.append(p)
        
        self.assertEqual(len(self.postomat.parcels), 3)
        
        # Получаем одну
        self.postomat.receive_parcel(parcels[0].tracking_number, self.recipient, "user1")
        self.assertEqual(len(self.postomat.parcels), 2)
        
        # Получаем остальные
        for p in parcels[1:]:
            self.postomat.receive_parcel(p.tracking_number, self.recipient, "user1")
        
        self.assertEqual(len(self.postomat.parcels), 0)
    
    def test_maintenance_cycle(self):
        """Тест цикла обслуживания"""
        # Ломаем ячейку
        self.postomat.break_random_locker()
        broken_before = len([l for l in self.postomat.lockers if not l.is_functional])
        
        # Обслуживание
        report = self.postomat.perform_maintenance("Техник")
        self.assertEqual(report["broken_before"], broken_before)
        
        broken_after = len([l for l in self.postomat.lockers if not l.is_functional])
        self.assertLessEqual(broken_after, broken_before)
    
    def test_maintenance_after_failures(self):
        """Тест обслуживания после нескольких поломок"""
        # Ломаем несколько ячеек
        for _ in range(2):
            self.postomat.break_random_locker()
        
        broken_before = len([l for l in self.postomat.lockers if not l.is_functional])
        
        # Проводим обслуживание
        report = self.postomat.perform_maintenance("Техник")
        
        self.assertEqual(report["broken_before"], broken_before)
        self.assertLessEqual(report["broken_after"], broken_before)
    
    def test_security_flow(self):
        """Тест потока безопасности"""
        # Нормальная операция
        parcel = Parcel(self.sender, self.recipient, ParcelSize.SMALL)
        self.postomat.send_parcel(parcel, "user1")
        
        # Попытка несанкционированного доступа
        wrong = Recipient("Другой", "+375441234567", "other@ex.com")
        self.postomat.receive_parcel(parcel.tracking_number, wrong, "user2")
        
        self.assertEqual(len(self.postomat.security_alerts), 1)
        
        # Проверка статуса
        status = self.postomat.get_security_status()
        self.assertEqual(status["alerts_count"], 1)
        
        # Сброс
        self.postomat.reset_security()
        self.assertEqual(len(self.postomat.security_alerts), 0)
    
    def test_security_with_multiple_users(self):
        """Тест безопасности с несколькими пользователями"""
        parcel = Parcel(self.sender, self.recipient, ParcelSize.SMALL)
        self.postomat.send_parcel(parcel, "user1")
        
        # Разные пользователи выполняют операции
        for i in range(10):
            self.postomat._check_security(f"user{i}", "test")
        
        status = self.postomat.get_security_status()
        # Проверяем, что количество пользователей >= 10
        self.assertGreaterEqual(status["active_users"], 10)
        self.assertGreaterEqual(status["total_user_operations"], 11)
    
    def test_full_cycle_with_maintenance(self):
        """Тест полного цикла с обслуживанием"""
        # Отправляем посылку
        parcel = Parcel(self.sender, self.recipient, ParcelSize.SMALL)
        self.postomat.send_parcel(parcel, "user")
        
        # Ломаем ячейку
        self.postomat.break_random_locker()
        
        # Обслуживание
        report = self.postomat.perform_maintenance("Техник")
        
        # Получаем посылку
        self.postomat.receive_parcel(parcel.tracking_number, self.recipient, "user")
        
        # Проверяем статистику
        stats = self.postomat.get_statistics()
        self.assertEqual(stats["active_parcels"], 0)
    
    def test_parcel_size_matching(self):
        """Тест соответствия размеров"""
        # Проверяем, что маленькая посылка может пойти в любую ячейку
        parcel_small = Parcel(self.sender, self.recipient, ParcelSize.SMALL)
        locker = self.postomat.find_available_locker(ParcelSize.SMALL)
        self.assertIsNotNone(locker)
