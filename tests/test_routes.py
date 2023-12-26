import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from flask import url_for
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_index(client):
    response = client.get(url_for("index"))
    assert response.status_code == 200
    assert b"Expenses App" in response.data


def test_submit_expense(client):
    data = {"name": "Test", "amount": 100, "category": "Food"}
    response = client.post(url_for("submit_expense"), data=data)
    assert response.status_code == 302


# Testing Database Connectivity
def test_database_connection():
    # Logic to test database connectivity
    pass


# Testing the Submission of Valid Expenses
def test_submit_valid_expense(client):
    valid_data = {
        "day": 1,
        "month": "January",
        "year": 2023,
        "amount": 100,
        "category": "Groceries",
        "notes": "Test grocery shopping",
    }
    response = client.post(url_for("submit"), data=valid_data)
    assert response.status_code == 302


# Testing the Submission of Invalid Expenses
@pytest.mark.parametrize(
    "invalid_data",
    [
        {
            "day": -1,
            "month": "January",
            "year": 2023,
            "amount": 100,
            "category": "Groceries",
            "notes": "",
        },  # Invalid day
        {
            "day": 1,
            "month": "InvalidMonth",
            "year": 2023,
            "amount": 100,
            "category": "Groceries",
            "notes": "",
        },  # Invalid month
    ],
)
def test_submit_invalid_expense(client, invalid_data):
    response = client.post(url_for("submit"), data=invalid_data)
    assert response.status_code == 400  # or appropriate status code for invalid input
    # Verify that invalid data is not added to the database


# Testing Date Format Validation
def test_date_format_validation(client):
    invalid_date_data = {
        # Assuming the app expects a specific date format
        "day": "32",
        "month": "January",
        "year": "2023",
        "amount": 100,
        "category": "Groceries",
        "notes": "",
    }
    response = client.post(url_for("submit"), data=invalid_date_data)
    assert response.status_code == 400  # Invalid date format should return an error


# Testing Handling of Non-Numeric Values in Numeric Fields
def test_non_numeric_amount(client):
    non_numeric_data = {
        "day": "1",
        "month": "January",
        "year": "2023",
        "amount": "one hundred",
        "category": "Groceries",
        "notes": "",
    }
    response = client.post(url_for("submit"), data=non_numeric_data)
    assert response.status_code == 400  # Non-numeric amount should return an error


# Testing Redirects and Flash Messages
def test_redirects_and_flash_messages(client):
    valid_data = {
        "day": 1,
        "month": "January",
        "year": 2023,
        "amount": 100,
        "category": "Groceries",
        "notes": "Test grocery shopping 2",
    }
    response = client.post(url_for("submit"), data=valid_data, follow_redirects=True)
    assert response.status_code == 200
    assert (
        b"Success" in response.data
    )  # Assuming 'Success' is a part of the flash message


# Testing Database Rollback on Error
def test_database_rollback_on_error(client):
    # Insert logic to simulate a database error and verify rollback
    pass


# Testing Security Aspects (SQL Injection)
def test_sql_injection_security(client):
    sql_injection_data = {
        "day": "1",
        "month": "January'; DROP TABLE expenses; --",
        "year": "2023",
        "amount": 100,
        "category": "Groceries",
        "notes": "",
    }
    response = client.post(url_for("submit"), data=sql_injection_data)
    assert response.status_code != 500  # The application should not crash


# Testing User Interface Elements in Rendered Templates
def test_ui_elements_in_index(client):
    response = client.get(url_for("index"))
    assert b"<form" in response.data  # Check for a form tag
    assert b"<input" in response.data  # Check for input fields
    assert b"<button" in response.data  # Check for buttons
