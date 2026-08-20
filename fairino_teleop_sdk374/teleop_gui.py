#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
====================================================================
FAIRINO COBOT FR5 / FR10 TELEOPERATION GUI (Python SDK v3.7.4)
====================================================================
Aplikasi GUI Desktop sederhana berbasis Tkinter untuk kontrol manual cobot.
"""

import sys
import os
import time
import threading
try:
    import tkinter as tk
    from tkinter import ttk, messagebox
except ImportError:
    print("[ERROR] Tkinter tidak ditemukan di sistem Python ini.")
    sys.exit(1)

# Ensure local fairino package is imported
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

try:
    from fairino import RPC
    from config import DEFAULT_ROBOT_IP, DEFAULT_JOG_VEL, DEFAULT_JOG_ACC, DEFAULT_STEP_DIS
except ImportError as e:
    print(f"[ERROR] Gagal mengimpor SDK Fairino: {e}")
    sys.exit(1)


class TeleopGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Fairino Cobot FR5 Teleoperation Control (SDK 3.7.4)")
        self.root.geometry("620x720")
        self.root.resizable(False, False)

        self.robot = None
        self.connected = False
        self.robot_ip = tk.StringVar(value=DEFAULT_ROBOT_IP)
        self.status_msg = tk.StringVar(value="Status: Disconnected")
        
        self.vel_var = tk.DoubleVar(value=DEFAULT_JOG_VEL)
        self.step_var = tk.DoubleVar(value=DEFAULT_STEP_DIS)
        self.mode_var = tk.StringVar(value="joint")  # "joint" or "cart"

        self.joint_labels = []
        self.tcp_labels = []
        self.stop_thread = False

        self._build_ui()

    def _build_ui(self):
        # 1. Connection Frame
        conn_frame = ttk.LabelFrame(self.root, text=" Koneksi Controller ", padding=10)
        conn_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(conn_frame, text="Robot IP:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(conn_frame, textvariable=self.robot_ip, width=15).grid(row=0, column=1, padx=5, pady=5)
        
        self.btn_connect = ttk.Button(conn_frame, text="Connect", command=self.toggle_connect)
        self.btn_connect.grid(row=0, column=2, padx=10, pady=5)

        self.btn_reset = ttk.Button(conn_frame, text="Reset Error", command=self.reset_errors, state="disabled")
        self.btn_reset.grid(row=0, column=3, padx=5, pady=5)

        # 2. Telemetry Status
        tele_frame = ttk.LabelFrame(self.root, text=" Telemetri Real-time ", padding=10)
        tele_frame.pack(fill="x", padx=10, pady=5)

        # Joint Positions (2 columns x 3 rows)
        joint_sub = ttk.Frame(tele_frame)
        joint_sub.pack(fill="x")
        ttk.Label(joint_sub, text="Posisi Sendi (Degrees):", font=('Helvetica', 9, 'bold')).pack(anchor="w")

        j_grid = ttk.Frame(joint_sub)
        j_grid.pack(fill="x", pady=2)
        for i in range(6):
            r = i // 3
            c = (i % 3) * 2
            ttk.Label(j_grid, text=f"J{i+1}:").grid(row=r, column=c, sticky="e", padx=2, pady=2)
            lbl = ttk.Label(j_grid, text="0.00°", width=10, font=('Monospace', 9))
            lbl.grid(row=r, column=c+1, sticky="w", padx=5, pady=2)
            self.joint_labels.append(lbl)

        # TCP Pose
        tcp_sub = ttk.Frame(tele_frame)
        tcp_sub.pack(fill="x", pady=(8, 0))
        ttk.Label(tcp_sub, text="TCP Pose (mm / deg):", font=('Helvetica', 9, 'bold')).pack(anchor="w")

        t_grid = ttk.Frame(tcp_sub)
        t_grid.pack(fill="x", pady=2)
        names = ["X", "Y", "Z", "Rx", "Ry", "Rz"]
        for i in range(6):
            r = i // 3
            c = (i % 3) * 2
            ttk.Label(t_grid, text=f"{names[i]}:").grid(row=r, column=c, sticky="e", padx=2, pady=2)
            lbl = ttk.Label(t_grid, text="0.0", width=10, font=('Monospace', 9))
            lbl.grid(row=r, column=c+1, sticky="w", padx=5, pady=2)
            self.tcp_labels.append(lbl)

        # 3. Control Panel (Speed & Mode)
        ctrl_frame = ttk.LabelFrame(self.root, text=" Pengaturan Jogging ", padding=10)
        ctrl_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(ctrl_frame, text="Kecepatan Jog (%)").grid(row=0, column=0, padx=5, sticky="w")
        vel_scale = ttk.Scale(ctrl_frame, from_=1.0, to=100.0, variable=self.vel_var, orient="horizontal")
        vel_scale.grid(row=0, column=1, fill="x", padx=5)
        ttk.Label(ctrl_frame, textvariable=self.vel_var).grid(row=0, column=2, padx=5)

        ttk.Label(ctrl_frame, text="Mode Jog:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        rb_joint = ttk.Radiobutton(ctrl_frame, text="Joint Space (J1-J6)", variable=self.mode_var, value="joint")
        rb_joint.grid(row=1, column=1, sticky="w", padx=5)
        rb_cart = ttk.Radiobutton(ctrl_frame, text="Cartesian Space (Base)", variable=self.mode_var, value="cart")
        rb_cart.grid(row=1, column=2, sticky="w", padx=5)

        # 4. Axis Jogging Buttons
        jog_frame = ttk.LabelFrame(self.root, text=" Tombol Control Teleop ", padding=10)
        jog_frame.pack(fill="both", expand=True, padx=10, pady=5)

        axis_names = ["Axis 1 (J1 / X)", "Axis 2 (J2 / Y)", "Axis 3 (J3 / Z)",
                      "Axis 4 (J4 / Rx)", "Axis 5 (J5 / Ry)", "Axis 6 (J6 / Rz)"]

        self.jog_buttons = []
        for i in range(6):
            row_f = ttk.Frame(jog_frame)
            row_f.pack(fill="x", pady=3)

            ttk.Label(row_f, text=axis_names[i], width=18).pack(side="left", padx=5)
            
            btn_pos = ttk.Button(row_f, text=" + ", width=8)
            btn_pos.pack(side="left", padx=5)
            btn_pos.bind("<ButtonPress>", lambda e, ax=i+1: self.start_jog(ax, 1))
            btn_pos.bind("<ButtonRelease>", lambda e: self.stop_jog())

            btn_neg = ttk.Button(row_f, text=" - ", width=8)
            btn_neg.pack(side="left", padx=5)
            btn_neg.bind("<ButtonPress>", lambda e, ax=i+1: self.start_jog(ax, 0))
            btn_neg.bind("<ButtonRelease>", lambda e: self.stop_jog())

            self.jog_buttons.extend([btn_pos, btn_neg])

        # 5. Bottom Quick Actions & Emergency Stop
        bot_frame = ttk.Frame(self.root, padding=10)
        bot_frame.pack(fill="x", side="bottom")

        btn_estop = tk.Button(bot_frame, text="STOP ALL (SPACE)", bg="red", fg="white", font=('Helvetica', 11, 'bold'),
                              command=self.stop_jog)
        btn_estop.pack(fill="x", ipady=5)

        # Status Bar
        lbl_status = ttk.Label(self.root, textvariable=self.status_msg, relief="sunken", anchor="w")
        lbl_status.pack(fill="x", side="bottom")

    def toggle_connect(self):
        if not self.connected:
            ip = self.robot_ip.get().strip()
            try:
                self.robot = RPC(ip)
                time.sleep(0.3)
                res = self.robot.GetActualJointPosDegree()
                if isinstance(res, (tuple, list)) and res[0] == 0:
                    self.connected = True
                    self.btn_connect.config(text="Disconnect")
                    self.btn_reset.config(state="normal")
                    self.status_msg.set(f"Terhubung ke Fairino Robot di {ip}")
                    
                    # Auto enable
                    self.robot.ResetAllError()
                    self.robot.Mode(1)
                    self.robot.RobotEnable(1)

                    # Start Telemetry Worker Thread
                    self.stop_thread = False
                    threading.Thread(target=self._telemetry_worker, daemon=True).start()
                else:
                    messagebox.showerror("Koneksi Gagal", f"Gagal membaca data dari robot IP {ip}.")
            except Exception as e:
                messagebox.showerror("Error RPC", str(e))
        else:
            self.stop_thread = True
            self.connected = False
            self.robot = None
            self.btn_connect.config(text="Connect")
            self.btn_reset.config(state="disabled")
            self.status_msg.set("Terputus dari robot.")

    def reset_errors(self):
        if self.robot and self.connected:
            try:
                self.robot.ResetAllError()
                time.sleep(0.2)
                self.robot.Mode(1)
                time.sleep(0.2)
                self.robot.RobotEnable(1)
                self.status_msg.set("Error di-reset dan power servo di-enable.")
            except Exception as e:
                self.status_msg.set(f"Error reset: {e}")

    def start_jog(self, axis_num, direction):
        if self.robot and self.connected:
            ref_type = 0 if self.mode_var.get() == "joint" else 1
            vel = float(self.vel_var.get())
            step = float(self.step_var.get())
            self.robot.StartJOG(ref_type, axis_num, direction, step, vel)

    def stop_jog(self):
        if self.robot and self.connected:
            try:
                self.robot.ImmStopJOG()
            except Exception:
                pass

    def _telemetry_worker(self):
        while self.connected and not self.stop_thread:
            try:
                res_j = self.robot.GetActualJointPosDegree()
                if isinstance(res_j, (tuple, list)) and res_j[0] == 0:
                    joints = list(res_j[1:7])
                    for i in range(6):
                        self.joint_labels[i].config(text=f"{joints[i]:.2f}°")

                res_p = self.robot.GetActualTCPPose()
                if isinstance(res_p, (tuple, list)) and res_p[0] == 0:
                    pose = list(res_p[1:7])
                    for i in range(6):
                        self.tcp_labels[i].config(text=f"{pose[i]:.1f}")
            except Exception:
                pass
            time.sleep(0.15)


def main():
    root = tk.Tk()
    app = TeleopGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
