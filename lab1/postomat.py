
"""
Модель автоматизированного почтомата
Вариант 79

Предметная область: автоматизированные пункты выдачи и приема почтовых отправлений.
Сущности: почтомат, почтовые отправления, получатель, отправитель, уведомление.
Операции: отправка, получение, уведомление, техобслуживание, безопасность.
"""

from enum import Enum
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple, Set
import time
import hashlib
import random
import re

class PostomatError(Exception):
    """Базовое исключение для всех ошибок почтомата"""
    pass


class ParcelError(PostomatError):
    """Ошибка, связанная с посылкой"""
    pass


class LockerError(PostomatError):
    """Ошибка, связанная с ячейкой"""
    pass


class SecurityError(PostomatError):
    """Ошибка безопасности"""
    pass


class NotificationError(PostomatError):
    """Ошибка отправки уведомления"""
    pass


class ValidationError(PostomatError):
    """Ошибка валидации данных"""
    pass


class ParcelStatus(str, Enum):
    """Статусы посылки"""
    CREATED = "создана"
    IN_POSTOMAT = "в почтомате"
    DELIVERED = "получена"
    EXPIRED = "просрочена"


class ParcelSize(str, Enum):
    """Размеры посылок"""
    SMALL = "S"
    MEDIUM = "M"
    LARGE = "L"


