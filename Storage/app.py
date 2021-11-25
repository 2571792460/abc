from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
import datetime
import connexion
from connexion import NoContent
from water_temperature import WaterTemperature
from ph_value import PhValue
import logging, logging.config
import json
from pykafka import KafkaClient
from  pykafka.common import OffsetType
from threading import Thread
from sqlalchemy import and_
import yaml
import time
import os
if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

with open("app_conf.yml", "r") as f:
    app_config = yaml.safe_load(f.read())
    db_info = app_config["db"]

with open("log_conf.yml", "r") as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    logger = logging.getLogger("basicLogger")
    logger.info("App Conf File: %s" % app_conf_file)
    logger.info("Log Conf File: %s" % log_conf_file)

DB_ENGINE = create_engine("mysql+pymysql://%s:%s@%s:%s/%s"
                          % (db_info["user"], db_info["password"], db_info["hostname"], db_info["port"], db_info["db"]))
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

# def report_ph_value_readings(body):
#     """ Receives a ph value reading """
#
#     session = DB_SESSION()
#
#     pv = PhValue(body['SwimminPool_id'],
#                  body['Device_id'],
#                  body['timestamp'],
#                  body['Water_ph'])
#
#     session.add(pv)
#
#     session.commit()
#     session.close()
#     logger.info("Connecting to DB. Hostname:oliversilab6.eastus.cloudapp.azure.com, Port:3306")
#
#     return NoContent, 201
def get_report_ph_value_readings(timestamp, end_timestamp):
    session = DB_SESSION()
    timestamp_datetime = datetime.datetime.strptime(timestamp ,"%Y-%m-%dT%H:%M:%SZ" )
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%SZ")
    # readings = session.query(PhValue).filter(PhValue.date_created >= timestamp_datetime)
    readings = session.query(PhValue).filter(
        and_(PhValue.date_created >= timestamp_datetime,
            PhValue.date_created < end_timestamp_datetime))
    results_list = []
    for reading in readings:
        results_list.append(reading.to_dict())
    session.close()
    logger.info("Query for ph value readings after %s returns %d results" % (timestamp, len(results_list)))
    return results_list, 200

def get_water_temperature_readings(timestamp, end_timestamp):
    session = DB_SESSION()
    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%SZ")
    readings = session.query(WaterTemperature).filter(
        and_(WaterTemperature.date_created >= timestamp_datetime,
            WaterTemperature.date_created < end_timestamp_datetime))
    results_list = []
    for reading in readings:
        results_list.append(reading.to_dict())
    session.close()
    logger.info("Query for water temperature readings after %s returns %d results" % (timestamp, len(results_list)))
    return results_list, 200


# def report_water_temperature_readings(body):
#     """ Receives a water temperature reading """
#
#     session = DB_SESSION()
#
#     wt = WaterTemperature(body['SwimminPool_id'],
#                           body['Device_id'],
#                           body['timestamp'],
#                           body['Water_temperature'])
#
#     session.add(wt)
#
#     session.commit()
#     session.close()
#     logger.info("Connecting to DB. Hostname:oliversilab6.eastus.cloudapp.azure.com, Port:3306")
#
#     return NoContent, 201
def process_messages():
    """ Process event messages """
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    # client = KafkaClient(hosts=hostname)
    timestried = app_config["Hi"]["timestried"]
    maxtired = app_config["Hi"]["maxtired"]
    while timestried < maxtired:
        logger.info("Connecting to Kafka. It's time" + str(timestried) + ".")
        try:
            client = KafkaClient(hosts=hostname)
            topic = client.topics[str.encode(app_config["events"]["topic"])]
            break
        except:
            logger.info("Connection failed.")
            time.sleep(app_config["Hi"]["sleep"])
            timestried = timestried + 1
            
    # Create a consume on a consumer group, that only reads new messages
    # (uncommitted messages) when the service re-starts (i.e., it doesn't
    # read all the old messages from the history in the message queue).
    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                         reset_offset_on_start=False,
                                         auto_offset_reset=OffsetType.LATEST)
    # This is blocking - it will wait for a new message
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)
        payload = msg["payload"]
        if msg["type"] == "wt":
            # Store the event1 (i.e., the payload) to the DB
            session = DB_SESSION()
            wt = WaterTemperature(payload['SwimminPool_id'],
                                  payload['Device_id'],
                                  payload['timestamp'],
                                  payload['Water_temperature'])


            session.add(wt)

            session.commit()
            session.close()
            logger.info("Connecting to DB. Hostname:oooooliversi.eastus.cloudapp.azure.com, Port:3306")
        elif msg["type"] == "pv":
            # Store the event2 (i.e., the payload) to the DB
            session = DB_SESSION()


            pv = PhValue(payload['SwimminPool_id'],
                                  payload['Device_id'],
                                  payload['timestamp'],
                                  payload['Water_ph'])
            session.add(pv)

            session.commit()
            session.close()
            logger.info("Connecting to DB. Hostname:oooooliversi.eastus.cloudapp.azure.com, Port:3306")
        # Commit the new message as being read
        consumer.commit_offsets()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090)
