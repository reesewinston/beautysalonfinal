import mysql.connector
from mysql.connector import Error


def createConnection():
    try:
        connection = mysql.connector.connect(
            user='appuser',
            password='AppPass123!',
            host='127.0.0.1',
            port=3306,
            database='beauty_booking_system'
        )
        return connection
    except Error as e:
        print(f'connection error: {e}')
        return None
