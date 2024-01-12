import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

# Establish a connection to the database
connection = mysql.connector.connect(
    user = 'root',
    password = os.getenv('SQL_PASS'),
    host = '127.0.0.1',
    database = 'indonesian_restaurant'
)
        

def get_order_status(order_id: int):
    # Create a cursor object to execute SQL queries
    cursor = connection.cursor()

    # Execute the query
    query = f"SELECT status FROM order_tracking WHERE order_id = {order_id}"
    cursor.execute(query)

    # Fetch the results
    result = cursor.fetchone()

    # Close the cursor when done
    cursor.close()

    if result is not None:
        return result[0]
    else:
        return None
    

if __name__ == "__main__":
    print(get_order_status(41))
