# -*- coding: gbk -*-

import os
import sys
import subprocess

# ʹ��PyInstaller����Python�ű�
subprocess.run(["pyinstaller", "--onefile","--icon=cfs.ico","--clean","CleanFiles.py"])