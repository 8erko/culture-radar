#!/usr/bin/env python3
"""
Culture Radar – Reddit Miner
Zieht taeglich echte Top-Posts + Top-Kommentare aus Berks Subreddits
und schreibt sie als data/latest.json (+ dated Archiv).

Nutzt Reddits oeffentliche .json-Endpunkte (kein API-Key noetig).
Laeuft kostenlos via GitHub Actions.
"""
import json, os, time, datetime, urllib.request, urllib.error

# ---- Config laden ----
HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "config.json"), "r", encoding="utf-8") as f:
    CFG = json.load(f)

SUBREDDITS      = CFG["subreddits"]          # Liste {name, keywords?, min_score?}
TOP_TIMEFRAME   = CFG.get("timeframe", "day")  # day / week
POSTS_PER_SUB   = CFG.get("posts_per_sub", 12)
COMMENTS_PER_POST = CFG.get("comments_per_post", 4)
GLOBAL_MIN_SCORE  = CFG.get("min_score", 20)
UA = {"User-Agent": "culture-radar-miner/1.0 (daily personal trend digest)"}

def fetch(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            print(f"  retry {i+1} for {url}: {e}")
            time.sleep(4 * (i + 1))
    return None

def matches(text, keywords):
    if not keywords:
        return True
    t = (text or "").lower()
    return any(k.lower() in t for k in keywords)

def get_top_comments(permalink, limit):
    data = fetch(f"https://www.reddit.com{permalink}.json?limit={limit}&sort=top")
    out = []
    if not data or len(data) < 2:
        return out
    for c in data[1]["data"]["children"]:
        d = c.get("data", {})
        body = d.get("body")
        if not body or d.get("stickied"):
            continue
        out.append({
            "body": body.strip()[:600],
            "author": d.get("author", "[unknown]"),
            "score": d.get("score", 0),
            "permalink": "https://www.reddit.com" + d.get("permalink", ""),
        })
        if len(out) >= limit:
            break
    return out

def mine_sub(sub):
    name = sub["name"]
    keywords = sub.get("keywords", [])
    min_score = sub.get("min_score", GLOBAL_MIN_SCORE)
    print(f"r/{name} ...")
    data = fetch(f"https://www.reddit.com/r/{name}/top.json?t={TOP_TIMEFRAME}&limit=40")
    posts = []
    if not data:
        return {"name": name, "posts": posts, "error": "fetch_failed"}
    for child in data["data"]["children"]:
        d = child["data"]
        if d.get("stickied") or d.get("score", 0) < min_score:
            continue
        if not matches(d.get("title", "") + " " + d.get("selftext", ""), keywords):
            continue
        permalink = d.get("permalink", "")
        post = {
            "title": d.get("title", "").strip(),
            "url": "https://www.reddit.com" + permalink,
            "score": d.get("score", 0),
            "num_comments": d.get("num_comments", 0),
            "flair": d.get("link_flair_text"),
            "created_utc": d.get("created_utc"),
            "selftext": (d.get("selftext", "") or "")[:500],
            "top_comments": get_top_comments(permalink, COMMENTS_PER_POST),
        }
        posts.append(post)
        time.sleep(1.5)  # hoeflich gegenueber Reddit
        if len(posts) >= POSTS_PER_SUB:
            break
    return {"name": name, "posts": posts}

def main():
    result = {
        "generated_utc": datetime.datetime.utcnow().isoformat() + "Z",
        "date": datetime.date.today().isoformat(),
        "subreddits": [mine_sub(s) for s in SUBREDDITS],
    }
    out_dir = os.path.join(HERE, "data")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "latest.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    with open(os.path.join(out_dir, f"{result['date']}.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    total = sum(len(s["posts"]) for s in result["subreddits"])
    print(f"Fertig: {total} Posts in data/latest.json")

if __name__ == "__main__":
    main()
