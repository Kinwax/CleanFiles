# -*- coding: gbk -*-

import os
import sys
import subprocess

# 使用PyInstaller编译Python脚本
subprocess.run(["pyinstaller", "--onefile","--icon=cfs.ico","--clean","CleanFiles.py"])