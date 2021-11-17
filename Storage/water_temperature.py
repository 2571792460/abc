from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class WaterTemperature(Base):
    """ Water Temperature """

    __tablename__ = "Water_temperature"

    # id = Column(Integer, primary_key=True)
    SwimminPool_id = Column(String(250), nullable=False,primary_key=True)
    Device_id = Column(String(250), nullable=False)
    timestamp = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)
    Water_temperature = Column(Integer, nullable=False)

    def __init__(self, SwimminPool_id, Device_id, timestamp, Water_temperature):
        """ Initializes a water temperature reading """
        self.SwimminPool_id = SwimminPool_id
        self.Device_id = Device_id
        self.timestamp = timestamp
        self.date_created = datetime.datetime.now() # Sets the date/time record is created
        self.Water_temperature = Water_temperature

    def to_dict(self):
        """ Dictionary Representation of a water temperature reading """
        dict = {}
        # dict['id'] = self.id
        dict['SwimminPool_id'] = self.SwimminPool_id
        dict['Device_id'] = self.Device_id
        dict['Water_temperature'] = self.Water_temperature
        dict['timestamp'] = self.timestamp
        dict['date_created'] = self.date_created

        return dict
