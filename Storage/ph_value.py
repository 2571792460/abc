from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class PhValue(Base):
    """ Ph Value """

    __tablename__ = "Ph_value"

    id = Column(Integer, primary_key=True)
    SwimminPool_id = Column(String(250), nullable=False)
    Device_id = Column(String(250), nullable=False)
    timestamp = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)
    Water_ph = Column(Integer, nullable=False)

    def __init__(self, SwimminPool_id, Device_id, timestamp, Water_ph):
        """ Initializes a ph value reading """
        self.SwimminPool_id = SwimminPool_id
        self.Device_id = Device_id
        self.timestamp = timestamp
        self.date_created = datetime.datetime.now() # Sets the date/time record is created
        self.Water_ph = Water_ph

    def to_dict(self):
        """ Dictionary Representation of a ph value reading """
        dict = {}
        dict['id'] = self.id
        dict['SwimminPool_id'] = self.SwimminPool_id
        dict['Device_id'] = self.Device_id
        dict['Water_ph'] = self.Water_ph
        dict['timestamp'] = self.timestamp
        dict['date_created'] = self.date_created

        return dict
