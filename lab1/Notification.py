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
