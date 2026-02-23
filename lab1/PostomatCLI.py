class PostomatCLI:
    """Интерфейс командной строки"""
    
    def __init__(self):
        self.postomat: Optional[Postomat] = None
        self.current_user_id = f"user_{random.randint(1000, 9999)}"
    
    def clear_screen(self):
        """Очистка экрана"""
        print("\n" * 2)
    
    def print_header(self, text: str):
        """Печать заголовка"""
        print("=" * 60)
        print(f" {text} ".center(60))
        print("=" * 60)
    
    def print_menu(self):
        """Печать главного меню"""
        print("\n" + "-" * 60)
        print(" ГЛАВНОЕ МЕНЮ ".center(60))
        print("-" * 60)
        print("1. Отправить посылку")
        print("2. Получить посылку")
        print("3. Отправить уведомление")
        print("4. Техническое обслуживание")
        print("5. Безопасность")
        print("6. Статус почтомата")
        print("7. Сломать ячейку (тест)")
        print("0. Выход")
        print("-" * 60)
        print(f"Пользователь: {self.current_user_id}")
    
    def input_with_validation(self, prompt: str, validator, error_message: str, required: bool = True) -> str:
        """
        Ввод с валидацией
        
        Args:
            prompt: Приглашение для ввода
            validator: Функция-валидатор
            error_message: Сообщение об ошибке
            required: Обязательно ли поле
        """
        while True:
            value = input(prompt).strip()
            
            if not value and not required:
                return value
            
            if not value and required:
                print(f"Ошибка: {error_message}")
                continue
            
            if validator(value):
                return value
            else:
                print(f"Ошибка: {error_message}")
    
    def run(self):
        """Запуск интерфейса"""
        self.clear_screen()
        self.print_header("СИСТЕМА УПРАВЛЕНИЯ ПОЧТОМАТОМ")
        
        self._setup_postomat()
        
        while True:
            self.print_menu()
            choice = input("\nВыберите действие: ").strip()
            
            if choice == "0":
                self._exit()
                break
            elif choice == "1":
                self._send_parcel()
            elif choice == "2":
                self._receive_parcel()
            elif choice == "3":
                self._send_notification()
            elif choice == "4":
                self._maintenance()
            elif choice == "5":
                self._security()
            elif choice == "6":
                self._status()
            elif choice == "7":
                self._break_locker()
            else:
                print("\nНеверный выбор. Нажмите Enter...")
                input()
    
    def _setup_postomat(self):
        """Настройка почтомата"""
        print("\n--- Настройка почтомата ---")
        
        postomat_id = input("ID почтомата [PM001]: ").strip()
        if not postomat_id:
            postomat_id = "PM001"
        
        address = self.input_with_validation(
            "Адрес: ",
            Validator.validate_address,
            "Адрес должен содержать минимум 5 символов и не состоять только из цифр"
        )
        
        while True:
            try:
                lockers = int(input("Количество ячеек [20]: ").strip() or "20")
                if lockers > 0:
                    break
                print("Количество ячеек должно быть положительным")
            except ValueError:
                print("Введите число")
        
        print("\nУровень безопасности:")
        print("1. Низкий")
        print("2. Средний")
        print("3. Высокий")
        
        sec_choice = input("Выберите (1-3) [2]: ").strip() or "2"
        security_map = {"1": SecurityLevel.LOW, "2": SecurityLevel.MEDIUM, "3": SecurityLevel.HIGH}
        security_level = security_map.get(sec_choice, SecurityLevel.MEDIUM)
        
        try:
            self.postomat = Postomat(postomat_id, address, lockers, security_level)
            print(f"\nПочтомат {postomat_id} создан")
            print(f"Адрес: {address}")
            print(f"Ячеек: {lockers}")
            print(f"Уровень безопасности: {security_level.name}")
            print(f"Ваш ID пользователя: {self.current_user_id}")
        except Exception as e:
            print(f"\nОшибка: {e}")
            exit(1)
    
    def _input_sender(self) -> Sender:
        """Ввод данных отправителя с валидацией"""
        print("\nДанные ОТПРАВИТЕЛЯ:")
        
        name = self.input_with_validation(
            "  Имя: ",
            Validator.validate_name,
            "Имя должно содержать минимум 2 символа, только буквы, пробелы или дефис (без цифр)"
        )
        
        phone = self.input_with_validation(
            "  Телефон (+375XXXXXXXXX): ",
            Validator.validate_phone,
            "Неверный формат телефона. Используйте +375 и код оператора (24,25,29,33,44). Пример: +375291234567"
        )
        
        email = self.input_with_validation(
            "  Email: ",
            Validator.validate_email,
            "Неверный формат email. Пример: name@domain.by"
        )
        
        address = self.input_with_validation(
            "  Адрес: ",
            Validator.validate_address,
            "Адрес должен содержать минимум 5 символов и не состоять только из цифр"
        )
        
        return Sender(name, phone, email, address)
    
    def _input_recipient(self) -> Recipient:
        """Ввод данных получателя с валидацией"""
        print("\nДанные ПОЛУЧАТЕЛЯ:")
        
        name = self.input_with_validation(
            "  Имя: ",
            Validator.validate_name,
            "Имя должно содержать минимум 2 символа, только буквы, пробелы или дефис (без цифр)"
        )
        
        phone = self.input_with_validation(
            "  Телефон (+375XXXXXXXXX): ",
            Validator.validate_phone,
            "Неверный формат телефона. Используйте +375 и код оператора (24,25,29,33,44). Пример: +375291234567"
        )
        
        email = self.input_with_validation(
            "  Email: ",
            Validator.validate_email,
            "Неверный формат email. Пример: name@domain.by"
        )
        
        return Recipient(name, phone, email)
    
    def _send_parcel(self):
        """Отправка посылки"""
        self.clear_screen()
        self.print_header("ОТПРАВКА ПОСЫЛКИ")
        
        try:
            sender = self._input_sender()
            recipient = self._input_recipient()
            
            print("\nРазмер посылки:")
            print("1. S - Маленькая")
            print("2. M - Средняя")
            print("3. L - Большая")
            
            while True:
                size_choice = input("Выберите размер (1-3): ").strip()
                size_map = {
                    "1": ParcelSize.SMALL,
                    "2": ParcelSize.MEDIUM,
                    "3": ParcelSize.LARGE
                }
                if size_choice in size_map:
                    size = size_map[size_choice]
                    break
                print("Выберите 1, 2 или 3")
            
            description = self.input_with_validation(
                "Описание посылки (необязательно, без цифр): ",
                Validator.validate_description,
                "Описание не должно содержать цифр",
                required=False
            )
            
            parcel = Parcel(sender, recipient, size, description)
            print(f"\nСоздан трек-номер: {parcel.tracking_number}")
            
            print("Отправка...")
            
            success, message = self.postomat.send_parcel(parcel, self.current_user_id)
            
            if success:
                print(f"\n{message}")
            else:
                print(f"\nОшибка: {message}")
                
        except ValidationError as e:
            print(f"\nОшибка валидации: {e}")
        except Exception as e:
            print(f"\nОшибка: {e}")
        
        input("\nНажмите Enter для продолжения...")
    
    def _receive_parcel(self):
        """Получение посылки"""
        self.clear_screen()
        self.print_header("ПОЛУЧЕНИЕ ПОСЫЛКИ")
        
        try:
            recipient = self._input_recipient()
            
            tracking = input("\nВведите номер отслеживания: ").strip()
            
            if not tracking:
                print("Номер отслеживания обязателен")
                input("Нажмите Enter...")
                return
            
            print(f"Поиск посылки {tracking}...")
            
            success, message, parcel = self.postomat.receive_parcel(tracking, recipient, self.current_user_id)
            
            if success and parcel:
                print(f"\n{message}")
                print(f"\nИнформация о посылке:")
                print(f"  Отправитель: {parcel.sender.name}")
                print(f"  Описание: {parcel.description}")
                print(f"  Размер: {parcel.size.value}")
                print(f"  Получена: {parcel.delivered_at.strftime('%d.%m.%Y %H:%M')}")
            else:
                print(f"\nОшибка: {message}")
                
        except ValidationError as e:
            print(f"\nОшибка валидации: {e}")
        except Exception as e:
            print(f"\nОшибка: {e}")
        
        input("\nНажмите Enter для продолжения...")
    
    def _send_notification(self):
        """Отправка уведомления"""
        self.clear_screen()
        self.print_header("ОТПРАВКА УВЕДОМЛЕНИЯ")
        
        tracking = input("Номер отслеживания: ").strip()
        
        if not tracking:
            print("Номер отслеживания обязателен")
            input("Нажмите Enter...")
            return
        
        print("\nШаблоны сообщений:")
        print("1. Стандартное напоминание")
        print("2. Посылка готова к выдаче")
        print("3. Своё сообщение")
        
        template = input("\nВыберите шаблон (1-3): ").strip()
        
        if template == "3":
            custom_message = input("Введите сообщение: ").strip()
        else:
            templates = {
                "1": f"Напоминание о посылке {tracking}",
                "2": f"Посылка {tracking} готова к выдаче в почтомате"
            }
            custom_message = templates.get(template, f"Уведомление о посылке {tracking}")
        
        success, message = self.postomat.notify_recipient(tracking, custom_message, self.current_user_id)
        
        if success:
            print(f"\n{message}")
        else:
            print(f"\nОшибка: {message}")
        
        input("\nНажмите Enter для продолжения...")
    
    def _maintenance(self):
        """Техническое обслуживание"""
        self.clear_screen()
        self.print_header("ТЕХНИЧЕСКОЕ ОБСЛУЖИВАНИЕ")
        
        # Показываем текущее состояние перед обслуживанием
        broken = [l for l in self.postomat.lockers if not l.is_functional]
        if broken:
            print(f"Требуют ремонта: {len(broken)} ячеек")
            for locker in broken:
                print(f"  • Ячейка {locker.number} [{locker.size.value}] - НЕИСПРАВНА")
        else:
            print("Все ячейки исправны")
        
        print("\n" + "-" * 40)
        
        technician = input("Имя техника: ").strip()
        if not technician:
            technician = "Техник"
        
        print("\nПроводится обслуживание...")
        time.sleep(1)  # Имитация работы
        
        try:
            report = self.postomat.perform_maintenance(technician)
            
            print(f"\n{'=' * 50}")
            print(f"ОТЧЕТ О ТЕХНИЧЕСКОМ ОБСЛУЖИВАНИИ")
            print(f"{'=' * 50}")
            print(f"Техник: {report['technician']}")
            print(f"Время: {report['timestamp'].strftime('%d.%m.%Y %H:%M:%S')}")
            print(f"\nПроверено ячеек: {report['lockers_checked']}")
            print(f"Неисправно до ремонта: {report['broken_before']}")
            print(f"Отремонтировано: {report['lockers_repaired']}")
            print(f"Не подлежат ремонту: {report['failed_repairs']}")
            print(f"Осталось неисправных: {report['broken_after']}")
            
            
            if report['broken_after'] > 0:
                print(f"\n ВНИМАНИЕ: {report['broken_after']} ячеек требуют замены!")
            elif report['lockers_repaired'] > 0:
                print(f"\nВсе неисправности устранены")
            else:
                print(f"\nВсе ячейки исправны, профилактика проведена")
            
            print(f"{'=' * 50}")
            
        except Exception as e:
            print(f"\nОшибка: {e}")
        
        input("\nНажмите Enter для продолжения...")
    
    def _break_locker(self):
        """Принудительная поломка ячейки (для демонстрации)"""
        self.clear_screen()
        self.print_header("ПОЛОМКА ЯЧЕЙКИ")
        
        success, message = self.postomat.break_random_locker()
        
        if success:
            print(f"\n{message}")
            print("Ячейка теперь неисправна и требует ремонта")
        else:
            print(f"\nОшибка: {message}")
        
        input("\nНажмите Enter для продолжения...")
    
    def _security(self):
        """Меню безопасности"""
        while True:
            self.clear_screen()
            self.print_header("БЕЗОПАСНОСТЬ")
            
            status = self.postomat.get_security_status()
            
            print(f"Уровень безопасности: {status['level']}")
            print(f"Состояние: {'РАБОТАЕТ' if status['is_operational'] else 'ЗАБЛОКИРОВАН'}")
            print(f"Всего инцидентов: {status['alerts_count']}")
            print(f"Активных пользователей: {status['active_users']}")
            print(f"Всего операций: {status['total_user_operations']}")
            
            if status['recent_alerts']:
                print("\nПоследние инциденты:")
                for alert in status['recent_alerts']:
                    time_str = alert['timestamp'].strftime("%H:%M:%S")
                    print(f"  [{time_str}] {alert['type']}: {alert['description']}")
            
            print("\n--- МЕНЮ БЕЗОПАСНОСТИ ---")
            print("1. Просмотр всех инцидентов")
            print("2. Сбросить безопасность")
            print("3. Назад")
            
            choice = input("\nВыберите действие: ").strip()
            
            if choice == "3":
                break
            elif choice == "1":
                self._view_all_alerts()
            elif choice == "2":
                self._reset_security()
            else:
                print("\nНеверный выбор")
                input("Нажмите Enter...")
    
    def _view_all_alerts(self):
        """Просмотр всех инцидентов"""
        self.clear_screen()
        self.print_header("ВСЕ ИНЦИДЕНТЫ БЕЗОПАСНОСТИ")
        
        if not self.postomat.security_alerts:
            print("Инцидентов не зарегистрировано")
        else:
            print(f"Всего инцидентов: {len(self.postomat.security_alerts)}")
            print("\nПолный список:")
            for i, alert in enumerate(self.postomat.security_alerts, 1):
                time_str = alert['timestamp'].strftime("%d.%m.%Y %H:%M:%S")
                print(f"\n{i}. [{time_str}]")
                print(f"   Тип: {alert['type']}")
                print(f"   Описание: {alert['description']}")
        
        input("\nНажмите Enter для продолжения...")
    
    def _reset_security(self):
        """Сброс системы безопасности"""
        self.clear_screen()
        self.print_header("СБРОС БЕЗОПАСНОСТИ")
        
        confirm = input("Вы уверены? (да/нет): ").strip().lower()
        
        if confirm == "да":
            success, message = self.postomat.reset_security()
            print(f"\n{message}")
        else:
            print("\nОперация отменена")
        
        input("\nНажмите Enter для продолжения...")
    
    def _status(self):
        """Статус почтомата"""
        self.clear_screen()
        self.print_header("СТАТУС ПОЧТОМАТА")
        
        print(self.postomat)
        
        stats = self.postomat.get_statistics()
        print(f"\nДетальная информация:")
        print(f"  Всего уведомлений: {stats['total_notifications']}")
        print(f"  Неисправных ячеек: {stats['broken_lockers']}")
        print(f"  Инцидентов безопасности: {stats['security_alerts']}")
        print(f"  Всего операций пользователей: {stats['total_user_operations']}")
        
        if self.postomat.parcels:
            print(f"\nПосылки в почтомате:")
            for tracking, parcel in self.postomat.parcels.items():
                expires = parcel.storage_until.strftime("%d.%m") if parcel.storage_until else "неизвестно"
                status = "ПРОСРОЧЕНА" if parcel.status == ParcelStatus.EXPIRED else "в норме"
                functional = "ЯЧЕЙКА НЕИСПРАВНА" if not self.postomat.lockers[parcel.locker_number-1].is_functional else ""
                print(f"  • {tracking} - {parcel.recipient.name} (ячейка {parcel.locker_number}, до {expires}) - {status} {functional}")
        else:
            print(f"\nПосылок в почтомате нет")
        
        input("\nНажмите Enter для продолжения...")
    
    def _exit(self):
        """Выход из программы"""
        self.clear_screen()
        self.print_header("ЗАВЕРШЕНИЕ РАБОТЫ")
        
        print(f"\nПользователь {self.current_user_id} выполнил {self.postomat.user_operations.get(self.current_user_id, 0)} операций")
        print("Работа программы завершена")
        print("До свидания!\n")

def main():
    """Точка входа в программу"""
    cli = PostomatCLI()
    cli.run()

if __name__ == "__main__":
    main()
