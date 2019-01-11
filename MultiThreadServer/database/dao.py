import datetime
import hashlib
# import logging

import MySQLdb
import pymongo

from .config import config

def md5(password):
    hash = hashlib.md5(password.encode('utf8')).hexdigest()
    return hash

def sha256(password):
    hash = hashlib.sha256(password.encode()).hexdigest()
    return hash

class MongoDao(object):
    def __init__(self):
        self.client = pymongo.MongoClient(host='127.0.0.1', port=27017)
        self.db = self.client['lab_safety']

        self.upload_data_table = self.db['data_model']

        self.user_table = self.db['user_model']
        self.user_log = self.db['user_log_model']

        self.device_table = self.db['device_model']
        self.device_log_table = self.db['device_log_model']

    def refresh_connect(self):
        self.client = pymongo.MongoClient(host='127.0.0.1', port=27017)
        self.db = self.client['lab_safety']

        self.upload_data_table = self.db['data_model']

        self.user_table = self.db['user_model']
        self.user_log = self.db['user_log_model']

        self.device_table = self.db['device_model']
        self.device_log_table = self.db['device_log_model']

    def insert_data(self, data):
        self.upload_data_table.insert_one(data)

    def login(self, phone_number, password):
        result = self.user_table.find_one({'phone_number': phone_number, 'password': sha256(password)})
        if result:
            return True
        else:
            return False

    def device_log(self, device_id, action, ip, phone_number):
        data = {
            'data_time': datetime.datetime.now(),
            'device_id': device_id,
            'action': str(action),
            'ip': ip,
            'phone_number': phone_number,
        }
        self.device_log_table.insert_one(data)
        if action == 0:
            self.device_table.update_one({"device_id": device_id}, {"$set": {"status": False}})
        elif action == 1:
            self.device_table.update_one({"device_id": device_id}, {"$set": {"status": True}})

class Dao(object):
    def __init__(self):
        self.config = config
        self.connector = MySQLdb.connect(host=config['host'], user=config['user'],
                                         password=config['password'], db=config['database'])
        # self.connector = mysql.connector.connect(**config)

    def __del__(self):
        self.connector.close()

    def refresh_connector(self):
        # if not self.connector.is_connected():
        self.connector = MySQLdb.connect(host=config['host'], user=config['user'],
                                         password=config['password'], db=config['database'])
    def get_connect(self):
        try:
            conn = MySQLdb.connect(host=config['host'], user=config['user'],
                                   password=config['password'], db=config['database'])
            return conn
        except Exception as err:
            print("[ {} ]: ERROR: {}".format(datetime.datetime.now(), err))
            return None

    def insert_data(self, data):
        # self.refresh_connector()
        try:
            conn = self.get_connect()
            cur = conn.cursor()
            sql = (
                "SELECT `id`"
                "FROM `management_device`"
                "WHERE device_id=%s"
            )
            cur.execute(sql, (data['device_id_id'],))
            device_id_id = cur.fetchone()[0]
            # print(device_id_id)
            data['device_id_id'] = device_id_id
            sql = ("INSERT INTO `management_data` "
                   "(device_id_id, data_time, switch_status, voltage_value, current_value, active_power_value, "
                   "total_active_power_value, power_factor_value, co2_emission_value, frequency_value) "
                   "VALUES (%(device_id_id)s, %(data_time)s, %(switch_status)s, %(voltage_value)s, %(current_value)s, "
                   "%(active_power_value)s, %(total_active_power_value)s, %(power_factor_value)s, %(co2_emission_value)s, "
                   "%(frequency_value)s);")

            cur.execute(sql, data)
            conn.commit()

            cur.close()
            conn.close()
        except Exception as err:
            print("[ {} ]: ERROR: {}".format(datetime.datetime.now(), err))

    def login(self, phone_number, password):
        result = [-1]
        try:
            conn = self.get_connect()
            cur = conn.cursor()
            sql = (
                "SELECT COUNT(*) AS `count` FROM `management_userprofile`"
                "WHERE phone_number=%s AND device_password=%s"
            )
            # cur.execute(sql, (phone_number, md5(password)))
            cur.execute(sql, (phone_number, password))
            result = cur.fetchone()

            cur.close()
            conn.close()
        except Exception as err:
            print("[ {} ]: ERROR: {}".format(datetime.datetime.now(), err))

        if result[0] >= 1:
            return True
        else:
            return False

    def _get_phone_id(self, phone_number):
        phone_number_id = ""
        try:
            conn = self.get_connect()
            cur = conn.cursor()

            sql = (
                "SELECT `id`"
                "FROM `management_userprofile`"
                "WHERE `phone_number`=%s"
            )
            cur.execute(sql, (phone_number,))
            phone_number_id = cur.fetchone()[0]

            cur.close()
            conn.close()
        except Exception as err:
            print("[ {} ]: ERROR: {}".format(datetime.datetime.now(), err))

        return phone_number_id

    def _get_device_id_id(self, device_id):
        device_id_id = ""

        try:
            conn = self.get_connect()
            cur = conn.cursor()
            sql = (
                "SELECT `id`"
                "FROM `management_device`"
                "WHERE `device_id`=%s"
            )
            cur.execute(sql, (device_id,))
            device_id_id = cur.fetchone()[0]

            cur.close()
            conn.close()
        except Exception as err:
            print("[ {} ]: ERROR: {}".format(datetime.datetime.now(), err))

        return device_id_id

    def device_log(self, device_id, action, ip, phone_number):
        device_id_id = self._get_device_id_id(device_id)
        phone_number_id = self._get_phone_id(phone_number)

        try:
            conn = self.get_connect()
            cur = conn.cursor()

            sql = (
                "INSERT INTO `management_devicelog`"
                "(data_time, device_id_id, action, ip, phone_number_id)"
                "VALUES (%s, %s, %s, %s, %s)"
            )
            cur.execute(sql, (datetime.datetime.utcnow(), device_id_id, action, ip, phone_number_id))
            conn.commit()

            cur.close()
            conn.close()
        except Exception as err:
            print("[ {} ]: ERROR: {}".format(datetime.datetime.now(), err))

dao = Dao()
mongo_dao = MongoDao()

# if __name__ == '__main__':
    # mongo_dao.user_table.insert_one({'phone_number': '18300864707', 'password': sha256('123456'), 'comment': '测试用户'})
    # ret = mongo_dao.login('18300864707', '123456')
    # print(ret)
    # device_log('999', 0, '127.0.0.1', '18300864707')
    # cur = connector.cursor()
    # sql = (
    #     "SELECT `id`"
    #     "FROM `management_device`"
    #     "WHERE `device_id`=%s"
    # )
    # cur.execute(sql, ('999',))
    # phone_number_id = cur.fetchone()[0]
    # print(phone_number_id)
