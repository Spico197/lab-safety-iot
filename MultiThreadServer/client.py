"""
非阻塞式的测试客户端（参数命令行）

usage: client.py [-h] [-t THREADS] [-d DEVICE_ID] host port

positional arguments:
  host                  host ip
  port                  host port

optional arguments:
  -h, --help            show this help message and exit
  -t THREADS, --threads THREADS
                        thread number
  -d DEVICE_ID, --device_id DEVICE_ID
                        设备号，需指定线程数为1时方可使用，内置999和888两个设备
"""
__author__ = "spico1026@gmail.com"

import socket
import threading
import time
import select
import re
import random
import struct
import argparse


class WorkThread(threading.Thread):
    """主工作线程"""
    def __init__(self, sock, param):
        super().__init__()
        self.sock = sock
        self.sock.setblocking(True)
        self.param = param
        self.device_id = param['device_id']
        self.phone_number = param['phone_number']
        self.password = param['password']

    def int2hex(self, int_val):
        """
        把int类型的值转为4字节bytes类型，方便发送
        :param int_val: 输入值
        :return: bytes类型数据
        """
        byte = struct.pack('@i', int_val)
        ret = list(byte)
        ret.reverse()
        return bytes(ret)

    def run(self):
        """
        工作开始线程
        :return: None
        """
        while True:
            ready = select.select([], [self.sock], [], 2)
            if ready[1]:
                print('{} - START:{}{}{}'
                    .format(self.getName(), self.device_id, self.phone_number, self.password))
                self.sock.sendall('START:{}{}{}'
                    .format(self.device_id, self.phone_number, self.password).encode())
                break
        while True:
            ready = select.select([self.sock], [], [], 2)
            if ready[0]:
                return_data = self.sock.recv(1024).decode()
                print("{} - RECV: {}".format(self.getName(), return_data))
                break
        match_obj = re.match(r'START:(\d{3})(OK|ER)ACK', return_data)
        if match_obj:
            if match_obj.group(1) == self.device_id:
                if match_obj.group(2) == "OK":
                    print(return_data)

                    # 启动心跳包相应线程
                    heart_thread = HeartThread(self.sock, self.param)
                    heart_thread.start()

                    while True:
                        # 构造测试数据
                        time.sleep(random.randint(1, 5))
                        frame_head = bytes([0x5A, 0xA5, 0x3C, 0xC3]) + self.device_id.encode()
                        voltage_value = self.int2hex(random.randint(0, 2500000))
                        current_value = self.int2hex(random.randint(0, 50000))
                        active_power_value = self.int2hex(random.randint(0, 100000000))
                        total_active_power_value = self.int2hex(random.randint(0, 1000000))
                        power_factor_value = self.int2hex(random.randint(0, 2500000))
                        co2_emission_value = self.int2hex(random.randint(0, 2500000))
                        frequency_value = self.int2hex(random.randint(0, 2500000))
                        frame = frame_head + voltage_value + current_value + active_power_value\
                                + total_active_power_value + power_factor_value + co2_emission_value\
                                + frequency_value + bytes([0x11])
                        self.sock.sendall(frame)
                        # print(len(frame))
                        # ready = select.select([], [self.sock], [], 2)
                        # if ready[1]:
                        #     self.sock.sendall(frame)

                        # # 输入‘q’即可退出客户端
                        # _ = input()
                        # if _ == "q":
                        #     break


class HeartThread(threading.Thread):
    """心跳线程"""
    def __init__(self, sock, param):
        super().__init__()
        self.sock = sock
        self.sock.setblocking(False)
        self.device_id = param['device_id']
        self.phone_number = param['phone_number']
        self.password = param['password']

    def run(self):
        while True:
            ready = select.select([self.sock], [], [])
            if ready[0]:
                heart_string = self.sock.recv(1024).decode()
                print("HEART RECV: {}".format(heart_string))
                match_obj = re.match(r'(\d{3}):HEART\?', heart_string)
                if match_obj:
                    if match_obj.group(1) == self.device_id:
                        while True:
                            ready = select.select([], [self.sock], [])
                            if ready[1]:
                                self.sock.sendall("HEART:{}".format(self.device_id).encode())
                                print("HEART SEND: {}".format("HEART:{}".format(self.device_id)))
                                break
                            else:
                                continue
                    else:
                        print("device_id not matched")
                else:
                    print('not heart package {}'.format(heart_string))
            else:
                continue


param1 = dict(
    device_id = '999',
    phone_number = '18300864707',
    password = '123456'
)
param2 = dict(
    device_id = '888',
    phone_number = '11011101110',
    password = '123456'
)

def thread1(host, port):
    client1 = socket.socket()
    client1.connect_ex((host, port))
    client1.setblocking(False)

    work_thread1 = WorkThread(client1, param1)
    work_thread1.start()

def thread2(host, port):
    client2 = socket.socket()
    client2.connect_ex((host, port))
    client2.setblocking(False)

    work_thread2 = WorkThread(client2, param2)
    work_thread2.start()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="host ip", default='127.0.0.1')
    parser.add_argument("port", help="host port", default=65432, type=int)
    parser.add_argument('-t', '--threads', help='thread number', default=1, type=int)
    parser.add_argument('-d', '--device_id', help='device_id', default='999')
    args = parser.parse_args()

    if args.threads == 1:
        if args.device_id == '999':
            thread1(args.host, args.port)
        else:
            thread2(args.host, args.port)
    elif args.threads == 2:
        thread1(args.host, args.port)
        # time.sleep(2)
        thread2(args.host, args.port)
    else:
        for i in range(args.threads):
            time.sleep(1)
            thread1(args.host, args.port)
