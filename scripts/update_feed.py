#!/usr/bin/env python3
"""Merge each Substack RSS snapshot into a persistent JSON archive."""
import html, json, re, urllib.request, xml.etree.ElementTree as ET
from pathlib import Path
FEED_URL = "https://zeynepcancelikoglu.substack.com/feed"
OUTPUT = Path("posts.json")
def clean_text(value):
    value = html.unescape(value or "")
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\\s+", " ", value).strip()
def main():
    req = urllib.request.Request(FEED_URL, headers={"User-Agent":"WakeAndWonderFeed/1.0"})
    with urllib.request.urlopen(req, timeout=30) as response: root = ET.fromstring(response.read())
    existing = {}
    if OUTPUT.exists():
        try:
            for post in json.loads(OUTPUT.read_text(encoding="utf-8")):
                key = post.get("url") or post.get("id")
                if key: existing[key] = post
        except (json.JSONDecodeError, TypeError): print("Could not parse existing archive; rebuilding from feed.")
    channel = root.find("channel")
    if channel is None: raise RuntimeError("RSS channel not found")
    for item in channel.findall("item"):
        title = clean_text(item.findtext("title")); link = (item.findtext("link") or "").strip()
        if not title or not link: continue
        existing[link] = {"id":(item.findtext("guid") or link).strip(),"title":title,"url":link,
          "date":(item.findtext("pubDate") or "").strip(),
          "description":clean_text(item.findtext("description"))[:320],"category":"Journal"}
    posts = sorted(existing.values(),key=lambda p:p.get("date",""),reverse=True)
    OUTPUT.write_text(json.dumps(posts,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Saved {len(posts)} posts.")
if __name__ == "__main__": main()
