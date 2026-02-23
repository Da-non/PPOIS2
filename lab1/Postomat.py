class Postomat:
    """Автоматизированный почтомат"""
    
    def __init__(self, 
                 postomat_id: str,
                 address: str,
                 total_lockers: int = 20,
                 security_level: SecurityLevel = SecurityLevel.MEDIUM):
        """
        Инициализация почтомата
        
        Args:
            postomat_id: Идентификатор почтомата
            address: Адрес установки
            total_lockers: Общее количество ячеек
            security_level: Уровень безопасности
        """
        if not postomat_id or not address:
            raise ValueError("ID и адрес почтомата обязательны")
        
        if total_lockers <= 0:
            raise ValueError("Количество ячеек должно быть положительным")
        
        self.id = postomat_id
        self.address = address
        self.total_lockers = total_lockers
        self.security_level = security_level
        self.is_operational = True
        self.security_alerts: List[Dict] = []
        
        # Словарь для отслеживания количества операций по пользователям
        self.user_operations: Dict[str, int] = {}
        
        # Инициализация ячеек (все исправны с самого начала)
        self.lockers: List[Locker] = self._create_lockers()
        
        # Хранилище посылок
        self.parcels: Dict[str, Parcel] = {}
        
        # История
        self.notifications: List[Notification] = []
        self.maintenance_log: List[Dict] = []
    
    def _create_lockers(self) -> List[Locker]:
        """Создание ячеек с распределением по размерам"""
        lockers = []
        
        # Распределение: 50% S, 30% M, 20% L
        s_count = int(self.total_lockers * 0.5)
        m_count = int(self.total_lockers * 0.3)
        l_count = self.total_lockers - s_count - m_count
        
        # Создаем ячейки разных размеров
        for i in range(1, s_count + 1):
            lockers.append(Locker(i, ParcelSize.SMALL))
        
        for i in range(s_count + 1, s_count + m_count + 1):
            lockers.append(Locker(i, ParcelSize.MEDIUM))
        
        for i in range(s_count + m_count + 1, self.total_lockers + 1):
            lockers.append(Locker(i, ParcelSize.LARGE))
        
        # Перемешиваем, чтобы размеры были в случайном порядке
        random.shuffle(lockers)
        
        # Перенумеровываем после перемешивания
        for i, locker in enumerate(lockers, 1):
            locker.number = i
        
        return lockers
    
    def find_available_locker(self, required_size: ParcelSize) -> Optional[Locker]:
        """Поиск свободной ячейки подходящего размера"""
        size_order = {ParcelSize.SMALL: 1, ParcelSize.MEDIUM: 2, ParcelSize.LARGE: 3}
        min_required_size = size_order[required_size]
        
        for locker in self.lockers:
            if not locker.is_occupied and locker.is_functional:
                if size_order[locker.size] >= min_required_size:
                    return locker
        return None
    

    
    def send_parcel(self, parcel: Parcel, user_id: str = "user") -> Tuple[bool, str]:
        """
        Отправка посылки через почтомат
        
        Args:
            parcel: Посылка для отправки
            user_id: ID пользователя
            
        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        # Проверка безопасности
        security_check = self._check_security(user_id, "send")
        if not security_check[0]:
            return False, security_check[1]
        
        if not self.is_operational:
            return False, "Почтомат временно не работает"
        
        if parcel.tracking_number in self.parcels:
            return False, f"Посылка {parcel.tracking_number} уже находится в почтомате"
        
        locker = self.find_available_locker(parcel.size)
        if not locker:
            return False, "Нет свободных ячеек подходящего размера"
        
        try:
            locker.put_parcel(parcel)
            self.parcels[parcel.tracking_number] = parcel
            
            self._notify_recipient(
                parcel.recipient,
                parcel,
                f"Посылка {parcel.tracking_number} поступила в почтомат по адресу {self.address}. Ячейка {locker.number}"
            )
            
            return True, f"Посылка {parcel.tracking_number} отправлена в ячейку {locker.number}"
            
        except LockerError as e:
            return False, f"Ошибка ячейки: {e}"
        except Exception as e:
            return False, f"Системная ошибка: {e}"
    
    
    
    def receive_parcel(self, tracking_number: str, recipient: Recipient, user_id: str = "user") -> Tuple[bool, str, Optional[Parcel]]:
        """
        Получение посылки из почтомата
        
        Args:
            tracking_number: Номер отслеживания
            recipient: Получатель
            user_id: ID пользователя
            
        Returns:
            Tuple[bool, str, Optional[Parcel]]: (успех, сообщение, посылка)
        """
        # Проверка безопасности
        security_check = self._check_security(user_id, "receive")
        if not security_check[0]:
            return False, security_check[1], None
        
        if not self.is_operational:
            return False, "Почтомат временно не работает", None
        
        if tracking_number not in self.parcels:
            return False, f"Посылка {tracking_number} не найдена", None
        
        parcel = self.parcels[tracking_number]
        
        # Проверка прав получателя
        if parcel.recipient.id != recipient.id:
            self._log_security_alert("unauthorized_access", f"Попытка получения {tracking_number} неполучателем")
            return False, "У вас нет прав на получение этой посылки", None
        
        if parcel.status != ParcelStatus.IN_POSTOMAT:
            return False, f"Посылка не готова к выдаче (статус: {parcel.status.value})", None
        
        if parcel.is_expired():
            parcel.status = ParcelStatus.EXPIRED
            return False, "Срок хранения посылки истек", None
        
        locker = None
        for l in self.lockers:
            if l.number == parcel.locker_number:
                locker = l
                break
        
        if not locker:
            return False, "Ошибка: ячейка не найдена", None
        
        try:
            locker.open()
            received_parcel = locker.take_parcel()
            locker.close()
            
            received_parcel.deliver()
            del self.parcels[tracking_number]
            
            return True, f"Посылка {tracking_number} получена", received_parcel
            
        except LockerError as e:
            return False, f"Ошибка при получении: {e}", None
    
    
    def _notify_recipient(self, recipient: Recipient, parcel: Parcel, message: str) -> Optional[Notification]:
        """Внутренний метод отправки уведомления"""
        try:
            notification = Notification(recipient, parcel, message)
            notification.send()
            self.notifications.append(notification)
            return notification
        except NotificationError:
            return None
    
    def notify_recipient(self, tracking_number: str, custom_message: str = "", user_id: str = "user") -> Tuple[bool, str]:
        """
        Публичный метод отправки уведомления
        
        Args:
            tracking_number: Номер посылки
            custom_message: Пользовательское сообщение
            user_id: ID пользователя
            
        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        security_check = self._check_security(user_id, "notify")
        if not security_check[0]:
            return False, security_check[1]
        
        if tracking_number not in self.parcels:
            return False, f"Посылка {tracking_number} не найдена"
        
        parcel = self.parcels[tracking_number]
        message = custom_message or f"Напоминание: посылка {tracking_number} ожидает в почтомате"
        
        notification = self._notify_recipient(parcel.recipient, parcel, message)
        
        if notification and notification.is_sent:
            return True, f"Уведомление отправлено {parcel.recipient.name}"
        else:
            return False, "Не удалось отправить уведомление"
    
    
    def perform_maintenance(self, technician: str) -> Dict:
        """
        Техническое обслуживание почтомата
        
        Args:
            technician: Имя техника
            
        Returns:
            Dict: Отчет о обслуживании
        """
        if not technician:
            raise ValueError("Имя техника обязательно")
        
        # Проверяем, какие ячейки неисправны ДО обслуживания
        broken_before = [l for l in self.lockers if not l.is_functional]
        
        report = {
            "timestamp": datetime.now(),
            "technician": technician,
            "lockers_checked": len(self.lockers),
            "broken_before": len(broken_before),
            "broken_after": 0,
            "lockers_repaired": 0,
            "failed_repairs": 0,
            "issues": []
        }
        
        # Информация о неисправностях до ремонта
        for locker in broken_before:
            report["issues"].append(f"Ячейка {locker.number} была неисправна")
        
        # Ремонт ячеек
        for locker in self.lockers:
            if not locker.is_functional:
                # 85% вероятность успешного ремонта
                if random.random() < 0.85:
                    locker.repair()
                    report["lockers_repaired"] += 1
                    report["issues"].append(f"Ячейка {locker.number} отремонтирована")
                else:
                    report["failed_repairs"] += 1
                    report["issues"].append(f"⚠️ Ячейка {locker.number} требует замены")
            else:
                # Профилактика исправных ячеек
                locker.last_maintenance = datetime.now()
        
        # Проверяем, сколько осталось неисправных
        report["broken_after"] = len([l for l in self.lockers if not l.is_functional])
        
        self.maintenance_log.append(report)
        return report
    
    def break_random_locker(self) -> Tuple[bool, str]:
        """
        Принудительно сломать случайную ячейку (для тестирования)
        
        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        functional_lockers = [l for l in self.lockers if l.is_functional and not l.is_occupied]
        
        if not functional_lockers:
            return False, "Нет исправных свободных ячеек для поломки"
        
        locker = random.choice(functional_lockers)
        locker.is_functional = False
        self._log_security_alert("manual_failure", f"Ячейка {locker.number} принудительно сломана")
        
        return True, f"Ячейка {locker.number} сломана"
    
    
    def _check_security(self, user_id: str, operation: str) -> Tuple[bool, str]:
        """
        Проверка безопасности операции
        
        Args:
            user_id: ID пользователя
            operation: Тип операции
            
        Returns:
            Tuple[bool, str]: (разрешено, сообщение)
        """
        if not self.is_operational:
            return False, "Почтомат заблокирован по соображениям безопасности"
        
        # Увеличиваем счетчик операций пользователя
        self.user_operations[user_id] = self.user_operations.get(user_id, 0) + 1
        
        # Проверка на подозрительную активность (более 50 операций)
        if self.user_operations[user_id] > 50:
            self._log_security_alert("suspicious_activity", 
                                    f"Пользователь {user_id} выполнил {self.user_operations[user_id]} операций")
            
            if self.security_level == SecurityLevel.HIGH:
                return False, "Обнаружена подозрительная активность. Операция заблокирована"
        
        return True, "OK"
    
    def _log_security_alert(self, alert_type: str, description: str):
        """Логирование события безопасности"""
        self.security_alerts.append({
            "timestamp": datetime.now(),
            "type": alert_type,
            "description": description
        })
        
        # Автоматическая блокировка при серьезных инцидентах на HIGH уровне
        if self.security_level == SecurityLevel.HIGH and alert_type in ["unauthorized_access", "suspicious_activity"]:
            self.is_operational = False
    
    def get_security_status(self) -> Dict:
        """Получение статуса безопасности"""
        return {
            "level": self.security_level.name,
            "is_operational": self.is_operational,
            "alerts_count": len(self.security_alerts),
            "total_user_operations": sum(self.user_operations.values()),
            "active_users": len(self.user_operations),
            "recent_alerts": self.security_alerts[-5:] if self.security_alerts else []
        }
    
    def reset_security(self) -> Tuple[bool, str]:
        """
        Сброс системы безопасности (для администратора)
        
        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        self.is_operational = True
        self.security_alerts.clear()
        self.user_operations.clear()
        return True, "Система безопасности сброшена"
    
    def check_expired_parcels(self) -> List[Parcel]:
        """Проверка просроченных посылок"""
        expired = []
        for tracking, parcel in list(self.parcels.items()):
            if parcel.is_expired() and parcel.status == ParcelStatus.IN_POSTOMAT:
                parcel.status = ParcelStatus.EXPIRED
                expired.append(parcel)
                
                # Уведомление отправителю
                self._notify_recipient(
                    Recipient(parcel.sender.name, parcel.sender.phone, parcel.sender.email),
                    parcel,
                    f"Посылка {tracking} не получена. Срок хранения истек."
                )
        
        return expired
    
    def get_statistics(self) -> Dict:
        """Получение статистики"""
        total_lockers = len(self.lockers)
        occupied = sum(1 for l in self.lockers if l.is_occupied)
        functional = sum(1 for l in self.lockers if l.is_functional)
        
        return {
            "id": self.id,
            "address": self.address,
            "status": "работает" if self.is_operational else "заблокирован",
            "security_level": self.security_level.name,
            "total_lockers": total_lockers,
            "occupied_lockers": occupied,
            "free_lockers": total_lockers - occupied,
            "functional_lockers": functional,
            "broken_lockers": total_lockers - functional,
            "active_parcels": len(self.parcels),
            "total_notifications": len(self.notifications),
            "security_alerts": len(self.security_alerts),
            "total_user_operations": sum(self.user_operations.values())
        }
    
    def __str__(self) -> str:
        stats = self.get_statistics()
        security_status = "НОРМА"
        if not stats['status'] == "работает":
            security_status = "ЗАБЛОКИРОВАН"
        elif stats['security_alerts'] > 10:
            security_status = "ВНИМАНИЕ"
            
        return (f"Почтомат {self.id}\n"
                f"Адрес: {self.address}\n"
                f"Статус: {stats['status']}\n"
                f"Безопасность: {stats['security_level']} ({security_status})\n"
                f"Ячейки: {stats['free_lockers']} свободно из {stats['total_lockers']}\n"
                f"Посылок: {stats['active_parcels']}")
