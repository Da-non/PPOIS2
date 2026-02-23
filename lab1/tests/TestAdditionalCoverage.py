class TestAdditionalCoverage(unittest.TestCase):
    """Дополнительные тесты для повышения покрытия"""
    
    def setUp(self):
        self.postomat = Postomat("PM002", "ул. Дополнительная, 1", total_lockers=3)
        self.sender = Sender("Тест", "+375291234567", "test@ex.com", "ул. Тестовая")
        self.recipient = Recipient("Получатель", "+375331234567", "rec@ex.com")
    
    def test_validator_edge_cases(self):
        """Тест граничных случаев валидатора"""
        self.assertTrue(Validator.validate_description(""))  # Пустое описание валидно
        
        # Спецсимволы
        self.assertFalse(Validator.validate_name("Иван@Петров"))
        self.assertFalse(Validator.validate_email("user@example..com"))
        self.assertTrue(Validator.validate_name("Иван-Петр"))  # Дефис работает
    
    def test_postomat_security_levels(self):
        """Тест разных уровней безопасности"""
        p_low = Postomat("LOW", "адрес", security_level=SecurityLevel.LOW)
        p_high = Postomat("HIGH", "адрес", security_level=SecurityLevel.HIGH)
        
        self.assertEqual(p_low.security_level, SecurityLevel.LOW)
        self.assertEqual(p_high.security_level, SecurityLevel.HIGH)
    
    def test_postomat_find_locker_all_broken(self):
        """Тест поиска ячейки, когда все сломаны"""
        for locker in self.postomat.lockers:
            locker.is_functional = False
        
        locker = self.postomat.find_available_locker(ParcelSize.SMALL)
        self.assertIsNone(locker)
