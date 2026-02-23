class ParcelStatus(str, Enum):
    """Статусы посылки"""
    CREATED = "создана"
    IN_POSTOMAT = "в почтомате"
    DELIVERED = "получена"
    EXPIRED = "просрочена"
