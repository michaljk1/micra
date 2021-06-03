from typing import List

from app.models.settlementuser import SettlementUser
from app.services import PaymentUtil


class Settlement:
    def __init__(self, settlement_users: List[SettlementUser], total_kilometers: int):
        self.settlement_users = settlement_users
        self.total_kilometers = total_kilometers
        self.parking_charge = PaymentUtil.PARKING_CHARGE
        self.gas_charge = PaymentUtil.convert_kilometers_to_money(total_kilometers)
        self.total_charge = self.gas_charge + self.parking_charge

