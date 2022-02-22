import configparser
import datetime

class SysConfig():
    def __init__(self, file_name='./common/config.cfg', section='development'):
        self.file_name = file_name
        self.section = section
    
    def get(self)->dict:
        config = configparser.ConfigParser()
        le = {}
        if not config.read(self.file_name) == None:
            config.sections()
            le = self.trans(config[self.section])
        return le

    def trans(slef, config):
        le = {}
        for k,v in config.items():
            if v.startswith("datetime"):
                v = eval(v)
            le[k.upper()] = v
        return le