class SecurityLevel(int, Enum):
    """Уровни безопасности"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class NotificationType(str, Enum):
    """Типы уведомлений"""
    SMS = "SMS"
    EMAIL = "Email"

class Validator:
    """Класс для валидации данных."""

    # Допустимые коды белорусских операторов
    BELARUSIAN_OPERATORS: List[str] = ["24", "25", "29", "33", "44"]

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """
        Проверка формата белорусского телефона.

        Допустимые форматы:
        - +375XXXXXXXXX
        - 80XXXXXXXXX
        - 375XXXXXXXXX
        - 8XXXXXXXXX

        Первые две цифры после кода должны быть кодом оператора (24, 25, 29, 33, 44).

        Args:
            phone: Номер телефона для проверки.

        Returns:
            True если номер валидный, иначе False.
        """
        # Удаляем все пробелы, дефисы, скобки
        cleaned: str = re.sub(r'[\s\-\(\)]', '', phone)

        # Определяем проверочный номер в едином формате
        check_phone: str

        # Если номер уже в формате +375XXXXXXXXX
        if re.match(r'^\+375\d{9}$', cleaned):
            check_phone = cleaned
        # Если номер в формате 80XXXXXXXXX
        elif re.match(r'^80\d{9}$', cleaned):
            operator_code: str = cleaned[2:4]
            if operator_code not in Validator.BELARUSIAN_OPERATORS:
                return False
            check_phone = '+375' + cleaned[2:]
        # Если номер в формате 375XXXXXXXXX
        elif re.match(r'^375\d{9}$', cleaned):
            operator_code = cleaned[3:5]
            if operator_code not in Validator.BELARUSIAN_OPERATORS:
                return False
            check_phone = '+' + cleaned
        # Если номер в формате 8XXXXXXXXX (10 цифр)
        elif re.match(r'^8\d{9}$', cleaned) and len(cleaned) == 10:
            operator_code = cleaned[1:3]
            if operator_code not in Validator.BELARUSIAN_OPERATORS:
                return False
            check_phone = '+375' + cleaned[1:]
        else:
            return False

        # Проверяем, что получился правильный формат
        if not re.match(r'^\+375\d{9}$', check_phone):
            return False

        return True

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Проверка формата email.

        Допустимые форматы: username@domain.zone

        Args:
            email: Email для проверки.

        Returns:
            True если email валидный, иначе False.
        """
        email = email.strip().lower()

        # Общая проверка формата email
        pattern: str = r'^[a-zA-Z0-9][a-zA-Z0-9._%+-]*[a-zA-Z0-9]@[a-zA-Z0-9][a-zA-Z0-9.-]*\.[a-zA-Z]{2,}$'

        if not re.match(pattern, email):
            return False

        # Проверка на двойные точки
        if '..' in email or '..' in email.split('@')[0]:
            return False

        # Проверка на недопустимые символы в начале/конце
        local_part: str = email.split('@')[0]
        if local_part.startswith('.') or local_part.endswith('.'):
            return False

        return True

    @staticmethod
    def validate_name(name: str) -> bool:
        """
        Проверка имени.

        Только буквы, пробелы и дефис, без цифр, минимум 2 символа.

        Args:
            name: Имя для проверки.

        Returns:
            True если имя валидное, иначе False.
        """
        name = name.strip()

        if len(name) < 2:
            return False

        # Проверяем, что нет цифр
        if re.search(r'\d', name):
            return False

        # Только буквы, пробелы и дефис
        pattern: str = r'^[а-яА-ЯёЁa-zA-Z\s\-]+$'
        return bool(re.match(pattern, name))

    @staticmethod
    def validate_description(description: str) -> bool:
        """
        Проверка описания посылки.

        Необязательное, но без цифр, если есть.

        Args:
            description: Описание для проверки.

        Returns:
            True если описание валидное, иначе False.
        """
        description = description.strip()

        # Пустое описание разрешено
        if not description:
            return True

        # Проверяем, что нет цифр
        if re.search(r'\d', description):
            return False

        # Только буквы, пробелы, знаки препинания
        pattern: str = r'^[а-яА-ЯёЁa-zA-Z\s\.,!?\-]+$'
        return bool(re.match(pattern, description))

    @staticmethod
    def validate_address(address: str) -> bool:
        """
        Проверка адреса.

        Не пустой, минимум 5 символов, не только цифры.

        Args:
            address: Адрес для проверки.

        Returns:
            True если адрес валидный, иначе False.
        """
        address = address.strip()

        if len(address) < 5:
            return False

        # Адрес не должен состоять только из цифр
        if address.isdigit():
            return False

        return True

    @staticmethod
    def validate_tracking(tracking: str) -> bool:
        """
        Проверка формата трек-номера.

        Формат: 3 заглавные буквы + 5-15 цифр.

        Args:
            tracking: Трек-номер для проверки.

        Returns:
            True если трек-номер валидный, иначе False.
        """
        if not tracking or not isinstance(tracking, str):
            return False

        # Убираем пробелы
        tracking = tracking.strip()

        # Проверяем минимальную длину (3 буквы + 5 цифр = 8)
        if len(tracking) < 8:
            return False

        # Проверяем формат: 3 заглавные буквы + цифры
        letters_part: str = tracking[:3]
        digits_part: str = tracking[3:]

        # Проверяем, что первые 3 символа - заглавные буквы
        if not letters_part.isalpha() or not letters_part.isupper():
            return False

        # Проверяем, что остальные символы - цифры
        if not digits_part.isdigit():
            return False

        # Проверяем длину цифровой части (5-15 цифр)
        if len(digits_part) < 5 or len(digits_part) > 15:
            return False

        return True

    @staticmethod
    def normalize_phone(phone: str) -> str:
        """
        Приведение телефона к единому формату +375XXXXXXXXX.

        Args:
            phone: Номер телефона для нормализации.

        Returns:
            Номер в формате +375XXXXXXXXX.
        """
        cleaned: str = re.sub(r'[\s\-\(\)]', '', phone)

        # Если уже в правильном формате
        if re.match(r'^\+375\d{9}$', cleaned):
            return cleaned

        # Если начинается с 80
        if re.match(r'^80\d{9}$', cleaned):
            return '+375' + cleaned[2:]

        # Если начинается с 8 (без 0)
        if re.match(r'^8\d{9}$', cleaned) and len(cleaned) == 10:
            return '+375' + cleaned[1:]

        # Если начинается с 375
        if re.match(r'^375\d{9}$', cleaned):
            return '+' + cleaned

        return cleaned

