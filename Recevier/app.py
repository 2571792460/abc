import requests
import connexion
from connexion import NoContent
import yaml
from pykafka import KafkaClient
import datetime
import json
import logging, logging.config
import time
import os
HEADERS = {"content-type": "application/json"}

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

with open("log_conf.yml", "r") as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
logger = logging.getLogger("basicLogger")
logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

timestried = app_config["Hi"]["timestried"]
maxtired = app_config["Hi"]["maxtired"]
while timestried < maxtired:
    logger.info("Connecting to Kafka. It's time" + str(timestried) + ".")
    try:
        client = KafkaClient(hosts='oooooliversi.eastus.cloudapp.azure.com:9092')
        topic = client.topics[str.encode(app_config["events"]["topic"])]
        break
    except:
        logger.info("Connection failed.")
        time.sleep(app_config["Hi"]["sleep"])
        timestried = timestried + 1

def report_ph_value_reading(body):
    # logger.info("Received event %s request with a unique id of %s"
    #             % ("ph value", body["SwimminPool_id"]))
    # response = requests.post(app_config["water_ph"]["url"],
    #                          json=body, headers=HEADERS)
    #
    # logger.info("Returned event %s response %s with status %s"
    #             % ("ph value", body["SwimminPool_id"], response.status_code))
    # return NoContent, response.status_code

    
    producer = topic.get_sync_producer()

    msg = {"type": "pv", "datetime": datetime.datetime.now().strftime(
        "%Y-%m-%dT%H:%M:%S"), "payload": body }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode("utf-8"))
    return NoContent, 201

def report_water_temperature_reading(body):
    # logger.info("Received event %s request with a unique id of %s"
    #             % ("water temperature", body["SwimminPool_id"]))
    # response = requests.post(app_config["water_temperature"]["url"],
    #                          json=body, headers=HEADERS)
    # logger.info("Returned event %s response %s with status %s"
    #             % ("water temperature", body["SwimminPool_id"], response.status_code))
    #
    # return NoContent, response.status_code
    client = KafkaClient(hosts='oooooliversi.eastus.cloudapp.azure.com:9092')

    topic = client.topics[str.encode("events")]
    producer = topic.get_sync_producer()

    msg = {"type": "wt", "datetime": datetime.datetime.now().strftime(
        "%Y-%m-%dT%H:%M:%S"), "payload": body}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode("utf-8"))
    return NoContent, 201


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api('openapi.yaml',
            strict_validation=True,
            validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080)


