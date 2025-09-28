import requests
from bs4 import BeautifulSoup
import smtplib
import os

# 🔑 Load secrets (from GitHub Actions)
EMAIL = os.getenv("ALERT_EMAIL")
PASSWORD = os.getenv("ALERT_PASSWORD")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ✅ Amazon product URL and target price (INR)
PRODUCT_URL = "https://www.amazon.in/dp/B0F9FJ2PRQ"
TARGET_PRICE = 4000

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                  " AppleWebKit/537.36 (KHTML, like Gecko)"
                  " Chrome/117.0.0.0 Safari/537.36",
    "Accept-Language": "en-IN,en;q=0.9"
}

def get_price():
    try:
        response = requests.get(PRODUCT_URL, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        title_tag = soup.select_one("#productTitle")
        price_tag = soup.select_one(".a-price-whole")

        if not title_tag or not price_tag:
            print("[WARN] Could not find title or price. Amazon page structure might have changed.")
            return None, None

        title = title_tag.get_text(strip=True)
        price = int(price_tag.get_text(strip=True).replace(",", ""))

        return title, price

    except Exception as e:
        print(f"[ERROR] Failed to fetch price: {e}")
        return None, None

def send_email(subject, body):
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL, PASSWORD)
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(EMAIL, EMAIL, message)
            print("[INFO] Email sent successfully!")
    except Exception as e:
        print(f"[ERROR] Email not sent: {e}")

def send_telegram(body):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": body}
        requests.post(url, data=payload)
        print("[INFO] Telegram alert sent successfully!")
    except Exception as e:
        print(f"[ERROR] Telegram not sent: {e}")

def main():
    title, price = get_price()
    if not title or not price:
        print("[INFO] Skipping alert, no valid price found.")
        return

    print(f"[INFO] {title} → Current Price: ₹{price}")
    if price <= TARGET_PRICE:
        alert = f"🔥 PRICE DROP ALERT 🔥\n\n{title}\nCurrent Price: ₹{price}\n{PRODUCT_URL}"
        send_email("Amazon Price Drop Alert!", alert)
        send_telegram(alert)
    else:
        print("[INFO] Price is still higher than target.")

if __name__ == "__main__":
    main()
