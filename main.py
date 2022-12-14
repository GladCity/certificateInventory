import argparse
import threading
# from multiprocessing import Process
from telegrambot import telegram
from DataBase import DataBase
from Scanner import Scanner
import datetime


def main():
    parser = argparse.ArgumentParser(
        description='This application is designed to periodically scan services running'
                    ' over the HTTPS protocol and verify their certificates')
    parser.add_argument('-i', '--ip', type=str, default="csv",
                        help="IP addresses: x.x.x.x/-x.x.x.x or x.x.x.x/mask or csv default=csv")
    parser.add_argument('-p', '--port', type=str, default="443-443", help="Ports for scan default=443-443")
    parser.add_argument('-I', '--interval', type=int, default=24, help="Scan interval in hours default=24")
    parser.add_argument('-t', '--token', type=str, default="5894305427:AAE03pvAh-6u9p3nftQzYHlyx5E2Ra9GekM",
                        help="Telegram bot token")
    parser.add_argument('-C', '--checkCenter', type=str, default="", help="Specify your certification authority")
    parser.add_argument('-D', '--checkDate', type=str, default="",
                        help="Output valid certificates up to a certain date (YYYYMMDDHHMM)")
    parser.add_argument('-y', '--i1Y', help='Do not allocate certificates issued for more than a year',
                        action='store_true')
    parser.add_argument('-k', '--iKL', help='Do not allocate certificates with a small key length', action='store_true')
    parser.add_argument('-n', '--iNVC', help='Do not allocate self-signed certificates', action='store_true')
    parser.add_argument('-e', '--iExc', help='Do not allocate expired certificates', action='store_true')
    parser.add_argument('-a', '--iAlg', help='Do not allocate certificates with outdated algorithms',
                        action='store_true')
    parser.add_argument('-l', '--last', help='Run the latest configuration', action='store_true')
    prs = parser.parse_args()
    db = DataBase()

    db.set_conf(
        next_scan=str(datetime.datetime.now()).split('.')[0].replace("-", "").replace(" ", "").replace(":", "")[:-2])
    if not prs.last:
        db.set_conf(str(datetime.datetime.now()).split('.')[0].replace("-", "").replace(" ", "").replace(":", "")[:-2],
                    prs.interval, prs.ip, prs.port, prs.i1Y, prs.iKL, prs.iNVC,
                    prs.iExc, prs.iAlg, prs.checkCenter, prs.checkDate)

    bot = telegram(prs.token, db)
    scanner = Scanner(db, bot)
    bot.scan = scanner

    t1 = threading.Thread(target=scanner.run)
    # t1 = Process(target=scanner.run)
    t2 = threading.Thread(target=bot.bot_start)
    # t2 = Process(target=bot.bot_start)
    t1.start()
    t2.start()


if __name__ == '__main__':
    main()
