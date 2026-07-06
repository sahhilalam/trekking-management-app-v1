from flask import Flask, request, session, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

from models import db, User, Trek, Booking
from routes.admin_routes import admin_routes
from routes.auth_routes import auth_routes
from routes.staff_routes import staff_routes
from routes.user_routes import user_routes

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
db.init_app(app)

admin_routes(app)
auth_routes(app)
staff_routes(app)
user_routes(app)

@app.route("/test")
def test():
    return render_template("test.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        admin = User.query.filter_by(role="Admin").first()
        if not admin:
            admin = User(name="Admin", email="admin@trek.com", password="admin123", phone="12345", role="Admin", account_status="Approved")
            db.session.add(admin)
            db.session.commit()
            print("Admin created successfully!")
        else:
            print("Admin already exists!")
    
    app.run(debug=True)