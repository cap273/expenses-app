from flask import Flask, request, render_template, redirect, url_for
from sqlalchemy import create_engine, select, update
from sqlalchemy.exc import SQLAlchemyError
import os
import json
from dotenv import load_dotenv
import logging
from datetime import datetime
from flask_login import (
    LoginManager,
    login_required,
    logout_user,
    current_user,
)
from urllib.parse import urlparse

from utils.db_tools import populate_categories_table, get_categories, get_database_url
from utils.session import login_and_update_last_login
from database.models import db, Account, Person
from database.tables import (
    expenses_table,
    categories_table,
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
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"  # Configure session cookies

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


@login_manager.user_loader
def load_user(user_id):
    with db.session.begin():
        return db.session.get(Account, int(user_id))


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
                new_user = Account(
                    account_name=username,
                    user_email=email,
                    display_name=username,
                    currency='USD', # Default to USD
                )

                # Set password (this will hash the password)
                new_user.set_password(password)

                # Add new user to database
                db.session.add(new_user)
                db.session.commit()

                # Create a new Person instance associated with this account
                new_person = Person(AccountID=new_user.id, PersonName=username)

                # Add new person to database
                db.session.add(new_person)
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

    # Fetch persons associated with the current user's account
    persons = Person.query.filter_by(AccountID=current_user.id).all()

    # Also convert to JSON
    persons_data = [{"PersonID": person.PersonID, "PersonName": person.PersonName} for person in persons]
    persons_json = json.dumps(persons_data)

    return render_template(
        "index.html",
        categories=categories,
        persons=persons,
        persons_json=persons_json
    )


@app.route("/submit", methods=["POST"])
@login_required
def submit():
    form_data = request.form
    current_user_account_id = current_user.id

    # Process the form data
    rows = zip(
        form_data.getlist("scope[]"),
        form_data.getlist("day[]"),
        form_data.getlist("month[]"),
        form_data.getlist("year[]"),
        form_data.getlist("amount[]"),
        form_data.getlist("category[]"),
        form_data.getlist("notes[]"),
    )

    try:
        with engine.connect() as conn:
            for scope, day, month, year, amount, category, notes in rows:
                try:
                    expense_date = datetime.strptime(
                        f"{year}-{month}-{day}", "%Y-%B-%d"
                    ).date()

                    # Determine if the scope is joint or individual
                    person_id = None if scope == "Joint" else scope
                    expense_scope = "Joint" if scope == "Joint" else "Individual"

                    conn.execute(
                        expenses_table.insert().values(
                            AccountID=current_user_account_id,
                            ExpenseScope=expense_scope, # Set to Joint or Individual
                            PersonID=person_id,  # Set to None if Joint, otherwise set to PersonID
                            Day=day,
                            Month=month,
                            Year=year,
                            ExpenseDate=expense_date,
                            Amount=float(
                                amount.replace(",", "")
                            ),  # Ensure no commas in submission from thousands separator
                            ExpenseCategory=category,
                            AdditionalNotes=notes,
                            Currency=current_user.currency,
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


@app.route("/view_expenses")
@login_required
def view_expenses():

    # Create a SQL query to select expenses for the current user
    query = select(
        expenses_table.c.ExpenseDate,
        expenses_table.c.Amount,
        expenses_table.c.ExpenseCategory,
        expenses_table.c.AdditionalNotes,
        expenses_table.c.Currency,
    ).where(expenses_table.c.AccountID == current_user.id)

    # Execute the query using SQLAlchemy Core
    with engine.connect() as connection:
        result = connection.execute(query)
        user_expenses = result.fetchall()

    # Convert raw results to a list of dicts
    expenses = [row._asdict() for row in user_expenses]

    # Format the amount in each expense
    for expense in expenses:
        if expense["Currency"] == 'USD':
            expense["Amount"] = "${:,.2f}".format(expense["Amount"])
        elif expense["Currency"] == 'EUR':
            expense["Amount"] = "€{:,.2f}".format(expense["Amount"])

    return render_template("view_expenses.html", expenses=expenses)


# -------------------------------- User Management Routes ---------------------


@app.route("/profile")
@login_required
def profile():
    # Assuming you have a relationship set up to get persons associated with the user
    persons = Person.query.filter_by(AccountID=current_user.id).all()
    print(persons)  # Debugging: Check if persons contain data
    return render_template("profile.html", current_user=current_user, persons=persons)


@app.route("/update_profile", methods=["POST"])
@login_required
def update_profile():
    display_name = request.form.get("display_name")
    new_password = request.form.get("new_password")
    new_currency = request.form.get("currency")  # Get the new currency from the form

    # Update display name
    if display_name:
        current_user.display_name = display_name

    # Update password, if provided
    if new_password:
        # Hash the new password
        current_user.set_password(new_password)

    # Update currency, if different
    if new_currency and new_currency != current_user.currency:
        current_user.currency = new_currency

    person_ids = request.form.getlist("person_ids[]")
    person_names = request.form.getlist("person_names[]")

    for person_id, person_name in zip(person_ids, person_names):
        if person_id == 'new':
            new_person = Person(AccountID=current_user.id, PersonName=person_name)
            db.session.add(new_person)
        else:
            person = Person.query.filter_by(PersonID=person_id, AccountID=current_user.id).first()
            if person:
                person.PersonName = person_name

    # Commit changes to the database
    db.session.commit()

    return redirect(url_for("profile"))


# -------------------------------- Main Execution ------------------------------

if __name__ == "__main__":
    if FLASK_ENV == "development":
        app.run(debug=True)
    else:
        app.run(debug=False)
