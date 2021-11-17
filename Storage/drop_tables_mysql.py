import mysql.connector

db_conn = mysql.connector.connect(host="oooooliversi.eastus.cloudapp.azure.com", user="user",
                                  password="password", database="events")
db_cursor = db_conn.cursor()

db_cursor.execute('''
          DROP TABLE Ph_value
          ''')

db_cursor.execute('''
          DROP TABLE Water_temperature
          ''')

db_cursor.close()
