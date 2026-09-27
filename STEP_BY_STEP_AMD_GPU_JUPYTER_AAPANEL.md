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

## 7. Verifikasi Performa GPU AMD di Container

Untuk memastikan GPU AMD Instinct MI300X tetap berfungsi normal setelah konfigurasi:

```bash
# Tes eksekusi PyTorch di GPU AMD
docker exec -it rocm python3 -c "import torch; print('GPU Available:', torch.cuda.is_available(), '| Model:', torch.cuda.get_device_name(0))"

# Cek monitoring realtime GPU
amd-smi monitor
```
