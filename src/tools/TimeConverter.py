import os
from datetime import datetime
import pytz


class TimeConverter:
    @staticmethod
    def convert(input_time: datetime):
        server_timezone = os.environ['SERVER_TIMEZONE']
        server_timezone_obj= pytz.timezone(server_timezone)
        local_time = input_time.replace(tzinfo=pytz.utc).astimezone(server_timezone_obj)
        return server_timezone_obj.normalize(local_time)

    @staticmethod
    def now():
        current_utc_time = datetime.utcnow()
        return TimeConverter.convert(current_utc_time)
