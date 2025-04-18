import tweepy
import requests
from datetime import datetime

# X API 憑證
API_KEY = "你的API_KEY"
API_SECRET = "你的API_SECRET"
ACCESS_TOKEN = "你的ACCESS_TOKEN"
ACCESS_TOKEN_SECRET = "你的ACCESS_TOKEN_SECRET"

# ntfy.sh 主題
NTFY_TOPIC = "811_moniter_x"

# 目標帳號
TARGET_USER = "fakeloh"

# 設置 X API 認證
auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

# 獲取貼文數和回覆數
def get_tweet_and_reply_counts():
    try:
        user = api.get_user(screen_name=TARGET_USER)
        total_tweets = user.statuses_count
        tweets = api.user_timeline(screen_name=TARGET_USER, count=100, tweet_mode="extended")
        reply_count = sum(1 for tweet in tweets if tweet.in_reply_to_status_id is not None)
        tweet_count = total_tweets - reply_count
        return tweet_count, reply_count, total_tweets
    except tweepy.TweepyException as e:
        print(f"獲取計數失敗: {e}")
        return 0, 0, 0

# 生成測試通知
def generate_test_notification():
    tweet_count, reply_count, total_tweets = get_tweet_and_reply_counts()
    test_message = (
        f"[{datetime.now()}] fakeloh 測試訊息:\n這是一條模擬貼文或回覆\n"
        f"目前貼文數: {tweet_count} | 回覆數: {reply_count} | 總數: {total_tweets}"
    )
    # 輸出 curl 命令
    curl_command = (
        f'curl -d "{test_message}" https://ntfy.sh/{NTFY_TOPIC}'
    )
    print("請複製以下 curl 命令執行：")
    print(curl_command)
    
    # 直接發送測試通知
    url = f"https://ntfy.sh/{NTFY_TOPIC}"
    response = requests.post(url, data=test_message.encode("utf-8"))
    if response.status_code == 200:
        print("測試通知已發送")
    else:
        print(f"測試通知發送失敗: {response.text}")

if __name__ == "__main__":
    generate_test_notification()
