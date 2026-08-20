# -*- coding: utf-8 -*-
"""
Konfigurasi Default Teleoperasi Fairino Cobot FR5 / FR10
"""
import os

# IP Address controller robot (dapat di-override via environment variable ROBOT_IP)
DEFAULT_ROBOT_IP = os.environ.get("ROBOT_IP", "192.168.58.2")

# Port XML-RPC default
DEFAULT_ROBOT_PORT = int(os.environ.get("ROBOT_PORT", 20003))

# Batas Kecepatan & Akselerasi Jogging Default
DEFAULT_JOG_VEL = 20.0       # persen (1 - 100%)
DEFAULT_JOG_ACC = 50.0       # persen
DEFAULT_STEP_DIS = 5.0       # derajat / mm per langkah

# Mode robot awal
DEFAULT_MANUAL_MODE = 1      # 1 = Manual Mode, 0 = Auto Mode
DEFAULT_ENABLE_POWER = 1     # 1 = Power Servo ON, 0 = OFF
