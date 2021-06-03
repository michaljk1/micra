from typing import List

from app.models.settlementuser import SettlementUser
from app.services import PaymentUtil


class Expense:
    def __init__(self, cost: str, group_id: int, splitwise_users: List[SettlementUser]):
        self.cost = cost
        self.group_id = group_id
        self.splitwise_users = splitwise_users

    def to_request(self):
        params = {'cost': self.cost, 'description': 'Micra', 'currency_code': 'PLN', 'group_id': self.group_id}
        for number, splitwise_user in enumerate(self.splitwise_users):
            params['users__' + str(number) + '__user_id'] = splitwise_user.user.splitwise_id
            params['users__' + str(number) + '__paid_share'] = self.get_paying_cost(splitwise_user)
            params['users__' + str(number) + '__owed_share'] = str(splitwise_user.total_charge)
        return params

    def get_paying_cost(self, splitwise_user):
        if splitwise_user.paying:
            return self.cost
        else:
            return '0.00'
