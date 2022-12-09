import csv
from typing import List
import struct
import socket
import ipaddress
from DataBase import DataBase

class Scanner:
    def read_csv(self, path):
        with open(path, newline='', mode='r') as csvfile:
            spamreader = csv.reader(csvfile, dialect='excel')
            out = [i[0] for i in spamreader]
            return out

    def rafip_to_iplist(self, l: List[str]):
        out = []
        for i in l:
            if i.count("/") == 1:
                out += self.mask_to_list(i)
                continue
            if i.count("-") == 1:
                out += self.diap_to_list(i)
                continue
            out.append(i)
        return out

    def mask_to_list(self, ipm):
        return [str(ip) for ip in ipaddress.IPv4Network(ipm)]

    def diap_to_list(self, ipd):
        out = []
        beg, end = ipd.split("-")
        for j in range(self.__ip2int(beg), self.__ip2int(end) + 1):
            out.append(self.__int2ip(j))
        return out

    def __ip2int(self, addr):
        return struct.unpack("!I", socket.inet_aton(addr))[0]

    def __int2ip(self, addr):
        return socket.inet_ntoa(struct.pack("!I", addr))


if __name__ == "__main__":
    s = Scanner()
    f = s.read_csv("iplist.csv")
    print(s.rafip_to_iplist(f))
