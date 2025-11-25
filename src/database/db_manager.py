from typing import List, Dict, Any, Optional
import json

from src.database import DatabaseConnection, execute_query
from src.models.employer import Employer
from src.models.vacancy import Vacancy, Salary


class DBManager:
    """
    Класс для работы с данными в базе данных PostgreSQL.
    Предоставляет методы для работы с работодателями и вакансиями.
    """

    # ===== Методы для работы с работодателями =====

    @staticmethod
    def get_companies_and_vacancies_count() -> List[Dict[str, Any]]:
        """
        Получает список всех компаний и количество вакансий у каждой компании.

        :return: Список словарей с информацией о компаниях и количестве вакансий
        """
        query = """
        SELECT 
            e.id, 
            e.name, 
            COUNT(v.id) as vacancies_count
        FROM employers e
        LEFT JOIN vacancies v ON e.id = v.employer_id
        GROUP BY e.id, e.name
        ORDER BY vacancies_count DESC
        """

        with DatabaseConnection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]

    @staticmethod
    def get_employer(employer_id: str) -> Optional[Employer]:
        """
        Получает информацию о работодателе по его ID.

        :param employer_id: ID работодателя
        :return: Объект Employer или None, если работодатель не найден
        """
        query = """
        SELECT * FROM employers 
        WHERE id = %s
        """

        result = execute_query(query, (employer_id,), fetch=True)
        if not result:
            return None

        return Employer.from_dict(dict(result))

    @staticmethod
    def save_employer(employer: Employer) -> bool:
        """
        Сохраняет или обновляет информацию о работодателе в базе данных.

        :param employer: Объект работодателя
        :return: True, если операция выполнена успешно, иначе False
        """
        query = """
        INSERT INTO employers (
            id, name, url, site_url, description, 
            logo_url, open_vacancies, trusted, created_at
        ) VALUES (
            %(id)s, %(name)s, %(url)s, %(site_url)s, %(description)s, 
            %(logo_url)s, %(open_vacancies)s, %(trusted)s, %(created_at)s
        )
        ON CONFLICT (id) DO UPDATE SET
            name = EXCLUDED.name,
            url = EXCLUDED.url,
            site_url = EXCLUDED.site_url,
            description = EXCLUDED.description,
            logo_url = EXCLUDED.logo_url,
            open_vacancies = EXCLUDED.open_vacancies,
            trusted = EXCLUDED.trusted
        """

        employer_dict = employer.to_dict()
        try:
            execute_query(query, employer_dict)
            return True
        except Exception as e:
            print(f"Ошибка при сохранении работодателя {employer.id}: {e}")
            return False

    # ===== Методы для работы с вакансиями =====

    @staticmethod
    def get_all_vacancies() -> List[Dict[str, Any]]:
        """
        Получает список всех вакансий с указанием названия компании,
        названия вакансии, зарплаты и ссылки на вакансию.

        :return: Список словарей с информацией о вакансиях
        """
        query = """
        SELECT 
            v.id,
            v.name as vacancy_name,
            e.name as company_name,
            v.salary_from,
            v.salary_to,
            v.salary_currency,
            v.salary_gross,
            v.url
        FROM vacancies v
        JOIN employers e ON v.employer_id = e.id
        ORDER BY 
            COALESCE(v.salary_to, v.salary_from, 0) DESC,
            v.published_at DESC
        """

        with DatabaseConnection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]

    @staticmethod
    def get_vacancies_by_employer(employer_id: str) -> List[Vacancy]:
        """
        Получает все вакансии указанного работодателя.

        :param employer_id: ID работодателя
        :return: Список объектов Vacancy
        """
        query = """
        SELECT * FROM vacancies 
        WHERE employer_id = %s
        ORDER BY published_at DESC
        """

        with DatabaseConnection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (employer_id,))
                columns = [desc[0] for desc in cur.description]
                return [
                    Vacancy.from_dict(dict(zip(columns, row)))
                    for row in cur.fetchall()
                ]

    @staticmethod
    def save_vacancy(vacancy: Vacancy) -> bool:
        """
        Сохраняет или обновляет информацию о вакансии в базе данных.

        :param vacancy: Объект вакансии
        :return: True, если операция выполнена успешно, иначе False
        """
        query = """
        INSERT INTO vacancies (
            id, name, url, employer_id, salary_from, salary_to,
            salary_currency, salary_gross, description, requirements,
            responsibility, experience, employment, schedule,
            key_skills, published_at, created_at
        ) VALUES (
            %(id)s, %(name)s, %(url)s, %(employer_id)s, %(salary_from)s, 
            %(salary_to)s, %(salary_currency)s, %(salary_gross)s, %(description)s, 
            %(requirements)s, %(responsibility)s, %(experience)s, %(employment)s, 
            %(schedule)s, %(key_skills)s, %(published_at)s, %(created_at)s
        )
        ON CONFLICT (id) DO UPDATE SET
            name = EXCLUDED.name,
            url = EXCLUDED.url,
            salary_from = EXCLUDED.salary_from,
            salary_to = EXCLUDED.salary_to,
            salary_currency = EXCLUDED.salary_currency,
            salary_gross = EXCLUDED.salary_gross,
            description = EXCLUDED.description,
            requirements = EXCLUDED.requirements,
            responsibility = EXCLUDED.responsibility,
            experience = EXCLUDED.experience,
            employment = EXCLUDED.employment,
            schedule = EXCLUDED.schedule,
            key_skills = EXCLUDED.key_skills,
            published_at = EXCLUDED.published_at
        """

        # Подготавливаем данные для вставки
        vacancy_dict = vacancy.to_dict()
        salary = vacancy_dict.pop('salary', {})

        # Добавляем поля зарплаты в основной словарь
        vacancy_dict.update({
            'salary_from': salary.get('from'),
            'salary_to': salary.get('to'),
            'salary_currency': salary.get('currency'),
            'salary_gross': salary.get('gross', False)
        })

        # Сериализуем JSON-поля
        for field in ['experience', 'employment', 'schedule', 'key_skills']:
            if field in vacancy_dict and vacancy_dict[field] is not None:
                vacancy_dict[field] = json.dumps(vacancy_dict[field])

        try:
            execute_query(query, vacancy_dict)
            return True
        except Exception as e:
            print(f"Ошибка при сохранении вакансии {vacancy.id}: {e}")
            return False

    # ===== Аналитические методы =====

    @staticmethod
    def get_avg_salary() -> Dict[str, float]:
        """
        Получает среднюю зарплату по всем вакансиям.

        :return: Словарь с информацией о средней зарплате
        """
        query = """
        WITH salary_data AS (
            SELECT 
                COALESCE(salary_from, 0) as salary_from,
                COALESCE(salary_to, 0) as salary_to,
                salary_currency
            FROM vacancies
            WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
        )
        SELECT 
            AVG((salary_from + salary_to) / 2) as avg_salary,
            salary_currency
        FROM salary_data
        GROUP BY salary_currency
        """

        with DatabaseConnection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                result = cur.fetchall()

                if not result:
                    return {"avg_salary": 0, "currency": None}

                # Возвращаем первую валюту (можно доработать для поддержки нескольких валют)
                return {
                    "avg_salary": float(result[0][0]),
                    "currency": result[0][1] or 'RUR'
                }

    @staticmethod
    def get_vacancies_with_higher_salary() -> List[Dict[str, Any]]:
        """
        Получает список всех вакансий, у которых зарплата выше средней.

        :return: Список словарей с информацией о вакансиях
        """
        query = """
        WITH avg_salary AS (
            SELECT AVG((COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2) as avg
            FROM vacancies
            WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
        )
        SELECT 
            v.id,
            v.name as vacancy_name,
            e.name as company_name,
            v.salary_from,
            v.salary_to,
            v.salary_currency,
            v.salary_gross,
            v.url
        FROM vacancies v
        JOIN employers e ON v.employer_id = e.id
        CROSS JOIN avg_salary
        WHERE (COALESCE(v.salary_from, 0) + COALESCE(v.salary_to, 0)) / 2 > avg_salary.avg
        ORDER BY (COALESCE(v.salary_to, v.salary_from, 0)) DESC
        """

        with DatabaseConnection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]

    @staticmethod
    def get_vacancies_with_keyword(keyword: str) -> List[Dict[str, Any]]:
        """
        Ищет вакансии по ключевому слову в названии.

        :param keyword: Ключевое слово для поиска
        :return: Список словарей с информацией о найденных вакансиях
        """
        query = """
        SELECT 
            v.id,
            v.name as vacancy_name,
            e.name as company_name,
            v.salary_from,
            v.salary_to,
            v.salary_currency,
            v.salary_gross,
            v.url
        FROM vacancies v
        JOIN employers e ON v.employer_id = e.id
        WHERE LOWER(v.name) LIKE %s
        ORDER BY v.published_at DESC
        """

        with DatabaseConnection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (f'%{keyword.lower()}%',))
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]
