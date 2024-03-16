import os
from datetime import datetime

CWD = os.path.dirname(__file__)

LOGFILE = os.path.join(CWD, "logs", "out.log")
def log(message):
    message = str(message)
    print(message)
    with open(LOGFILE, "a") as f:
        f.write(datetime.now().strftime("[%a %b %d %H:%M:%S.%f %Y] ") + message + "\n")
