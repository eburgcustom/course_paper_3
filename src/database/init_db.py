import sys
from pathlib import Path

# Добавляем корневую директорию проекта в PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.database import create_database, execute_query


def create_tables() -> None:
    """
    Создает таблицы в базе данных, если они не существуют.
    """
    # SQL-запросы для создания таблиц
    create_employers_table = """
    CREATE TABLE IF NOT EXISTS employers (
        id VARCHAR(20) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        url VARCHAR(255),
        site_url TEXT,
        description TEXT,
        logo_url TEXT,
        open_vacancies INTEGER DEFAULT 0,
        trusted BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )
    """

    create_vacancies_table = """
    CREATE TABLE IF NOT EXISTS vacancies (
        id VARCHAR(20) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        url VARCHAR(255) NOT NULL,
        employer_id VARCHAR(20) REFERENCES employers(id) ON DELETE CASCADE,
        salary_from NUMERIC(12, 2),
        salary_to NUMERIC(12, 2),
        salary_currency VARCHAR(10),
        salary_gross BOOLEAN DEFAULT FALSE,
        description TEXT,
        requirements TEXT,
        responsibility TEXT,
        experience JSONB,
        employment JSONB,
        schedule JSONB,
        key_skills JSONB,
        published_at TIMESTAMP WITH TIME ZONE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )
    """

    # Создаем таблицы
    try:
        print("Создаем таблицы в базе данных...")

        # Создаем таблицу работодателей
        execute_query(create_employers_table)
        print("Таблица 'employers' успешно создана")

        # Создаем таблицу вакансий
        execute_query(create_vacancies_table)
        print("Таблица 'vacancies' успешно создана")

        print("Инициализация базы данных завершена успешно!")

    except Exception as e:
        print(f"Ошибка при создании таблиц: {e}")
        raise


def init_database() -> None:
    """
    Инициализирует базу данных: создает БД и таблицы.
    """
    try:
        print("Начало инициализации базы данных...")

        # Создаем базу данных, если она не существует
        create_database()

        # Создаем таблицы
        create_tables()

    except Exception as e:
        print(f"Ошибка при инициализации базы данных: {e}")
        sys.exit(1)


if __name__ == "__main__":
    init_database()
