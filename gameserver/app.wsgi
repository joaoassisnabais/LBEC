import sys
import os
CWD = os.path.dirname(__file__)

sys.path.insert(0, CWD)


activate_this = os.path.join(CWD, "virtualenv", "bin", "activate_this.py")

with open(activate_this) as f:
	exec(f.read(), dict(__file__=activate_this))


from app import app as application
