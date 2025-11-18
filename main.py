import os
import requests
import hashlib
import time
import urllib.parse

# Xuan酱 UID
BILIBILI_UID = "14848367"
UP_NAME = "Xuan酱"

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
DATABASE_ID = os.environ["DATABASE_ID"]

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

# -------------------------
# WBI 签名算法（官方逆向）
# -------------------------

def get_wbi_mixin_key(img_url, sub_url):
    mixin = img_url.split('/')[-1].split('.')[0] + sub_url.split('/')[-1].split('.')[0]
    table = "f2lup9mdqc6jkvwt7s8neb4ga5yhrx13"
    return "".join([mixin[int(i)] for i in range(32)])


def get_wbi_params(params):
    # 获取 wbi key
    nav = requests.get("https://api.bilibili.com/x/web-interface/nav").json()
    img_url = nav["data"]["wbi_img"]["img_url"]
    sub_url = nav["data"]["wbi_img"]["sub_url"]
    mixin_key = get_wbi_mixin_key(img_url, sub_url)

    params = dict(sorted(params.items()))
    query = urllib.parse.urlencode(params)
    to_sign = query + mixin_key
    sign = hashlib.md5(to_sign.encode()).hexdigest()

    params["wts"] = int(time.time())
    params["w_rid"] = sign
    return params


# -------------------------
# 调用 B 站官方 API 获取视频
# -------------------------

def fetch_bilibili_videos(uid):
    api = "https://api.bilibili.com/x/space/wbi/arc/search"

    base_params = {
        "mid": uid,
        "ps": 30,
        "pn": 1,
        "order": "pubdate",
        "index": 1
    }

    params = get_wbi_params(base_params)

    resp = requests.get(api, params=params).json()

    if resp["code"] != 0:
        print("API error:", resp)
        return []

    vlist = resp["data"]["list"]["vlist"]
    return vlist


# -------------------------
# 写入 Notion
# -------------------------

def send_to_notion(title, url, published, author, thumbnail):
    data = {
        "parent": {"database_id": DATABASE_ID},

        # 页面封面，让 Notion Gallery 显示大图
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


# -------------------------
# 主流程
# -------------------------

def main():
    print("Fetching videos for Xuan酱 ...")

    videos = fetch_bilibili_videos(BILIBILI_UID)

    print("Total videos found:", len(videos))

    for v in videos[:3]:  # 取最新三条
        title = v["title"]
        bvid = v["bvid"]
        url = f"https://www.bilibili.com/video/{bvid}"
        published = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(v["created"]))
        thumbnail = v["pic"]

        print("Sending:", title, url, published, thumbnail)
        send_to_notion(title, url, published, UP_NAME, thumbnail)


if __name__ == "__main__":
    main()
