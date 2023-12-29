# models.py
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()  # Initialize Flask-SQLAlchemy


class Account(UserMixin, db.Model):
    __tablename__ = "accounts"
    id = db.Column("AccountID", db.Integer, primary_key=True)
    account_name = db.Column("AccountName", db.String(255), unique=True, nullable=False)
    password = db.Column("Password", db.String(255))
    user_email = db.Column("UserEmail", db.String(255), unique=True)
    create_date = db.Column("CreateDate", db.Date)
    last_updated = db.Column("LastUpdated", db.Date)
    last_login_date = db.Column("LastLoginDate", db.Date)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
