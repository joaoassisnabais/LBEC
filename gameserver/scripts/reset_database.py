import subprocess
import os
CWD = os.path.dirname(__file__)
schema_path = os.path.join(CWD, "sql", "schema.sql")
populate_path = os.path.join(CWD, "sql", "populate.sql")

subprocess.run(["psql", "-U", "rui", "-d", "game", "-a", "-f", schema_path])
subprocess.run(["psql", "-U", "rui", "-d", "game", "-a", "-f", populate_path])
