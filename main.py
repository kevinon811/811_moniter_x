import tweepy
import requests
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# X API 憑證
API_KEY = "你的API_KEY"
API_SECRET = "你的API_SECRET"
ACCESS_TOKEN = "你的ACCESS_TOKEN"
ACCESS_TOKEN_SECRET = "你的ACCESS_TOKEN_SECRET"

# ntfy.sh 主題
NTFY_TOPIC = "fakeloh-updates"

# 設置 X API 認證
auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

# 目標帳號
TARGET_USER = "fakeloh"

# 儲存最新貼文和回覆的 ID
last_tweet_id = None
last_reply_id = None

# ntfy.sh 通知函數
def send_ntfy_notify(message):
    url = f"https://ntfy.sh/{NTFY_TOPIC}"
    response = requests.post(url, data=message.encode("utf-8"))
    if response.status_code == 200:
        print("通知發送成功")
    else:
        print(f"通知發送失敗: {response.text}")

# 獲取貼文數和回覆數
def get_tweet_and_reply_counts():
    try:
        user = api.get_user(screen_name=TARGET_USER)
        total_tweets = user.statuses_count  # 包含貼文和回覆的總數
        # 獲取最近的貼文，過濾出回覆
        tweets = api.user_timeline(screen_name=TARGET_USER, count=100, tweet_mode="extended")
        reply_count = sum(1 for tweet in tweets if tweet.in_reply_to_status_id is not None)
        # 假設 total_tweets 是準確的，貼文數 = 總數 - 回覆數
        tweet_count = total_tweets - reply_count
        return tweet_count, reply_count, total_tweets
    except tweepy.TweepyException as e:
        print(f"獲取計數失敗: {e}")
        return 0, 0, 0

# 監控函數
def monitor_tweets():
    global last_tweet_id, last_reply_id
    while True:
        try:
            # 獲取最新的貼文和回覆
            tweets = api.user_timeline(screen_name=TARGET_USER, count=10, tweet_mode="extended")
            if tweets:
                for tweet in tweets:
                    tweet_id = tweet.id
                    tweet_text = tweet.full_text
                    is_reply = tweet.in_reply_to_status_id is not None

                    # 處理回覆
                    if is_reply and (last_reply_id is None or tweet_id > last_reply_id):
                        tweet_count, reply_count, total_tweets = get_tweet_and_reply_counts()
                        message = (
                            f"[{datetime.now()}] fakeloh 新回覆:\n{tweet_text}\n"
                            f"目前貼文數: {tweet_count} | 回覆數: {reply_count} | 總數: {total_tweets}"
                        )
                        print(message)
                        send_ntfy_notify(message)
                        last_reply_id = tweet_id

                    # 處理貼文（非回覆）
                    elif not is_reply and (last_tweet_id is None or tweet_id > last_tweet_id):
                        tweet_count, reply_count, total_tweets = get_tweet_and_reply_counts()
                        message = (
                            f"[{datetime.now()}] fakeloh 新貼文:\n{tweet_text}\n"
                            f"目前貼文數: {tweet_count} | 回覆數: {reply_count} | 總數: {total_tweets}"
                        )
                        print(message)
                        send_ntfy_notify(message)
                        last_tweet_id = tweet_id

        except tweepy.TweepyException as e:
            print(f"錯誤: {e}")
        
        time.sleep(60)  # 每 60 秒檢查一次

# 簡單的 HTTP 伺服器，防止休眠
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")

def run_server():
    server_address = ("", 8000)
    httpd = HTTPServer(server_address, SimpleHandler)
    print("HTTP 伺服器啟動於端口 8000")
    httpd.serve_forever()

if __name__ == "__main__":
    # 啟動 HTTP 伺服器以防止休眠
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    monitor_tweets()
