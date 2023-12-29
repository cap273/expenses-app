# models.py
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()  # Initialize Flask-SQLAlchemy


class Account(UserMixin, db.Model):
    __tablename__ = "accounts"
    __table_args__ = {'implicit_returning': False}  # Avoid conflicts with database triggers for ID generation

    id = db.Column("AccountID", db.Integer, primary_key=True)
    account_name = db.Column("AccountName", db.String(255), unique=True, nullable=False)
    password = db.Column("Password", db.String(255))
    user_email = db.Column("UserEmail", db.String(255), unique=True)
    display_name = db.Column("AccountDisplayName", db.String(255))
    currency = db.Column("Currency", db.String(255))
    create_date = db.Column("CreateDate", db.Date)
    last_updated = db.Column("LastUpdated", db.Date)
    last_login_date = db.Column("LastLoginDate", db.Date)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Person(db.Model):
    __tablename__ = 'persons'
    __table_args__ = {'implicit_returning': False}

    PersonID = db.Column(db.Integer, primary_key=True)
    AccountID = db.Column(db.Integer, db.ForeignKey('accounts.AccountID'), nullable=False)
    PersonName = db.Column(db.String(255), nullable=False)
    CreateDate = db.Column(db.Date)
    LastUpdated = db.Column(db.Date)