"""
Простой тестовый скрипт для терминала
"""

import os
import pathlib

from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.repository.sqlite_repository import SqliteRepository
from bookkeeper.utils import read_tree

# Создаем директорию для базы данных, если она не существует
data_dir = pathlib.Path.home() / '.bookkeeper'
os.makedirs(data_dir, exist_ok=True)

# Путь к файлу базы данных
db_path = data_dir / 'bookkeeper.db'

# Создаем репозитории для категорий и расходов
cat_repo = SqliteRepository(str(db_path), Category)
exp_repo = SqliteRepository(str(db_path), Expense)

cats = '''
продукты
    мясо
        сырое мясо
        мясные продукты
    сладости
книги
одежда
'''.splitlines()

Category.create_from_tree(read_tree(cats), cat_repo)

while True:
    try:
        cmd = input('$> ')
    except EOFError:
        break
    if not cmd:
        continue
    if cmd == 'категории':
        print(*cat_repo.get_all(), sep='\n')
    elif cmd == 'расходы':
        print(*exp_repo.get_all(), sep='\n')
    elif cmd[0].isdecimal():
        amount, name = cmd.split(maxsplit=1)
        try:
            cat = cat_repo.get_all({'name': name})[0]
        except IndexError:
            print(f'категория {name} не найдена')
            continue
        exp = Expense(int(amount), cat.pk)
        exp_repo.add(exp)
        print(exp)
