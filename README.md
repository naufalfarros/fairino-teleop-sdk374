# 🤖 Fairino Cobot FR5 — Multi-Platform Teleoperation Package (SDK v3.7.4)

Repositori ini adalah paket **portabel dan cross-platform** untuk mengontrol **Robot Fisik Cobot Fairino FR5 / FR10** menggunakan **Fairino Python SDK versi 3.7.4**.

Script `interactive_teleop.py` dapat berjalan langsung di **Windows, Ubuntu/Linux, dan macOS** tanpa perlu mengubah kode apapun — cukup salin seluruh folder ini ke device tujuan dan jalankan.

---

## 🛑 PENTING: KHUSUS ROBOT FISIK (PHYSICAL HARDWARE)

- **Target Hardware**: Controller Box Cobot Fairino FR5 / FR10 Fisik.
- **IP Default Controller (Kabel LAN Ethernet)**: `192.168.58.2` (Port XML-RPC: `20003`).
- **IP Default Controller (Wi-Fi Hotspot AP)**: `192.168.57.2` (Port XML-RPC: `20003`).
- **Komunikasi Jaringan**: Direct Ethernet Cable RJ45 atau Wi-Fi AP.

---

## ✅ Kompatibilitas Platform

| Platform | Status | Versi Teruji |
|----------|--------|-------------|
| 🐧 Ubuntu / Linux | ✅ Didukung | Ubuntu 20.04, 22.04, 24.04 |
| 🍏 macOS | ✅ Didukung | Ventura, Sonoma, Sequoia |
| 🪟 Windows | ✅ Didukung | Windows 10, Windows 11 |

**Prasyarat**: Python 3.8 atau lebih baru. **Tidak perlu `pip install` apapun** — semua dependensi menggunakan standard library Python bawaan.

---

## 📁 Struktur Berkas Repositori

```text
fairino python sdk 374/
├── interactive_teleop.py                  # Script teleoperasi utama (cross-platform)
├── README.md                              # Dokumentasi & panduan ini
└── fairino-python-sdk-main/
    ├── linux/fairino/
    │   └── Robot.py                       # SDK Python v3.7.4 untuk Linux & macOS
    └── windows/fairino/
        └── Robot.py                       # SDK Python v3.7.4 untuk Windows
```

> **Catatan:** Script secara otomatis memilih SDK yang benar berdasarkan OS yang terdeteksi (`platform.system()`). Tidak perlu konfigurasi manual.

---

## 🔌 TUTORIAL LENGKAP PENGATURAN IP DI BERBAGAI OS (UBUNTU, MAC, WINDOWS)

Agar laptop dapat berkomunikasi dengan controller robot fisik Fairino FR5, laptop dan robot harus berada dalam **satu subnet jaringan IP yang sama**. Ubah konfigurasi jaringan laptop Anda dari **Automatic (DHCP)** menjadi **Manual (Static IP)** sesuai sistem operasi yang digunakan.

---

### 🐧 1. UBUNTU LINUX

#### 🔹 Cara GUI (Ubuntu 20.04 / 22.04 / 24.04):
1. Buka **Settings** (Pengaturan) ➔ pilih menu **Network** (Jaringan).
2. Di bagian **Wired** (Koneksi Kabel LAN), klik ikon Roda Gigi / Gear **⚙️** di samping koneksi aktif.
3. Buka tab **IPv4**.
4. Ubah **IPv4 Method** dari `Automatic (DHCP)` menjadi **`Manual`**.
5. Isikan data pada kolom **Addresses**:
   - **Address**: `192.168.58.100` *(Kabel LAN)* atau `192.168.57.100` *(Wi-Fi)*
   - **Netmask**: `255.255.255.0`
   - **Gateway**: `192.168.58.1` *(boleh dikosongkan)*
6. Klik tombol **Apply** di sudut kanan atas.
7. Matikan koneksi Wired (Toggle OFF) lalu nyalakan kembali (Toggle ON) agar IP aktif.

#### 🔹 Cara Terminal CLI (`nmcli`):
```bash
# Cek nama interface jaringan Anda
nmcli device status

# Set IP Manual Static (Ganti "Wired connection 1" sesuai nama interface)
nmcli con mod "Wired connection 1" ipv4.addresses 192.168.58.100/24 ipv4.method manual
nmcli con up "Wired connection 1"
```

---

### 🍏 2. macOS (MACBOOK / MAC MINI / MAC STUDIO)

#### 🔹 Cara GUI (macOS Ventura, Sonoma, Sequoia):
1. Klik logo Apple **** di sudut kiri atas layar ➔ pilih **System Settings...** (Pengaturan Sistem).
2. Pilih menu **Network** (Jaringan) pada sidebar kiri.
3. Klik pada adaptor jaringan Anda: **Ethernet** atau nama Adapter USB-C to Ethernet Anda (misal: *AX88179A* / *USB 10/100/1000 LAN*).
4. Klik tombol **Details...** (Rincian).
5. Pada menu sebelah kiri dialog, pilih tab **TCP/IP**.
6. Ubah menu drop-down **Configure IPv4** dari `Using DHCP` menjadi **`Manually`**.
7. Masukkan nilai konfigurasi:
   - **IP Address**: `192.168.58.100`
   - **Subnet Mask**: `255.255.255.0`
   - **Router**: `192.168.58.1` *(boleh dikosongkan)*
