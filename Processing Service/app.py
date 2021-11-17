import datetime
import json
import logging.config
import os

import connexion
import requests
import yaml
from apscheduler.schedulers.background import BackgroundScheduler
from flask_cors import CORS, cross_origin

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())
    data_file = app_config["datastore"]["filename"]

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    logger = logging.getLogger('basicLogger')

def get_stats():
    logger.info('Get stats request started')
    if os.path.isfile('data.json'):
        with open(app_config['datastore']['filename']) as f:
            logger.info('Request has ended')
            return json.load(f), 200
    else:
        logger.error('file does not exist')
        msg = 'file does not exist'
        return msg, 404
def populate_stats():
    """ Periodically update stats """
    logger.info(f"Start Periodic Processing")
    current_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(data_file, "r") as f:
        last_update = json.load(f)["last_updated"]

    response_water_temperature = requests.get(app_config["water_temperature"]["url"], params={'timestamp': last_update})
    response_ph_value = requests.get(app_config["water_ph"]["url"], params={'timestamp': last_update})

    if len(response_water_temperature.json()) != 0 and len(response_ph_value.json()) != 0:
        temp_list = []
        for tmd in response_water_temperature.json():
            temp_list.append(tmd['Water_temperature'])

        max_wt_reading = max(temp_list)
        num_wt_readings = len(response_water_temperature.json())

        ph_value_list = []
        for ph_value in response_ph_value.json():
            ph_value_list.append(ph_value['Water_ph'])
        max_pv_reading = max(ph_value_list)
        num_pv_readings = len(response_ph_value.json())

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