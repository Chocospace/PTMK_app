import click
import sqlite3
import datetime
import random
import faker
import pandas


@click.group()
def cli():
    pass


@click.command()
def myApp_1():
    """Создание таблицы с полями, представляющими ФИО, дату рождения, пол"""
    db = sqlite3.connect('PTMK_app.db')
    cur = db.cursor()
    try:
        cur.execute('''CREATE TABLE users (
        Name TEXT,
        Date_of_birth TEXT,
        Gender TEXT)''')
        print('Таблица "users" создана.')
    except:
        print('Таблица уже существует')

    db.commit()
    db.close()


@click.command()
@click.option('--name', default='XXX XXX', help='Введите имя')
@click.option('--date_of_birth', default='2000-01-01' , help='Введите дату рождения в формате ГГГГ-ММ-ДД')
@click.option('--gender', default='Male' , help='Введите пол Male/Female')
def myApp_2(name, date_of_birth, gender):
    """Создание новой записи. Использовать следующий формат:
    myApp 2 ФИО ДатаРождения Пол"""
    db = sqlite3.connect('PTMK_app.db')
    cur = db.cursor()
    cur.execute("INSERT INTO users VALUES (?, ?, ?)", (name, date_of_birth, gender))
    db.commit()
    db.close()
    print('Запись добавлена в БД.')


@click.command()
def myApp_3():
    """Вывод всех строк с уникальным значением ФИО+дата, отсортированным по ФИО,
     вывести ФИО, Дату рождения, пол, кол-во полных лет"""
    db = sqlite3.connect('PTMK_app.db')
    cur = db.cursor()
    output = cur.execute("SELECT DISTINCT Name, Date_of_birth, Gender FROM users ORDER BY Name ASC")

    def age(date_of_birth):
        """Определяет возраст"""
        list_date_of_birth = date_of_birth.split('-')
        user_age = datetime.datetime.now().year - int(list_date_of_birth[0])
        if (int(list_date_of_birth[1]) < datetime.datetime.now().month):
            user_age += 1
        elif (int(list_date_of_birth[1]) == datetime.datetime.now().month) and (
                int(list_date_of_birth[2]) < datetime.datetime.now().day):
            user_age += 1
        return (user_age)

    for i in output:
        print(i[0].ljust(20), '|'.rjust(5), i[1].rjust(5), '|'.rjust(5), i[2].ljust(8), '|'.center(5),
              age(str(i[1]).ljust(5)))
    db.commit()
    db.close()


@click.command()
def myApp_4():
    """Заполнение автоматически 1000000 строк.
    Распределение пола в них должно быть относительно равномерным, начальной буквы ФИО также.
    Заполнение автоматически 100 строк, в которых пол мужской и ФИО начинается с "F"."""

    fake = faker.Faker()

    def create_f_rows(num=1):
        """Генерирует строки в которых пол мужской и ФИО начинается в 'F'."""
        output = []
        flag = 0
        while flag < 100:
            name = fake.last_name() + ' ' + fake.first_name_male()
            if name[0] == 'F':
                flag += 1
                output.append({'name': name,
                               'date_of_birth': str(fake.date_between()),
                               'gender': 'Male'})
        return output

    def create_rows(num=1):
        """Генерирует рандомные данные"""
        range_list = [random.randint(0, 1) for y in range(num)]
        output = [{
            'name': fake.last_name() + ' ' + fake.first_name_male() if x == 0 else fake.last_name() + ' ' + fake.first_name_female(),
            'date_of_birth': str(fake.date_between()),
            'gender': 'Male' if x == 0 else 'Female'} for x in range_list]
        return output

    f_users = pandas.DataFrame(create_f_rows(100))
    users = pandas.DataFrame(create_rows(999900))

    # Записывает в ДБ
    db = sqlite3.connect('PTMK_app.db')
    cur = db.cursor()
    for index, row in f_users.iterrows():
        cur.execute("INSERT INTO users VALUES (?, ?, ?)", (row['name'], row['date_of_birth'], row['gender']))

    for index, row in users.iterrows():
        cur.execute("INSERT INTO users VALUES (?, ?, ?)", (row['name'], row['date_of_birth'], row['gender']))
    db.commit()
    db.close()
    print('БД заполнена.')


@click.command()
def myApp_5():
    """Результат выборки из таблицы по критерию: пол мужской, ФИО  начинается с "F". Сделать замер времени исполнения.
    Вывод приложения должен содержать время"""
    return myApp_5_body('users')


def myApp_5_body(table):
    start_time = datetime.datetime.now()
    db = sqlite3.connect('PTMK_app.db')
    cur = db.cursor()
    output = cur.execute(f"SELECT Name, Gender FROM {table} WHERE Gender == 'Male' AND Name LIKE 'F%'")

    for i in output:
        print(i[0].ljust(30), '|'.rjust(5), i[1].ljust(20))

    db.commit()
    db.close()
    end_time = datetime.datetime.now()
    myApp_5_time = str(end_time - start_time)
    print(f"Затрачено времени {myApp_5_time}.")
    return myApp_5_time



@click.command()
def myApp_6():
    """Произвести определенные манипуляции над базой данных для ускорения запроса из пункта 5.
    Убедиться, что время исполнения уменьшилось.
    Объяснить смысл произведенных действий. Предоставить результаты замера до и после"""

    def manipulation():
        """Производит манипуляции. Создает новую таблицу 'new_users', в которой создает индексы для столбцов с
        именем и полом. """
        db = sqlite3.connect('PTMK_app.db')
        cur = db.cursor()
        cur.execute('''CREATE TABLE new_users (
            _id INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT,
            Date_of_birth TEXT,
            Gender TEXT)''')

        cur.execute("INSERT INTO new_users (Name, Date_of_birth, Gender) SELECT Name, Date_of_birth, Gender FROM users")
        cur.execute("CREATE INDEX new_index ON new_users (Name, Gender)")
        db.commit()
        db.close()

    def new_myApp_5():
        """Результат выборки из новой тоблицы 'new_users'"""
        return myApp_5_body('new_users')

    try:
        manipulation()
    except:
        pass
    old = myApp_5_body('users')
    new = myApp_5_body('new_users')

    print(f'Создана новаю таблица "new_users", в которой созданы индексы для столбцов с именем и полом. Время выполнения старой выборки: {old}. Время выполнения новой выборки: {new}.')


cli.add_command(myApp_1)
cli.add_command(myApp_2)
cli.add_command(myApp_3)
cli.add_command(myApp_4)
cli.add_command(myApp_5)
cli.add_command(myApp_6)


if __name__ == '__main__':
    cli()