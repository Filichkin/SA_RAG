import re
import smtplib
import string
import secrets
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings


def generate_password_by_pattern() -> str:
    """
    Генерирует пароль по паттерну из настроек.

    Returns:
        str: Сгенерированный пароль, соответствующий password_pattern
    """
    # Извлекаем требования из паттерна
    # Паттерн: r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'

    # Минимальная длина из паттерна (8 символов)
    # Паттерн требует минимум 8 символов, поэтому используем
    # max(8, settings.user_password_min_len)
    min_length = max(8, settings.user_password_min_len)

    # Символы для генерации
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    special_chars = '@$!%*?&'

    # Объединяем все допустимые символы
    all_chars = lowercase + uppercase + digits + special_chars

    # Максимальное количество попыток для генерации валидного пароля
    max_attempts = 100

    for attempt in range(max_attempts):
        # Генерируем пароль с гарантированным наличием всех типов символов
        password_chars = []

        # Добавляем по одному символу каждого типа
        password_chars.append(secrets.choice(lowercase))
        password_chars.append(secrets.choice(uppercase))
        password_chars.append(secrets.choice(digits))
        password_chars.append(secrets.choice(special_chars))

        # Заполняем остальную длину случайными символами
        for _ in range(min_length - 4):
            password_chars.append(secrets.choice(all_chars))

        # Перемешиваем символы
        secrets.SystemRandom().shuffle(password_chars)

        password = ''.join(password_chars)

        # Проверяем соответствие паттерну
        if re.match(settings.password_pattern, password):
            return password

    # Если не удалось сгенерировать валидный пароль за max_attempts попыток
    # Возвращаем гарантированно валидный пароль
    return 'Password123!'


def generate_2fa_code() -> str:
    """
    Генерирует 6-значный числовой код для двухфакторной аутентификации.

    Returns:
        str: 6-значный числовой код
    """
    return ''.join([str(secrets.randbelow(10)) for _ in range(6)])


def is_2fa_code_expired(created_at: datetime) -> bool:
    """
    Проверяет, истек ли срок действия 2FA кода.

    Args:
        created_at: Время создания кода

    Returns:
        bool: True если код истек, False иначе
    """
    expiration_time = created_at + timedelta(minutes=10)
    return datetime.now(timezone.utc) > expiration_time


class EmailService:
    """Сервис для отправки email сообщений"""

    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.email = settings.yandax_email
        self.password = settings.yandex_app_pass

    async def send_password_reset_email(
        self,
        to_email: str,
        new_password: str,
        user_name: str
    ) -> bool:
        """
        Отправляет email с новым паролем пользователю.

        Args:
            to_email: Email получателя
            new_password: Новый пароль
            user_name: Имя пользователя

        Returns:
            bool: True если email отправлен успешно, False иначе
        """
        try:
            # Создаем сообщение
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = to_email
            msg['Subject'] = 'Сброс пароля - SA_RAG Agent'

            # Создаем тело письма
            body = f'''
Добро пожаловать, {user_name}!

Ваш пароль был сброшен. Используйте новый пароль для входа:

Новый пароль: {new_password}

ВАЖНО:
- Сохраните этот пароль в безопасном месте
- После входа рекомендуем сменить пароль в настройках профиля
- Все ваши активные сессии были завершены

Если вы не запрашивали сброс пароля, немедленно свяжитесь с
администратором.

С уважением,
Команда SA_RAG Agent
'''

            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            # Подключаемся к серверу и отправляем
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.send_message(msg)

            return True

        except Exception as e:
            # В продакшене использовать логирование
            print(f'Ошибка отправки email: {e}')
            return False

    async def send_2fa_code_email(
        self,
        to_email: str,
        code: str,
        user_name: str
    ) -> bool:
        """
        Отправляет email с кодом двухфакторной аутентификации.

        Args:
            to_email: Email получателя
            code: 6-значный код
            user_name: Имя пользователя

        Returns:
            bool: True если email отправлен успешно, False иначе
        """
        try:
            # Создаем сообщение
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = to_email
            msg['Subject'] = 'Код подтверждения - SA_RAG Agent'

            # Создаем тело письма
            body = f'''
Добро пожаловать, {user_name}!

Ваш код подтверждения для входа в систему:

{code}

ВАЖНО:
- Код действителен в течение 10 минут
- Не передавайте этот код третьим лицам
- Если вы не запрашивали вход в систему, проигнорируйте это письмо

С уважением,
Команда SA_RAG Agent
'''

            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            # Подключаемся к серверу и отправляем
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.send_message(msg)

            return True

        except Exception as e:
            # В продакшене использовать логирование
            print(f'Ошибка отправки 2FA email: {e}')
            return False

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str
    ) -> bool:
        """
        Общий метод для отправки email.

        Args:
            to_email: Email получателя
            subject: Тема письма
            body: Тело письма

        Returns:
            bool: True если email отправлен успешно, False иначе
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.send_message(msg)

            return True

        except Exception as e:
            # В продакшене использовать логирование
            print(f'Ошибка отправки email: {e}')
            return False


# Создаем экземпляр сервиса
email_service = EmailService()
