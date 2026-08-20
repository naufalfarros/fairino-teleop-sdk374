#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
====================================================================
FAIRINO COBOT FR5 / FR10 TELEOPERATION CLI (Python SDK v3.7.4)
====================================================================
Script teleoperasi independen dan portabel untuk kontrol manual cobot.
Dapat dijalankan di komputer/device manapun tanpa dependensi eksternal.
"""

import sys
import os
import time
import select

# Memastikan package SDK lokal 'fairino' terdeteksi
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

try:
    from fairino import RPC
    from config import DEFAULT_ROBOT_IP, DEFAULT_JOG_VEL, DEFAULT_JOG_ACC, DEFAULT_STEP_DIS
except ImportError as e:
    print(f"[ERROR] Gagal mengimpor SDK Fairino: {e}")
    sys.exit(1)

# Platform check untuk termios (Linux/macOS)
IS_POSIX = os.name == 'posix'
if IS_POSIX:
    import termios
    import tty


def get_key_posix():
    """Membaca 1 tombol dari stdin tanpa blocking (Linux/macOS)"""
    rlist, _, _ = select.select([sys.stdin], [], [], 0.02)
    if rlist:
        return sys.stdin.read(1)
    return ''


def print_dashboard(robot, active_axis, frame_mode, step_size, vel, is_enabled, is_drag):
    """Menampilkan telemetry & dashboard status robot di terminal"""
    # Ambil Posisi Sendi
    res_j = robot.GetActualJointPosDegree()
    err_j, joints = (res_j[0], list(res_j[1:7])) if (isinstance(res_j, (tuple, list)) and len(res_j) == 2) else (-1, [0.0]*6)

    # Ambil Kode Error
    res_e = robot.GetRobotErrorCode()
    err_e, codes = (res_e[0], res_e[1]) if (isinstance(res_e, (tuple, list)) and len(res_e) == 2) else (-1, [0, 0])
    main_code = codes[0] if isinstance(codes, (list, tuple)) and len(codes) >= 1 else 0
    sub_code = codes[1] if isinstance(codes, (list, tuple)) and len(codes) >= 2 else 0

    # Ambil Status E-Stop
    res_s = robot.GetRobotEmergencyStopState()
    err_s, estop = (res_s[0], res_s[1]) if (isinstance(res_s, (tuple, list)) and len(res_s) == 2) else (-1, 0)

    # Ambil TCP Pose
    res_p = robot.GetActualTCPPose()
    err_p, pose = (res_p[0], list(res_p[1:7])) if (isinstance(res_p, (tuple, list)) and len(res_p) == 2) else (-1, [0.0]*6)

    # Clear Terminal
    print("\033[H\033[J", end="")
    print("==================================================================")
    print("      TELEOPERASI MANUAL COBOT FAIRINO FR5 (SDK v3.7.4)           ")
    print("==================================================================")

    if err_j == 0:
        estop_str = "🛑 AKTIF (EMERGENCY STOP)" if estop == 1 else "✅ Normal"
        enable_str = "🟢 ON (POWERED)" if is_enabled == 1 else "🔴 OFF (DISABLED)"
        drag_str = "🤝 AKTIF (DRAG TEACH)" if is_drag == 1 else " Off"
        err_str = f"Main: {main_code}, Sub: {sub_code}" if (main_code != 0 or sub_code != 0) else "Tidak Ada Error"

        print(f" [STATUS] Power: {enable_str} | E-Stop: {estop_str} | Drag: {drag_str}")
        print(f" [ALARM ] {err_str}")
        print("------------------------------------------------------------------")
        print(f" [MODE  ] Frame: {frame_mode.upper()} | Sumbu Aktif: Axis {active_axis}")
        print(" [SENDI (DEGREE)]")
        for i in range(6):
            mark = "👉" if (i + 1) == active_axis and frame_mode == "joint" else "  "
            print(f"   {mark} Joint {i+1}: {joints[i]:8.3f}°")
        print("------------------------------------------------------------------")
        if err_p == 0:
            labels = ["X", "Y", "Z", "Rx", "Ry", "Rz"]
            print(" [TCP POSE (MM / DEG)]")
            pose_str = " | ".join([f"{labels[i]}:{pose[i]:.1f}" for i in range(6)])
            print(f"   {pose_str}")
        print("------------------------------------------------------------------")
        print(" [KONTROL KEYBOARD]")
        print(f"   [1]..[6]  : Pilih Joint / Cartesian Axis (Aktif: Axis {active_axis})")
        print(f"   [m]       : Switch Mode (Joint Space ↔ Cartesian Space)")
        print(f"   [u] / [+] : Jog Arah Positif (+)")
        print(f"   [i] / [-] : Jog Arah Negatif (-)")
        print(f"   [d]       : Toggle Drag Teaching Mode (Hand Guiding)")
        print(f"   [e]       : Toggle Servo Power Enable (ON/OFF)")
        print(f"   [r]       : Reset Alarm / Recover Error Robot")
        print(f"   [,] / [.] : Kecepatan Jog: {vel:.1f}%")
        print(f"   [SPACE]/[s]: STOP SEMENTARA SEMUA GERAKAN")
        print(f"   [q]       : Keluar Teleoperasi")
        print("==================================================================")
    else:
        print(f" [ERROR] Tidak dapat membaca telemetry dari robot (Code: {err_j})")


def main():
    robot_ip = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ROBOT_IP
    print(f" Connecting to Fairino Cobot at IP {robot_ip}...")

    try:
        robot = RPC(robot_ip)
        time.sleep(0.5)
    except Exception as exc:
        print(f"[FATAL] Gagal menginisialisasi RPC ke {robot_ip}: {exc}")
        sys.exit(1)

    # Verifikasi koneksi awal
    res_j = robot.GetActualJointPosDegree()
    if not isinstance(res_j, (tuple, list)) or res_j[0] != 0:
        err_code = res_j if isinstance(res_j, int) else (res_j[0] if isinstance(res_j, (tuple, list)) else -1)
        print(f"\n[ERROR] Gagal terhubung ke robot di IP {robot_ip} (ErrCode: {err_code}).")
        print("[HINT] Pastikan robot atau simulator simmachine aktif dan IP berada di subnet yang sama.")
        return

    print("[INFO] Mereset alarm, mengaktifkan Manual Mode & Servo Power...")
    is_enabled = 1
    is_drag = 0
    try:
        robot.ResetAllError()
        time.sleep(0.2)
        robot.Mode(1)         # Manual Mode
        time.sleep(0.2)
        robot.RobotEnable(1)  # Enable Servo Power
        is_enabled = 1
    except Exception as exc:
        print(f"[WARN] Inisialisasi awal robot: {exc}")

    # Teleop Configuration
    active_axis = 1      # 1..6
    frame_mode = "joint" # "joint" atau "cart"
    step_size = DEFAULT_STEP_DIS
    vel = DEFAULT_JOG_VEL
    acc = DEFAULT_JOG_ACC

    # Set terminal mode untuk Linux
    old_settings = None
    if IS_POSIX and sys.stdin.isatty():
        old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())

    try:
        last_update = 0
        running = True

        while running:
            now = time.time()
            if now - last_update > 0.15:  # Refresh Rate ~6.6Hz
                print_dashboard(robot, active_axis, frame_mode, step_size, vel, is_enabled, is_drag)
                last_update = now

            key = get_key_posix() if (IS_POSIX and sys.stdin.isatty()) else ''
            if not key:
                time.sleep(0.02)
                continue

            if key in ['1', '2', '3', '4', '5', '6']:
                active_axis = int(key)
            elif key == 'm':
                frame_mode = "cart" if frame_mode == "joint" else "joint"
            elif key in ['u', '+']:
                ref_type = 0 if frame_mode == "joint" else 1
                robot.StartJOG(ref_type, active_axis, 1, step_size, vel)
            elif key in ['i', '-']:
                ref_type = 0 if frame_mode == "joint" else 1
                robot.StartJOG(ref_type, active_axis, 0, step_size, vel)
            elif key == 'd':
                is_drag = 0 if is_drag == 1 else 1
                if is_drag == 1:
                    robot.StartDragTeach()
                else:
                    robot.StopDragTeach()
            elif key == 'e':
                is_enabled = 0 if is_enabled == 1 else 1
                robot.RobotEnable(is_enabled)
            elif key == 'r':
                robot.ResetAllError()
                time.sleep(0.2)
                robot.Mode(1)
                time.sleep(0.2)
                robot.RobotEnable(1)
                is_enabled = 1
            elif key in [' ', 's', 'S']:
                robot.ImmStopJOG()
            elif key == ',':
                vel = max(5.0, vel - 5.0)
            elif key == '.':
                vel = min(100.0, vel + 5.0)
            elif key in ['q', '\x03']:  # 'q' or Ctrl+C
                robot.ImmStopJOG()
                if is_drag == 1:
                    robot.StopDragTeach()
                running = False

    except Exception as exc:
        print(f"\n[ERROR] Terjadi kesalahan saat teleoperasi: {exc}")
    finally:
        if old_settings and sys.stdin.isatty():
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        print("\n[TELEOP] Sesi teleoperasi selesai. Robot dihentikan secara aman.")


if __name__ == "__main__":
    main()
