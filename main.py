import os
import requests
import time

# Xuan酱 UID
UID = "14848367"
UP_NAME = "Xuan酱"

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
DATABASE_ID = os.environ["DATABASE_ID"]

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

API_URL = f"https://biliworker.vercel.app/api/video_list?mid={UID}"

def fetch_videos():
    print("Fetching videos...")
    resp = requests.get(API_URL).json()
    return resp["data"]["list"]  # 视频列表

def send_to_notion(title, url, published, author, thumbnail):
    data = {
        "parent": {"database_id": DATABASE_ID},
        "cover": {
            "type": "external",
            "external": {"url": thumbnail}
        },
        "properties": {
            "Title": {"title": [{"text": {"content": title}}]},
            "URL": {"url": url},
            "Published": {"date": {"start": published}},
            "UP主": {"rich_text": [{"text": {"content": author}}]}
        }
    }
    r = requests.post("https://api.notion.com/v1/pages", json=data, headers=headers)
    print("Notion status:", r.status_code)

def main():
    videos = fetch_videos()
    print("Total videos:", len(videos))

    for v in videos[:3]:  # 最新 3 条
        title = v["title"]
        bvid = v["bvid"]
        link = f"https://www.bilibili.com/video/{bvid}"
        created = v["created"]
        published = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(created))
        pic = v["pic"]

        print("Sending:", title)
        send_to_notion(title, link, published, UP_NAME, pic)

if __name__ == "__main__":
    main()
