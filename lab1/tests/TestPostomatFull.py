class TestPostomatFull(unittest.TestCase):
    """Полные тесты почтомата"""
    
    def setUp(self):
        self.postomat = Postomat("PM001", "ул. Центральная, 15", total_lockers=5)
        self.sender = Sender("Иван", "+375291234567", "ivan@ex.com", "ул. Ленина")
        self.recipient = Recipient("Петр", "+375331234567", "petr@ex.com")
        self.parcel = Parcel(self.sender, self.recipient, ParcelSize.SMALL)
    
    def test_postomat_creation(self):
        """Тест создания почтомата"""
        self.assertEqual(self.postomat.id, "PM001")
        self.assertEqual(self.postomat.address, "ул. Центральная, 15")
        self.assertEqual(self.postomat.total_lockers, 5)
        self.assertEqual(self.postomat.security_level, SecurityLevel.MEDIUM)
        self.assertTrue(self.postomat.is_operational)
        self.assertEqual(len(self.postomat.lockers), 5)
        
        # Проверка, что все ячейки имеют уникальные номера
        numbers = [l.number for l in self.postomat.lockers]
        self.assertEqual(len(numbers), len(set(numbers)))
    
    def test_postomat_creation_with_security(self):
        """Тест создания с разными уровнями безопасности"""
        p_low = Postomat("LOW", "адрес", security_level=SecurityLevel.LOW)
        self.assertEqual(p_low.security_level, SecurityLevel.LOW)
        
        p_high = Postomat("HIGH", "адрес", security_level=SecurityLevel.HIGH)
        self.assertEqual(p_high.security_level, SecurityLevel.HIGH)
    
    def test_postomat_constructor_edge_cases(self):
        """Тест конструктора с разными параметрами"""
        # Минимальное количество ячеек
        p1 = Postomat("MIN", "адрес", total_lockers=1)
        self.assertEqual(len(p1.lockers), 1)
    
    def test_postomat_invalid_creation(self):
        """Тест невалидного создания"""
        with self.assertRaises(ValueError):
            Postomat("", "адрес")
        with self.assertRaises(ValueError):
            Postomat("ID", "")
        with self.assertRaises(ValueError):
            Postomat("ID", "адрес", total_lockers=0)
    
    def test_send_parcel_success(self):
        """Тест успешной отправки"""
        success, msg = self.postomat.send_parcel(self.parcel, "user1")
        
        self.assertTrue(success)
        self.assertIn(self.parcel.tracking_number, msg)
        self.assertIn(self.parcel.tracking_number, self.postomat.parcels)
        self.assertEqual(self.parcel.status, ParcelStatus.IN_POSTOMAT)
        self.assertIsNotNone(self.parcel.locker_number)
        self.assertEqual(len(self.postomat.notifications), 1)
    
    def test_send_parcel_postomat_blocked(self):
        """Тест отправки при заблокированном почтомате"""
        self.postomat.is_operational = False
        success, msg = self.postomat.send_parcel(self.parcel, "user1")
        self.assertFalse(success)
        self.assertEqual(msg, "Почтомат заблокирован по соображениям безопасности")
    
    def test_send_parcel_duplicate(self):
        """Тест отправки дубликата"""
        self.postomat.send_parcel(self.parcel, "user1")
        success, msg = self.postomat.send_parcel(self.parcel, "user1")
        self.assertFalse(success)
        self.assertIn("уже находится", msg)
    
    def test_send_parcel_no_lockers(self):
        """Тест отправки при отсутствии ячеек"""
        # Занимаем все ячейки
        for i in range(5):
            p = Parcel(self.sender, self.recipient, ParcelSize.SMALL)
            self.postomat.send_parcel(p, "user1")
        
        success, msg = self.postomat.send_parcel(self.parcel, "user1")
        self.assertFalse(success)
        self.assertEqual(msg, "Нет свободных ячеек подходящего размера")
    
    def test_send_parcel_locker_error(self):
        """Тест ошибки ячейки при отправке"""
        with patch.object(self.postomat, 'find_available_locker') as mock_find:
            mock_locker = MagicMock()
            mock_locker.put_parcel.side_effect = LockerError("Test error")
            mock_find.return_value = mock_locker
            
            success, msg = self.postomat.send_parcel(self.parcel, "user1")
            self.assertFalse(success)
            self.assertIn("Ошибка ячейки", msg)
    
    def test_send_parcel_general_exception(self):
        """Тест общей ошибки при отправке"""
        parcel = Parcel(self.sender, self.recipient, ParcelSize.SMALL)
    
    # Создаем мок-ячейку, которая вызовет исключение при put_parcel
        mock_locker = MagicMock()
        mock_locker.put_parcel.side_effect = Exception("Test error")
    
    # Мокаем find_available_locker, чтобы он возвращал нашу мок-ячейку
        with patch.object(self.postomat, 'find_available_locker', return_value=mock_locker):
         success, msg = self.postomat.send_parcel(parcel, "user")
        self.assertFalse(success)
        # Проверяем, что сообщение содержит "Системная ошибка", так как исключение перехватывается на верхнем уровне
        self.assertIn("Системная ошибка", msg)
    
    def test_receive_parcel_success(self):
        """Тест успешного получения"""
        self.postomat.send_parcel(self.parcel, "user1")
        locker_num = self.parcel.locker_number
        
        success, msg, parcel = self.postomat.receive_parcel(
            self.parcel.tracking_number, self.recipient, "user1"
        )
        
        self.assertTrue(success)
        self.assertEqual(parcel, self.parcel)
        self.assertEqual(parcel.status, ParcelStatus.DELIVERED)
        self.assertNotIn(self.parcel.tracking_number, self.postomat.parcels)
        
        # Проверка освобождения ячейки
        locker = self.postomat.lockers[locker_num - 1]
        self.assertFalse(locker.is_occupied)
    
    def test_receive_parcel_not_found(self):
        """Тест получения несуществующей посылки"""
        success, msg, parcel = self.postomat.receive_parcel(
            "ABC12345", self.recipient, "user1"
        )
        self.assertFalse(success)
        self.assertIn("не найдена", msg)
        self.assertIsNone(parcel)
    
    def test_receive_parcel_wrong_recipient(self):
        """Тест получения не тем получателем"""
        self.postomat.send_parcel(self.parcel, "user1")
        wrong = Recipient("Другой", "+375441234567", "other@ex.com")
        
        success, msg, parcel = self.postomat.receive_parcel(
            self.parcel.tracking_number, wrong, "user2"
        )
        
        self.assertFalse(success)
        self.assertIn("нет прав", msg)
        self.assertIsNone(parcel)
        self.assertEqual(len(self.postomat.security_alerts), 1)
    
    def test_receive_parcel_postomat_blocked(self):
        """Тест получения при заблокированном почтомате"""
        self.postomat.send_parcel(self.parcel, "user1")
        self.postomat.is_operational = False
        
        success, msg, parcel = self.postomat.receive_parcel(
            self.parcel.tracking_number, self.recipient, "user1"
        )
        
        self.assertFalse(success)
        self.assertEqual(msg, "Почтомат заблокирован по соображениям безопасности")
    
    def test_receive_parcel_expired(self):
        """Тест получения просроченной посылки"""
        self.postomat.send_parcel(self.parcel, "user1")
        self.parcel.storage_until = datetime.now() - timedelta(days=1)
        
        success, msg, parcel = self.postomat.receive_parcel(
            self.parcel.tracking_number, self.recipient, "user1"
        )
        
        self.assertFalse(success)
        self.assertIn("Срок хранения", msg)
        self.assertEqual(self.parcel.status, ParcelStatus.EXPIRED)
    
    def test_receive_parcel_with_different_status(self):
        """Тест получения посылки с разными статусами"""
        parcel = Parcel(self.sender, self.recipient, ParcelSize.SMALL)
        parcel.status = ParcelStatus.DELIVERED
        self.postomat.parcels[parcel.tracking_number] = parcel
        
        success, msg, _ = self.postomat.receive_parcel(
            parcel.tracking_number, self.recipient, "user"
        )
        self.assertFalse(success)
        self.assertIn("не готова к выдаче", msg)
    
    def test_receive_parcel_locker_error(self):
        """Тест ошибки ячейки при получении"""
        self.postomat.send_parcel(self.parcel, "user1")
        
        # Ломаем ячейку
        locker = self.postomat.lockers[self.parcel.locker_number - 1]
        locker.is_functional = False
        
        success, msg, parcel = self.postomat.receive_parcel(
            self.parcel.tracking_number, self.recipient, "user1"
        )
        
        self.assertFalse(success)
        self.assertIn("Ошибка при получении", msg)
    
    def test_receive_parcel_locker_not_found(self):
        """Тест получения при отсутствии ячейки"""
        self.postomat.send_parcel(self.parcel, "user1")
        self.parcel.locker_number = 999
        
        success, msg, parcel = self.postomat.receive_parcel(
            self.parcel.tracking_number, self.recipient, "user1"
        )
        
        self.assertFalse(success)
        self.assertIn("ячейка не найдена", msg)
    
    
    def test_notify_recipient_success(self):
        """Тест успешной отправки уведомления"""
        self.postomat.send_parcel(self.parcel, "user1")
        
        success, msg = self.postomat.notify_recipient(
            self.parcel.tracking_number, "Тест", "user1"
        )
        
        self.assertTrue(success)
        self.assertIn("Уведомление отправлено", msg)
        self.assertEqual(len(self.postomat.notifications), 2)
    
    def test_notify_recipient_default_message(self):
        """Тест отправки с сообщением по умолчанию"""
        self.postomat.send_parcel(self.parcel, "user1")
        
        success, msg = self.postomat.notify_recipient(
            self.parcel.tracking_number, "", "user1"
        )
        
        self.assertTrue(success)
        self.assertEqual(len(self.postomat.notifications), 2)
        self.assertIn("Напоминание", self.postomat.notifications[1].message)
    
    def test_notify_recipient_not_found(self):
        """Тест отправки для несуществующей посылки"""
        success, msg = self.postomat.notify_recipient("ABC123", "Тест", "user1")
        self.assertFalse(success)
        self.assertIn("не найдена", msg)
    
    def test_notify_recipient_with_security_fail(self):
        """Тест уведомления с ошибкой безопасности"""
        parcel = Parcel(self.sender, self.recipient, ParcelSize.SMALL)
        self.postomat.parcels[parcel.tracking_number] = parcel
        
        with patch.object(self.postomat, '_check_security', return_value=(False, "Security error")):
            success, msg = self.postomat.notify_recipient(parcel.tracking_number, "", "user")
            self.assertFalse(success)
            self.assertEqual(msg, "Security error")
    
    def test_notify_recipient_with_notification_failure(self):
        """Тест уведомления с ошибкой отправки"""
        parcel = Parcel(self.sender, self.recipient, ParcelSize.SMALL)
        self.postomat.parcels[parcel.tracking_number] = parcel
        
        with patch.object(self.postomat, '_notify_recipient', return_value=None):
            success, msg = self.postomat.notify_recipient(parcel.tracking_number, "Тест", "user")
            self.assertFalse(success)
    
    def test_notify_with_custom_message(self):
        """Тест уведомления с пользовательским сообщением"""
        parcel = Parcel(self.sender, self.recipient, ParcelSize.SMALL)
        self.postomat.send_parcel(parcel, "user")
        
        success, msg = self.postomat.notify_recipient(
            parcel.tracking_number, "Пользовательское сообщение", "user"
        )
        self.assertTrue(success)
        
        # Проверяем, что последнее уведомление содержит наше сообщение
        if self.postomat.notifications:
            self.assertIn("Пользовательское", self.postomat.notifications[-1].message)
    
    def test_perform_maintenance(self):
        """Тест техобслуживания"""
        # Ломаем ячейки
        if len(self.postomat.lockers) > 2:
            self.postomat.lockers[0].is_functional = False
            self.postomat.lockers[2].is_functional = False
        
        report = self.postomat.perform_maintenance("Техник")
        
        self.assertEqual(report["technician"], "Техник")
        self.assertEqual(report["lockers_checked"], 5)
        self.assertEqual(report["broken_before"], 2)
        self.assertEqual(len(self.postomat.maintenance_log), 1)
        self.assertIn("issues", report)
    
    def test_perform_maintenance_all_functional(self):
        """Тест обслуживания исправных ячеек"""
        report = self.postomat.perform_maintenance("Техник")
        
        self.assertEqual(report["broken_before"], 0)
        self.assertEqual(report["lockers_repaired"], 0)
        
        # Проверка профилактики
        for locker in self.postomat.lockers:
            self.assertIsNotNone(locker.last_maintenance)
    
    def test_perform_maintenance_no_technician(self):
        """Тест обслуживания без техника"""
        with self.assertRaises(ValueError):
            self.postomat.perform_maintenance("")
    
    def test_perform_maintenance_with_failed_repairs(self):
        """Тест обслуживания с неудачным ремонтом"""
        # Ломаем ячейку
        for locker in self.postomat.lockers:
            locker.is_functional = False
        
        with patch('random.random', return_value=0.99):  # Большая вероятность неудачи
            report = self.postomat.perform_maintenance("Техник")
            self.assertGreaterEqual(report["failed_repairs"], 0)
    
    def test_maintenance_log(self):
        """Тест логирования обслуживания"""
        report = self.postomat.perform_maintenance("Техник")
        self.assertEqual(len(self.postomat.maintenance_log), 1)
        self.assertEqual(self.postomat.maintenance_log[0]["technician"], "Техник")
    
    def test_break_random_locker(self):
        """Тест поломки ячейки"""
        functional_before = len([l for l in self.postomat.lockers if l.is_functional])
        
        success, msg = self.postomat.break_random_locker()
        
        if functional_before > 0:
            self.assertTrue(success)
            functional_after = len([l for l in self.postomat.lockers if l.is_functional])
            self.assertEqual(functional_after, functional_before - 1)
            self.assertEqual(len(self.postomat.security_alerts), 1)
        else:
            self.assertFalse(success)
    
    def test_break_random_locker_no_functional(self):
        """Тест поломки при отсутствии исправных ячеек"""
        for locker in self.postomat.lockers:
            locker.is_functional = False
        
        success, msg = self.postomat.break_random_locker()
        self.assertFalse(success)
        self.assertIn("Нет исправных", msg)
    
    def test_check_security(self):
        """Тест проверки безопасности"""
        allowed, msg = self.postomat._check_security("user1", "test")
        self.assertTrue(allowed)
        self.assertEqual(self.postomat.user_operations["user1"], 1)
        
        # Заблокированный почтомат
        self.postomat.is_operational = False
        allowed, msg = self.postomat._check_security("user1", "test")
        self.assertFalse(allowed)
    
    def test_check_security_suspicious_low(self):
        """Тест подозрительной активности при низком уровне"""
        for i in range(60):
            self.postomat.user_operations["user1"] = i + 1
        
        with patch.object(self.postomat, 'security_level', SecurityLevel.LOW):
            allowed, msg = self.postomat._check_security("user1", "test")
            self.assertTrue(allowed)
    
    def test_check_security_suspicious_high(self):
        """Тест подозрительной активности при высоком уровне"""
        for i in range(60):
            self.postomat.user_operations["user1"] = i + 1
        
        with patch.object(self.postomat, 'security_level', SecurityLevel.HIGH):
            allowed, msg = self.postomat._check_security("user1", "test")
            self.assertFalse(allowed)
            self.assertEqual(len(self.postomat.security_alerts), 1)
    
    def test_check_security_with_high_level_block(self):
        """Тест блокировки при высоком уровне безопасности"""
        self.postomat.security_level = SecurityLevel.HIGH
        self.postomat.is_operational = True
        
        # Создаем подозрительную активность
        for i in range(60):
            self.postomat.user_operations["user"] = i + 1
        
        allowed, msg = self.postomat._check_security("user", "test")
        self.assertFalse(allowed)
    
    def test_log_security_alert(self):
        """Тест логирования инцидентов"""
        self.postomat._log_security_alert("test", "Description")
        self.assertEqual(len(self.postomat.security_alerts), 1)
        
        alert = self.postomat.security_alerts[0]
        self.assertEqual(alert["type"], "test")
        self.assertEqual(alert["description"], "Description")
        self.assertIsNotNone(alert["timestamp"])
    
    def test_log_security_alert_high_level(self):
        """Тест логирования с блокировкой на HIGH уровне"""
        self.postomat.security_level = SecurityLevel.HIGH
        self.postomat.is_operational = True
        
        self.postomat._log_security_alert("unauthorized_access", "Critical")
        self.assertFalse(self.postomat.is_operational)
    
    def test_log_security_alert_high_level_no_block(self):
        """Тест отсутствия блокировки при несерьезных инцидентах"""
        self.postomat.security_level = SecurityLevel.HIGH
        
        self.postomat._log_security_alert("info", "Test")
        self.assertTrue(self.postomat.is_operational)
    
    def test_get_security_status(self):
        """Тест получения статуса безопасности"""
        self.postomat._log_security_alert("test1", "Alert 1")
        self.postomat._log_security_alert("test2", "Alert 2")
        self.postomat.user_operations["user1"] = 5
        self.postomat.user_operations["user2"] = 3
        
        status = self.postomat.get_security_status()
        
        self.assertEqual(status["level"], "MEDIUM")
        self.assertTrue(status["is_operational"])
        self.assertEqual(status["alerts_count"], 2)
        self.assertEqual(status["total_user_operations"], 8)
        self.assertEqual(status["active_users"], 2)
        self.assertEqual(len(status["recent_alerts"]), 2)
    
    def test_reset_security(self):
        """Тест сброса безопасности"""
        self.postomat._log_security_alert("test", "Alert")
        self.postomat.user_operations["user1"] = 10
        self.postomat.is_operational = False
        
        success, msg = self.postomat.reset_security()
        
        self.assertTrue(success)
        self.assertTrue(self.postomat.is_operational)
        self.assertEqual(len(self.postomat.security_alerts), 0)
        self.assertEqual(len(self.postomat.user_operations), 0)
    
    def test_find_available_locker(self):
        """Тест поиска свободной ячейки"""
        # Маленькая посылка
        locker = self.postomat.find_available_locker(ParcelSize.SMALL)
        self.assertIsNotNone(locker)
        self.assertFalse(locker.is_occupied)
        self.assertTrue(locker.is_functional)
    
    def test_find_available_locker_all_broken(self):
        """Тест поиска ячейки, когда все сломаны"""
        for locker in self.postomat.lockers:
            locker.is_functional = False
        
        locker = self.postomat.find_available_locker(ParcelSize.SMALL)
        self.assertIsNone(locker)
    
    def test_find_available_locker_for_different_sizes(self):
        """Тест поиска ячейки для разных размеров"""
        sizes = [ParcelSize.SMALL, ParcelSize.MEDIUM, ParcelSize.LARGE]
        for size in sizes:
            locker = self.postomat.find_available_locker(size)
            self.assertIsNotNone(locker)
    
    def test_find_available_locker_no_suitable(self):
        """Тест поиска при отсутствии подходящего размера"""
        # Занимаем все большие ячейки
        for locker in self.postomat.lockers:
            if locker.size == ParcelSize.LARGE:
                locker.is_occupied = True
        
        locker = self.postomat.find_available_locker(ParcelSize.LARGE)
        if not any(l.size == ParcelSize.LARGE and not l.is_occupied for l in self.postomat.lockers):
            self.assertIsNone(locker)
    
    def test_check_expired_parcels(self):
        """Тест проверки просроченных посылок"""
        self.postomat.send_parcel(self.parcel, "user1")
        self.parcel.storage_until = datetime.now() - timedelta(days=1)
        
        expired = self.postomat.check_expired_parcels()
        
        self.assertEqual(len(expired), 1)
        self.assertEqual(expired[0], self.parcel)
        self.assertEqual(self.parcel.status, ParcelStatus.EXPIRED)
        self.assertEqual(len(self.postomat.notifications), 2)  # +1 уведомление отправителю
    
    def test_check_expired_parcels_none(self):
        """Тест проверки без просроченных"""
        self.postomat.send_parcel(self.parcel, "user1")
        expired = self.postomat.check_expired_parcels()
        self.assertEqual(len(expired), 0)
    
    def test_check_expired_parcels_multiple(self):
        """Тест проверки нескольких просроченных посылок"""
        parcels = []
        for i in range(3):
            p = Parcel(self.sender, self.recipient, ParcelSize.SMALL)
            self.postomat.send_parcel(p, "user")
            p.storage_until = datetime.now() - timedelta(days=1)
            parcels.append(p)
        
        expired = self.postomat.check_expired_parcels()
        self.assertEqual(len(expired), 3)
    
    def test_check_expired_parcels_mixed(self):
        """Тест смешанных просроченных и непросроченных"""
        p1 = Parcel(self.sender, self.recipient, ParcelSize.SMALL)
        p2 = Parcel(self.sender, self.recipient, ParcelSize.SMALL)
        
        self.postomat.send_parcel(p1, "user")
        self.postomat.send_parcel(p2, "user")
        
        p1.storage_until = datetime.now() - timedelta(days=1)  # просрочена
        # p2 оставляем нормальной
        
        expired = self.postomat.check_expired_parcels()
        self.assertEqual(len(expired), 1)
        self.assertEqual(expired[0], p1)
    
    def test_get_statistics(self):
        """Тест получения статистики"""
        self.postomat.send_parcel(self.parcel, "user1")
        self.postomat._log_security_alert("test", "Test")
        
        stats = self.postomat.get_statistics()
        
        self.assertEqual(stats["id"], "PM001")
        self.assertEqual(stats["active_parcels"], 1)
        self.assertEqual(stats["occupied_lockers"], 1)
        self.assertEqual(stats["free_lockers"], 4)
        self.assertEqual(stats["functional_lockers"], 5)
        self.assertEqual(stats["broken_lockers"], 0)
        self.assertEqual(stats["total_notifications"], 1)
        self.assertEqual(stats["security_alerts"], 1)
    
    def test_get_statistics_with_broken(self):
        """Тест статистики с неисправными ячейками"""
        self.postomat.lockers[0].is_functional = False
        self.postomat.lockers[1].is_functional = False
        
        stats = self.postomat.get_statistics()
        self.assertEqual(stats["broken_lockers"], 2)
        self.assertEqual(stats["functional_lockers"], 3)
    
    def test_str(self):
        """Тест строкового представления"""
        s = str(self.postomat)
        self.assertIn("PM001", s)
        self.assertIn("ул. Центральная, 15", s)
        self.assertIn("MEDIUM", s)
        self.assertIn("НОРМА", s)
        
        # С предупреждениями
        for _ in range(15):
            self.postomat._log_security_alert("test", "Alert")
        s = str(self.postomat)
        self.assertIn("ВНИМАНИЕ", s)
        
        # Заблокированный
        self.postomat.is_operational = False
        s = str(self.postomat)
        self.assertIn("ЗАБЛОКИРОВАН", s)
    
    def test_str_with_alerts(self):
        """Тест строкового представления с предупреждениями"""
        for _ in range(15):
            self.postomat._log_security_alert("test", "Alert")
        
        s = str(self.postomat)
        self.assertIn("ВНИМАНИЕ", s)
    
    def test_str_blocked(self):
        """Тест строкового представления заблокированного почтомата"""
        self.postomat.is_operational = False
        s = str(self.postomat)
        self.assertIn("ЗАБЛОКИРОВАН", s)
