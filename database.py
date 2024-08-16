import sqlite3

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path

    def execute_query(self, query, params=()):
        """
        Execute a query against the SQLite database.

        :param query: SQL query to execute.
        :param params: Parameters for the SQL query.
        :return: List of dictionaries representing the query results (for SELECT queries).
                 None for queries that don't return results.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(query, params)

            # If it's a SELECT query, fetch and return the results
            if query.strip().lower().startswith("select"):
                rows = cursor.fetchall()
                column_names = [description[0] for description in cursor.description]
                return [dict(zip(column_names, row)) for row in rows]
            else:
                # For INSERT, UPDATE, DELETE, etc., commit the transaction
                conn.commit()
                return None
        except Exception as e:
            conn.rollback()  # Rollback in case of error
            print(f"An error occurred: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def get_entities(self):
        """
        Retrieve all entities from the database.

        :return: List of entities with their IDs and names.
        """
        query = "SELECT id, name FROM pages"
        return self.execute_query(query)

    def get_secret_by_id(self, entity_id):
        """
        Retrieve the secret for a given entity ID.

        :param entity_id: ID of the entity.
        :return: Secret key for the entity.
        """
        query = "SELECT secret FROM pages WHERE id = ?"
        result = self.execute_query(query, (entity_id,))
        return result[0]['secret'] if result else None
