from flask import Flask, request, render_template, redirect, url_for
import pyodbc
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Float,
    Date,
    Boolean,
    ForeignKey,
)
from sqlalchemy.exc import SQLAlchemyError
import os
from dotenv import load_dotenv
import logging
from datetime import datetime, date

from utils.db import populate_categories_table, get_categories

app = Flask(__name__)

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


def get_database_url():
    drivers = [driver for driver in pyodbc.drivers()]
    driver = None

    if "ODBC Driver 18 for SQL Server" in drivers:
        driver = "ODBC Driver 18 for SQL Server"
    elif "ODBC Driver 17 for SQL Server" in drivers:
        driver = "ODBC Driver 17 for SQL Server"
    else:
        raise Exception("Suitable ODBC driver not found")

    # Database URL using environment variables. Using ODBC Driver 17 for SQL Server
    return f"mssql+pyodbc://{DB_USERNAME}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}?driver={driver}"


DATABASE_URL = get_database_url()

if FLASK_ENV == "development":
    print("Database URL: ", DATABASE_URL)

engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Define the expenses table
expenses_table = Table(
    "expenses",
    metadata,
    Column("ExpenseID", Integer, primary_key=True),
    Column("AccountID", Integer, ForeignKey("accounts.AccountID"), nullable=False),
    Column("ResponsibleEntity", String(255)),  # Either 'Joint' or the name of an individual
    Column("PersonID", Integer, ForeignKey("persons.PersonID"), nullable=True), # NULL if it's a joint expense
    Column("Day", Integer, nullable=False),
    Column("Month", String(50), nullable=False),
    Column("Year", Integer, nullable=False),
    Column("ExpenseDate", Date, nullable=False),
    Column("ExpenseDayOfWeek", String(50)),
    Column("Amount", Float, nullable=False),
    Column("AdjustedAmount", Float),  # Amount after adjustments
    Column("ExpenseCategory", String(255), nullable=False),
    Column("AdditionalNotes", String(255)),
    Column("CreateDate", Date),
    Column("LastUpdated", Date),
    Column("Currency", String(50)),
    Column("ManualCategory", String(255)),
    Column("SuggestedCategory", String(255)),
    Column("CategoryConfirmed", Boolean),
    extend_existing=False,
    # Set implicit_returning to False so that
    # SQLAlchemy won't try to use the OUTPUT clause to fetch the inserted ID.
    # This should avoid conflicts with database triggers for ID generation
    implicit_returning=False,
)

# Define the categories table
categories_table = Table(
    "categories",
    metadata,
    Column("CategoryID", Integer, primary_key=True),
    Column("CategoryName", String(255), unique=True, nullable=False),
    Column("CreateDate", Date),
    Column("LastUpdated", Date),
    extend_existing=False,
)

# Define list of categories
CATEGORY_LIST = [
    "Restaurant and Takeout (Non-Social)",
    "Shoes and Clothing",
    "Groceries",
    "Alcohol",
    "Entertainment",
    "Utilities",
    "Sports and Fitness",
    "Haircuts and Cosmetics",
    "Airplane Flights",
    "Hotel and Lodging",
    "Car-Related Expenses (excluding gasoline)",
    "Taxi and Ride-Sharing",
    "Gasoline",
    "Household Goods",
    "Other Transportation Expenses",
    "Healthcare and Medical",
    "Gifts and Donations",
    "Software and Electronics",
    "Education",
    "Internet, Cell Phone, and TV",
    "Miscellaneous",
    "Restaurant and Takeout (Social)",
    "Rent",
    "Interest and Banking Fees",
    "Car and Renters Insurance",
    "Other Memberships and Fees",
    "Mortgage Insurance",
    "Homeowners Insurance",
    "Property Taxes",
    "Mortgage P and I",
    "Home Services",
    "Capital Improvements",
    "Landlord Expenses",
]

# Define the accounts table
accounts_table = Table(
    "accounts",
    metadata,
    Column("AccountID", Integer, primary_key=True),
    Column("AccountName", String(255), nullable=False),
    Column("CreateDate", Date),
    Column("LastUpdated", Date),
    extend_existing=True,
)

# Define the persons table
persons_table = Table(
    "persons",
    metadata,
    Column("PersonID", Integer, primary_key=True),
    Column("AccountID", Integer, ForeignKey("accounts.AccountID"), nullable=False),
    Column("PersonName", String(255), nullable=False),
    Column("CreateDate", Date),
    Column("LastUpdated", Date),
    extend_existing=True,
)


# metadata.create_all(engine)  # Create the tables if they don't exist
populate_categories_table(engine, categories_table, CATEGORY_LIST)


@app.route("/", methods=["GET"])
def index():
    categories = get_categories(engine, categories_table)
    return render_template("index.html", categories=categories)


@app.route("/submit", methods=["POST"])
def submit():
    form_data = request.form

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
