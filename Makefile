# Makefile для проекта SA_RAG

.PHONY: help install test test-unit test-api test-integration test-coverage clean lint format

help: ## Показать справку
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Установить зависимости
	pip install -r requirements.txt

test: ## Запустить все тесты
	python -m pytest tests/ -v

test-unit: ## Запустить unit тесты
	python -m pytest tests/test_user_validation.py -v

test-api: ## Запустить API тесты
	python -m pytest tests/test_user_endpoints.py -v

test-integration: ## Запустить интеграционные тесты
	python -m pytest tests/test_user_integration.py -v

test-coverage: ## Запустить тесты с покрытием кода
	python -m pytest tests/ --cov=app --cov-report=html --cov-report=term-missing

test-fast: ## Запустить быстрые тесты (исключить медленные)
	python -m pytest tests/ -v -m "not slow"

test-auth: ## Запустить тесты аутентификации
	python -m pytest tests/ -v -m "auth"

test-admin: ## Запустить тесты администратора
	python -m pytest tests/ -v -m "admin"

clean: ## Очистить временные файлы
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -f test.db

lint: ## Проверить код линтером
	flake8 app/ tests/
	pylint app/ tests/

format: ## Форматировать код
	black app/ tests/
	isort app/ tests/

dev-install: ## Установить зависимости для разработки
	pip install -r requirements.txt
	pip install flake8 pylint black isort pytest-cov

run: ## Запустить приложение
	uvicorn app.main:app --reload

run-tests: ## Запустить тесты через скрипт
	python run_tests.py
