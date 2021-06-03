import sys

from app import db
from app.models.car import Car
from pointer import app

with app.app_context():
    from app.models.usercourse import Admin

    car = Car(name="micra", odometer=400000, fuel_usage=8)
    admin = Admin(email=sys.argv[1], name=sys.argv[2],
                  surname=sys.argv[3], role='ADMIN', is_confirmed=True)
    admin.set_password(sys.argv[4])
    daniel = Admin(email='daniel@email.com', name='Daniel',splitwise_id=26104222,
                  surname='Baziak', role='ADMIN', is_confirmed=True)
    daniel.set_password(sys.argv[4])
    michal = Admin(email='michal@email.com', name='Michal', splitwise_id=28079081,
                  surname='Januszek', role='ADMIN', is_confirmed=True)
    michal.set_password(sys.argv[4])
    kuba = Admin(email='kuba@email.com', name='Kuba',splitwise_id=26772301,
                  surname='Malek', role='ADMIN', is_confirmed=True)
    kuba.set_password(sys.argv[4])
    db.session.add(car)
    db.session.add(michal)
    db.session.add(daniel)
    db.session.add(kuba)
    db.session.add(admin)

    db.session.commit()
