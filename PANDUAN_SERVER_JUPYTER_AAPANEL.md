# Panduan Konfigurasi Server AMD GPU, JupyterLab, & aaPanel

Dokumentasi ini merangkum langkah konfigurasi server remote GPU AMD Instinct MI300X, pemindahan port JupyterLab, instalasi aaPanel, dan koneksi remote kernel dari VS Code.

---

## 1. Informasi Server & SSH

- **Host IP Aktif:** `165.245.128.185` *(sebelumnya: 129.212.178.170)*
- **User:** `root`
- **Port:** `22`
- **SSH Key:** `C:\Users\LENOVO'\.ssh\gpuamd_z2uwg`
- **Spesifikasi:** Ubuntu 24.04 LTS, AMD Instinct MI300X VF, PyTorch ROCm 7.14

### Perintah Akses SSH (1 Baris)
```cmd
ssh -i "C:\Users\LENOVO'\.ssh\gpuamd_z2uwg" -p 22 -o ServerAliveInterval=60 -o ServerAliveCountMax=3 root@165.245.128.185
```

---

## 2. Struktur Container Docker di Server

- **`rocm`**: Container aktif yang menjalankan environment PyTorch ROCm dan JupyterLab.
  - Port internal yang di-mapping: `8000`, `8888`, `30000`.
- **`device-metrics-exporter`**: Exporter metrik GPU untuk monitoring.

### Perintah Cek Status Docker & GPU:
```bash
# Cek container
docker ps -a

# Tes deteksi GPU PyTorch ROCm
docker exec -it rocm python3 -c "import torch; print('CUDA/ROCm Available:', torch.cuda.is_available(), '| GPU:', torch.cuda.get_device_name(0))"

# Monitoring utilisasi GPU di host
amd-smi monitor
```

---

## 3. Pemindahan Port JupyterLab ke Port `9999`

Web proxy **Caddy** bawaan mendengarkan di **Port 80** dan meneruskannya ke JupyterLab (`localhost:8888`). Port 80 dipindahkan agar tidak bentrok dengan web server aaPanel.

### Langkah-langkah Pemindahan Port di Terminal SSH:

1. **Ubah port listen Caddy dari `:80` menjadi `:9999`:**
   ```bash
   sudo sed -i 's/:80/:9999/g' /etc/caddy/Caddyfile
   ```

2. **Periksa isi file konfigurasi:**
   ```bash
   cat /etc/caddy/Caddyfile
   ```
   *Pastikan isinya:*
   ```caddy
   :9999 {
           reverse_proxy localhost:8888
   }
   ```

3. **Buka port 9999 di Firewall UFW:**
   ```bash
   sudo ufw allow 9999/tcp
   sudo ufw reload
   ```

4. **Restart service Caddy:**
   ```bash
   sudo systemctl restart caddy
   ```

5. **Verifikasi port listening (Pastikan port 80 kosong):**
   ```bash
   ss -tulpn | grep -E ':(80|9999)\b'
   ```

### Akses JupyterLab Web Browser Baru:
- **URL:** `http://165.245.128.185:9999`
- **Token Baru:** `vsb0vjjm4B3Sgq2a/adGxNFDVvfuw4LJhbi+zGHm6bNpysz/p`

---

## 4. Instalasi aaPanel

Setelah port 80 kosong:

### 1. Jalankan Script Installer aaPanel:
```bash
wget -O install.sh http://www.aapanel.com/script/install-ubuntu_6.0_en.sh && sudo bash install.sh aapanel
```

### 2. Konfirmasi Direktori:
```text
Do you want to install aaPanel to the /www directory now?(y/n):
```
Ketik **`y`** lalu tekan **Enter**.

### 3. Buka Port Dashboard aaPanel di Firewall:
Setelah instalasi selesai, terminal akan menampilkan kredensial login (URL, Port acak, Username, Password).  
Buka port dashboard tersebut di UFW (misal portnya `11924` atau sesuai output):
```bash
sudo ufw allow <PORT_AAPANEL>/tcp
sudo ufw reload
```

---

## 5. Menghubungkan VS Code `.ipynb` ke Remote Jupyter Server

1. **Buka file `.ipynb` di VS Code**.
2. Klik tombol **`Select Kernel`** di pojok kanan atas notebook.
3. Pilih opsi **`Existing Jupyter Server...`**.
4. Masukkan URL lengkap server (tanpa `/lab`):
   ```text
   http://165.245.128.185:9999/?token=vsb0vjjm4B3Sgq2a/adGxNFDVvfuw4LJhbi+zGHm6bNpysz/p
   ```
5. Tekan **Enter**, beri nama koneksi (misal: `AMD-MI300X-Server`).
6. Pilih kernel **Python 3** dari container ROCm.

### Verifikasi di Cell Notebook VS Code:
```python
import torch

print("GPU Available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("Device Name:", torch.cuda.get_device_name(0))
    x = torch.randn(2048, 2048, device="cuda")
    print("Matrix Sum Result:", (x @ x).sum().item())
```
