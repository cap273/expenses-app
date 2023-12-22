import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from flask import url_for
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index(client):
    response = client.get(url_for('index'))
    assert response.status_code == 200
    assert b"Expenses App" in response.data  # replace "Welcome" with actual content you expect

def test_submit_expense(client):
    data = {'name': 'Test', 'amount': 100, 'category': 'Food'}
    response = client.post(url_for('submit_expense'), data=data)
    assert response.status_code == 302