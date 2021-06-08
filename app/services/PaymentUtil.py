from typing import List
import requests
from flask import current_app

from app import db
from app.models.car import Period
from app.models.expense import Expense
from app.models.settlement import Settlement
from app.models.settlementuser import SettlementUser

PARKING_CHARGE = 300
LITERS_OF_GAS_PER_100KM = 8.0
PRICE_OF_ONE_LITER_OF_GAS = 2.5
CREATE_EXPENSE_URL = "https://secure.splitwise.com/api/v3.0/create_expense"


def settle(period_id):
    period = Period.query.filter_by(id=period_id).first()
    if period.settled:
        raise Exception('Period already settled')
    settlement_users = get_users_for_settlement(period)
    total_kilometers = 0
    for settlement_user in settlement_users:
        total_kilometers += settlement_user.kilometers
    for settlement_user in settlement_users:
        calculate_charge(settlement_user, total_kilometers)
    settlement = Settlement(settlement_users=settlement_users, total_kilometers=total_kilometers)
    response = create_expense(settlement)
    if spy_response(response):
        period.settled = True
        db.session.add(period)
        db.session.commit()


def create_expense(settlement):
    headers = {"Authorization": "Bearer " + current_app.config['SPLITWISE_BEARER']}
    expense = Expense(cost=str(settlement.total_charge), group_id=current_app.config['GROUP_ID'], splitwise_users=settlement.settlement_users)
    response = requests.post(url=CREATE_EXPENSE_URL, data=expense.to_request(), headers=headers)
    return response


def get_users_for_settlement(period):
    settlement_users: List[SettlementUser] = []
    for balance in period.balances:
        user = balance.user
        paying = user.name == 'Michal'
        settlement_users.append(
            SettlementUser(user=user, kilometers=balance.parking_kilometers, paying=paying, parking_charge=0,
                           gas_charge=0, total_charge=0))
    return settlement_users


def calculate_charge(settlement_user: SettlementUser, total_kilometers):
    parking_charge = calculate_parking_charge(settlement_user.kilometers, total_kilometers)
    gas_charge = convert_kilometers_to_money(settlement_user.kilometers)
    settlement_user.parking_charge = parking_charge
    settlement_user.gas_charge = gas_charge
    settlement_user.total_charge = gas_charge + parking_charge


def calculate_parking_charge(user_kilometers, total_kilometers):
    parking_charge: float = user_kilometers / total_kilometers * PARKING_CHARGE
    return parking_charge


def convert_kilometers_to_money(kilometers):
    return kilometers * get_price_for_one_kilometer()


def get_price_for_one_kilometer():
    return PRICE_OF_ONE_LITER_OF_GAS * LITERS_OF_GAS_PER_100KM / 100


def spy_response(response):
    return response.status_code == 200 and 'base' not in str(response)
