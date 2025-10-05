import os
import re
import time
import requests # type: ignore
from bs4 import BeautifulSoup # type: ignore
from selenium import webdriver # type: ignore
from selenium.webdriver.chrome.options import Options # type: ignore
from PIL import Image, ImageFilter, ImageOps # type: ignore
import pytesseract # type: ignore

BASE_PAGE = "https://nopecha.com/demo/textcaptcha"
BASE_URL = "https://nopecha.com"
OUTPUT_DIR = "captchas"
OUTPUT_TEXT = "capture_codes.txt"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def setup_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    return webdriver.Chrome(options=options)

def download_image(url, idx):
    filename = os.path.join(OUTPUT_DIR, f"captcha_{idx}.jpeg")
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, stream=True, timeout=15)
    if resp.status_code == 200:
        with open(filename, "wb") as f:
            for chunk in resp.iter_content(1024):
                f.write(chunk)
        return filename
    return None

def preprocess_image(in_path, threshold=150):
    out_path = in_path.replace(".jpeg", "_proc.png")
    img = Image.open(in_path).convert("L")
    img = ImageOps.autocontrast(img)
    img = img.point(lambda p: 255 if p > threshold else 0)
    img = img.filter(ImageFilter.MedianFilter(size=3))
    img.save(out_path)
    return out_path

def run_ocr(image_path):
    config = r"--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    return pytesseract.image_to_string(Image.open(image_path), config=config)

def clean_text(raw_text):
    parts = re.findall(r"[A-Za-z0-9]+", raw_text.strip())
    return parts[0] if parts else ""

def collect_captchas(driver, count=10):
    urls = []
    driver.get(BASE_PAGE)
    time.sleep(3)

    for i in range(count):
        # Switch into iframe
        iframe = driver.find_element("tag name", "iframe")
        driver.switch_to.frame(iframe)

        # Parse captcha image
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        img = soup.find("img", {"class": "captchapict"})
        if img:
            url = BASE_URL + img["src"]
            urls.append(url)
            print(f"📥 Found captcha {i+1}: {url}")

        driver.switch_to.default_content()
        driver.refresh()
        time.sleep(3)

    return urls

def main():
    try:
        count = int(input("👉 Enter number of captchas to capture: "))
    except ValueError:
        print("⚠️ Invalid input. Defaulting to 5 captchas.")
        count = 5

    driver = setup_driver()
    results = []
    try:
        print("🌐 Collecting captchas...")
        image_urls = collect_captchas(driver, count=count)
        print(f"🔗 Collected {len(image_urls)} captcha URLs.")

        for idx, url in enumerate(image_urls, start=1):
            raw_file = download_image(url, idx)
            if not raw_file:
                print(f"❌ Failed to download {url}")
                continue

            proc_file = preprocess_image(raw_file)
            raw = run_ocr(proc_file)
            cleaned = clean_text(raw)

            print(f"🔍 OCR Raw: {repr(raw)}")
            print(f"✅ Cleaned: {cleaned or '(none)'}")

            results.append({
                "file": raw_file,
                "url": url,
                "raw": raw,
                "cleaned": cleaned
            })

        # Save results
        with open(OUTPUT_TEXT, "w", encoding="utf-8") as f:
            for r in results:
                f.write(f"Image: {r['file']}\n")
                f.write(f"URL: {r['url']}\n")
                f.write(f"OCR Raw: {r['raw']}\n")
                f.write(f"Cleaned: {r['cleaned']}\n")
                f.write("-" * 50 + "\n")

        print(f"\n💾 Results saved to {OUTPUT_TEXT}")
        print(f"🖼️ Captchas saved in: {OUTPUT_DIR}")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
