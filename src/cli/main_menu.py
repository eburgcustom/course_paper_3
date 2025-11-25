import sys

from src.database.db_manager import DBManager
from src.services.data_loader import HHDataLoader


class MainMenu:
    """
    Главное меню приложения для взаимодействия с пользователем.
    """

    def __init__(self):
        """Инициализирует меню и создает экземпляры необходимых классов."""
        self.db_manager = DBManager()
        self.data_loader = HHDataLoader(self.db_manager)

    def run(self):
        """Запускает главное меню."""
        while True:
            self._clear_screen()
            print("\n=== Парсер вакансий с HeadHunter ===")
            print("1. Загрузить данные о компаниях и вакансиях")
            print("2. Просмотреть список всех компаний")
            print("3. Просмотреть все вакансии")
            print("4. Получить среднюю зарплату по вакансиям")
            print("5. Получить вакансии с зарплатой выше средней")
            print("6. Поиск вакансий по ключевому слову")
            print("0. Выход")

            choice = input("\nВыберите действие: ").strip()

            if choice == "1":
                self._load_data_menu()
            elif choice == "2":
                self._show_companies()
            elif choice == "3":
                self._show_all_vacancies()
            elif choice == "4":
                self._show_avg_salary()
            elif choice == "5":
                self._show_high_salary_vacancies()
            elif choice == "6":
                self._search_vacancies()
            elif choice == "0":
                print("\nДо свидания!")
                sys.exit(0)
            else:
                print("\nНеверный ввод. Пожалуйста, выберите действие из списка.")
                input("\nНажмите Enter для продолжения...")

    def _load_data_menu(self):
        """Меню загрузки данных."""
        while True:
            self._clear_screen()
            print("\n=== Загрузка данных ===")
            print("1. Загрузить тестовые данные (популярные IT-компании)")
            print("2. Загрузить данные по ID работодателя")
            print("3. Найти работодателя по названию")
            print("0. Назад в главное меню")

            choice = input("\nВыберите действие: ").strip()

            if choice == "1":
                self._load_example_data()
                break
            elif choice == "2":
                self._load_by_employer_id()
                break
            elif choice == "3":
                self._search_and_load_employer()
            elif choice == "0":
                return
            else:
                print("\nНеверный ввод. Пожалуйста, выберите действие из списка.")
                input("\nНажмите Enter для продолжения...")

    def _load_example_data(self):
        """Загружает тестовые данные."""
        print("\nЗагрузка тестовых данных...")
        example_employers = [
            '1740',  # Яндекс
            '3529',  # Сбер
            '78638',  # Тинькофф
            '3776',  # МТС
            '2180',  # Озон
        ]
        self.data_loader.load_employers(example_employers)
        input("\nНажмите Enter для продолжения...")

    def _load_by_employer_id(self):
        """Загружает данные по ID работодателя."""
        employer_id = input("\nВведите ID работодателя: ").strip()
        if not employer_id:
            print("ID работодателя не может быть пустым.")
            input("\nНажмите Enter для продолжения...")
            return

        print(f"\nЗагрузка данных для работодателя с ID {employer_id}...")
        self.data_loader.load_employers([employer_id])
        input("\nНажмите Enter для продолжения...")

    def _search_and_load_employer(self):
        """Ищет работодателя по названию и загружает его данные."""
        query = input("\nВведите название компании для поиска: ").strip()
        if not query:
            print("Название компании не может быть пустым.")
            input("\nНажмите Enter для продолжения...")
            return

        print(f"\nПоиск работодателей по запросу: {query}")
        employers = self.data_loader.search_employers(query, per_page=5)

        if not employers:
            print("Работодатели не найдены.")
            input("\nНажмите Enter для продолжения...")
            return

        print("\nНайденные работодатели:")
        for i, emp in enumerate(employers, 1):
            print(f"{i}. {emp['name']} (ID: {emp['id']}, вакансий: {emp['open_vacancies']})")

        while True:
            choice = input("\nВыберите номер работодателя для загрузки (или 0 для отмены): ").strip()
            if choice == "0":
                return
            try:
                index = int(choice) - 1
                if 0 <= index < len(employers):
                    employer_id = employers[index]['id']
                    print(f"\nЗагрузка данных для {employers[index]['name']}...")
                    self.data_loader.load_employers([employer_id])
                    break
                else:
                    print("Неверный номер. Пожалуйста, выберите номер из списка.")
            except ValueError:
                print("Пожалуйста, введите число.")

        input("\nНажмите Enter для продолжения...")

    def _show_companies(self):
        """Показывает список всех компаний и количество вакансий."""
        print("\n=== Список компаний ===")
        companies = self.db_manager.get_companies_and_vacancies_count()

        if not companies:
            print("Нет данных о компаниях.")
            input("\nНажмите Enter для продолжения...")
            return

        for i, company in enumerate(companies, 1):
            print(f"{i}. {company['name']} - {company['vacancies_count']} вакансий")

        input("\nНажмите Enter для продолжения...")

    def _show_all_vacancies(self):
        """Показывает все вакансии с информацией о зарплате."""
        print("\n=== Все вакансии ===")
        vacancies = self.db_manager.get_all_vacancies()

        if not vacancies:
            print("Нет данных о вакансиях.")
            input("\nНажмите Enter для продолжения...")
            return

        for i, vacancy in enumerate(vacancies, 1):
            salary_from = f"от {vacancy['salary_from']} {vacancy['salary_currency']}" if vacancy['salary_from'] else ""
            salary_to = f"до {vacancy['salary_to']} {vacancy['salary_currency']}" if vacancy['salary_to'] else ""
            salary = " ".join(filter(None, [salary_from, salary_to]))
            salary = salary or "з/п не указана"

            print(f"\n{i}. {vacancy['vacancy_name']}")
            print(f"   Компания: {vacancy['company_name']}")
            print(f"   Зарплата: {salary}")
            print(f"   Ссылка: {vacancy['url']}")

        input("\nНажмите Enter для продолжения...")

    def _show_avg_salary(self):
        """Показывает среднюю зарплату по вакансиям."""
        print("\n=== Средняя зарплата по вакансиям ===")
        result = self.db_manager.get_avg_salary()

        if not result or result['avg_salary'] == 0:
            print("Недостаточно данных для расчета средней зарплаты.")
        else:
            print(f"Средняя зарплата: {result['avg_salary']:.2f} {result['currency'] or 'RUR'}")

        input("\nНажмите Enter для продолжения...")

    def _show_high_salary_vacancies(self):
        """Показывает вакансии с зарплатой выше средней."""
        print("\n=== Вакансии с зарплатой выше средней ===")
        vacancies = self.db_manager.get_vacancies_with_higher_salary()

        if not vacancies:
            print("Нет вакансий с зарплатой выше средней.")
            input("\nНажмите Enter для продолжения...")
            return

        for i, vacancy in enumerate(vacancies, 1):
            salary_from = f"от {vacancy['salary_from']} {vacancy['salary_currency']}" if vacancy['salary_from'] else ""
            salary_to = f"до {vacancy['salary_to']} {vacancy['salary_currency']}" if vacancy['salary_to'] else ""
            salary = " ".join(filter(None, [salary_from, salary_to]))

            print(f"\n{i}. {vacancy['vacancy_name']}")
            print(f"   Компания: {vacancy['company_name']}")
            print(f"   Зарплата: {salary}")
            print(f"   Ссылка: {vacancy['url']}")

        input("\nНажмите Enter для продолжения...")

    def _search_vacancies(self):
        """Ищет вакансии по ключевому слову."""
        keyword = input("\nВведите ключевое слово для поиска: ").strip()
        if not keyword:
            print("Ключевое слово не может быть пустым.")
            input("\nНажмите Enter для продолжения...")
            return

        print(f"\n=== Результаты поиска по запросу: {keyword} ===")
        vacancies = self.db_manager.get_vacancies_with_keyword(keyword)

        if not vacancies:
            print("По вашему запросу ничего не найдено.")
            input("\nНажмите Enter для продолжения...")
            return

        for i, vacancy in enumerate(vacancies, 1):
            salary_from = f"от {vacancy['salary_from']} {vacancy['salary_currency']}" if vacancy['salary_from'] else ""
            salary_to = f"до {vacancy['salary_to']} {vacancy['salary_currency']}" if vacancy['salary_to'] else ""
            salary = " ".join(filter(None, [salary_from, salary_to]))
            salary = salary or "з/п не указана"

            print(f"\n{i}. {vacancy['vacancy_name']}")
            print(f"   Компания: {vacancy['company_name']}")
            print(f"   Зарплата: {salary}")
            print(f"   Ссылка: {vacancy['url']}")

        input("\nНажмите Enter для продолжения...")

    @staticmethod
    def _clear_screen():
        """Очищает экран консоли."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')


def main():
    """Точка входа в приложение."""
    try:
        menu = MainMenu()
        menu.run()
    except KeyboardInterrupt:
        print("\n\nРабота программы завершена пользователем.")
    except Exception as e:
        print(f"\nПроизошла ошибка: {e}")
        input("\nНажмите Enter для выхода...")


if __name__ == "__main__":
    main()
