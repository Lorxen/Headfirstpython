import mysql.connector

# DataBase class to configurate the SQL and use it with 'with'
class UseDataBase:

    def __init__(self, config:dict) -> None:
        # Store the data base configuration to self
        self.configuration = config
    
    def __enter__(self) -> 'cursor':
        # Initialize the cursor to use the database SQL
        self.conn = mysql.connector.connect(**self.configuration)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_value, exc_trace) -> None:
        # Close the cursor after using it
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
