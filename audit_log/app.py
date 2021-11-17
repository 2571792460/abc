import logging.config
import json
from pykafka import KafkaClient
import logging, logging.config
import yaml
import connexion


with open("app_conf.yml", "r") as f:
    app_config = yaml.safe_load(f.read())
    db_info = app_config["db"]

with open("log_conf.yml", "r") as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    logger = logging.getLogger("basicLogger")

def get_water_temperature_reading(index):
    """Get WT Reading in History"""
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                          app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    logger.info("Retrieving WTat index %d" % index)
    count = 0
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg['type'] == 'wt':
                count += 1
                if count == index:
                    return msg['payload'], 200
            return msg, 200
    except:
        logger.error("No more messages found")
    logger.error("Could not find WT at index %d" % index)
    return {"message": "Not Found"}, 404

def get_water_ph_reading(index):
    """Get WP Reading in History"""
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                          app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    logger.info("Retrieving PVat index %d" % index)
    count = 0
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg['type'] == 'pv':
                count += 1
                if count == index:
                    return msg['payload'], 200
            return msg, 200
    except:
        logger.error("No more messages found")
    logger.error("Could not find PV at index %d" % index)
    return {"message": "Not Found"}, 404


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8110)
