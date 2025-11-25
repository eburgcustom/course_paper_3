import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests


class HeadHunterAPI:
    """
    Класс для работы с API HeadHunter.
    Предоставляет методы для получения данных о работодателях и вакансиях.
    """

    BASE_URL = "https://api.hh.ru/"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )

    def get_employer_info(self, employer_id: str) -> Optional[Dict[str, Any]]:
        """
        Получает информацию о работодателе по его ID.

        :param employer_id: ID работодателя на hh.ru
        :return: Словарь с информацией о работодателе или None в случае ошибки
        """
        url = f"{self.BASE_URL}employers/{employer_id}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as e:
            print(f"Ошибка при получении данных о работодателе {employer_id}: {e}")
            return None

    def get_employer_vacancies(self, employer_id: str, per_page: int = 100) -> List[Dict[str, Any]]:
        """
        Получает список вакансий работодателя.

        :param employer_id: ID работодателя
        :param per_page: Количество вакансий на странице (максимум 100)
        :return: Список словарей с информацией о вакансиях
        """
        url = f"{self.BASE_URL}vacancies"
        params = {
            "employer_id": employer_id,
            "per_page": min(per_page, 100),  # API ограничивает 100 вакансий на страницу
            "page": 0,
        }

        vacancies = []

        while True:
            try:
                response = self.session.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                if "items" not in data or not data["items"]:
                    break

                vacancies.extend(data["items"])

                # Проверяем, есть ли еще страницы
                pages = data.get("pages", 0)
                if params["page"] >= pages - 1 or len(vacancies) >= data.get("found", 0):
                    break

                params["page"] += 1

                # Добавляем задержку, чтобы не превысить лимиты API
                time.sleep(0.5)

            except (requests.RequestException, ValueError) as e:
                print(f"Ошибка при получении вакансий работодателя {employer_id}: {e}")
                break

        return vacancies

    def get_vacancy_details(self, vacancy_id: str) -> Optional[Dict[str, Any]]:
        """
        Получает полную информацию о вакансии по её ID.

        :param vacancy_id: ID вакансии
        :return: Словарь с полной информацией о вакансии или None в случае ошибки
        """
        url = f"{self.BASE_URL}vacancies/{vacancy_id}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as e:
            print(f"Ошибка при получении данных о вакансии {vacancy_id}: {e}")
            return None

    def search_employers(self, query: str, area: int = 1, per_page: int = 10) -> List[Dict[str, Any]]:
        """
        Ищет работодателей по названию.

        :param query: Поисковый запрос (название компании)
        :param area: ID региона (1 - Москва, 2 - Санкт-Петербург и т.д.)
        :param per_page: Количество результатов на странице
        :return: Список словарей с информацией о найденных работодателях
        """
        url = f"{self.BASE_URL}employers"
        params = {"text": query, "area": area, "per_page": per_page, "only_with_vacancies": True}

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("items", [])
        except (requests.RequestException, ValueError) as e:
            print(f"Ошибка при поиске работодателей: {e}")
            return []


def format_salary(salary_data: Optional[Dict[str, Any]]) -> Optional[Dict[str, int]]:
    """
    Форматирует данные о зарплате из API hh.ru в удобный для работы формат.

    :param salary_data: Словарь с данными о зарплате из API
    :return: Словарь с отформатированными данными о зарплате
    """
    if not salary_data:
        return None

    formatted = {
        "from": salary_data.get("from"),
        "to": salary_data.get("to"),
        "currency": salary_data.get("currency"),
        "gross": salary_data.get("gross"),
    }

    # Конвертируем валюту в рубли, если нужно
    if formatted["currency"] and formatted["currency"].lower() != "rur":
        # Здесь можно добавить логику конвертации валют
        # Пока просто оставляем как есть
        pass

    return formatted


def format_datetime(date_str: str) -> Optional[datetime]:
    """
    Преобразует строку с датой из формата API в объект datetime.

    :param date_str: Строка с датой в формате ISO 8601
    :return: Объект datetime или None в случае ошибки
    """
    if not date_str:
        return None

    try:
        # Пробуем разные форматы даты
        for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S.%f%z"):
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None
    except (TypeError, ValueError):
        return None
