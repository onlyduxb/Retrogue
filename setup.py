"""Setup file."""

# Imports

import os
import subprocess
import sys
if __name__ == '__main__':
    python = sys.executable
    subprocess.check_call([python, "-m", "venv", ".venv"])

    if os.name == "nt":
        pip_path = os.path.join(".venv", "Scripts", "pip.exe")
    else:
        pip_path = os.path.join(".venv", "bin", "pip")

    subprocess.check_call([pip_path, "install", "--upgrade", "pip"])
    subprocess.check_call([pip_path, "install", "-r", "requirements.txt"])