class Person:
    """Базовый класс для отправителя и получателя"""
    
    def __init__(self, name: str, phone: str, email: str):
        """
        Инициализация персоны
        
        Args:
            name: Имя
            phone: Телефон
            email: Email
            
        Raises:
            ValidationError: Если данные не проходят валидацию
        """
        if not Validator.validate_name(name):
            raise ValidationError(
                "Имя должно содержать минимум 2 символа и только буквы, пробелы или дефис (без цифр)"
            )
        
        if not Validator.validate_phone(phone):
            raise ValidationError(
                "Неверный формат телефона. Используйте +375 и код оператора (24,25,29,33,44). "
                "Пример: +375291234567"
            )
        
        if not Validator.validate_email(email):
            raise ValidationError(
                "Неверный формат email. Пример: name@domain.by"
            )
        
        self.name = name.strip()
        self.phone = Validator.normalize_phone(phone)
        self.email = email.strip().lower()
        self.id = self._generate_id()
    
    def _generate_id(self) -> str:
        """Генерация уникального идентификатора"""
        data = f"{self.name}{self.phone}{self.email}".encode()
        return hashlib.md5(data).hexdigest()[:10]
    
    def __str__(self) -> str:
        return f"{self.name}"



class Sender(Person):
    """Отправитель посылки"""
    
    def __init__(self, name: str, phone: str, email: str, address: str):
        """
        Инициализация отправителя
        
        Args:
            name: Имя
            phone: Телефон
            email: Email
            address: Адрес отправителя
        """
        super().__init__(name, phone, email)
        
        if not Validator.validate_address(address):
            raise ValidationError(
                "Адрес должен содержать минимум 5 символов и не состоять только из цифр"
            )
        
        self.address = address.strip()
    
    def __str__(self) -> str:
        return f"Отправитель: {self.name}, адрес: {self.address}"


class Recipient(Person):
    """Получатель посылки"""
    
    def __init__(self, name: str, phone: str, email: str):
        """Инициализация получателя"""
        super().__init__(name, phone, email)
    
    def __str__(self) -> str:
        return f"Получатель: {self.name}"


class Parcel:
    """Почтовое отправление"""
    
    _existing_trackings: Set[str] = set()
    TRACKING_PREFIXES = ["ABC", "XYZ", "TRK", "PKG", "BOX", "SHP", "DLV", "POS"]
    
    def __init__(self, 
                 sender: Sender,
                 recipient: Recipient,
                 size: ParcelSize,
                 description: str = ""):
        """
        Инициализация посылки с автоматической генерацией трек-номера
        
        Args:
            sender: Отправитель
            recipient: Получатель
            size: Размер
            description: Описание (без цифр)
            
        Raises:
            ValidationError: Если описание содержит цифры
        """
        if not sender or not recipient:
            raise ValidationError("Отправитель и получатель обязательны")
        
        # Проверка описания на наличие цифр
        if not Validator.validate_description(description):
            raise ValidationError("Описание посылки не должно содержать цифр")
        
        self.tracking_number = self._generate_unique_tracking()
        self.sender = sender
        self.recipient = recipient
        self.size = size
        self.description = description.strip()
        self.status = ParcelStatus.CREATED
        self.created_at = datetime.now()
        self.placed_at: Optional[datetime] = None
        self.delivered_at: Optional[datetime] = None
        self.locker_number: Optional[int] = None
        self.storage_days = 3
        self.storage_until: Optional[datetime] = None
    
    @classmethod
    def _generate_unique_tracking(cls) -> str:
        """Генерация уникального трек-номера"""
        while True:
            prefix = random.choice(cls.TRACKING_PREFIXES)
            numbers = ''.join([str(random.randint(0, 9)) for _ in range(10)])
            tracking = f"{prefix}{numbers}"
            
            if tracking not in cls._existing_trackings:
                cls._existing_trackings.add(tracking)
                return tracking
    
    def place_in_locker(self, locker_number: int):
        """Размещение в ячейке"""
        self.status = ParcelStatus.IN_POSTOMAT
        self.placed_at = datetime.now()
        self.locker_number = locker_number
        self.storage_until = datetime.now() + timedelta(days=self.storage_days)
    
    def deliver(self):
        """Получение посылки"""
        self.status = ParcelStatus.DELIVERED
        self.delivered_at = datetime.now()
    
    def is_expired(self) -> bool:
        """Проверка на просрочку"""
        if not self.storage_until:
            return False
        return datetime.now() > self.storage_until
    
    def get_info(self) -> Dict:
        """Получение информации о посылке"""
        return {
            "tracking": self.tracking_number,
            "sender": str(self.sender),
            "recipient": str(self.recipient),
            "size": self.size.value,
            "description": self.description,
            "status": self.status.value,
            "created": self.created_at.strftime("%d.%m.%Y %H:%M"),
            "locker": self.locker_number,
            "storage_until": self.storage_until.strftime("%d.%m.%Y") if self.storage_until else None
        }
    
    def __str__(self) -> str:
        return f"Посылка {self.tracking_number} [{self.size.value}] - {self.status.value}"


