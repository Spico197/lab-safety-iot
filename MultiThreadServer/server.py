"""
阻塞式的服务端
"""
__author__ = "spico1026@gmail.com"

import socket
import threading
# import selectors
# import select
import time
import datetime
import re
import logging


from database.service import auth_login, data_insertion
from database.dao import dao, mongo_dao


logging.basicConfig(filename="routine-log.txt",
                    filemode="a",
                    format='%(asctime)s - %(levelname)s - %(message)s')

def get_native_time():
    return datetime.datetime.now()


class StuckHeartThread(threading.Thread):
    """
    阻塞式心跳线程

    Attrs：
        work_thread_name: 父线程名
        client: 连接到的客户端socket
        device_id: 设备号
        heart_time: 心跳时间
        address: 客户端地址
    """
    def __init__(self, work_thread_name):
        """
        线程初始化
        :param work_thread_name: 父线程名，可由父线程通过getName()方法得到
        """
        super(StuckHeartThread, self).__init__()
        self.work_thread_name = work_thread_name
        self.client = thread_names[work_thread_name]['client']
        self.device_id = thread_names[work_thread_name]['device_id']
        self.heart_time = thread_names[work_thread_name]['heart_time']
        self.address = thread_names[work_thread_name]['address']

    def refresh_thread_names(self):
        """
        刷新全局变量 thread_names
        :return None:
        """
        self.client = thread_names[self.work_thread_name]['client']
        self.device_id = thread_names[self.work_thread_name]['device_id']
        self.heart_time = thread_names[self.work_thread_name]['heart_time']
        self.address = thread_names[self.work_thread_name]['address']

    def get_flag(self):
        """
        获得当前线程的心跳运行状态
        :return: str 心跳状态
        """
        return thread_names[self.work_thread_name]['flag']

    def set_flag(self, flag):
        """
        设置心跳状态
        :param flag: 状态: 'dead': 向客户端发送心跳包后客户端未回应;
                           'wait': 等待客户端设备向服务器发送心跳回应;
                           'clear': 客户端正常运行
        :return: None
        """
        thread_names[self.work_thread_name]['flag'] = flag

    def run(self):
        """
        线程运行函数

        每隔self.heart_time秒的时间就判断当前客户端的心跳状态,
        如果是'clear', 则发送心跳包, 并标记状态为'wait'等待客户端回应;
        如果是'wait', 则认为上一个心跳包发送之后客户端未能回应, 致使父线程未清除标志, 将标志置为'dead', 结束心跳线程;
        如果标志位为dead, 则结束心跳线程, 默认客户端即将断线.

        :return: None
        """
        self.refresh_thread_names()
        while True:
            time.sleep(self.heart_time)

            if self.get_flag() == 'clear':
                try:
                    self.client.sendall("{}:HEART?".format(self.device_id).encode())
                    # print("[ {} ]: {} {}:HEART?".format(get_native_time(), self.address, self.device_id))
                    logging.info("HEART THREAD: work_thread_name: {}, device_id: {}, heart_time: {}, address: {} - {}"
                                 .format(self.work_thread_name, self.device_id, self.heart_time, self.address, "HEART?"))
                except socket.timeout:
                    # print("[ {} ]: device: {} heart package cannot be sent"
                    #       .format(get_native_time(), self.device_id))
                    logging.error("HEART THREAD: work_thread_name: {}, device_id: {}, heart_time: {}, address: {} - {}"
                                  .format(self.work_thread_name, self.device_id,
                                          self.heart_time, self.address, "heart package cannot be sent"))
                except ConnectionError as err:
                    print("[ {} ]: device: {} connection error"
                          .format(get_native_time(), self.address))
                    self.set_flag('dead')
                    logging.error("HEART THREAD: work_thread_name: {}, device_id: {}, heart_time: {}, address: {} - {}"
                                  .format(self.work_thread_name, self.device_id,
                                          self.heart_time, self.address, "connection error"))
                    break
                except OSError as err:
                    if isinstance(err, socket.timeout):
                        raise socket.timeout
                    else:
                        print("[ {} ]: device: {} OSError"
                              .format(get_native_time(), self.address))
                        self.set_flag('dead')
                        logging.error("HEART THREAD: work_thread_name: {}, device_id: {}, heart_time: {}, address: {} - {}"
                                      .format(self.work_thread_name, self.device_id,
                                              self.heart_time, self.address, "OSError"))
                        break
                finally:
                    self.set_flag('wait')
            elif self.get_flag() == 'wait':
                self.set_flag('dead')
                break
            else:
                break


