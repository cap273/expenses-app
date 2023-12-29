# tables.py
from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Date,
    Float,
    Boolean,
    ForeignKey,
)

metadata = MetaData()

# Define list of (default) categories
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
    "Education (including student loans)",
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
    "Mortgage Principal and Interest",
    "Home Services",
    "Capital Improvements",
    "Landlord Expenses",
]

# Define the expenses table
expenses_table = Table(
    "expenses",
    metadata,
    Column("ExpenseID", Integer, primary_key=True),
    Column("AccountID", Integer, ForeignKey("accounts.AccountID"), nullable=False),
    Column(
        "ExpenseScope", String(255)
    ),  # Either 'Joint' or the name of an individual
    Column(
        "PersonID", Integer, ForeignKey("persons.PersonID"), nullable=True
    ),  # NULL if it's a joint expense
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
