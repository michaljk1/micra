from app.models.usercourse import User


class SettlementUser:
    def __init__(self, user: User, kilometers: int, parking_charge: float, gas_charge: float, total_charge: float,
                 paying: bool):
        self.parking_charge = parking_charge
        self.user = user
        self.kilometers = kilometers
        self.gas_charge = gas_charge
        self.total_charge = total_charge
        self.paying = paying