8. Klik **OK**, lalu klik **Apply** (Terapkan).

#### 🔹 Cara Terminal macOS (`networksetup`):
```bash
# Cek daftar layanan jaringan
networksetup -listallnetworkservices

# Set Static IP (Ganti "Ethernet" dengan nama layanan jaringan Anda)
sudo networksetup -setmanual "Ethernet" 192.168.58.100 255.255.255.0 192.168.58.1
```

---

### 🪟 3. WINDOWS (WINDOWS 10 & WINDOWS 11)

#### 🔹 Cara GUI (Control Panel Network Connections):
1. Tekan tombol `Win + R` di keyboard, ketik `ncpa.cpl` lalu tekan **Enter**.
2. Klik kanan pada adaptor **Ethernet** (atau *Local Area Connection*) ➔ pilih **Properties**.
3. Klik dua kali pada opsi **Internet Protocol Version 4 (TCP/IPv4)**.
4. Pilih opsi **"Use the following IP address"** (Gunakan alamat IP berikut):
   - **IP address**: `192.168.58.100`
   - **Subnet mask**: `255.255.255.0`
   - **Default gateway**: `192.168.58.1`
5. Centang *Validate settings upon exit*, lalu klik **OK** dan **OK** lagi.

#### 🔹 Cara Command Prompt / PowerShell (Administrator):
```cmd
netsh interface ipv4 set address name="Ethernet" static 192.168.58.100 255.255.255.0 192.168.58.1
```

---

### 🧪 Step 4: Verifikasi Koneksi (Ping Test)

Buka Terminal (Ubuntu/macOS) atau Command Prompt (Windows), lalu tes koneksi ke robot:

```bash
ping 192.168.58.2
```

**Output Sukses (Robot Terhubung):**
```text
64 bytes from 192.168.58.2: icmp_seq=1 ttl=64 time=0.421 ms
64 bytes from 192.168.58.2: icmp_seq=2 ttl=64 time=0.380 ms
```

---

## 🚀 CARA MENJALANKAN PROGRAM TELEOPERASI

### Ubuntu / macOS:
```bash
cd "fairino python sdk 374"
python3 interactive_teleop.py
```

### Windows (Command Prompt / PowerShell):
```cmd
cd "fairino python sdk 374"
python interactive_teleop.py
```

> **Catatan:** IP robot default di script adalah `192.168.57.2` (Wi-Fi AP). Jika menggunakan kabel LAN Ethernet, edit baris `Robot.RPC('192.168.57.2')` di `interactive_teleop.py` menjadi `Robot.RPC('192.168.58.2')`.

---

## 🎮 Panduan Tombol Keyboard Teleoperasi

### Gerakan Manual Joint (JOG):

| Tombol | Fungsi |
|--------|--------|
| `1` / `q` | J1 Positif (+) / J1 Negatif (-) |
| `2` / `w` | J2 Positif (+) / J2 Negatif (-) |
| `3` / `e` | J3 Positif (+) / J3 Negatif (-) |
| `4` / `r` | J4 Positif (+) / J4 Negatif (-) |
| `5` / `t` | J5 Positif (+) / J5 Negatif (-) |
| `6` / `y` | J6 Positif (+) / J6 Negatif (-) |

### Pengaturan & Kontrol:

| Tombol | Fungsi |
|--------|--------|
| `m` | Ganti Mode JOG (Incremental ↔ Continuous) |
| `a` | Mode Gerak Otomatis (Semua J1—J6 berputar bergantian) |
| `[` / `]` | Kurangi / Tambah Step Size (-0.5° / +0.5°) |
| `,` / `.` | Kurangi / Tambah Kecepatan (-5% / +5%) |
| `c` | Reset / Clear Error & Alarm Controller |
| `p` | Refresh Dashboard Manual |
| `s` / `Spasi` | **STOP Seketika** (Instant Safety Stop) |
| `Esc` | Keluar dari program |

---

## 🔧 Perbedaan Teknis Cross-Platform

| Aspek | Linux / macOS | Windows |
|-------|--------------|---------|
| Keyboard Input | `termios` + `tty` + `select` | `msvcrt` |
| Clear Screen | ANSI escape `\033[H\033[J` | `os.system('cls')` |
| SDK Path | `fairino-python-sdk-main/linux/` | `fairino-python-sdk-main/windows/` |
| Python Command | `python3` | `python` |

Semua perbedaan ini ditangani **secara otomatis** oleh script — pengguna tidak perlu melakukan konfigurasi apapun.

---
