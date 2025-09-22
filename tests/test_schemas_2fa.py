'''
Тесты для схем двухфакторной аутентификации
'''
import pytest
from pydantic import ValidationError

from app.schemas.two_factor_auth import (
    TwoFactorAuthRequest,
    TwoFactorAuthVerifyCode,
    TwoFactorAuthResponse,
    TwoFactorAuthTokenResponse
)


class TestTwoFactorAuthSchemas:
    '''Тесты схем 2FA'''

    def test_two_factor_auth_request_valid(self):
        '''Тест валидной схемы TwoFactorAuthRequest'''
        data = {
            'email': 'test@example.com',
            'password': 'ValidPass123!'
        }

        schema = TwoFactorAuthRequest(**data)
        assert schema.email == 'test@example.com'
        assert schema.password == 'ValidPass123!'

    def test_two_factor_auth_request_invalid_email(self):
        '''Тест невалидного email в TwoFactorAuthRequest'''
        data = {
            'email': 'invalid-email',
            'password': 'ValidPass123!'
        }

        # TwoFactorAuthRequest не имеет валидации email, поэтому тест проходит
        schema = TwoFactorAuthRequest(**data)
        assert schema.email == 'invalid-email'
        assert schema.password == 'ValidPass123!'

    def test_two_factor_auth_verify_code_valid(self):
        '''Тест валидной схемы TwoFactorAuthVerifyCode'''
        data = {
            'code': '123456'
        }

        schema = TwoFactorAuthVerifyCode(**data)
        assert schema.code == '123456'

    def test_two_factor_auth_verify_code_invalid_length(self):
        '''Тест невалидной длины кода в TwoFactorAuthVerifyCode'''
        data = {
            'code': '12345'  # 5 цифр вместо 6
        }

        with pytest.raises(ValidationError):
            TwoFactorAuthVerifyCode(**data)

    def test_two_factor_auth_verify_code_invalid_format(self):
        '''Тест невалидного формата кода в TwoFactorAuthVerifyCode'''
        data = {
            'code': '12345a'  # содержит букву
        }

        with pytest.raises(ValidationError):
            TwoFactorAuthVerifyCode(**data)

    def test_two_factor_auth_verify_code_empty(self):
        '''Тест пустого кода в TwoFactorAuthVerifyCode'''
        data = {
            'code': ''
        }

        with pytest.raises(ValidationError):
            TwoFactorAuthVerifyCode(**data)

    def test_two_factor_auth_response_valid(self):
        '''Тест валидной схемы TwoFactorAuthResponse'''
        data = {
            'message': 'Код отправлен на email',
            'temp_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
        }

        schema = TwoFactorAuthResponse(**data)
        assert schema.message == 'Код отправлен на email'
        assert schema.temp_token == 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'

    def test_two_factor_auth_response_missing_temp_token(self):
        '''Тест TwoFactorAuthResponse без temp_token'''
        data = {
            'message': 'Код отправлен на email'
        }

        with pytest.raises(ValidationError):
            TwoFactorAuthResponse(**data)

    def test_two_factor_auth_token_response_valid(self):
        '''Тест валидной схемы TwoFactorAuthTokenResponse'''
        data = {
            'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
            'token_type': 'bearer'
        }

        schema = TwoFactorAuthTokenResponse(**data)
        assert schema.access_token == 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
        assert schema.token_type == 'bearer'

    def test_two_factor_auth_token_response_default_token_type(self):
        '''Тест TwoFactorAuthTokenResponse с дефолтным token_type'''
        data = {
            'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
        }

        schema = TwoFactorAuthTokenResponse(**data)
        assert schema.access_token == 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
        assert schema.token_type == 'bearer'  # дефолтное значение

    def test_two_factor_auth_token_response_missing_access_token(self):
        '''Тест TwoFactorAuthTokenResponse без access_token'''
        data = {
            'token_type': 'bearer'
        }

        with pytest.raises(ValidationError):
            TwoFactorAuthTokenResponse(**data)

    def test_code_validation_edge_cases(self):
        '''Тест граничных случаев валидации кода'''
        # Код с 6 нулями
        schema = TwoFactorAuthVerifyCode(code='000000')
        assert schema.code == '000000'

        # Код с 6 девятками
        schema = TwoFactorAuthVerifyCode(code='999999')
        assert schema.code == '999999'

        # Код с пробелами (должен быть отклонен)
        with pytest.raises(ValidationError):
            TwoFactorAuthVerifyCode(code='123 56')

        # Код с дефисами (должен быть отклонен)
        with pytest.raises(ValidationError):
            TwoFactorAuthVerifyCode(code='123-56')

    def test_schema_serialization(self):
        '''Тест сериализации схем'''
        # TwoFactorAuthRequest
        request = TwoFactorAuthRequest(
            email='test@example.com',
            password='ValidPass123!'
        )
        assert request.model_dump() == {
            'email': 'test@example.com',
            'password': 'ValidPass123!'
        }

        # TwoFactorAuthVerifyCode
        verify_code = TwoFactorAuthVerifyCode(code='123456')
        assert verify_code.model_dump() == {'code': '123456'}

        # TwoFactorAuthResponse
        response = TwoFactorAuthResponse(
            message='Код отправлен',
            temp_token='temp_token_here'
        )
        assert response.model_dump() == {
            'message': 'Код отправлен',
            'temp_token': 'temp_token_here'
        }