class StuckThread(threading.Thread):
    """
    阻塞式工作线程

    Attr:
        client: 客户端socket
        address: 客户端socket地址
        device_id: 客户端的设备号
        phone_number: 客户端登录的手机号
        password: 客户端用户密码
        heart_time: 心跳间隔时间
    """
    def __init__(self, client, address, timeout, wait_time):
        super(StuckThread, self).__init__()
        self.client = client
        self.client.settimeout(wait_time) # 客户端阻塞等待响应的时间
        self.address = address
        self.device_id = ""
        self.phone_number = ""
        self.password = ""
        self.heart_time = timeout

        # 更新全局dict
        thread_names[self.getName()] = {'client': self.client, 'address': self.address,
                                        'heart_time': self.heart_time, 'device_id': '',
                                        'flag': 'clear'}

    def sendall(self, data):
        """
        对客户端socket sendall函数的封装
        :param data: 待发送的数据
        :return: None
        """
        try:
            self.client.sendall(data)
        except ConnectionError as err:
            print("[ {} ]: device: {} connection error"
                  .format(get_native_time(), self.address))
            logging.error(
                "WORK THREAD: work_thread_name: {}, device_id: {}, heart_time: {}, address: {}, phone_number: {} - {}"
                  .format(self.getName(), self.device_id,
                          self.heart_time, self.address, self.phone_number, "send connection error"))
            self.close()
        except OSError as err:
            if isinstance(err, socket.timeout):
                raise socket.timeout
            else:
                print("[ {} ]: device: {} send os error"
                      .format(get_native_time(), self.address))
                logging.error(
                    "WORK THREAD: work_thread_name: {}, device_id: {}, heart_time: {}, address: {}, phone_number: {} - {}"
                        .format(self.getName(), self.device_id,
                                self.heart_time, self.address, self.phone_number, "send os error"))
                self.close()

    def recv(self, buffer_size=1024):
        """
        对客户端socket recv函数的封装
        :param buffer_size: 接收缓冲区大小，默认为1024
        :return: 接收到的数据内容
        """
        try:
            return self.client.recv(buffer_size)
        except ConnectionError as err:
            print("[ {} ]: device: {} connection error"
                  .format(get_native_time(), self.address))
            logging.error(
                "WORK THREAD: work_thread_name: {}, device_id: {}, heart_time: {}, address: {}, phone_number: {} - {}"
                .format(self.getName(), self.device_id,
                        self.heart_time, self.address, self.phone_number, "recv connection error"))
            self.close()
        except OSError as err:
            if isinstance(err, socket.timeout):
                raise socket.timeout
            else:
                print("[ {} ]: device: {} recv os error"
                      .format(get_native_time(), self.address))
                logging.error(
                    "WORK THREAD: work_thread_name: {}, device_id: {}, heart_time: {}, address: {}, phone_number: {} - {}"
                        .format(self.getName(), self.device_id,
                                self.heart_time, self.address, self.phone_number, "recv os error"))
                self.close()

    def close(self):
        """
        关闭客户端连接
        :return: None
        """
        if self.client in clients:
            clients.remove(self.client)
        print("number of clients: {}".format(len(clients)))
        logging.info(
            "WORK THREAD: work_thread_name: {}, device_id: {}, heart_time: {}, address: {}, phone_number: {} - {}"
            .format(self.getName(), self.device_id, self.heart_time, self.address, self.phone_number, "close client"))
        mongo_dao.device_log(self.device_id, 0, self.address[0]+':'+str(self.address[1]), self.phone_number)
        if self.client._closed is False:
            self.client.close()

    def get_flag(self):
        """
        获得线程工作标志
        :return: None
        """
        return thread_names[self.getName()].get('flag', 'clear')

    def set_flag(self, flag):
        """
        设置线程工作标志
        :param flag: 'dead': 向客户端发送心跳包后客户端未回应;
                     'wait': 等待客户端设备向服务器发送心跳回应;
                     'clear': 客户端正常运行
        :return: None
        """
        thread_names[self.getName()]['flag'] = flag

    def _insert_data(self, data):
        """
        向数据表中插入设备上传的数据
        :param data: bytes类型, 待上传的数据
        :return: None
        """
        if data[0: 4].hex() == '5aa53cc3':
            device_id_from_data = data[4: 7].decode()
            switch_status = True if data[-1] == 0x11 else False
            voltage_value = int(data[7: 11].hex(), 16) * 0.0001
            current_value = int(data[11: 15].hex(), 16) * 0.0001
            active_power_value = int(data[15: 19].hex(), 16) * 0.0001
            total_active_power_value = int(data[19: 23].hex(), 16) * 0.0001
            power_factor_value = int(data[23: 27].hex(), 16) * 0.001
            co2_emission_value = int(data[27: 31].hex(), 16) * 0.0001
            frequency_value = int(data[31: 35].hex(), 16) * 0.01

            insert_data = dict(
                device_id=device_id_from_data,
                switch_status=switch_status,
                voltage_value=voltage_value,
                current_value=current_value,
                active_power_value=active_power_value,
                total_active_power_value=total_active_power_value,
                power_factor_value=power_factor_value,
                co2_emission_value=co2_emission_value,
                frequency_value=frequency_value,
            )

            # print("[ {} ]: New data from {}".format(get_native_time(), self.address))
            data_insertion(insert_data)

    def decode_test(self, data, comment=''):
        """
        尝试将bytes数据decode为string
        :param data: 数据
        :return: decode成功，返回True；反之返回False
        """
        try:
            data.decode()
            return True
        except UnicodeDecodeError as err:
            print('[ {} ]: {} - {} DecodeError: {}'.format(get_native_time(), comment, data, err))
            logging.error(
                "WORK THREAD: work_thread_name: {}, device_id: {}, heart_time: {}, address: {}, phone_number: {} - {}"
                .format(self.getName(), self.device_id, self.heart_time, self.address,
                        self.phone_number, "{} DecodeError data: {}".format(comment, data)))
            return False

    def run(self):
        """
        线程工作函数
        :return: None
        """
        start_connect = b" "
        print("[ {} ]: Connect from {}:{}".format(get_native_time(), self.address[0], self.address[1]))
        logging.info(
            "WORK THREAD: work_thread_name: {}, device_id: {}, heart_time: {}, address: {}, phone_number: {} - {}"
                .format(self.getName(), self.device_id, self.heart_time, self.address,
                        self.phone_number, "receive connection"))
        try:
            start_connect = self.recv()
        except socket.timeout:
            print("[ {} ]: wait for {} start too long".format(get_native_time(), self.address))
            logging.error(
                "WORK THREAD: work_thread_name: {}, device_id: {}, heart_time: {}, address: {}, phone_number: {} - {}"
                    .format(self.getName(), self.device_id, self.heart_time, self.address,
                            self.phone_number, "wait for start too long"))
            self.close()
            return

        if not self.decode_test(start_connect, 'start connect'):
            self.close()
            return

        auth_return = ""
        match_obj = re.match(r'START:(\d{3})(\d{11})(\d{6})', start_connect.decode())
        if match_obj:
            self.device_id = match_obj.group(1)
            self.phone_number = match_obj.group(2)
            self.password = match_obj.group(3)

            auth_return = auth_login(self.device_id, self.phone_number,
                                     self.password, self.address[0] + ':' + str(self.address[1]))

            try:
                self.sendall("START:{}{}ACK".format(self.device_id, auth_return).encode())
            except socket.timeout:
                print("[ {} ]: {} start ack cannot be sent".format(get_native_time(), self.address))
                logging.info(
                    "WORK THREAD: work_thread_name: {}, device_id: {}, heart_time: {}, address: {}, phone_number: {} - {}"
                        .format(self.getName(), self.device_id, self.heart_time, self.address,
                                self.phone_number, "timeout: start ack cannot be sent"))
                self.close()
                return

            print("[ {} ]: START:{}{}ACK".format(get_native_time(), self.device_id, auth_return))
            logging.info(
                "WORK THREAD: work_thread_name: {}, device_id: {}, heart_time: {}, address: {}, phone_number: {} - {}"
                    .format(self.getName(), self.device_id, self.heart_time, self.address,
                            self.phone_number, "START:{}{}ACK".format(self.device_id, auth_return)))

            if auth_return != "OK":
                self.close()
                return

            thread_names[self.getName()]['device_id'] = self.device_id
            heart_thread = StuckHeartThread(self.getName())
            heart_thread.start()

            while True:
                if self.client._closed:
                    return
                try:
                    if self.get_flag() == 'dead':
                        print("[ {} ]: {} dead".format(get_native_time(), self.address))
                        logging.info(
                            "WORK THREAD: work_thread_name: {}, device_id: {}, heart_time: {}, address: {}, phone_number: {} - {}"
                                .format(self.getName(), self.device_id, self.heart_time, self.address,
                                        self.phone_number, "client dead"))
                        self.close()
                        return

                    data = b""
                    try:
                        data = self.recv(1024)
                    except socket.timeout:
                        continue

                    if len(data) == 36:
                        # print('new data')
                        self._insert_data(data)
                    else:

                        if not self.decode_test(data, 'heart data decode, length: {}'.format(len(data))):
                            continue

                        match_obj = re.match(r'HEART:(\d{3})', data.decode())
                        if match_obj:
                            if match_obj.group(1) == self.device_id:
                                if self.get_flag() == 'wait':
                                    self.set_flag('clear')
                                    # print('[ {} ]: {} HEART:{}'.format(get_native_time(), self.address, self.device_id))
                                    logging.info(
                                        "WORK THREAD: work_thread_name: {}, device_id: {}, heart_time: {}, address: {}, phone_number: {} - {}"
                                            .format(self.getName(), self.device_id, self.heart_time, self.address,
                                                    self.phone_number, "receive client heart package"))
                                elif self.get_flag() == 'dead':
                                    print("[ {} ]: {} dead".format(get_native_time(), self.address))
                                    logging.info(
                                        "WORK THREAD: work_thread_name: {}, device_id: {}, heart_time: {}, address: {}, phone_number: {} - {}"
                                            .format(self.getName(), self.device_id, self.heart_time, self.address,
                                                    self.phone_number, "client connection dead"))
                                    self.close()
                                    return
                except Exception as err:
                    # print("[ {} ]: {}".format(get_native_time(), err))
                    if self.get_flag() == 'dead':
                        print("[ {} ]: {} dead".format(get_native_time(), self.address))
                        logging.info(
                            "WORK THREAD: work_thread_name: {}, device_id: {}, heart_time: {}, address: {}, phone_number: {} - {}"
                                .format(self.getName(), self.device_id, self.heart_time, self.address,
                                        self.phone_number, "client connection dead"))
                        self.close()
                        return
                    continue

        self.close()


