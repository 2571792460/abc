import mysql.connector

db_conn = mysql.connector.connect(host="oooooliversi.eastus.cloudapp.azure.com", user="user",
                                  password="password", database="events")

db_cursor = db_conn.cursor()
db_cursor.execute('''
          CREATE TABLE Ph_value
          (id INT NOT NULL AUTO_INCREMENT, 
           SwimminPool_id VARCHAR(250) NOT NULL ,
           Device_id VARCHAR(250) NOT NULL,
           Water_ph INTEGER NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT water_ph_pk PRIMARY KEY (id))
          ''')

db_cursor.execute('''
          CREATE TABLE Water_temperature
          (id INT NOT NULL AUTO_INCREMENT, 
           SwimminPool_id VARCHAR(250) NOT NULL,
           Device_id VARCHAR(250) NOT NULL,
           Water_temperature INTEGER NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT water_temperature_pk PRIMARY KEY (id))
          ''')


db_cursor.close()
