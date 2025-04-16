import time
import random
import os
import threading
import undetected_chromedriver as uc
import chromedriver_autoinstaller
from shutil import rmtree
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from shutil import which

# Install otomatis chromedriver
chromedriver_autoinstaller.install()

# Fingerprints
fingerprints = [
    {
        "languages": ["en-US", "en"],
        "vendor": "Google Inc.",
        "platform": "Linux x86_64",
        "webgl_vendor": "Intel Inc.",
        "renderer": "Intel Iris Xe Graphics",
    },
    {
        "languages": ["fr-FR", "fr"],
        "vendor": "Google Inc.",
        "platform": "Linux x86_64",
        "webgl_vendor": "NVIDIA Corporation",
        "renderer": "GeForce GTX 1080/PCIe/SSE2",
    },
    {
        "languages": ["es-ES", "es"],
        "vendor": "Google Inc.",
        "platform": "Linux i686",
        "webgl_vendor": "Intel Open Source Technology Center",
        "renderer": "Mesa DRI Intel HD Graphics 4000",
    }
]

def load_list_from_file(filename):
    try:
        with open(filename, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"[!] File '{filename}' tidak ditemukan.")
        return []

user_agents = load_list_from_file("user_agents.txt")
proxies = load_list_from_file("proxies.txt")

def bersihkan_cache():
    try:
        path_cache = os.path.expanduser("~/.undetected_chromedriver")
        if os.path.exists(path_cache):
            rmtree(path_cache)
    except Exception as e:
        print(f"[!] Gagal hapus cache: {e}")

def klik_play(driver, timeout=10):
    try:
        wait = WebDriverWait(driver, timeout)
        tombol_play = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "div.bigPlayUIInner.ctp")
        ))
        time.sleep(random.uniform(1, 3))
        tombol_play.click()
        print("[INFO] Tombol Play diklik.")
    except Exception as e:
        print(f"[ERROR] Tidak bisa klik Play: {e}")

def klik_skip_iklan(driver):
    selectors = [
        (By.CSS_SELECTOR, "body > div.videoAdUi > div.videoAdUiBottomBar > div > div.videoAdUiSkipContainer.html5-stop-propagation > button"),
        (By.CSS_SELECTOR, ".videoAdUiSkipButton.videoAdUiAction.videoAdUiRedesignedSkipButton"),
        (By.XPATH, "//button[contains(text(), 'Skip Ad')]")
    ]
    for by, sel in selectors:
        try:
            btn = driver.find_element(by, sel)
            btn.click()
            print("[INFO] Skip iklan diklik.")
            break
        except:
            continue

def randomize_timezone():
    return random.choice(["America/New_York", "Europe/London", "Asia/Tokyo"])

def randomize_canvas_fingerprint():
    return '''
    var canvas = document.createElement('canvas');
    var ctx = canvas.getContext('2d');
    ctx.textBaseline = 'top';
    ctx.font = '14px Arial';
    ctx.fillText('fingerprint', 2, 2);
    canvas.toDataURL();
    '''

def jalankan_browser(index, url):
    try:
        # Menentukan path chromedriver yang benar
        chromedriver_path = which("chromedriver")
        if not chromedriver_path:
            print(f"[ERROR] Chromedriver tidak ditemukan!")
            return

        print(f"[{time.strftime('%H:%M:%S')}] [Thread-{index}] Membuka: {url}")
        options = uc.ChromeOptions()
        options.binary_location = '/usr/bin/google-chrome-stable'
        options.add_argument(f"executable_path={chromedriver_path}")

        if user_agents:
            ua = random.choice(user_agents)
            options.add_argument(f"user-agent={ua}")
            print(f"[Thread-{index}] UA: {ua}")

        if proxies:
            proxy = random.choice(proxies)
            options.add_argument(f"--proxy-server=http://{proxy}")
            print(f"[Thread-{index}] Proxy: {proxy}")

        win_size = f"{random.randint(1024, 1920)},{random.randint(768, 1080)}"
        options.add_argument(f"--window-size={win_size}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--start-maximized")
        options.add_argument("--headless")  # Menggunakan headless mode standar
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")

        driver = uc.Chrome(options=options)

        fp = random.choice(fingerprints)
        script = f'''
        Object.defineProperty(navigator, 'languages', {{ get: () => {fp["languages"]} }}); 
        Object.defineProperty(navigator, 'vendor', {{ get: () => "{fp["vendor"]}" }}); 
        Object.defineProperty(navigator, 'platform', {{ get: () => "{fp["platform"]}" }}); 
        WebGLRenderingContext.prototype.getParameter = new Proxy(WebGLRenderingContext.prototype.getParameter, {{
            apply: function(target, ctx, args) {{
                if (args[0] === 37445) return "{fp["webgl_vendor"]}";
                if (args[0] === 37446) return "{fp["renderer"]}";
                return Reflect.apply(target, ctx, args);
            }}
        }});
        Object.defineProperty(Intl.DateTimeFormat.prototype, 'resolvedOptions', {{
            value: function() {{
                return {{ timeZone: '{randomize_timezone()}' }};
            }}
        }});
        {randomize_canvas_fingerprint()}
        '''
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": script})

        driver.get(url)
        time.sleep(15)
        klik_play(driver)
        time.sleep(15)
        klik_skip_iklan(driver)

        time.sleep(120)  # Tonton 2 menit
        driver.quit()
        print(f"[{time.strftime('%H:%M:%S')}] [Thread-{index}] Browser ditutup.\n")

    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] [Thread-{index}] ERROR: {e}")

def start_looping_browser(urls, jumlah_threads=10):
    def worker(thread_index):
        while True:
            url = random.choice(urls)
            bersihkan_cache()
            jalankan_browser(thread_index, url)
            time.sleep(random.randint(5, 15))

    threads = []
    for i in range(jumlah_threads):
        t = threading.Thread(target=worker, args=(i + 1,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

def main():
    urls = load_list_from_file("urls.txt")
    if not urls:
        print("[!] Tidak ada URL di 'urls.txt'!")
        return

    print("[INFO] Menjalankan 10 thread paralel...")
    start_looping_browser(urls, jumlah_threads=10)

if __name__ == "__main__":
    main()
