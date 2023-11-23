from abc import ABC, abstractmethod
import requests


class GetAPI(ABC):
    """Абстрактный класс для работы с API"""

    @abstractmethod
    def get_data(self):
        """Метод получения данных по API"""
        pass


class CodeforcesAPI(GetAPI):
    """Класс для работы с API codeforces"""

    def __init__(self, api_codeforces) -> None:
        self.url = api_codeforces

    def get_data(self) -> list[dict]:
        """Метод получения данных по API"""

        response = requests.get(self.url, timeout=10)
        if response.ok:
            return response.json()['result']
        else:
            return 'Ошибка при получении данных'
