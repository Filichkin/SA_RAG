import pytest
from unittest.mock import AsyncMock, patch

from app.api.utils import generate_password_by_pattern, EmailService
from app.crud.user import user_crud
from app.models.user import User


class TestPasswordGeneration:
    """Тесты для генерации паролей"""

    def test_generate_password_by_pattern(self):
        """Тест генерации пароля по паттерну"""
        password = generate_password_by_pattern()
        
        # Проверяем, что пароль не пустой
        assert password is not None
        assert len(password) >= 8
        
        # Проверяем, что пароль содержит разные типы символов
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in '@$!%*?&' for c in password)
        
        assert has_lower, 'Пароль должен содержать строчные буквы'
        assert has_upper, 'Пароль должен содержать заглавные буквы'
        assert has_digit, 'Пароль должен содержать цифры'
        assert has_special, 'Пароль должен содержать спецсимволы'

    def test_generate_multiple_passwords_unique(self):
        """Тест генерации нескольких уникальных паролей"""
        passwords = [generate_password_by_pattern() for _ in range(10)]
        
        # Все пароли должны быть уникальными
        assert len(set(passwords)) == len(passwords), 'Пароли должны быть уникальными'


class TestEmailService:
    """Тесты для сервиса email"""

    def test_email_service_initialization(self):
        """Тест инициализации сервиса email"""
        service = EmailService()
        
        assert service.smtp_host is not None
        assert service.smtp_port is not None
        assert service.email is not None
        assert service.password is not None

    @patch('smtplib.SMTP')
    async def test_send_password_reset_email_success(self, mock_smtp):
        """Тест успешной отправки email с новым паролем"""
        # Настройка мока
        mock_server = AsyncMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        service = EmailService()
        
        # Вызываем метод
        result = await service.send_password_reset_email(
            to_email='test@example.com',
            new_password='NewPass123!',
            user_name='Test User'
        )
        
        assert result is True

    @patch('smtplib.SMTP')
    async def test_send_password_reset_email_failure(self, mock_smtp):
        """Тест неуспешной отправки email"""
        # Настройка мока для выброса исключения
        mock_smtp.side_effect = Exception('SMTP Error')
        
        service = EmailService()
        
        # Вызываем метод
        result = await service.send_password_reset_email(
            to_email='test@example.com',
            new_password='NewPass123!',
            user_name='Test User'
        )
        
        assert result is False


class TestUserCRUDResetPassword:
    """Тесты для CRUD операций сброса пароля"""

    @pytest.mark.asyncio
    async def test_reset_password_success(self):
        """Тест успешного сброса пароля"""
        # Создаем мок пользователя
        mock_user = User()
        mock_user.id = 1
        mock_user.email = 'test@example.com'
        mock_user.hashed_password = 'old_hash'
        mock_user.token_version = 1
        
        # Создаем мок сессии
        mock_session = AsyncMock()
        
        # Вызываем метод
        result = await user_crud.reset_password(
            user=mock_user,
            new_password='NewPass123!',
            session=mock_session
        )
        
        # Проверяем результат
        assert result is True
        
        # Проверяем, что версия токена увеличилась
        assert mock_user.token_version == 2
        
        # Проверяем, что пароль изменился
        assert mock_user.hashed_password != 'old_hash'
        
        # Проверяем, что сессия была закоммичена
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_reset_password_database_error(self):
        """Тест сброса пароля при ошибке базы данных"""
        # Создаем мок пользователя
        mock_user = User()
        mock_user.id = 1
        mock_user.email = 'test@example.com'
        mock_user.hashed_password = 'old_hash'
        mock_user.token_version = 1
        
        # Создаем мок сессии с ошибкой
        mock_session = AsyncMock()
        mock_session.commit.side_effect = Exception('Database error')
        
        # Вызываем метод
        result = await user_crud.reset_password(
            user=mock_user,
            new_password='NewPass123!',
            session=mock_session
        )
        
        # Проверяем результат
        assert result is False
        
        # Проверяем, что был вызван rollback
        mock_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_email_success(self):
        """Тест получения пользователя по email"""
        # Создаем мок сессии
        mock_session = AsyncMock()
        
        # Создаем мок пользователя
        mock_user = User()
        mock_user.id = 1
        mock_user.email = 'test@example.com'
        
        # Настраиваем мок для get_by_attribute
        with patch.object(user_crud, 'get_by_attribute', return_value=mock_user):
            result = await user_crud.get_by_email('test@example.com', mock_session)
            
            assert result == mock_user
            user_crud.get_by_attribute.assert_called_once_with(
                'email', 'test@example.com', mock_session
            )

    @pytest.mark.asyncio
    async def test_get_by_email_not_found(self):
        """Тест получения несуществующего пользователя по email"""
        # Создаем мок сессии
        mock_session = AsyncMock()
        
        # Настраиваем мок для get_by_attribute (возвращает None)
        with patch.object(user_crud, 'get_by_attribute', return_value=None):
            result = await user_crud.get_by_email('nonexistent@example.com', mock_session)
            
            assert result is None
            user_crud.get_by_attribute.assert_called_once_with(
                'email', 'nonexistent@example.com', mock_session
            )
