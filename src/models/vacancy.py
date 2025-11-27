from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class Salary:
    """
    Класс для представления данных о зарплате.

    Attributes:
        from_amount (Optional[float]): Нижняя граница вилки оклада
        to (Optional[float]): Верхняя граница вилки оклада
        currency (str): Валюта (код)
        gross (bool): Указана ли зарплата до вычета налогов
    """

    from_amount: Optional[float] = None
    to: Optional[float] = None
    currency: Optional[str] = None
    gross: bool = False

    @property
    def is_net(self) -> bool:
        """Возвращает True, если зарплата указана на руки (после вычета налогов)."""
        return not self.gross

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует объект в словарь для сохранения в БД."""
        return {"from": self.from_amount, "to": self.to, "currency": self.currency, "gross": self.gross}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Salary":
        """Создает экземпляр класса из словаря."""
        return cls(
            from_amount=data.get("from"),
            to=data.get("to"),
            currency=data.get("currency"),
            gross=data.get("gross", False),
        )

    def __str__(self) -> str:
        if not self.currency:
            return "Зарплата не указана"

        parts = []
        if self.from_amount is not None:
            parts.append(f"от {self.from_amount}")
        if self.to is not None:
            parts.append(f"до {self.to}")

        if not parts:
            return "Зарплата не указана"

        currency_symbol = {"RUR": "₽", "USD": "$", "EUR": "€", "KZT": "₸"}.get(self.currency.upper(), self.upper())

        salary_str = " ".join(parts)
        gross_str = "до вычета налогов" if self.gross else "на руки"

        return f"{salary_str} {currency_symbol} {gross_str}"


@dataclass
class Vacancy:
    """
    Класс для представления данных о вакансии.

    Attributes:
        id (str): Уникальный идентификатор вакансии
        name (str): Название вакансии
        url (str): Ссылка на вакансию
        employer_id (str): ID работодателя
        salary (Optional[Salary]): Информация о зарплате
        description (Optional[str]): Описание вакансии
        requirements (Optional[str]): Требования к кандидату
        responsibility (Optional[str]): Обязанности
        experience (Optional[Dict[str, Any]]): Опыт работы
        employment (Optional[Dict[str, Any]]): Тип занятости
        schedule (Optional[Dict[str, Any]]): График работы
        key_skills (List[Dict[str, str]]): Ключевые навыки
        published_at (datetime): Дата публикации вакансии
        created_at (datetime): Дата и время создания записи
    """

    id: str
    name: str
    url: str
    employer_id: str
    salary: Optional[Salary] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    responsibility: Optional[str] = None
    experience: Optional[Dict[str, Any]] = None
    employment: Optional[Dict[str, Any]] = None
    schedule: Optional[Dict[str, Any]] = None
    key_skills: List[Dict[str, str]] = field(default_factory=list)
    published_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def from_hh_dict(cls, data: Dict[str, Any]) -> "Vacancy":
        """
        Создает экземпляр класса из словаря, полученного от API hh.ru.

        :param data: Словарь с данными о вакансии из API
        :return: Экземпляр класса Vacancy
        """
        salary_data = data.get("salary")
        salary = Salary.from_dict(salary_data) if salary_data else None

        return cls(
            id=str(data["id"]),
            name=data["name"],
            url=data["alternate_url"],
            employer_id=str(data["employer"]["id"]),
            salary=salary,
            description=data.get("description"),
            requirements=data.get("snippet", {}).get("requirement"),
            responsibility=data.get("snippet", {}).get("responsibility"),
            experience=data.get("experience"),
            employment=data.get("employment"),
            schedule=data.get("schedule"),
            key_skills=data.get("key_skills", []),
            published_at=cls._parse_datetime(data.get("published_at")),
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразует объект в словарь для сохранения в БД.

        :return: Словарь с данными вакансии
        """
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "employer_id": self.employer_id,
            "salary": self.salary.to_dict() if self.salary else None,
            "description": self.description,
            "requirements": self.requirements,
            "responsibility": self.responsibility,
            "experience": self.experience,
            "employment": self.employment,
            "schedule": self.schedule,
            "key_skills": self.key_skills,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Vacancy":
        """
        Создает экземпляр класса из словаря, полученного из БД.

        :param data: Словарь с данными о вакансии из БД
        :return: Экземпляр класса Vacancy
        """
        salary_data = data.get("salary")
        salary = Salary.from_dict(salary_data) if salary_data else None

        return cls(
            id=str(data["id"]),
            name=data["name"],
            url=data["url"],
            employer_id=str(data["employer_id"]),
            salary=salary,
            description=data.get("description"),
            requirements=data.get("requirements"),
            responsibility=data.get("responsibility"),
            experience=data.get("experience"),
            employment=data.get("employment"),
            schedule=data.get("schedule"),
            key_skills=data.get("key_skills", []),
            published_at=cls._parse_datetime(data.get("published_at")),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.utcnow(),
        )

    @staticmethod
    def _parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
        """Парсит строку с датой в объект datetime."""
        if not dt_str:
            return None

        try:
            # Пробуем разные форматы даты
            for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S.%f%z"):
                try:
                    return datetime.strptime(dt_str, fmt)
                except ValueError:
                    continue
            return None
        except (TypeError, ValueError):
            return None

    def __str__(self) -> str:
        salary_str = str(self.salary) if self.salary else "Зарплата не указана"
        return f"{self.name} ({salary_str})"
