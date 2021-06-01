import sys

from app import db
from pointer import app

with app.app_context():
    from app.models.usercourse import Admin

    admin = Admin(email=sys.argv[1], name=sys.argv[2],
                  surname=sys.argv[3], role='ADMIN', is_confirmed=True)
    admin.set_password(sys.argv[4])
    daniel = Admin(email='daniel@email.com', name='Daniel',
                  surname='Baziak', role='ADMIN', is_confirmed=True)
    daniel.set_password(sys.argv[4])
    michal = Admin(email='michal@email.com', name='Michal',
                  surname='Januszek', role='ADMIN', is_confirmed=True)
    michal.set_password(sys.argv[4])
    kuba = Admin(email='kuba@email.com', name='Kuba',
                  surname='Malek', role='ADMIN', is_confirmed=True)
    kuba.set_password(sys.argv[4])
    db.session.add(michal)
    db.session.add(daniel)
    db.session.add(kuba)
    db.session.add(admin)

    db.session.commit()
