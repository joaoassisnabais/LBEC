import subprocess
import os
CWD = os.path.dirname(__file__)
schema_path = os.path.join(CWD, "sql", "schema.sql")
populate_path = os.path.join(CWD, "sql", "populate.sql")

subprocess.run(["psql", "-U", "nabais", "-d", "home", "-a", "-f", schema_path])
subprocess.run(["psql", "-U", "nabais", "-d", "home", "-a", "-f", populate_path])
