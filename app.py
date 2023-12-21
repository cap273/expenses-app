from flask import Flask, request, render_template, redirect, url_for
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float
from sqlalchemy.exc import SQLAlchemyError
import os
from dotenv import load_dotenv
import logging

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

# Database URL using environment variables
DATABASE_URL = f"mssql+pyodbc://{DB_USERNAME}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}?driver=ODBC+Driver+17+for+SQL+Server"

engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Define the table
inputs_table = Table(
    "expenses",
    metadata,
    Column("ExpenseID", Integer, primary_key=True),
    Column("Day", Integer),
    Column("Month", String(50)),
    Column("Year", Integer),
    Column("Amount", Float),
    Column("ExpenseCategory", String(255)),
    Column("AdditionalNotes", String(255)),
    extend_existing=True,
)

metadata.create_all(engine)  # Create the table if it doesn't exist


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


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
                # Skip rows with no data
                if not any([day, month, year, amount, category, notes]):
                    continue

                conn.execute(
                    inputs_table.insert().values(
                        Day=day,
                        Month=month,
                        Year=year,
                        Amount=amount if amount else 0,  # Default to 0 if empty
                        ExpenseCategory=category,
                        AdditionalNotes=notes,
                    )
                )
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
