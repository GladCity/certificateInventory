# certificateInventory

  -h, --help            show this help message and exit
  -i IP, --ip IP        IP addresses: x.x.x.x/-x.x.x.x or x.x.x.x/mask or csv
                        default=csv
  -p PORT, --port PORT  Ports for scan default=443-443
  -I INTERVAL, --interval INTERVAL
                        Scan interval in hours default=24
  -t TOKEN, --token TOKEN
                        Telegram bot token
  -C CHECKCENTER, --checkCenter CHECKCENTER
                        Specify your certification authority
  -D CHECKDATE, --checkDate CHECKDATE
                        Output valid certificates up to a certain date
                        (YYYYMMDDHHMM)
  -y, --i1Y             Do not allocate certificates issued for more than a
                        year
  -k, --iKL             Do not allocate certificates with a small key length
  -n, --iNVC            Do not allocate self-signed certificates
  -e, --iExc            Do not allocate expired certificates
  -a, --iAlg            Do not allocate certificates with outdated algorithms
  -l, --last            Run the latest configuration
  
  # Installation
  pip install schedule pyTelegramBotAPI pyOpenSSL psycopg2
  