class Locker:
    """Ячейка почтомата"""
    
    def __init__(self, number: int, size: ParcelSize):
        """
        Инициализация ячейки
        
        Args:
            number: Номер ячейки
            size: Размер ячейки
        """
        self.number = number
        self.size = size
        self.is_occupied = False
        self.is_functional = True
        self.current_parcel: Optional[Parcel] = None
        self.last_maintenance: Optional[datetime] = None
    
    def open(self) -> bool:
        """Открытие ячейки"""
        if not self.is_functional:
            raise LockerError(f"Ячейка {self.number} неисправна")
        return True
    
    def close(self) -> bool:
        """Закрытие ячейки"""
        return True
    
    def put_parcel(self, parcel: Parcel) -> bool:
        """Помещение посылки в ячейку"""
        if not self.is_functional:
            raise LockerError(f"Ячейка {self.number} неисправна")
        
        if self.is_occupied:
            raise LockerError(f"Ячейка {self.number} уже занята")
        
        size_order = {ParcelSize.SMALL: 1, ParcelSize.MEDIUM: 2, ParcelSize.LARGE: 3}
        if size_order[parcel.size] > size_order[self.size]:
            raise LockerError(f"Посылка слишком большая для ячейки {self.number}")
        
        self.is_occupied = True
        self.current_parcel = parcel
        parcel.place_in_locker(self.number)
        return True
    
    def take_parcel(self) -> Parcel:
        """Извлечение посылки из ячейки"""
        if not self.is_functional:
            raise LockerError(f"Ячейка {self.number} неисправна")
        
        if not self.is_occupied:
            raise LockerError(f"Ячейка {self.number} пуста")
        
        parcel = self.current_parcel
        self.is_occupied = False
        self.current_parcel = None
        return parcel
    
    def repair(self) -> bool:
        """Ремонт ячейки"""
        self.is_functional = True
        self.last_maintenance = datetime.now()
        return True
    
    def get_info(self) -> Dict:
        """Информация о ячейке"""
        return {
            "number": self.number,
            "size": self.size.value,
            "occupied": self.is_occupied,
            "functional": self.is_functional,
            "parcel": self.current_parcel.tracking_number if self.current_parcel else None,
            "last_maintenance": self.last_maintenance.strftime("%d.%m.%Y") if self.last_maintenance else None
        }
    
    def __str__(self) -> str:
        status = "занята" if self.is_occupied else "свободна"
        functional = "исправна" if self.is_functional else "неисправна"
        return f"Ячейка {self.number} [{self.size.value}] {status} ({functional})"



class Notification:
    """Уведомление получателя"""
    
    def __init__(self, 
                 recipient: Recipient,
                 parcel: Parcel,
                 message: str,
                 notification_type: NotificationType = NotificationType.SMS):
        """
        Инициализация уведомления
        
        Args:
            recipient: Получатель уведомления
            parcel: Посылка
            message: Текст сообщения
            notification_type: Тип уведомления
        """
        self.recipient = recipient
        self.parcel = parcel
        self.message = message
        self.type = notification_type
        self.created_at = datetime.now()
        self.sent_at: Optional[datetime] = None
        self.is_sent = False
        self.attempts = 0
    
    def send(self) -> bool:
        """Отправка уведомления"""
        self.attempts += 1
        try:
            time.sleep(0.1)
            self.sent_at = datetime.now()
            self.is_sent = True
            return True
        except Exception:
            raise NotificationError("Не удалось отправить уведомление")
    
    def __str__(self) -> str:
        status = "отправлено" if self.is_sent else "ожидает"
        return f"{self.type.value} {status}: {self.message[:30]}..."


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
