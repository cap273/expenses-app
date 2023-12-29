from flask import Flask, request, render_template, redirect, url_for
from sqlalchemy import create_engine, update
from sqlalchemy.exc import SQLAlchemyError
import os
from dotenv import load_dotenv
import logging
from datetime import datetime, date
from flask_login import (
    LoginManager,
    login_required,
    logout_user,
    current_user,
)
from urllib.parse import urlparse

from utils.db_tools import populate_categories_table, get_categories, get_database_url
from utils.session import get_current_currency, login_and_update_last_login
from database.models import db, Account
from database.tables import (
    expenses_table,
    categories_table,
    persons_table,
    CATEGORY_LIST,
)

# Load environment variables from .env file
load_dotenv()

# Retrieve database credentials from environment variables
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_SERVER = os.getenv("DB_SERVER")
DB_NAME = os.getenv("DB_NAME")
FLASK_ENV = os.getenv("FLASK_ENV")

# Configure logging based on the environment
if FLASK_ENV == "development":
    logging.basicConfig()
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
else:
    logging.basicConfig(level=logging.WARNING)

DATABASE_URL = get_database_url(DB_USERNAME, DB_PASSWORD, DB_SERVER, DB_NAME)

app = Flask(__name__)
app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY"
)  # Set the secret key to use for Flask sessions

# Using the ORM operations of Flask-SQLAlchemy to utilize
# Flask extensions like Flask-Login
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
db.init_app(app)  # Attach the SQLAlchemy instance to the Flask app

# Using SQLAlchemy Core to run lower-level database operations
engine = create_engine(DATABASE_URL)  # Create an engine for SQLAlchemy Core

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

if FLASK_ENV == "development":
    print("Database URL: ", DATABASE_URL)


# user_loader callback
@login_manager.user_loader
def load_user(user_id):
    return Account.query.get(int(user_id))


# metadata.create_all(engine)  # Create the tables if they don't exist
populate_categories_table(engine, categories_table, CATEGORY_LIST)


# Login view
@app.route("/login", methods=["GET", "POST"])
def login():
    error_message = None
    if request.method == "POST":
        user = Account.query.filter(
            (Account.account_name == request.form["username"])
            | (Account.user_email == request.form["username"])
        ).first()
        if user and user.check_password(request.form["password"]):
            login_and_update_last_login(user, engine)

            # The 'next' URL parameter is a feature of Flask-Login, which is used to handle the redirection of unauthenticated users
            next_page = request.args.get("next")

            # If there's no next page specified, or if the next page is for a different site (i.e., it has a network location component),
            # then default to redirecting to the index page
            if not next_page or urlparse(next_page).netloc != "":
                next_page = url_for("index")

            # Redirect to the next page (either the specified next page or the default index page)
            return redirect(next_page)
        else:
            error_message = "Invalid username or password"
    return render_template("login.html", error_message=error_message)


@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    error_message = None
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # Check if username already exists
        existing_user_by_username = Account.query.filter_by(
            account_name=username
        ).first()
        if existing_user_by_username:
            error_message = "Username already exists."
        else:
            # Check if email already exists
            existing_user_by_email = Account.query.filter_by(user_email=email).first()
            if existing_user_by_email:
                error_message = "Email address already exists."
            else:
                # Create new user instance
                new_user = Account(account_name=username, user_email=email)

                # Set password (this will hash the password)
                new_user.set_password(password)

                # Add new user to database
                db.session.add(new_user)
                db.session.commit()

                # Authenticate and login the new user
                login_and_update_last_login(new_user, engine)

                # Redirect to the index page
                return redirect(url_for("index"))

    return render_template("create_account.html", error_message=error_message)


# Logout view
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# Main page view
@app.route("/", methods=["GET"])
@login_required
def index():
    categories = get_categories(engine, categories_table)
    current_currency = get_current_currency()

    # Get the username of the logged-in user
    username = current_user.account_name

    return render_template(
        "index.html",
        categories=categories,
        currency=current_currency,
        username=username,
    )


@app.route("/submit", methods=["POST"])
@login_required
def submit():
    form_data = request.form
    current_user_account_id = current_user.id

    # Process the form data
    rows = zip(
        form_data.getlist("day[]"),
        form_data.getlist("month[]"),
        form_data.getlist("year[]"),
        form_data.getlist("amount[]"),
        form_data.getlist("category[]"),
        form_data.getlist("notes[]"),
    )

    try:
        with engine.connect() as conn:
            for day, month, year, amount, category, notes in rows:
                try:
                    expense_date = datetime.strptime(
                        f"{year}-{month}-{day}", "%Y-%B-%d"
                    ).date()

                    conn.execute(
                        expenses_table.insert().values(
                            AccountID=current_user_account_id,
                            Day=day,
                            Month=month,
                            Year=year,
                            ExpenseDate=expense_date,
                            Amount=float(
                                amount.replace(",", "")
                            ),  # Ensure no commas in submission from thousands separator
                            ExpenseCategory=category,
                            AdditionalNotes=notes,
                        )
                    )

                except ValueError:
                    # Handle invalid date
                    print("Invalid date:", day, month, year)
                    continue  # TODO: Handle this invalid date. For now, skip it.

            conn.commit()

    except SQLAlchemyError as e:
        print("Error occurred:", e)

    return redirect(url_for("index"))


# -------------------------------- Main Execution ------------------------------

if __name__ == "__main__":
    if FLASK_ENV == "development":
        app.run(debug=True)
    else:
        app.run(debug=False)
