from flask import Flask, request, session, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

from models import db
from routes.admin_routes import admin_routes
from routes.auth_routes import auth_routes
from routes.staff_routes import staff_routes
from routes.user_routes import user_routes

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db.init_app(app)

admin_routes(app)
auth_routes(app)
staff_routes(app)
user_routes(app)

if __name__ == "__main__":
    app.run(debug=True)