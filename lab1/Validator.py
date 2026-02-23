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
