import datetime

from .dao import dao, mongo_dao

def data_insertion(data):
    # data['data_time'] = datetime.datetime.now()
    data['data_time'] = datetime.datetime.now()

    mongo_dao.insert_data(data)

def auth_login(device_id, phone_number, password, ip):
    if mongo_dao.login(phone_number, password):
        mongo_dao.device_log(device_id, 1, ip, phone_number)
        return "OK"
    else:
        mongo_dao.device_log(device_id, 2, ip, phone_number)
        return "ER"


# if __name__ == '__main__':
#     data = {
#         'frequency_value': 222.2333,
#         'device_id': '999',
#         'voltage_value': '123.2333',
#         'current_value': '123.2333',
#         'active_power_value': '123.2333',
#         'total_active_power_value': '123.2333',
#         'power_factor_value': '123.2333',
#         'switch_status': '1',
#         'co2_emission_value': '123.2333',
#     }
#     data_insertion(data)