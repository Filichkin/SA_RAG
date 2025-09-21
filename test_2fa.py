#!/usr/bin/env python3
"""
Простой тест для проверки работы двухфакторной аутентификации
"""
import asyncio
import httpx
import json


async def test_2fa():
    """Тестирует двухфакторную аутентификацию"""
    base_url = 'http://localhost:8000'
    
    # Тестовые данные (замените на реальные)
    test_email = 'test@example.com'
    test_password = 'TestPass123!'
    
    async with httpx.AsyncClient() as client:
        print('🔐 Тестирование двухфакторной аутентификации')
        print('=' * 50)
        
        # Шаг 1: Первый этап входа (отправка кода)
        print('\n📧 Шаг 1: Отправка запроса на вход...')
        login_data = {
            'email': test_email,
            'password': test_password
        }
        
        try:
            response = await client.post(
                f'{base_url}/auth/2fa/login',
                json=login_data
            )
            
            print(f'Статус ответа: {response.status_code}')
            print(f'Ответ: {response.json()}')
            
            if response.status_code == 200:
                print('✅ Код успешно отправлен на email!')
                
                # Шаг 2: Второй этап входа (проверка кода)
                print('\n🔑 Шаг 2: Проверка кода...')
                print('Введите 6-значный код из email:')
                code = input('Код: ')
                
                verify_data = {
                    'email': test_email,
                    'code': code
                }
                
                response = await client.post(
                    f'{base_url}/auth/2fa/verify',
                    json=verify_data
                )
                
                print(f'Статус ответа: {response.status_code}')
                print(f'Ответ: {response.json()}')
                
                if response.status_code == 200:
                    print('✅ Успешный вход! Токен получен.')
                    token_data = response.json()
                    print(f'Токен: {token_data.get("access_token", "Не найден")[:50]}...')
                else:
                    print('❌ Ошибка при проверке кода')
            else:
                print('❌ Ошибка при отправке кода')
                
        except Exception as e:
            print(f'❌ Ошибка: {e}')


if __name__ == '__main__':
    asyncio.run(test_2fa())
