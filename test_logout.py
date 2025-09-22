#!/usr/bin/env python3
'''
Простой тест для проверки logout эндпоинта
'''
import asyncio
import httpx


async def test_logout():
    '''Тест logout эндпоинта'''
    base_url = 'http://localhost:8000'
    
    async with httpx.AsyncClient() as client:
        print('🧪 Тестирование logout эндпоинта...')
        
        # Тест 1: Logout без токена (должен вернуть 401)
        print('\n1. Тест logout без токена:')
        response = await client.post(f'{base_url}/auth/logout')
        print(f'   Статус: {response.status_code}')
        if response.status_code == 401:
            print('   ✅ Ожидаемый результат: 401 Unauthorized')
        else:
            print(f'   ❌ Неожиданный результат: {response.text}')
        
        # Тест 2: Logout с недействительным токеном (должен вернуть 401)
        print('\n2. Тест logout с недействительным токеном:')
        headers = {'Authorization': 'Bearer invalid_token'}
        response = await client.post(f'{base_url}/auth/logout', headers=headers)
        print(f'   Статус: {response.status_code}')
        if response.status_code == 401:
            print('   ✅ Ожидаемый результат: 401 Unauthorized')
        else:
            print(f'   ❌ Неожиданный результат: {response.text}')
        
        print('\n📋 Для полного тестирования необходимо:')
        print('   1. Запустить сервер: uvicorn app.main:app --reload')
        print('   2. Получить токен через 2FA процесс')
        print('   3. Выполнить logout с валидным токеном')
        print('   4. Проверить, что токен стал недействительным')


if __name__ == '__main__':
    asyncio.run(test_logout())
