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
