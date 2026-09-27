# Step-by-Step Penanganan AMD GPU Cloud PyTorch: Pindah Port JupyterLab & Instalasi aaPanel

Dokumentasi ini adalah panduan langkah demi langkah (*SOP / Runbook*) saat membuat atau mengonfigurasi Droplet Cloud baru berbasis **PyTorch on AMD Instinct (DigitalOcean 1-Click / Ubuntu 24.04)**, memeriksa Caddy & Docker JupyterLab pada port default, memindahkannya ke port `9999`, dan menginstal **aaPanel** tanpa konflik port.

---

## 1. Latar Belakang & Identifikasi Masalah

Pada image droplet AMD GPU Cloud:
- PyTorch dan JupyterLab berjalan di dalam container Docker bernama **`rocm`** dengan port internal `8888`, `8000`, dan `30000`.
- Web reverse proxy **`caddy`** secara default mendengarkan di **Port 80 (HTTP)** dan meneruskannya ke JupyterLab di `localhost:8888`.
- **Masalah:** Jika ingin memasang **aaPanel**, Nginx bawaan aaPanel mewajibkan **Port 80 & 443**. Jika Caddy masih aktif di port 80, Nginx aaPanel akan gagal berjalan (*port conflict*).
- **Solusi:** Pindahkan listening port Caddy ke **Port `9999`**, sehingga Port 80 kosong dan siap dipakai untuk aaPanel, sementara JupyterLab tetap aktif di port `9999`.

---

## 2. Langkah 1: Pengecekan Awal Caddy & Docker

Jalankan perintah berikut di terminal SSH server:

### A. Cek Container Docker yang Berjalan
```bash
docker ps -a
```
*Pastikan container `rocm` berstatus `Up`.*

### B. Cek Siapa yang Menggunakan Port 80
```bash
sudo ss -tulpn | grep :80
```
*Akan terlihat proses `caddy` sedang mendengarkan di port `*:80`.*

### C. Cek Konfigurasi Caddy Bawaan
```bash
cat /etc/caddy/Caddyfile
```
*Output default:*
```caddy
:80 {
        reverse_proxy localhost:8888
}
```

---

## 3. Langkah 2: Pindahkan Port Caddy / JupyterLab ke `9999`

Jalankan rangkaian perintah berikut:

```bash
# 1. Ubah port :80 menjadi :9999 di file konfigurasi Caddy
sudo sed -i 's/:80/:9999/g' /etc/caddy/Caddyfile

# 2. Buka port 9999 di Firewall UFW
sudo ufw allow 9999/tcp
sudo ufw reload

# 3. Restart service Caddy agar konfigurasi baru aktif
sudo systemctl restart caddy
```

---

## 4. Langkah 3: Verifikasi Port 80 Bebas & Port 9999 Aktif

Periksa kembali status port di server:
```bash
ss -tulpn | grep -E ':(80|9999)\b'
```

**Hasil yang diharapkan:**
```text
tcp   LISTEN 0      4096               *:9999             *:*    users:(("caddy",...))
```
- **Port 80:** Sudah **KOSONG** (tidak muncul di hasil).
- **Port 9999:** Sudah aktif mendengarkan koneksi untuk Caddy/JupyterLab.

---

## 5. Langkah 4: Instalasi aaPanel

Dengan port 80 yang telah kosong, jalankan installer aaPanel:

```bash
wget -O install.sh http://www.aapanel.com/script/install-ubuntu_6.0_en.sh && sudo bash install.sh aapanel
```

1. Saat muncul konfirmasi:
   ```text
   Do you want to install aaPanel to the /www directory now?(y/n):
   ```
   Ketik **`y`** lalu tekan **Enter**.
2. Tunggu proses instalasi selesai (~1–3 menit).
3. Setelah selesai, terminal akan menampilkan kredensial login:
   - **URL Panel:** `https://<IP-SERVER>:<PORT-AAPANEL>/<ENTRANCE>`
   - **Username:** `...`
   - **Password:** `...`
4. **Buka port firewall aaPanel:**
   ```bash
   sudo ufw allow <PORT-AAPANEL>/tcp
   sudo ufw reload
   ```

---

## 6. Akses Layanan Setelah Konfigurasi

