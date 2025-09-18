import sys
from pathlib import Path

from loguru import logger


class LoggingConfig:
    '''Конфигурация логирования с использованием loguru'''

    def __init__(self):
        self.logs_dir = Path(__file__).parent / 'logs'
        self.logs_dir.mkdir(exist_ok=True)

        # Удаляем стандартный обработчик loguru
        logger.remove()

        # Настройка формата логов
        self.log_format = (
            '<green>{time:YYYY-MM-DD HH:mm:ss}</green> | '
            '<level>{level: <8}</level> | '
            '<cyan>{name}</cyan>:<cyan>{function}</cyan>:'
            '<cyan>{line}</cyan> | <level>{message}</level>'
        )

        # Настройка консольного вывода
        self._setup_console_logging()

    def _setup_console_logging(self):
        '''Настройка вывода логов в консоль'''
        logger.add(
            sys.stdout,
            format=self.log_format,
            level='INFO',
            colorize=True,
            backtrace=True,
            diagnose=True
        )

    def add_endpoint_logger(self, endpoint_name: str, level: str = 'INFO'):
        '''
        Добавляет отдельный логгер для конкретного эндпоинта

        Args:
            endpoint_name: Название эндпоинта (например, 'user')
            level: Уровень логирования
        '''
        endpoint_log_file = self.logs_dir / f'{endpoint_name}.log'

        logger.add(
            endpoint_log_file,
            format=self.log_format,
            level=level,
            rotation='10 MB',
            retention='30 days',
            compression='zip',
            backtrace=True,
            diagnose=True,
            filter=lambda record: (
                record['extra'].get('endpoint') == endpoint_name
            )
        )

    def get_endpoint_logger(self, endpoint_name: str):
        '''
        Возвращает логгер для конкретного эндпоинта

        Args:
            endpoint_name: Название эндпоинта

        Returns:
            Логгер с контекстом эндпоинта
        '''
        return logger.bind(endpoint=endpoint_name)


# Создаем глобальный экземпляр конфигурации
logging_config = LoggingConfig()

# Добавляем логгеры для эндпоинтов
logging_config.add_endpoint_logger('user', 'INFO')

# Экспортируем основной логгер
__all__ = ['logger', 'logging_config']
