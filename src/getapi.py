from abc import ABC, abstractmethod
import requests

class GetAPI(ABC):
    """Абстрактный класс для работы с API"""

    @abstractmethod
    def get_data(self):
        pass


class CodeforcesAPI(GetAPI):
    """Класс для работы с API codeforces"""

    def __init__(self):
        self.url = f'https://codeforces.com/api/problemset.problems?order=BY_SOLVED_DESC'


    def get_data(self):
        """Метод получения данных по API"""

        response = requests.get(self.url)
        if response.status_code == 200:
            return response.json()['result']
        else:
            print('Ошибка при получении данных')

