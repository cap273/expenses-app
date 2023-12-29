from flask_login import login_user
from sqlalchemy import update, exc
from datetime import datetime

from database.models import Account


def get_current_currency():
    """
    Placeholder function to get the current currency for the session.
    This function should be replaced with actual logic to retrieve
    the session-specific currency.
    """
    # Placeholder implementation - this should be replaced
    return "USD"  # Default to 'USD' for now

def login_and_update_last_login(user, engine):
    try:
        # Log in the user
        login_user(user)

        # Update the last login date using SQLAlchemy Core
        with engine.begin() as connection:  # Automatically begins a transaction
            stmt = update(Account).where(Account.id == user.id).values(last_login_date=datetime.utcnow())
            connection.execute(stmt)

        return True
    except exc.SQLAlchemyError as e:
        print("Error occurred during login or update:", e)
        return False
