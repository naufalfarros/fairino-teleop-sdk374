import sys
import os
import platform
import time

# ============================================================================
# CROSS-PLATFORM KEYBOARD INPUT
# Mendukung: Windows, Linux (Ubuntu), macOS
# ============================================================================
IS_WINDOWS = platform.system() == "Windows"

if IS_WINDOWS:
    import msvcrt
else:
    import select
    import termios
    import tty

# Prioritaskan path SDK v3.7.4 (relatif terhadap lokasi script ini)
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if IS_WINDOWS:
    sys.path.insert(0, os.path.join(_SCRIPT_DIR, "fairino-python-sdk-main", "windows"))
else:
    sys.path.insert(0, os.path.join(_SCRIPT_DIR, "fairino-python-sdk-main", "linux"))

from fairino import Robot


def get_key():
    """Membaca satu karakter dari input standar tanpa blocking (cross-platform)"""
    if IS_WINDOWS:
        if msvcrt.kbhit():
            ch = msvcrt.getch()
            # Deteksi tombol khusus Windows (ESC = 0x1b, arrow keys = 0xe0 prefix)
            if ch == b'\x1b':
                return '\x1b'
            if ch == b'\xe0' or ch == b'\x00':
                # Tombol spesial (arrow, function keys) — abaikan byte kedua
                msvcrt.getch()
                return ''
            try:
                return ch.decode('utf-8', errors='ignore')
            except Exception:
                return ''
        return ''
    else:
        rlist, _, _ = select.select([sys.stdin], [], [], 0.02)  # Timeout 20ms
        if rlist:
            return sys.stdin.read(1)
        return ''


def clear_screen():
    """Membersihkan layar terminal (cross-platform)"""
    if IS_WINDOWS:
        os.system('cls')
    else:
        print("\033[H\033[J", end="")


def print_dashboard(robot, jog_mode, step_size, vel, auto_mode=False):
    """Menampilkan dashboard status robot yang bersih dan informatif di terminal"""
    err, state = robot.GetRobotRealTimeState()
    if err == 0:
        mode_str = "MANUAL" if state.robot_mode == 1 else "AUTO"
        enable_str = "ON" if state.rbtEnableState == 1 else "OFF"
        estop_str = "AKTIF (BAHAYA!)" if state.EmergencyStop == 1 else "Normal"
        collision_str = "TABRAKAN!" if state.collisionState == 1 else "Normal"
        
        err_str = "Tidak Ada"
        if state.main_code != 0 or state.sub_code != 0:
            err_str = f"Main Code: {state.main_code}, Sub Code: {state.sub_code}"
            
        status_auto = "AKTIF (J1-J6 BERGERAK)" if auto_mode else "OFF (Manual)"
        os_str = platform.system()
            
        # Bersihkan terminal
        clear_screen()
        print("==================================================================")
        print("            KONTROL MANUAL & OTOMATIS JOG (ROBOT FR5)            ")
        print(f"                  [ Cross-Platform — {os_str} ]                  ")
        print("==================================================================")
        print(f" [STATUS ROBOT] Mode: {mode_str} | Enable: {enable_str} | E-Stop: {estop_str}")
        print(f" [COLLISION]    {collision_str} | [ALARM/ERROR] {err_str}")
        print("------------------------------------------------------------------")
        print(" [KONFIGURASI JOG]")
        print(f"   Mode JOG    : {jog_mode.upper()}  (Tekan [m] untuk ganti)")
        print(f"   Mode Auto   : {status_auto}  (Tekan [a] Mulai Auto | [s] Stop)")
        print(f"   Step Size   : {step_size:.1f}°   (Tekan [ [ ] Kurangi | [ ] ] Tambah)")
        print(f"   Kecepatan   : {vel:.0f}%     (Tekan [ , ] Kurangi | [ . ] Tambah)")
        print("------------------------------------------------------------------")
        print(" [POSISI SENDI SAAT INI]")
        print(f"   J1: {state.actual_joint_pos[0]:8.2f}° | J2: {state.actual_joint_pos[1]:8.2f}° | J3: {state.actual_joint_pos[2]:8.2f}°")
        print(f"   J4: {state.actual_joint_pos[3]:8.2f}° | J5: {state.actual_joint_pos[4]:8.2f}° | J6: {state.actual_joint_pos[5]:8.2f}°")
        print("------------------------------------------------------------------")
        print(" Tombol Gerakan Manual:")
        print("   J1: [1] J1+ | [q] J1-   J4: [4] J4+ | [r] J4-")
        print("   J2: [2] J2+ | [w] J2-   J5: [5] J5+ | [t] J5-")
        print("   J3: [3] J3+ | [e] J3-   J6: [6] J6+ | [y] J6-")
        print(" Tombol Fungsi:")
        print("   [a] : Mode Gerak Otomatis (J1-J6)   [s]/[Spasi] : STOP Gerakan")
        print("   [c] : Reset/Clear Error             [p]         : Refresh Dashboard")
        print("   [Esc] : Keluar Program")
        print("==================================================================")
        print("Input >> ", end="")
        sys.stdout.flush()
    else:
        print(f"\r[Error] Gagal mengambil status real-time robot (Kode: {err})", end="")
        sys.stdout.flush()


