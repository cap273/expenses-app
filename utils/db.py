from sqlalchemy import select


def populate_categories_table(engine, categories_table, category_list):
    with engine.connect() as connection:
        # Get existing categories in one query
        existing_categories_query = select(categories_table.c.CategoryName)
        existing_categories = connection.execute(existing_categories_query).fetchall()
        existing_categories = {row.CategoryName for row in existing_categories}

        # Find which categories need to be added
        new_categories = [
            category
            for category in category_list
            if category not in existing_categories
        ]

        # Insert new categories in one query, if there are any
        if new_categories:
            insert_query = categories_table.insert().values(
                [{"CategoryName": category} for category in new_categories]
            )
            connection.execute(insert_query)
            connection.commit()  # Commit the transaction after insertions


def get_categories(engine, categories_table):
    query = select(categories_table.c.CategoryName)
    with engine.connect() as connection:
        result = connection.execute(query)
        categories = [row.CategoryName for row in result]
        return categories  # Access the column as an attribute
