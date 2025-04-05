import tweepy
import requests
import time
from datetime import datetime

# X API 憑證
API_KEY = "s9iFWW9K8ckCExfY55JZLAINr"
API_SECRET = "nAqaNjPIUGQlYCqrST6ou5d9wxC2G3iB6pivCwSKFBzFExYNzU"
ACCESS_TOKEN = "1908479247167217669-dWy9a5ebiFUege3IGC6L1DB1oiYQaZ"
ACCESS_TOKEN_SECRET = "hc1Bof00u6lkM1KlBz6LGQ3jPCErmMdaHOTCg9qPc7jQT"

# ntfy.sh 主題
NTFY_TOPIC = "fakeloh-updates"

# 設置 X API 認證
auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

# 目標帳號
TARGET_USER = "fakeloh"

# 儲存最新貼文 ID
last_tweet_id = None

# ntfy.sh 通知函數
def send_ntfy_notify(message):
    url = f"https://ntfy.sh/{NTFY_TOPIC}"
    response = requests.post(url, data=message.encode("utf-8"))
    if response.status_code == 200:
        print("通知發送成功")
    else:
        print(f"通知發送失敗: {response.text}")

# 監控函數
def monitor_tweets():
    global last_tweet_id
    while True:
        try:
            tweets = api.user_timeline(screen_name=TARGET_USER, count=1, tweet_mode="extended")
            if tweets:
                latest_tweet = tweets[0]
                tweet_id = latest_tweet.id
                tweet_text = latest_tweet.full_text

                if last_tweet_id is None or tweet_id > last_tweet_id:
                    message = f"[{datetime.now()}] fakeloh 新貼文:\n{tweet_text}"
                    print(message)
                    send_ntfy_notify(message)
                    last_tweet_id = tweet_id

        except tweepy.TweepyException as e:
            print(f"錯誤: {e}")
        
        time.sleep(60)  # 每 60 秒檢查一次

if __name__ == "__main__":
    monitor_tweets()