| Layanan | Cara Akses / URL | Keterangan |
| :--- | :--- | :--- |
| **JupyterLab (Web Browser)** | `http://<IP-SERVER>:9999` | Masukkan token bawaan droplet |
| **VS Code (`.ipynb` Kernel)** | `http://<IP-SERVER>:9999/?token=<TOKEN>` | Pilih *Select Kernel* -> *Existing Jupyter Server* (tanpa `/lab`) |
| **aaPanel Admin** | `https://<IP-SERVER>:<PORT-AAPANEL>/<ENTRANCE>` | Buka port di UFW terlebih dahulu |
| **Website Baru di aaPanel** | `http://<IP-SERVER>` (Port 80/443) | Kelola via menu *Website* di aaPanel |

---

## 7. Panduan Lengkap Koneksi VS Code (`.ipynb`) ke Remote Server

Agar file notebook `.ipynb` yang dibuka di VS Code lokal Anda dapat langsung menggunakan komputasi GPU AMD Instinct MI300X di server remote:

### A. Prasyarat Ekstensi di VS Code
Pastikan ekstensi **Jupyter** (`ms-toolsai.jupyter`) sudah terpasang di VS Code Anda.

### B. Format URL Remote Server
VS Code membutuhkan URL dasar HTTP server beserta token autentikasinya (**tanpa akhiran `/lab`**):
```text
http://<IP-SERVER>:9999/?token=<TOKEN>
```
*Contoh untuk server saat ini (`165.245.128.185`):*
```text
http://165.245.128.185:9999/?token=vsb0vjjm4B3Sgq2a/adGxNFDVvfuw4LJhbi+zGHm6bNpysz/p
```

### C. Langkah Koneksi di VS Code:
1. **Buka file `.ipynb`** di editor VS Code Anda.
2. Di pojok kanan atas tampilan notebook, klik tombol **`Select Kernel`** (atau nama kernel yang sedang aktif).
3. Pilih opsi **`Existing Jupyter Server...`**.
4. Masukkan URL lengkap di atas (yang menyertakan port `9999` dan token).
5. Tekan **Enter**, lalu ketik nama identitas server (contoh: `AMD-MI300X-Remote`).
6. VS Code akan menampilkan daftar kernel yang tersedia di server. Pilih kernel **`Python 3 (ipykernel)`** dari container `rocm`.

### D. Sel Pengujian (Verifikasi GPU di Notebook):
Buat cell baru di dalam notebook `.ipynb` dan jalankan kode berikut:

```python
import torch

print("=== DETEKSI GPU PYTORCH ROCm ===")
print("CUDA/ROCm Available :", torch.cuda.is_available())

if torch.cuda.is_available():
    print("Device Count        :", torch.cuda.device_count())
    print("Device Name (GPU 0) :", torch.cuda.get_device_name(0))
    
    # Tes komputasi perkalian matriks langsung di memori GPU AMD
    a = torch.randn(4096, 4096, device='cuda')
    b = torch.randn(4096, 4096, device='cuda')
    c = a @ b
    print("Komputasi GPU Sukses! Tensor Sum:", c.sum().item())
else:
    print("GPU belum terdeteksi oleh PyTorch.")
```

### E. Opsi Alternatif: Koneksi via SSH Tunnel (Jika Port 9999 Dibatasi)
Jika koneksi HTTP langsung ke port `9999` dibatasi oleh provider atau ingin koneksi yang lebih privat/terenkripsi, buat SSH tunnel dari **PowerShell / Terminal lokal Windows Anda** (bukan di dalam terminal remote server):

```powershell
ssh -i "C:\Users\LENOVO'\.ssh\gpuamd_z2uwg" -L 9999:localhost:9999 root@165.245.128.185
```

Setelah tunnel aktif:
- Masukkan URL ini di VS Code *Existing Jupyter Server*:
  ```text
  http://localhost:9999/?token=vsb0vjjm4B3Sgq2a/adGxNFDVvfuw4LJhbi+zGHm6bNpysz/p
  ```

---

## 8. Verifikasi Performa GPU AMD di Terminal Host

Untuk memantau performa dan temperatur GPU AMD Instinct MI300X secara realtime di server:

```bash
# Monitoring live utilisasi GPU di terminal server
amd-smi monitor

# Cek info detail ROCm
rocminfo
```

