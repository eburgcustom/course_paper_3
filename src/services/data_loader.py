import time
from typing import Any, Dict, List, Optional

from src.api import HeadHunterAPI
from src.database.db_manager import DBManager
from src.models.employer import Employer
from src.models.vacancy import Vacancy


class HHDataLoader:
    """
    Класс для загрузки данных о работодателях и вакансиях с hh.ru.
    """

    def __init__(self, db_manager: DBManager):
        """
        Инициализирует загрузчик данных.

        :param db_manager: Экземпляр DBManager для работы с базой данных
        """
        self.api = HeadHunterAPI()
        self.db = db_manager

    def load_employers(self, employer_ids: List[str]) -> None:
        """
        Загружает информацию о работодателях и их вакансиях.

        :param employer_ids: Список ID работодателей для загрузки
        """
        print(f"Начало загрузки данных для {len(employer_ids)} работодателей...")

        for employer_id in employer_ids:
            try:
                # Получаем данные о работодателе
                employer_data = self.api.get_employer_info(employer_id)
                if not employer_data:
                    print(f"Не удалось загрузить данные работодателя с ID {employer_id}")
                    continue

                # Создаем объект Employer
                employer = Employer.from_hh_dict(employer_data)

                # Сохраняем работодателя в БД
                if self.db.save_employer(employer):
                    print(f"Сохранен работодатель: {employer.name}")
                else:
                    print(f"Ошибка при сохранении работодателя {employer.name}")
                    continue

                # Загружаем вакансии работодателя
                self.load_vacancies(employer_id)

                # Делаем паузу, чтобы не перегружать API
                time.sleep(0.5)

            except Exception as e:
                print(f"Ошибка при загрузке данных работодателя {employer_id}: {e}")

    def load_vacancies(self, employer_id: str) -> None:
        """
        Загружает вакансии указанного работодателя.

        :param employer_id: ID работодателя
        """
        try:
            # Получаем вакансии с API
            vacancies_data = self.api.get_employer_vacancies(employer_id)
            if not vacancies_data:
                print(f"Не найдено вакансий для работодателя {employer_id}")
                return

            print(f"Найдено {len(vacancies_data)} вакансий для работодателя {employer_id}")

            # Обрабатываем каждую вакансию
            for vacancy_data in vacancies_data:
                try:
                    # Создаем объект Vacancy
                    vacancy = Vacancy.from_hh_dict(vacancy_data)

                    # Сохраняем вакансию в БД
                    if self.db.save_vacancy(vacancy):
                        print(f"  - Сохранена вакансия: {vacancy.name}")
                    else:
                        print(f"  - Ошибка при сохранении вакансии {vacancy.name}")

                except Exception as e:
                    print(f"Ошибка при обработке вакансии: {e}")
                    continue

                # Делаем небольшую задержку между запросами
                time.sleep(0.2)

        except Exception as e:
            print(f"Ошибка при загрузке вакансий работодателя {employer_id}: {e}")

    def search_employers(self, query: str, area: int = 1, per_page: int = 10) -> List[Dict[str, Any]]:
        """
        Ищет работодателей по названию.

        :param query: Поисковый запрос
        :param area: ID региона (1 - Москва, 2 - Санкт-Петербург и т.д.)
        :param per_page: Количество результатов на странице
        :return: Список найденных работодателей
        """
        try:
            employers = self.api.search_employers(query, area=area, per_page=per_page)

            # Форматируем результат для вывода
            result = []
            for emp in employers:
                result.append(
                    {
                        "id": emp["id"],
                        "name": emp["name"],
                        "url": emp.get("alternate_url", ""),
                        "open_vacancies": emp.get("open_vacancies", 0),
                        "trusted": emp.get("trusted", False),
                    }
                )

            return result

        except Exception as e:
            print(f"Ошибка при поиске работодателей: {e}")
            return []


def load_example_data() -> None:
    """
    Загружает тестовые данные в базу данных.
    """
    # ID популярных IT-компаний на hh.ru
    example_employers = [
        "1740",  # Яндекс
        "3529",  # Сбер
        "78638",  # Тинькофф
        "3776",  # МТС
        "2180",  # Озон
        "87021",  # ВКонтакте
        "15478",  # Райффайзен Банк
        "1122462",  # СберТех
        "1057",  # Альфа-Банк
        "1373",  # МегаФон
    ]

    # Инициализируем менеджер БД и загрузчик
    db_manager = DBManager()
    loader = HHDataLoader(db_manager)

    # Загружаем данные
    loader.load_employers(example_employers)

    print("\nЗагрузка данных завершена!")


if __name__ == "__main__":
    load_example_data()
