import requests
import time
from typing import List, Dict, Any

class HeadHunterAPI:
    base_url = "https://api.hh.ru"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
        'Referer': 'https://hh.ru/',
        'Connection': 'keep-alive',
    }

    def get_employer(self, employer_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/employers/{employer_id}"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Ошибка {response.status_code} при получении работодателя {employer_id}")
                return {}
        except Exception as e:
            print(f"Исключение: {e}")
            return {}

    def get_employer_vacancies(self, employer_id: int) -> List[Dict[str, Any]]:
        params = {'employer_id': employer_id, 'per_page': 100, 'page': 0}
        all_vacancies = []
        while True:
            try:
                response = requests.get(
                    f"{self.base_url}/vacancies",
                    params=params,
                    headers=self.headers,
                    timeout=10
                )
                if response.status_code != 200:
                    break
                data = response.json()
                vacancies = data.get('items', [])
                all_vacancies.extend(vacancies)
                time.sleep(0.5)
                if params['page'] >= data.get('pages', 1) - 1:
                    break
                params['page'] += 1
            except Exception:
                break
        return all_vacancies
