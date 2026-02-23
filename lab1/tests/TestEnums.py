class TestEnums(unittest.TestCase):
    """Тесты перечислений"""
    
    def test_enums(self):
        """Тест значений перечислений"""
        self.assertEqual(ParcelStatus.CREATED.value, "создана")
        self.assertEqual(ParcelStatus.IN_POSTOMAT.value, "в почтомате")
        self.assertEqual(ParcelStatus.DELIVERED.value, "получена")
        self.assertEqual(ParcelStatus.EXPIRED.value, "просрочена")
        
        self.assertEqual(ParcelSize.SMALL.value, "S")
        self.assertEqual(ParcelSize.MEDIUM.value, "M")
        self.assertEqual(ParcelSize.LARGE.value, "L")
        
        self.assertEqual(SecurityLevel.LOW.value, 1)
        self.assertEqual(SecurityLevel.MEDIUM.value, 2)
        self.assertEqual(SecurityLevel.HIGH.value, 3)
        
        self.assertEqual(NotificationType.SMS.value, "SMS")
        self.assertEqual(NotificationType.EMAIL.value, "Email")
        
        self.assertEqual(len(ParcelStatus), 4)
        self.assertEqual(len(ParcelSize), 3)
        self.assertEqual(len(SecurityLevel), 3)
        self.assertEqual(len(NotificationType), 2)

