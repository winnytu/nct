from datetime import datetime, timedelta,date
import json

class ItemIdGenerator():
    def __init__(self,_type,table):
        self._type = _type
        self.table = table

    def create(self):
        today = date.today()
        tomorrow = today + timedelta(days=1)
        today_str = today.strftime("%Y%m%d")
        table = self.table
        count = table.query.filter(table.create_time>today).filter(table.create_time<tomorrow).count()
        # 還要處理刪除資料後可能會重複itemId
        if self._type == 'exchange':
            return 'EI' + today_str+str(count+1).zfill(6)
        elif self._type == 'together':
            return 'TI' + today_str+str(count+1).zfill(6)


class DateEncoder(json.JSONEncoder):
    def default(self,obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime(DATETIME)
        elif isinstance(obj,datetime.date):
            return obj.strftime(DATE)
        elif isinstance(obj,Decimal):
            return str(obj)
        else:
            return json.JSONEncoder.default(self,obj)
    