def main():
    print(f"[INFO] Platform terdeteksi: {platform.system()} ({platform.machine()})")
    print("Menghubungkan ke robot di IP 192.168.57.2...")
    try:
        robot = Robot.RPC('192.168.57.2')
        time.sleep(1)
        if not robot.is_connect:
            print("Gagal terhubung ke robot. Pastikan simulator/hardware aktif di IP 192.168.57.2.")
            return
    except Exception as e:
        print(f"Error saat menghubungkan ke robot: {e}")
        return

    # Diagnostik Awal & Setup Automatis
    err, state = robot.GetRobotRealTimeState()
    if err == 0:
        if state.robot_mode == 0:
            print("Robot berada di Mode AUTO. Mengubah ke Mode MANUAL...")
            robot.Mode(1)
            time.sleep(1)
        if state.rbtEnableState == 0:
            print("Robot belum ENABLE. Mengaktifkan servo robot...")
            robot.RobotEnable(1)
            time.sleep(3)
    else:
        print("Gagal mendiagnosis robot di awal.")
        return

    # Inisialisasi parameter kontrol
    jog_mode = "Incremental"  # Pilihan: 'Incremental' atau 'Continuous'
    step_size = 10.0           # Default step size dalam derajat
    vel = 15.0                # Kecepatan default
    acc = 30.0                # Akselerasi default
    ref = 0                   # 0 = Joint Coordinate System
    
    # Map keys ke (nb, direction)
    jog_map = {
        '1': (1, 1), 'q': (1, 0),
        '2': (2, 1), 'w': (2, 0),
        '3': (3, 1), 'e': (3, 0),
        '4': (4, 1), 'r': (4, 0),
        '5': (5, 1), 't': (5, 0),
        '6': (6, 1), 'y': (6, 0),
    }

    # Simpan konfigurasi terminal lama (hanya POSIX)
    old_settings = None
    if not IS_WINDOWS:
        old_settings = termios.tcgetattr(sys.stdin)
    
    try:
        # Atur terminal ke mode cbreak (hanya POSIX — Windows msvcrt sudah unbuffered)
        if not IS_WINDOWS:
            tty.setcbreak(sys.stdin.fileno())
        
        # Tampilkan dashboard awal
        print_dashboard(robot, jog_mode, step_size, vel)
        
        while True:
            key = get_key()
            
            if not key:
                time.sleep(0.01)
                continue
                
            if key == '\x1b':  # Kunci ESC
                break
                
            elif key in [' ', 's', 'S']:  # Kunci SPASI atau 's' untuk STOP
                robot.ImmStopJOG()
                robot.StopMotion()
                print_dashboard(robot, jog_mode, step_size, vel, auto_mode=False)
                
            elif key in ['a', 'A']:  # Mode Gerak Otomatis Semua Joint (J1 - J6)
                print_dashboard(robot, jog_mode, step_size, vel, auto_mode=True)
                
                # Urutan gerakan otomatis untuk semua 6 joint (J1..J6)
                # Format: (joint_id, direction: 1=+, 0=-)
                auto_sequence = [
                    (1, 1), (1, 0),
                    (2, 1), (2, 0),
                    (3, 1), (3, 0),
                    (4, 1), (4, 0),
                    (5, 1), (5, 0),
                    (6, 1), (6, 0),
                ]
                
                stop_requested = False
                
                while not stop_requested:
                    for nb, direction in auto_sequence:
                        dir_str = "+" if direction == 1 else "-"
                        print(f"\r[AUTO] Bergerak J{nb} ({dir_str}) sebesar {step_size:.1f}°... TEKAN [s] UNTUK BERHENTI!", end="")
                        sys.stdout.flush()
                        
                        err = robot.StartJOG(ref, nb, direction, step_size, vel, acc)
                        if err != 0:
                            print(f"\r[AUTO Error] StartJOG J{nb} Kode: {err}", end="")
                            sys.stdout.flush()
                            time.sleep(1.0)
                            stop_requested = True
                            break
                            
                        # Monitoring gerakan & respon cepat jika tombol 's' ditekan
                        start_wait = time.time()
                        while time.time() - start_wait < 3.0:
                            k = get_key()
                            if k in ['s', 'S', ' ', '\x1b']:
                                robot.ImmStopJOG()
                                robot.StopMotion()
                                stop_requested = True
                                print("\r[STOP] Gerakan otomatis BERHENTI oleh tombol 's'!         ", end="")
                                sys.stdout.flush()
                                time.sleep(0.5)
                                break
                                
                            _, state = robot.GetRobotRealTimeState()
                            if state.main_code != 0 or state.EmergencyStop == 1:
                                robot.ImmStopJOG()
                                robot.StopMotion()
                                stop_requested = True
                                print(f"\r[AUTO Error] Terdeteksi Alarm/E-Stop! Gerakan otomatis dihentikan.", end="")
                                sys.stdout.flush()
                                time.sleep(1.0)
                                break
                                
                            if state.robot_state == 1:  # Status robot 1 = Stopped
                                break
                                
                            time.sleep(0.02)
                            
                        if stop_requested:
                            break
                            
                        time.sleep(0.1)  # Jeda antar gerakan sendi
                        
                robot.ImmStopJOG()
                robot.StopMotion()
                print_dashboard(robot, jog_mode, step_size, vel, auto_mode=False)
                
            elif key == 'c':  # Reset Error
                print("\r[RESET] Membersihkan semua alarm/error...", end="")
                sys.stdout.flush()
                robot.ResetAllError()
                time.sleep(0.5)
                print_dashboard(robot, jog_mode, step_size, vel)
                
            elif key == 'p':  # Refresh manual
                print_dashboard(robot, jog_mode, step_size, vel)
                
            elif key == 'm':  # Toggle mode jog
                jog_mode = "Continuous" if jog_mode == "Incremental" else "Incremental"
                print_dashboard(robot, jog_mode, step_size, vel)
                
            elif key == ']':  # Tambah step size
                step_size = min(10.0, step_size + 0.5)
                print_dashboard(robot, jog_mode, step_size, vel)
                
            elif key == '[':  # Kurangi step size
                step_size = max(0.1, step_size - 0.5)
                print_dashboard(robot, jog_mode, step_size, vel)
                
            elif key == '.':  # Tambah kecepatan
                vel = min(100.0, vel + 5.0)
                print_dashboard(robot, jog_mode, step_size, vel)
                
            elif key == ',':  # Kurangi kecepatan
                vel = max(5.0, vel - 5.0)
                print_dashboard(robot, jog_mode, step_size, vel)
                
            elif key in jog_map:
                nb, direction = jog_map[key]
                dir_str = "+" if direction == 1 else "-"
                
                # Cek status sebelum bergerak
                _, state = robot.GetRobotRealTimeState()
                
                # Abaikan input jika robot sedang bergerak dalam mode incremental
                if jog_mode == "Incremental" and state.robot_state == 2:
                    continue
                    
                if jog_mode == "Incremental":
                    print(f"\r[JOG] Menggerakkan J{nb} ({dir_str}) sebesar {step_size:.1f}°...", end="")
                    sys.stdout.flush()
                    
                    err = robot.StartJOG(ref, nb, direction, step_size, vel, acc)
                    if err != 0:
                        print(f"\rGagal mengirim perintah! Kode error: {err}", end="")
                        sys.stdout.flush()
                        time.sleep(1.0)
                    else:
                        # Tunggu robot selesai melakukan gerakan incremental
                        time.sleep(0.05)
                        start_wait = time.time()
                        while time.time() - start_wait < 2.0:
                            k = get_key()
                            if k in ['s', 'S', ' ', '\x1b']:
                                robot.ImmStopJOG()
                                robot.StopMotion()
                                break
                            _, state = robot.GetRobotRealTimeState()
                            if state.robot_state == 1:  # 1 = Stopped
                                break
                            time.sleep(0.02)
                    print_dashboard(robot, jog_mode, step_size, vel)
                    
                else:
                    # Mode Continuous: Bergerak terus sampai dihentikan oleh user
                    print(f"\r[JOG] J{nb} ({dir_str}) bergerak terus... TEKAN [s] / [SPASI] UNTUK BERHENTI!", end="")
                    sys.stdout.flush()
                    
                    # Beri limit aman sejauh 90.0 derajat
                    err = robot.StartJOG(ref, nb, direction, 90.0, vel, acc)
                    if err != 0:
                        print(f"\rGagal mengirim perintah! Kode error: {err}", end="")
                        sys.stdout.flush()
                        time.sleep(1.0)
                        print_dashboard(robot, jog_mode, step_size, vel)
                    else:
                        # Loop menunggu tombol stop ('s' / Spasi / Esc)
                        while True:
                            stop_key = get_key()
                            if stop_key in [' ', 's', 'S', '\x1b']:
                                robot.ImmStopJOG()
                                robot.StopMotion()
                                break
                            time.sleep(0.01)
                        print_dashboard(robot, jog_mode, step_size, vel)
                        
    except KeyboardInterrupt:
        pass
    finally:
        # Bersihkan terminal dan pastikan robot berhenti total sebelum keluar
        print("\nKeluar program... Memastikan robot berhenti.")
        try:
            robot.ImmStopJOG()
        except:
            pass
        # Kembalikan konfigurasi terminal lama (hanya POSIX)
        if not IS_WINDOWS and old_settings is not None:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

if __name__ == '__main__':
    main()
