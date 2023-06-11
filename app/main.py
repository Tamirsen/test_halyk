import os
from . import app, db
from app.models import User


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}

def create_admin():
    admin_username = os.getenv("ADMIN_USERNAME")
    admin_password = os.getenv("ADMIN_PASSWORD")

    if not admin_username or not admin_password:
        raise ValueError("Admin username and password must be set in .env file")
    
    with app.app_context():
        if User.query.filter_by(username=admin_username).first() is None:
            admin = User(username=admin_username)
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)