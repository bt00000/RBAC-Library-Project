from app import app, db
from app.models import Role

def create_tables():
    db.create_all()

def setup_roles():
    existing_roles = Role.query.count()
    if existing_roles == 0:
        roles = ['Student', 'Administrator', 'Librarian']
        for role_name in roles:
            role = Role(name=role_name)
            db.session.add(role)
        db.session.commit()
        print("Roles setup completed.")
    else:
        print("Roles already setup.")

if __name__ == '__main__':
    with app.app_context():
        create_tables()
        setup_roles()
    app.run(debug=True)
