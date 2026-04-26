import psycopg2
from config import config

class DBManager:
    """Класс для выполнения запросов к базе данных."""
    def __init__(self):
        params = config()
        params['database'] = 'hh_vacancies'
        self.conn = psycopg2.connect(**params)

    def get_companies_and_vacancies_count(self):
        """Возвращает список всех компаний и количество их вакансий."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT employer_name, COUNT(vacancy_id)
                FROM employers e
                LEFT JOIN vacancies v ON e.employer_id = v.employer_id
                GROUP BY e.employer_id, e.employer_name
                ORDER BY 2 DESC;
            """)
            return cur.fetchall()

    def get_all_vacancies(self):
        """Возвращает список всех вакансий с указанием компании, зарплаты и ссылки."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT e.employer_name, v.vacancy_name, v.salary_from, v.salary_to, v.vacancy_url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.employer_id;
            """)
            return cur.fetchall()

    def get_avg_salary(self):
        """Возвращает среднюю зарплату по всем вакансиям."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT AVG((COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2)
                FROM vacancies
                WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL;
            """)
            return cur.fetchone()[0]

    def get_vacancies_with_higher_salary(self):
        """Возвращает список вакансий с зарплатой выше средней."""
        avg_salary = self.get_avg_salary()
        if avg_salary is None:
            return []
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT v.vacancy_name, e.employer_name, 
                       (COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2 AS avg_vac_salary,
                       v.vacancy_url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.employer_id
                WHERE (COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2 > %s
                ORDER BY avg_vac_salary DESC;
            """, (avg_salary,))
            return cur.fetchall()

    def get_vacancies_with_keyword(self, keyword: str):
        """Возвращает вакансии, в названии которых есть ключевое слово."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT v.vacancy_name, e.employer_name, v.vacancy_url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.employer_id
                WHERE LOWER(v.vacancy_name) LIKE %s;
            """, (f"%{keyword.lower()}%",))
            return cur.fetchall()
