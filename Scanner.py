import csv
from typing import List
import struct
import socket
import ipaddress
from DataBase import DataBase


class Scanner:

    def __init__(self, db: DataBase):
        self.__db = DataBase

    @staticmethod
    def read_csv(path):
        with open(path, newline='', mode='r') as csvfile:
            spamreader = csv.reader(csvfile, dialect='excel')
            out = [i[0] for i in spamreader]
            return out

    @staticmethod
    def rafip_to_iplist(l: List[str]):
        out = []
        for i in l:
            if i.count("/") == 1:
                out += Scanner.mask_to_list(i)
                continue
            if i.count("-") == 1:
                out += Scanner.diap_to_list(i)
                continue
            out.append(i)
        return out

    @staticmethod
    def mask_to_list(ipm):
        return [str(ip) for ip in ipaddress.IPv4Network(ipm)]

    @staticmethod
    def diap_to_list(ipd):
        out = []
        beg, end = ipd.split("-")
        for j in range(Scanner.__ip2int(beg), Scanner.__ip2int(end) + 1):
            out.append(Scanner.__int2ip(j))
        return out

    @staticmethod
    def __ip2int(addr):
        return struct.unpack("!I", socket.inet_aton(addr))[0]

    @staticmethod
    def __int2ip(addr):
        return socket.inet_ntoa(struct.pack("!I", addr))
