import argparse


def main():
    parser = argparse.ArgumentParser(description='scanner')
    parser.add_argument('-i', '--ip', type=str, default="csv", help="IP addresses: x.x.x.x-x.x.x.x or x.x.x.x/mask "
                                                                    "or csv:path to csv default=csv")
    parser.add_argument('-p', '--port', type=str, default="443-443", help="ports for scan default=443-443")
    parser.add_argument('-I', '--interval', type=int, default=24, help="scan interval in hours default=24")
    parser.add_argument('-I', '--interval', type=int, default=24, help="scan interval in hours default=24")
    parser.add_argument('ScanDateTime', type=str, help='date and time of the first scan (DD.MM.YY_HH:MM)')
    parser.add_argument('-t', '--token', type=str, default="5894305427:AAE03pvAh-6u9p3nftQzYHlyx5E2Ra9GekM",
                        help="telegram bot token")
    my_namespace = parser.parse_args()


if __name__ == '__main__':
    main()
