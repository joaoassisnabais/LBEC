import subprocess

subprocess.run(["git", "pull"])
subprocess.run(["sudo", "systemctl", "restart", "apache2"])
