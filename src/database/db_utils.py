import configparser
from pathlib import Path
from typing import Any, Dict, Optional

import psycopg2
from psycopg2.extras import DictCursor


def get_db_config(config_path: str = "config/database.ini", section: str = "postgresql") -> Dict[str, str]:
    """
    Получает параметры подключения к базе данных из конфигурационного файла.

    :param config_path: Путь к файлу конфигурации
    :param section: Секция в конфигурационном файле
    :return: Словарь с параметрами подключения
    """
    # Создаем парсер конфигурации
    parser = configparser.ConfigParser()

    # Получаем абсолютный путь к файлу конфигурации
    config_file = Path(__file__).parent.parent.parent / config_path

    # Читаем конфигурационный файл
    parser.read(config_file)

    # Получаем секцию с настройками
    db_config = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db_config[param[0]] = param[1]
    else:
        raise Exception(f"Секция {section} не найдена в файле {config_path}")

    return db_config


class DatabaseConnection:
    """
    Класс для управления подключением к базе данных PostgreSQL.

    Использование:
        with DatabaseConnection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM employers")
                result = cur.fetchall()
    """

    def __init__(self, config_path: str = "config/database.ini"):
        """
        Инициализирует подключение к базе данных.

        :param config_path: Путь к файлу конфигурации
        """
        self.config_path = config_path
        self.conn = None

    def __enter__(self):
        """Открывает соединение с базой данных при входе в контекстный менеджер."""
        try:
            # Получаем параметры подключения
            params = get_db_config(self.config_path)

            # Устанавливаем соединение с базой данных
            self.conn = psycopg2.connect(**params, cursor_factory=DictCursor)
            self.conn.autocommit = False
            return self.conn

        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Ошибка при подключении к PostgreSQL: {error}")
            if self.conn is not None:
                self.conn.rollback()
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Закрывает соединение с базой данных при выходе из контекстного менеджера."""
        if self.conn is not None:
            if exc_type is not None:
                # Если произошло исключение, откатываем транзакцию
                self.conn.rollback()
            else:
                # Иначе фиксируем изменения
                self.conn.commit()
            self.conn.close()


def create_database() -> None:
    """
    Создает базу данных, если она не существует.

    :raises psycopg2.DatabaseError: Если произошла ошибка при создании базы данных
    """
    try:
        # Подключаемся к серверу PostgreSQL (к базе данных postgres по умолчанию)
        params = get_db_config()
        db_name = params.pop("database")  # Удаляем имя базы данных из параметров

        conn = psycopg2.connect(**params)
        conn.autocommit = True

        with conn.cursor() as cur:
            # Проверяем существование базы данных
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            exists = cur.fetchone()

            if not exists:
                # Создаем базу данных
                cur.execute(f"CREATE DATABASE {db_name}")
                print(f"База данных {db_name} успешно создана")
            else:
                print(f"База данных {db_name} уже существует")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Ошибка при создании базы данных: {error}")
        raise
    finally:
        if conn is not None:
            conn.close()


def execute_query(query: str, params: tuple = None, fetch: bool = False, many: bool = False):
    """
    Выполняет SQL-запрос к базе данных.

    :param query: SQL-запрос
    :param params: Параметры запроса
    :param fetch: Если True, возвращает результат запроса
    :param many: Если True, возвращает все строки, иначе только первую
    :return: Результат запроса или None
    """
    result = None
    with DatabaseConnection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(query, params or ())
                if fetch:
                    result = cur.fetchall() if many else cur.fetchone()
                return result
            except Exception as e:
                print(f"Ошибка при выполнении запроса: {e}")
                raise