if __name__ == '__main__':
    # main为主线程
    ip_port = ('0.0.0.0', 65432)    # 默认监听外网地址的65432端口
    max_listen_num = 10 # 最大连接数为10
    timeout = 60    # 心跳间隔为30秒
    wait_time = 5   # 阻塞式方法等待响应时间(秒)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 面向Internet的流式套接字
    server.bind(ip_port) # 绑定地址
    server.listen(50)   # 开始监听
    print('{} Server - {}:{} Listening {}'.format('-'*20, ip_port[0], ip_port[1], '-'*20))
    logging.info('{} Server - {}:{} Listening {}'.format('-'*20, ip_port[0], ip_port[1], '-'*20))

    thread_names = {}   # 全局flag

    # server.setblocking(False)
    # while True:
    #     try:
    #         client, address = server.accept()
    #
    #         work_thread = AcceptThread(client, address, timeout)
    #         work_thread.start()
    #     except BlockingIOError:
    #         continue

    clients = []
    def  main_thread_entrance(max_listen_num, timeout, wait_time):
        while True:
            # 直到达到最大连接数为止, 不断尝试建立新的连接
            if len(clients) >= max_listen_num:
                continue

            client, address = server.accept()

            clients.append(client)
            # print("[ {} ]: number of clients: {}".format(get_native_time(), len(clients)))
            logging.info("number of clients: {}".format(len(clients)))

            stuck_thread = StuckThread(client, address, timeout, wait_time)
            stuck_thread.start()

    handle = threading.Thread(target=main_thread_entrance, args=(max_listen_num, timeout, wait_time))
    handle.start()

    while True:
        cmd = input(">>> ")
        if cmd == 'number':
            print("The number of clients: {}".format(len(clients)))
