class TestExceptions(unittest.TestCase):
    """Тесты исключений"""
    def test_exceptions(self):
        """Тест иерархии исключений"""
        self.assertTrue(issubclass(ParcelError, PostomatError))
        self.assertTrue(issubclass(LockerError, PostomatError))
        self.assertTrue(issubclass(SecurityError, PostomatError))
        self.assertTrue(issubclass(NotificationError, PostomatError))
        self.assertTrue(issubclass(ValidationError, PostomatError))
        # Проверка сообщений
        self.assertEqual(str(PostomatError("test")), "test")
        self.assertEqual(str(ValidationError("invalid")), "invalid")

