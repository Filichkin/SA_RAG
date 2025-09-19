#!/usr/bin/env python3
"""
Скрипт для запуска тестов
"""
import subprocess
import sys
import os


def run_tests():
    """Запуск тестов"""
    # Устанавливаем переменные окружения для тестов
    os.environ['TESTING'] = 'true'
    
    # Команды для запуска тестов
    commands = [
        # Запуск всех тестов
        ['python', '-m', 'pytest', 'tests/', '-v'],
        
        # Запуск только unit тестов
        # ['python', '-m', 'pytest', 'tests/test_user_validation.py', '-v'],
        
        # Запуск только API тестов
        # ['python', '-m', 'pytest', 'tests/test_user_endpoints.py', '-v'],
        
        # Запуск только интеграционных тестов
        # ['python', '-m', 'pytest', 'tests/test_user_integration.py', '-v'],
    ]
    
    for cmd in commands:
        print(f"Запуск команды: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, check=True)
            print(f"Команда выполнена успешно с кодом: {result.returncode}")
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при выполнении команды: {e}")
            sys.exit(1)
        except FileNotFoundError:
            print("pytest не найден. Установите зависимости:")
            print("pip install -r requirements.txt")
            sys.exit(1)


if __name__ == "__main__":
    run_tests()
