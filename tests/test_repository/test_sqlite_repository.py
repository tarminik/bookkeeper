import os
import tempfile
from datetime import datetime

import pytest

from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.repository.sqlite_repository import SqliteRepository


@pytest.fixture
def db_path():
    """Create a temporary database file for testing"""
    fd, path = tempfile.mkstemp(suffix='.db')
    yield path
    os.close(fd)
    os.unlink(path)


@pytest.fixture
def custom_class():
    class Custom:
        pk = 0
        name = ''
        test = ''

    return Custom


@pytest.fixture
def category_repo(db_path):
    return SqliteRepository(db_path, Category)


@pytest.fixture
def expense_repo(db_path):
    return SqliteRepository(db_path, Expense)


@pytest.fixture
def custom_repo(db_path, custom_class):
    return SqliteRepository(db_path, custom_class)


def test_crud(custom_repo, custom_class):
    obj = custom_class()
    obj.name = 'test'
    pk = custom_repo.add(obj)
    assert obj.pk == pk
    assert custom_repo.get(pk).name == 'test'
    
    obj2 = custom_class()
    obj2.pk = pk
    obj2.name = 'updated'
    custom_repo.update(obj2)
    assert custom_repo.get(pk).name == 'updated'
    
    custom_repo.delete(pk)
    assert custom_repo.get(pk) is None


def test_cannot_add_with_pk(custom_repo, custom_class):
    obj = custom_class()
    obj.pk = 1
    with pytest.raises(ValueError):
        custom_repo.add(obj)


def test_cannot_update_without_pk(custom_repo, custom_class):
    obj = custom_class()
    with pytest.raises(ValueError):
        custom_repo.update(obj)


def test_cannot_delete_nonexistent(custom_repo):
    with pytest.raises(KeyError):
        custom_repo.delete(999)


def test_get_all(custom_repo, custom_class):
    objects = []
    for i in range(5):
        obj = custom_class()
        obj.name = f'test{i}'
        custom_repo.add(obj)
        objects.append(obj)
    
    all_objects = custom_repo.get_all()
    assert len(all_objects) == 5
    assert all(obj.name.startswith('test') for obj in all_objects)


def test_get_all_with_condition(custom_repo, custom_class):
    for i in range(5):
        obj = custom_class()
        obj.name = f'test{i}'
        obj.test = 'common'
        custom_repo.add(obj)
    
    filtered = custom_repo.get_all({'name': 'test0'})
    assert len(filtered) == 1
    assert filtered[0].name == 'test0'
    
    filtered = custom_repo.get_all({'test': 'common'})
    assert len(filtered) == 5


def test_category_repo(category_repo):
    cat = Category('Food')
    pk = category_repo.add(cat)
    assert cat.pk == pk
    
    retrieved = category_repo.get(pk)
    assert retrieved is not None
    assert retrieved.name == 'Food'
    assert retrieved.parent is None
    
    # Test with parent
    child = Category('Fruits', pk)
    child_pk = category_repo.add(child)
    
    retrieved_child = category_repo.get(child_pk)
    assert retrieved_child is not None
    assert retrieved_child.name == 'Fruits'
    assert retrieved_child.parent == pk


def test_expense_repo(expense_repo, category_repo):
    # Create a category first
    cat = Category('Food')
    cat_pk = category_repo.add(cat)
    
    # Create an expense
    expense = Expense(100, cat_pk, comment='Groceries')
    pk = expense_repo.add(expense)
    
    retrieved = expense_repo.get(pk)
    assert retrieved is not None
    assert retrieved.amount == 100
    assert retrieved.category == cat_pk
    assert retrieved.comment == 'Groceries'
    assert isinstance(retrieved.expense_date, datetime)
    assert isinstance(retrieved.added_date, datetime)


def test_datetime_handling(expense_repo, category_repo):
    # Create a category
    cat = Category('Food')
    cat_pk = category_repo.add(cat)
    
    # Create an expense with specific dates
    test_date = datetime(2023, 1, 1, 12, 0, 0)
    expense = Expense(100, cat_pk, expense_date=test_date, added_date=test_date)
    pk = expense_repo.add(expense)
    
    # Retrieve and check dates
    retrieved = expense_repo.get(pk)
    assert retrieved is not None
    assert retrieved.expense_date.year == 2023
    assert retrieved.expense_date.month == 1
    assert retrieved.expense_date.day == 1
    assert retrieved.expense_date.hour == 12
