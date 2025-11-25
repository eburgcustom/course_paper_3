from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class Employer:
    """
    Класс для представления данных о работодателе.
    
    Attributes:
        id (str): Уникальный идентификатор работодателя
        name (str): Название компании
        url (str): Ссылка на страницу компании на hh.ru
        site_url (Optional[str]): Ссылка на сайт компании
        description (Optional[str]): Описание компании
        logo_url (Optional[str]): Ссылка на логотип компании
        industries (List[Dict[str, str]]): Список отраслей компании
        open_vacancies (int): Количество открытых вакансий
        trusted (bool): Является ли компания доверенной
        created_at (datetime): Дата и время создания записи
    """
    id: str
    name: str
    url: str
    site_url: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    industries: list[dict[str, str]] = field(default_factory=list)
    open_vacancies: int = 0
    trusted: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    @classmethod
    def from_hh_dict(cls, data: Dict[str, Any]) -> 'Employer':
        """
        Создает экземпляр класса из словаря, полученного от API hh.ru.
        
        :param data: Словарь с данными о работодателе из API
        :return: Экземпляр класса Employer
        """
        logo = data.get('logo_urls', {}) or {}
        
        return cls(
            id=str(data['id']),
            name=data['name'],
            url=data['alternate_url'],
            site_url=data.get('site_url'),
            description=data.get('description'),
            logo_url=logo.get('original'),
            industries=data.get('industries', []),
            open_vacancies=data.get('open_vacancies', 0),
            trusted=data.get('trusted', False)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразует объект в словарь для сохранения в БД.
        
        :return: Словарь с данными работодателя
        """
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'site_url': self.site_url,
            'description': self.description,
            'logo_url': self.logo_url,
            'industries': self.industries,
            'open_vacancies': self.open_vacancies,
            'trusted': self.trusted,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Employer':
        """
        Создает экземпляр класса из словаря, полученного из БД.
        
        :param data: Словарь с данными о работодателе из БД
        :return: Экземпляр класса Employer
        """
        from datetime import datetime
        
        created_at = datetime.fromisoformat(data['created_at']) if 'created_at' in data else datetime.utcnow()
        
        return cls(
            id=str(data['id']),
            name=data['name'],
            url=data['url'],
            site_url=data.get('site_url'),
            description=data.get('description'),
            logo_url=data.get('logo_url'),
            industries=data.get('industries', []),
            open_vacancies=data.get('open_vacancies', 0),
            trusted=data.get('trusted', False),
            created_at=created_at
        )