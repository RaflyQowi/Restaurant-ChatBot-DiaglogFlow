import mysql.connector
from dotenv import load_dotenv
import os
from decimal import Decimal

load_dotenv()

# Establish a connection to the database
connection = mysql.connector.connect(
    user = 'root',
    password = os.getenv('SQL_PASS'),
    host = '127.0.0.1',
    database = 'indonesian_restaurant'
)

def insert_order_tracking(order_id, status):
    # Create a cursor object to execute SQL queries
    cursor = connection.cursor()

    # Execute the query
    query = ("INSERT INTO indonesian_restaurant.order_tracking (order_id, status) "
            "VALUES (%s, %s)")

    # Execute the query and commit the changes to the database
    cursor.execute(query, (order_id, status))
    connection.commit()

    # Close the cursor when done
    print("Order tracking inserted successfully!")
    cursor.close()


def get_total_price(order_id):
    # Create a cursor object to execute SQL queries
    cursor = connection.cursor()

    # Execute the query
    query = ("SELECT SUM(total_price) FROM indonesian_restaurant.orders WHERE order_id = %s")
    cursor.execute(query, (order_id,))

    # Fetch the results
    result = cursor.fetchone()

    # Close the cursor when done
    cursor.close()

    if result is not None:
        return result[0]
    else:
        return None
    
def insert_order_item(food_item, food_quantity, next_order_id):
    try:
        # Get the food ID and price for the given food item
        food_id, price = get_food_id_price(food_item)

        # Calculate the total price based on the quantity and individual item price
        total_price = price * food_quantity

        # Define the SQL query for inserting the order item
        query = ("INSERT INTO indonesian_restaurant.orders (order_id, item_id, quantity, total_price) "
                 "VALUES (%s, %s, %s, %s)")

        # Specify the values to be inserted into the table
        values = (int(next_order_id), int(food_id), int(food_quantity), total_price)

        # Create a cursor to execute the SQL query
        cursor = connection.cursor()

        # Execute the query and commit the changes to the database
        cursor.execute(query, values)
        connection.commit()

        print("Data inserted successfully!")

        # Close the cursor in the 'finally' block to ensure it's always closed
        cursor.close()

        # Return 1 to indicate success
        return 1

    except mysql.connector.Error as err:
        # Handle any database errors
        print(f"Error: {err}")

        # Rollback changes if necessary
        connection.rollback()

        # Return -1 to indicate an error
        return -1
    
    except Exception as e:
        print(f"An error occurred: {e}")
        # Rollback changes if necessary
        connection.rollback()

        return -1

def get_food_id_price(food_name):
    cursor = connection.cursor()

    # Execute the query
    query = "SELECT item_id, price FROM indonesian_restaurant.food_items WHERE name = %s"
    cursor.execute(query, (food_name,))

    # Fetch the results
    result = cursor.fetchone()

    # Close the cursor when done
    cursor.close()

    if result:
        return (result[0], result[1])
    else:
        return None

def get_next_avaliable_order_id():
    cursor = connection.cursor()

    # Execute the query
    query = "SELECT max(order_id) FROM orders"
    cursor.execute(query)

    # Fetch the results
    result = cursor.fetchone()[0]

    # Close the cursor when done
    cursor.close()

    if result is None:
        return 1
    else:
        return result + 1

  
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
    # print(get_order_status(41))
    # print(get_next_avaliable_order_id())
    # print(get_food_id_price("Nasi Goreng"))
    # insert_order_item("Nasi Goreng", 5, 1)
    # print(get_total_price(41))
    # insert_order_tracking(42, "in progress")
    pass
