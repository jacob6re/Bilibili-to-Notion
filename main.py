import os
import feedparser
import requests

# ⚠️ 将你的 B 站 UID 放在这里
BILIBILI_UIDS = [
    {"name": "Xuan酱", "uid": "14848367"},
    # {"name": "你的博主名2", "uid": "654321"},
]

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
DATABASE_ID = os.environ["DATABASE_ID"]

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def send_to_notion(title, url, published, author, thumbnail):
    data = {
        "parent": {"database_id": DATABASE_ID},

        # 设置页面封面（Notion Gallery 会显示）
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
    print("Notion status:", r.status_code, r.text)

def fetch_bilibili(uid, author):
    rss = f"https://rsshub.app/bilibili/user/video/{uid}"
    print(f"\nFetching RSS for {author}: {rss}")
    feed = feedparser.parse(rss)

    print(f"Found {len(feed.entries)} items for {author}")

    for entry in feed.entries[:3]:  # 最新 3 条
        title = entry.title
        link = entry.link
        published = entry.published

        # 封面解析
        try:
            thumbnail = entry.media_thumbnail[0]["url"]
        except:
            thumbnail = None

        print("Sending:", title, link, published, thumbnail)
        send_to_notion(title, link, published, author, thumbnail)

def main():
    for item in BILIBILI_UIDS:
        fetch_bilibili(item["uid"], item["name"])

if __name__ == "__main__":
    main()
