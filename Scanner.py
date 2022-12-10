import csv
import threading
# from multiprocessing import Process
import time
from typing import List
import struct
import socket
import ipaddress
import schedule
from DataBase import DataBase
from datetime import datetime
from datetime import timedelta
import ssl_check


class Scanner:
    def __init__(self, db: DataBase, bot):
        self.__bot = bot
        self.__db = db
        self.__update_conf()
        self.__update = False

    def __update_conf(self):
        self.__conf = self.__db.get_conf()
        dt = str(self.__conf['next_scan'])
        self.__next_scan = datetime(int(dt[0:4]), int(dt[4:6]), int(dt[6:8]), int(dt[8:10]), int(dt[10:]))
        self.__scandelta = timedelta(hours=self.__conf['scandelta'])
        ip = self.__conf['ip']
        if ip == "csv":
            out = Scanner.rafip_to_iplist(Scanner.read_csv("iplist.csv"))
        else:
            out = Scanner.rafip_to_iplist([ip])
        self.__ips = out
        self.__check_centers = self.__db.get_sign_center_list()
        if self.__conf["checkdate"] != "":
            dt = self.__conf['checkdate']
            self.__check_date = datetime(int(dt[0:4]), int(dt[4:6]), int(dt[6:8]), int(dt[8:10]), int(dt[10:]))
        self.__portb = int(self.__conf['port'].split('-')[0])
        self.__porte = int(self.__conf['port'].split('-')[1])

    def scan(self, flag=False):
        lists = []
        if flag:
            self.__next_scan += self.__scandelta
            self.__db.set_conf(next_scan=str(self.__next_scan).replace("-", "").replace(" ", "").replace(":", "")[:-2])
        if self.__update:
            return schedule.CancelJob
        id = self.__db.make_scan()
        for ip in self.__ips:
            for port in range(self.__portb, self.__porte + 1):
                verdict = ""
                liste = []
                domain_chain = ssl_check.cert_domain_info(ip, port)
                if not self.__conf["ignore1y"]:
                    liste.append(ssl_check.is_valid_period_too_long(domain_chain))
                    verdict += liste[-1] + "; "
                if not self.__conf["ignorekl"]:
                    liste.append(ssl_check.is_public_key_length_enough(domain_chain))
                    verdict += liste[-1] + "; "
                if not self.__conf["ignorenvc"]:
                    liste.append(ssl_check.is_certified_by_trusted_root_certification_authority(self.__check_centers,
                                                                                                domain_chain))
                    verdict += liste[-1] + "; "
                if not self.__conf["ignoreexc"]:
                    liste.append(ssl_check.is_valid_period_exceeded(domain_chain))
                    verdict += liste[-1] + "; "
                if not self.__conf["ignorealgo"]:
                    liste.append(ssl_check.is_encription_algorithm_unreliable(domain_chain))
                    verdict += liste[-1] + "; "
                if self.__conf["checkcenter"] != "":
                    liste.append(ssl_check.is_certificate_issued_by_specific_CA(self.__conf["checkCenter"],
                                                                                domain_chain))
                    verdict += liste[-1] + "; "
                if self.__conf["checkdate"] != "":
                    liste.append(ssl_check.is_valid_period_ends_before_specified_date(self.__check_date,
                                                                                      domain_chain))
                    verdict += liste[-1]

                self.__db.insert_cert(id, verdict, domain_chain[0]["Алгоритм шифрования"],
                                      domain_chain[0]['Серийный номер'], domain_chain[0]['Хэш имени субъекта'],
                                      domain_chain[0]['Длинна открытого ключа'], domain_chain[0]["Кому выдан"],
                                      domain_chain[0]["Кем выдан"], domain_chain[0]["Действует до"])
                lists.append([ip, *liste, domain_chain[0]["Алгоритм шифрования"],
                              domain_chain[0]['Серийный номер'], domain_chain[0]['Хэш имени субъекта'],
                              domain_chain[0]['Длинна открытого ключа'], domain_chain[0]["Кому выдан"],
                              domain_chain[0]["Кем выдан"], domain_chain[0]["Действует до"]])
        Scanner.write_csv(lists)
        threading.Thread(target=self.__bot.broadcast_file.start, args="report.csv").start()
        # Process(target=self.__bot.broadcast_file.start, args=("report.csv")).start()
        return schedule.CancelJob if self.__update else None

    def update(self):
        self.__update = True

    def run(self):
        self.__next_scan += self.__scandelta
        self.__db.set_conf(next_scan=str(self.__next_scan).replace("-", "").replace(" ", "").replace(":", "")[:-2])
        print(str(self.__next_scan).replace("-", "").replace(" ", "").replace(":", "")[:-2])
        while True:
            schedule.every(self.__scandelta.seconds // 3600).hours.do(self.scan, flag=True)
            self.__update = False
            while True:
                schedule.run_pending()
                time.sleep(1)

    @staticmethod
    def read_csv(path):
        with open(path, newline='', mode='r') as csvfile:
            spamreader = csv.reader(csvfile, dialect='excel')
            out = [i[0] for i in spamreader]
            return out

    @staticmethod
    def write_csv(list):
        with open('report.csv', 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, dialect='excel', delimiter=';')
            for i in list:
                spamwriter.writerow(i)

    @staticmethod
    def rafip_to_iplist(l: List[str]):
        out = []
        for i in l:
            if i.count("/") == 1:
                out += Scanner.mask_to_list(i)
                continue
            if i.count("/-") == 1:
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


# if __name__ == "__main__":
#     sc = Scanner(DataBase())
#     sc.scan()
