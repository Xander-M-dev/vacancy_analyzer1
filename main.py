import json
import psycopg2
from utils import create_database
from db_manager import DBManager
from config import config


def load_from_json(filepath: str = "data/vacancies.json"):
    """Читает JSON (ответ hh.ru), извлекает компании и вакансии, заполняет БД."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    items = data.get('items', [])
    if not items:
        print("Файл не содержит вакансий.")
        return

    employers = {}
    for vac in items:
        emp = vac.get('employer')
        if emp and emp['id'] not in employers:
            employers[emp['id']] = {
                'employer_id': int(emp['id']),
                'employer_name': emp['name'],
                'employer_url': emp.get('alternate_url')
            }

    db_params = config()
    db_params['database'] = 'hh_vacancies'
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()

    for emp in employers.values():
        cur.execute("""
            INSERT INTO employers (employer_id, employer_name, employer_url)
            VALUES (%s, %s, %s) ON CONFLICT (employer_id) DO NOTHING
        """, (emp['employer_id'], emp['employer_name'], emp['employer_url']))

    for vac in items:
        salary = vac.get('salary')
        salary_from = salary.get('from') if salary else None
        salary_to = salary.get('to') if salary else None
        cur.execute("""
            INSERT INTO vacancies
            (vacancy_id, employer_id, vacancy_name, salary_from, salary_to, vacancy_url)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (vacancy_id) DO NOTHING
        """, (
            int(vac['id']),
            int(vac['employer']['id']),
            vac['name'],
            salary_from,
            salary_to,
            vac['alternate_url']
        ))

    conn.commit()
    cur.close()
    conn.close()
    print(f"Загружено {len(employers)} компаний и {len(items)} вакансий.")


def user_interaction(db_manager: DBManager):
    """Интерактивный интерфейс для работы с программой."""
    while True:
        print("\n" + "=" * 50)
        print("Выберите действие:")
        print("1. Список компаний и количество вакансий")
        print("2. Список всех вакансий (компания, название, зарплата, ссылка)")
        print("3. Средняя зарплата по всем вакансиям")
        print("4. Вакансии с зарплатой выше средней")
        print("5. Поиск вакансий по ключевому слову в названии")
        print("0. Выход")
        print("=" * 50)

        choice = input("Ваш выбор: ").strip()
        if choice == '0':
            print("До свидания!")
            break

        elif choice == '1':
            results = db_manager.get_companies_and_vacancies_count()
            if not results:
                print("Нет данных о компаниях.")
            else:
                print("\n--- Компании и количество вакансий ---")
                for company, count in results:
                    print(f"  • {company}: {count} вакансий")

        elif choice == '2':
            results = db_manager.get_all_vacancies()
            if not results:
                print("Нет вакансий в базе данных.")
            else:
                print("\n--- Список всех вакансий ---")
                for company, vacancy, salary_from, salary_to, url in results:
                    if salary_from and salary_to:
                        salary_str = f"{salary_from} - {salary_to}"
                    elif salary_from:
                        salary_str = f"от {salary_from}"
                    elif salary_to:
                        salary_str = f"до {salary_to}"
                    else:
                        salary_str = "не указана"
                    print(f"  • {vacancy} в компании {company}")
                    print(f"    Зарплата: {salary_str}")
                    print(f"    Ссылка: {url}\n")

        elif choice == '3':
            avg = db_manager.get_avg_salary()
            if avg is None or avg == 0:
                print("Нет данных о зарплатах для расчёта среднего значения.")
            else:
                print(f"\n--- Средняя зарплата по всем вакансиям ---")
                print(f"  {int(avg)} рублей")

        elif choice == '4':
            results = db_manager.get_vacancies_with_higher_salary()
            if not results:
                print("Нет вакансий с зарплатой выше средней.")
            else:
                print("\n--- Вакансии с зарплатой выше средней ---")
                for vacancy, company, salary_avg, url in results:
                    print(f"  • {vacancy} ({company}) – средняя зарплата {int(salary_avg)} руб.")
                    print(f"    Ссылка: {url}\n")

        elif choice == '5':
            keyword = input("Введите ключевое слово для поиска (например, 'python'): ").strip()
            if not keyword:
                print("Ключевое слово не может быть пустым.")
                continue
            results = db_manager.get_vacancies_with_keyword(keyword)
            if not results:
                print(f"Вакансии, содержащие '{keyword}' в названии, не найдены.")
            else:
                print(f"\n--- Вакансии, содержащие '{keyword}' в названии ---")
                for vacancy, company, url in results:
                    print(f"  • {vacancy} – {company}")
                    print(f"    Ссылка: {url}\n")
        else:
            print("Неверный ввод. Пожалуйста, выберите цифру от 0 до 5.")


def main():
    create_database()
    load_from_json("data/vacancies.json")
    db_manager = DBManager()
    user_interaction(db_manager)

if __name__ == "__main__":
    main()
