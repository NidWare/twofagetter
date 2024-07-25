import sqlite3

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path

    def execute_query(self, query, params=()):
        """
        Execute a query against the SQLite database.

        :param query: SQL query to execute.
        :param params: Parameters for the SQL query.
        :return: List of dictionaries representing the query results.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        conn.close()
        return [dict(zip(column_names, row)) for row in rows]

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
