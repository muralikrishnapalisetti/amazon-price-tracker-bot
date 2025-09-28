import requests
from bs4 import BeautifulSoup
import smtplib
import os

# 🔑 Load secrets (from GitHub Actions secrets)
EMAIL = os.getenv("ALERT_EMAIL")
PASSWORD = os.getenv("ALERT_PASSWORD")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ✅ Your Amazon product URL (Indian site)
PRODUCT_URL = "https://www.amazon.in/dp/B0CQ7Y9XYZ"  # Change this
TARGET_PRICE = 35000  # INR

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                  " AppleWebKit/537.36 (KHTML, like Gecko)"
                  " Chrome/117.0.0.0 Safari/537.36",
    "Accept-Language": "en-IN,en;q=0.9"
}


def get_price():
    response = requests.get(PRODUCT_URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    title = soup.select_one("#productTitle").get_text(strip=True)

    price_str = soup.select_one(".a-price-whole").get_text(strip=True).replace(",", "")
    price = int(price_str)

    return title, price


def send_email(subject, body):
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL, PASSWORD)
        message = f"Subject: {subject}\n\n{body}"
        server.sendmail(EMAIL, EMAIL, message)


def send_telegram(body):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": body}
    requests.post(url, data=payload)


def main():
    try:
        title, price = get_price()
        print(f"[INFO] {title} → Current Price: ₹{price}")

        if price <= TARGET_PRICE:
            alert = f"🔥 PRICE DROP ALERT 🔥\n\n{title}\nCurrent Price: ₹{price}\n{PRODUCT_URL}"
            send_email("Amazon Price Drop Alert!", alert)
            send_telegram(alert)
        else:
            print("[INFO] No price drop yet.")

    except Exception as e:
        print(f"[ERROR] {e}")


if __name__ == "__main__":
    main()
