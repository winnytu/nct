import sys
import os
import configparser
import datetime
import requests
import random
from werkzeug.security import generate_password_hash, check_password_hash
#import sentry_sdk as sentry
#from sentry_sdk import configure_scope

class Base:
    def __init__(self):
        self.default_lang = 'ZH-CN'
        self.abs_path = os.path.dirname(os.path.abspath(__file__))
        self.config_cfg = f'{self.abs_path}/config/config.cfg'
        self.lang_cfg = f'{self.abs_path}/config/lang.cfg'
        self.env = os.environ.get('FLASK_ENV', 'development')
        self.config = self.get_cfg(self.config_cfg, self.env)
        self.lang = self.get_cfg(self.lang_cfg, self.default_lang)
        print(self.config['DEBUG'])
        if self.config['DEBUG']:
            print(self.config['JWT_REFRESH_TOKEN_EXPIRES'])
            print(f'abs_path = {self.abs_path}')
            print(f'config_cfg = {self.config_cfg}')
            print(f'lang_cfg = {self.lang_cfg}')
            print(self.lang['PLEASE_ENTER_PHONE_NUMBER'])

        #sentry
        #sentry.init(dsn=self.para['dsn'])
    
    def echo(self):
        return 'hello'

    #safe_str_cmp(user.password.encode('utf-8'), password.encode('utf-8'))
    def check_password(self, pwhash, password):
        if self.config['DEBUG']:
            print(f"pwhash={pwhash}, password={password}")
            
        if check_password_hash(pwhash, password):
            return True
        else:
            return False

    def gen_password(self, password):
        return generate_password_hash(password)

    def check_length(ps, min, max):
        if not ps.isalnum():
            return False

        if len(ps) >= min and len(ps) <= max:
            return True

        return False

    def cook_return(self, code, msg='', body={}):
        if not code == 200: #set sentry of exception in future
            msg = self.lang.get(f'ERR_{code}', '')
        return {'code' : code, 'msg' : msg, 'body' : body}    
            
    def send_sms(self, phone):
        sms_code = random.randint(1, 999999)
        
        headers = {'content-type': 'application/x-www-form-urlencoded', 'Accept':'application/json;charset=utf-8'}
        params = {'apikey' : self.config['SMS_API'], 
                    'mobile' : phone, 
                    'text' : f"{self.config['SMS_TITLE']}{sms_code}"}
        if self.config['DEBUG']:
            print(f"url={self.config['SMS_URL']}, header={headers}, params={params}")

        #don't allow empty string
        if phone.strip() == '':
            return False
        
        r = requests.post(self.config['SMS_URL'], headers=headers, data=params)
        if r.status_code == 200:
            return sms_code
        else: #set sentry of exception in future
            '''print(f'status={r.status_code}')
            print(f'text={r.text}')
            res = json.loads(r.text)
            print(res)'''
            return False

    def get_cfg(self, config_cfg, section)->dict:
        conf = configparser.ConfigParser()
        le = {}
        if not conf.read(config_cfg) == None:
            conf.sections()
            le = self.cfg_trans(conf[section])
        return le

    def cfg_trans(slef, conf):
        le = {}
        for k,v in conf.items():
            if v.startswith("datetime"):
                v = eval(v)
            le[k.upper()] = v
        return le

'''
        if os.path.exists(self.ini_file) != True:
            arg = {'level':'fatal', 'msg':'env.ini file not exist!'}
            self.trigger(arg)
            return False
        cf = configparser.ConfigParser()
        cf.read(self.ini_file)
        if self.env == 'dev' or self.env == 'stage':
            self.para = cf[self.env]
        else:
            self.para = cf['production']
        return self.para
    
    
        '''



Base()