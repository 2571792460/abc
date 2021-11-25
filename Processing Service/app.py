import datetime
import json
import logging.config
import os

import connexion
import requests
import yaml
from apscheduler.schedulers.background import BackgroundScheduler
from flask_cors import CORS, cross_origin
import os
if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"
with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())
    data_file = app_config["datastore"]["filename"]

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
logger = logging.getLogger('basicLogger')
logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

with open(data_file, "r") as f:
    json_file = json.load(f)
    last_update = json_file["last_updated"]
    num_wt_readings_old = json_file["num_wt_readings"]
    num_pv_readings_old = json_file["num_pv_readings"]
    max_wt_reading_old = json_file["max_wt_reading"]
    max_pv_reading_old = json_file["max_pv_reading"]

def get_stats():
    logger.info('Get stats request started')
    if os.path.isfile('data.json'):
        with open(app_config['datastore']['filename']) as f:
            logger.info('Request has ended')
            return json.load(f), 200
    else:
        with open(data_file, 'w') as json_file :
            temp = json.dumps({
                "num_wt_readings": 0,
            "max_wt_reading": 0,
            "num_pv_readings": 0,
            "max_pv_reading": 0,
            "last_updated": '2019-04-25T10:12:23Z'
            })
            json_file.write(temp)
        
        logger.error('file does not exist')
        msg = 'file does not exist create one'
        return msg, 404
def populate_stats():
    """ Periodically update stats """
    logger.info(f"Start Periodic Processing")
    current_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(data_file, "r") as f:
        last_update = json.load(f)["last_updated"]

    # response_water_temperature = requests.get(app_config["water_temperature"]["url"] , params={'timestamp': last_update} )
    # response_ph_value = requests.get(app_config["water_ph"]["url"], params={'timestamp': last_update})
    response_water_temperature = requests.get(app_config["water_temperature"]["url"] + "?timestamp=" + last_update + "&end_timestamp=" + current_time)
    response_ph_value = requests.get(app_config["water_ph"]["url"] + "?timestamp=" + last_update + "&end_timestamp=" + current_time)

    if len(response_water_temperature.json()) != 0 and len(response_ph_value.json()) != 0:
        temp_list = []
        for tmd in response_water_temperature.json():
            temp_list.append(tmd['Water_temperature'])
        temp_list.append(max_wt_reading_old)
        max_wt_reading = max(temp_list)
        num_wt_readings = len(response_water_temperature.json()) + num_wt_readings_old

        ph_value_list = []
        for ph_value in response_ph_value.json():
            ph_value_list.append(ph_value['Water_ph'])
        ph_value_list.append(max_pv_reading_old)
        max_pv_reading = max(ph_value_list)
        num_pv_readings = len(response_ph_value.json()) + num_pv_readings_old

        data = json.dumps({
            "num_wt_readings": num_wt_readings,
            "max_wt_reading": max_wt_reading,
            "num_pv_readings": num_pv_readings,
            "max_pv_reading": max_pv_reading,
            "last_updated": current_time
        })

        with open('data.json', 'w') as f:
            f.write(data)

        logger.debug(data)

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,
                  'interval',
                  seconds=app_config['scheduler']['period_sec'])
    sched.start()

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("open.yml",
            strict_validation=True,
            validate_responses=True)
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
if __name__ == "__main__":# run our standalone gevent server#
    init_scheduler()
    app.run(port=8100, use_reloader=False)