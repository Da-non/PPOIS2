class TestNotificationFull(unittest.TestCase):
    """Полные тесты уведомления"""
    
    def setUp(self):
        self.sender = Sender("Иван", "+375291234567", "ivan@ex.com", "ул. Ленина")
        self.recipient = Recipient("Петр", "+375331234567", "petr@ex.com")
        self.parcel = Parcel(self.sender, self.recipient, ParcelSize.SMALL)
        self.message = "Тестовое сообщение"
    
    def test_notification_creation(self):
        """Тест создания уведомления"""
        notif = Notification(self.recipient, self.parcel, self.message)
        self.assertEqual(notif.recipient, self.recipient)
        self.assertEqual(notif.parcel, self.parcel)
        self.assertEqual(notif.message, self.message)
        self.assertEqual(notif.type, NotificationType.SMS)
        self.assertFalse(notif.is_sent)
        self.assertEqual(notif.attempts, 0)
        self.assertIsNotNone(notif.created_at)
        self.assertIsNone(notif.sent_at)
        
        # С указанием типа
        notif2 = Notification(self.recipient, self.parcel, self.message, NotificationType.EMAIL)
        self.assertEqual(notif2.type, NotificationType.EMAIL)
    
    @patch('time.sleep')
    def test_send_success(self, mock_sleep):
        """Тест успешной отправки"""
        notif = Notification(self.recipient, self.parcel, self.message)
        result = notif.send()
        
        self.assertTrue(result)
        self.assertTrue(notif.is_sent)
        self.assertEqual(notif.attempts, 1)
        self.assertIsNotNone(notif.sent_at)
        mock_sleep.assert_called_once_with(0.1)
    
    def test_send_failure(self):
        """Тест ошибки отправки"""
        notif = Notification(self.recipient, self.parcel, self.message)
        
        # Мокаем time.sleep, чтобы вызвать исключение
        with patch('time.sleep', side_effect=Exception("Network error")):
            with self.assertRaises(NotificationError):
                notif.send()
        
        self.assertEqual(notif.attempts, 1)
        self.assertFalse(notif.is_sent)
    
    def test_send_multiple_attempts(self):
        """Тест нескольких попыток отправки"""
        notif = Notification(self.recipient, None, "Тест")
        
        with patch('time.sleep', side_effect=[None, Exception("Error")]):
            # Первая попытка успешна
            result = notif.send()
            self.assertTrue(result)
            self.assertEqual(notif.attempts, 1)
            self.assertTrue(notif.is_sent)
    
    def test_str(self):
        """Тест строкового представления"""
        # Не отправлено
        notif = Notification(self.recipient, self.parcel, "Короткое")
        self.assertIn("SMS ожидает", str(notif))
        
        # Отправлено
        notif.is_sent = True
        self.assertIn("SMS отправлено", str(notif))
        
        # Email
        notif2 = Notification(self.recipient, self.parcel, "Тест", NotificationType.EMAIL)
        self.assertIn("Email ожидает", str(notif2))
        
        # Длинное сообщение
        notif3 = Notification(self.recipient, self.parcel, "A" * 50)
        self.assertIn("A" * 30, str(notif3))
