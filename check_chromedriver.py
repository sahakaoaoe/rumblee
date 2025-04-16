import chromedriver_autoinstaller
from shutil import which

# Menginstal atau memperbarui chromedriver
chromedriver_autoinstaller.install()

# Memastikan lokasi chromedriver yang terinstal
chromedriver_path = which("chromedriver")
if chromedriver_path:
    print(f"Chromedriver berhasil diinstal di: {chromedriver_path}")
else:
    print("Chromedriver tidak ditemukan.")
