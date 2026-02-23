class TestCLIFull(unittest.TestCase):
    """Ключевые тесты CLI"""
    
    def setUp(self):
        self.cli = PostomatCLI()
        self.patcher_input = patch('builtins.input')
        self.mock_input = self.patcher_input.start()
        self.patcher_print = patch('builtins.print')
        self.mock_print = self.patcher_print.start()
    
    def tearDown(self):
        self.patcher_input.stop()
        self.patcher_print.stop()
    
    def test_initialization(self):
        """Тест инициализации"""
        self.assertIsNone(self.cli.postomat)
        self.assertTrue(self.cli.current_user_id.startswith("user_"))
        self.assertEqual(len(self.cli.current_user_id.split("_")[1]), 4)
    
    def test_clear_screen(self):
        """Тест очистки экрана"""
        self.cli.clear_screen()
        self.mock_print.assert_called_with("\n" * 2)
    
    def test_print_header(self):
        """Тест печати заголовка"""
        self.cli.print_header("Тест")
        self.assertGreater(self.mock_print.call_count, 2)
    
    def test_input_validation_valid(self):
        """Тест ввода с валидацией"""
        self.mock_input.side_effect = ["Иван Петров"]
        result = self.cli.input_with_validation(
            "Имя: ", Validator.validate_name, "Ошибка"
        )
        self.assertEqual(result, "Иван Петров")
    
    def test_input_validation_invalid_then_valid(self):
        """Тест ввода с ошибкой, затем успех"""
        self.mock_input.side_effect = ["123", "Иван Петров"]
        result = self.cli.input_with_validation(
            "Имя: ", Validator.validate_name, "Ошибка"
        )
        self.assertEqual(result, "Иван Петров")
    
    def test_input_validation_not_required(self):
        """Тест необязательного поля"""
        self.mock_input.side_effect = [""]
        result = self.cli.input_with_validation(
            "Описание: ", Validator.validate_description, "Ошибка", required=False
        )
        self.assertEqual(result, "")
    
    def test_setup_postomat(self):
        """Тест настройки почтомата"""
        self.mock_input.side_effect = ["PM001", "ул. Тест", "10", "2"]
        
        # Вызываем метод напрямую
        with patch('builtins.print'):  # Подавляем вывод
            self.cli._setup_postomat()
        
        self.assertIsNotNone(self.cli.postomat)
    
    def test_setup_postomat_defaults(self):
        """Тест настройки с значениями по умолчанию"""
        self.mock_input.side_effect = ["", "ул. Тест", "", ""]
        
        with patch('builtins.print'):
            self.cli._setup_postomat()
        
        self.assertIsNotNone(self.cli.postomat)
    
    def test_input_sender(self):
        """Тест ввода отправителя"""
        self.mock_input.side_effect = [
            "Иван Петров", "+375291234567", "ivan@ex.com", "ул. Ленина, 10"
        ]
        sender = self.cli._input_sender()
        
        self.assertEqual(sender.name, "Иван Петров")
        self.assertEqual(sender.phone, "+375291234567")
        self.assertEqual(sender.email, "ivan@ex.com")
        self.assertEqual(sender.address, "ул. Ленина, 10")
    
    def test_input_recipient(self):
        """Тест ввода получателя"""
        self.mock_input.side_effect = [
            "Петр Иванов", "+375331234567", "petr@ex.com"
        ]
        recipient = self.cli._input_recipient()
        
        self.assertEqual(recipient.name, "Петр Иванов")
        self.assertEqual(recipient.phone, "+375331234567")
        self.assertEqual(recipient.email, "petr@ex.com")
    
    def test_exit(self):
        """Тест выхода"""
        self.cli.postomat = MagicMock()
        self.cli.postomat.user_operations = {"test_user": 5}
        self.cli.current_user_id = "test_user"
        
        with patch('builtins.print'):
            self.cli._exit()
        
        self.assertTrue(True)

