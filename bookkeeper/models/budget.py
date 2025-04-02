"""
Модуль описывает модель бюджета
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Budget:
    """
    Модель бюджета
    
    Attributes
    ----------
    pk : int
        Первичный ключ
    date : datetime
        Дата создания бюджета
    daily_amount : int
        Дневной бюджет в копейках
    weekly_amount : int
        Недельный бюджет в копейках
    monthly_amount : int
        Месячный бюджет в копейках
    """
    pk: int
    date: datetime
    daily_amount: int
    weekly_amount: int
    monthly_amount: int