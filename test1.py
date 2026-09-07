import requests
from bs4 import BeautifulSoup
import os


# ========================================
# 股票設定
# ========================================

stock = ["2337"]


# ========================================
# Telegram 設定
# ========================================

# 從 GitHub Secrets 取得 Bot Token
token = os.environ.get("TELEGRAM_BOT_TOKEN")

# 你的 Telegram Chat ID
chat_id = "8938101262"


# 確認 Token 是否存在
if not token:
    raise Exception(
        "❌ 找不到 Telegram Bot Token！\n"
        "請確認 GitHub Secrets 是否設定："
        "TELEGRAM_BOT_TOKEN"
    )


# ========================================
# Telegram API
# ========================================

telegram_url = (
    "https://api.telegram.org/bot"
    + token
    + "/sendMessage"
)


# ========================================
# 股票爬蟲
# ========================================

for i in range(len(stock)):

    stockid = stock[i]

    print("========================================")
    print("開始抓取股票：" + stockid)
    print("========================================")


    # Yahoo 股市網址
    url = (
        "https://tw.stock.yahoo.com/quote/"
        + stockid
        + ".TW"
    )


    # User-Agent
    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }


    # ========================================
    # 取得 Yahoo 網頁
    # ========================================

    r = requests.get(
        url,
        headers=headers,
        timeout=15
    )


    if r.status_code != 200:
        raise Exception(
            "❌ Yahoo 股市連線失敗！\n"
            "HTTP Status："
            + str(r.status_code)
        )


    # ========================================
    # BeautifulSoup 解析
    # ========================================

    soup = BeautifulSoup(
        r.text,
        "html.parser"
    )


    # ========================================
    # 找股票價格
    # ========================================

    price = None
    trend = "➡️ 平盤"


    spans = soup.find_all("span")


    for span in spans:

        class_list = span.get("class", [])


        # Yahoo 股價基本 class
        required_class = [
            "Fz(32px)",
            "Fw(b)",
            "Lh(1)",
            "Mend(16px)",
            "D(f)",
            "Ai(c)"
        ]


        # 判斷是否為股票價格
        if all(
            x in class_list
            for x in required_class
        ):

            text = span.get_text(
                strip=True
            )


            # 確認內容是數字
            if (
                text
                and any(
                    char.isdigit()
                    for char in text
                )
            ):

                price = text


                # ====================================
                # 判斷漲跌
                # ====================================

                if "C($c-trend-up)" in class_list:

                    trend = "📈 上漲"


                elif "C($c-trend-down)" in class_list:

                    trend = "📉 下跌"


                else:

                    trend = "➡️ 平盤"


                break


    # ========================================
    # 確認股價是否取得成功
    # ========================================

    if price is None:

        raise Exception(
            "❌ 找不到股票 "
            + stockid
            + " 的股價！\n"
            "可能是 Yahoo 股市網頁格式變更。"
        )


    print("股票代號：" + stockid)
    print("即時股價：" + price)
    print("狀態：" + trend)


    # ========================================
    # Telegram 訊息
    # ========================================

    message = (
        "📊 股票即時股價通知\n"
        "\n"
        "股票代號：" + stockid + "\n"
        "即時股價：" + price + "\n"
        "狀態：" + trend
    )


    # ========================================
    # 發送 Telegram
    # ========================================

    response = requests.get(
        telegram_url,
        params={
            "chat_id": chat_id,
            "text": message
        },
        timeout=15
    )


    result = response.json()


    # ========================================
    # 確認 Telegram 是否成功
    # ========================================

    if not result.get("ok"):

        print("❌ Telegram 發送失敗")
        print(response.text)

        raise Exception(
            "Telegram 訊息發送失敗！"
        )


    print("✅ Telegram 發送成功！")
    print("----------------------------------------")
    print(message)
    print("----------------------------------------")


print("\n========================================")
print("✅ 股票助手執行完成！")
print("========================================")
