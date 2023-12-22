from sqlalchemy import select

def populate_categories_table(engine, categories_table, category_list):
    with engine.connect() as connection:
        for category in category_list:
            # Check if the category already exists
            query = select(categories_table).where(categories_table.c.CategoryName == category)
            result = connection.execute(query).fetchone()
            if not result:
                # Insert the category if it doesn't exist
                insert_query = categories_table.insert().values(CategoryName=category)
                connection.execute(insert_query)
                connection.commit()

def get_categories(engine, categories_table):
    query = select(categories_table.c.CategoryName)
    with engine.connect() as connection:
        result = connection.execute(query)
        return [row.CategoryName for row in result]  # Access the column as an attribute
