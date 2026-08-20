# 🤖 Fairino Cobot FR5 Physical Robot Teleoperation Package (SDK v3.7.4)

Repositori ini disusun secara mendalam dan portabel **khusus untuk mengontrol Robot Fisik Cobot Fairino FR5 / FR10** (bukan untuk lingkungan simulasi) menggunakan **Fairino Python SDK versi 3.7.4**.

Dengan paket ini, Anda dapat menghubungkan laptop (Ubuntu, macOS, Windows) ke controller box robot fisik, menjalankan teleoperasi manual (Jogging & Drag Teaching), serta membagikan kodenya ke laptop/device lain via GitHub.

---

## 🛑 PENTING: KHUSUS ROBOT FISIK (PHYSICAL HARDWARE)

- **Target Hardware**: Controller Box Cobot Fairino FR5 / FR10 Fisik.
- **IP Default Controller (Kabel LAN Ethernet)**: `192.168.58.2` (Port XML-RPC: `20003`).
- **IP Default Controller (Wi-Fi Hotspot AP)**: `192.168.57.2` (Port XML-RPC: `20003`).
- **Komunikasi Jaringan**: Direct Ethernet Cable RJ45 atau Wi-Fi AP.

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
1. Klik logo Apple **** di sudut kiri atas layar ➔ pilih **System Settings...** (Pengaturan Sistem).
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

## 📁 Struktur Berkas Repositori

```text
fairino_teleop_sdk374/
├── fairino/               # SDK Python 3.7.4 Lokal (Robot.py & RPC Client)
│   ├── __init__.py
│   └── Robot.py
├── config.py              # Konfigurasi IP Robot Fisik (192.168.58.2) & Safety Limits
├── teleop_cli.py          # Program Teleoperasi Terminal Interaktif (Keyboard Jog J1-J6)
├── teleop_gui.py          # Program Teleoperasi GUI Desktop (Tkinter Panel)
├── requirements.txt       # Kebutuhan Python (Pure Standard Library Python 3.7+)
├── .gitignore             # Aturan ignoransi berkas cache/build untuk Git
└── README.md              # Dokumentasi & panduan langkah demi langkah ini
```

---

## 🚀 CARA MENJALANKAN PROGRAM TELEOPERASI ROBOT FISIK

### 1. Mode Terminal Interaktif (CLI)

```bash
cd /home/fr5/fairino_teleop_sdk374

# Menjalankan teleoperasi ke IP default robot fisik via LAN Ethernet
python3 teleop_cli.py 192.168.58.2

# Atau via Wi-Fi AP Hotspot Robot Fisik
python3 teleop_cli.py 192.168.57.2
```

**Panduan Navigasi Tombol Keyboard Teleop:**
- `[1]` s/d `[6]` : Pilih Joint aktif (J1..J6) atau Sumbu Kartesian (X, Y, Z, Rx, Ry, Rz).
- `[m]` : Switch Mode Jogging (**Joint Space** ↔ **Cartesian Space**).
- `[u]` / `[+]` : Gerakkan Jogging arah **Positif (+)**.
- `[i]` / `[-]` : Gerakkan Jogging arah **Negatif (-)**.
- `[d]` : Toggle mode **Drag Teaching** *(Hand-Guiding: Robot fisik bebas ditarik/didorong)*.
- `[e]` : Toggle Power Servo **Enable / Disable**.
- `[r]` : Reset Error / Alarm Controller Robot Fisik.
- `[,]` / `[.]` : Kurangi / Tambah Kecepatan Jog (-5% / +5%).
- `[SPACE]` / `[s]` : Stop Seketika (*Instant Safety Stop*).
- `[q]` : Keluar dari program teleoperasi.

---

### 2. Mode Desktop GUI (Tkinter Panel)

```bash
python3 teleop_gui.py
```

---