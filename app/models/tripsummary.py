from typing import List

from app.models.car import Balance


class TripSummary:
    def __init__(self, balances: List[Balance], total_kilometers: int):
        self.balances = balances
        self.total_kilometers = total_kilometers