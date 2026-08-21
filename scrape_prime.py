# -*- coding: utf-8 -*-
"""
Amazon Prime Videoの「配信終了予定作品」を vedyro.com から取得する。

このスクリプトは非公式サイトのHTML構造に依存しています。
サイト側のデザインが変わると動かなくなる可能性があるため、
定期的に動作確認してください。
"""
import re
import html
import datetime
import requests

URL = "https://vedyro.com/prime-video/leaving-soon"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; PersonalVODBot/1.0; +https://example.com)"
}

# 作品カードのタイトルリンクのパターン:
# <a class="leaving-soon__title" href="/titles/xxxx?..." data-cta="detail" data-title="..." data-expire="2026-08-23">タイトル</a>
# data-expire属性に配信終了日(YYYY-MM-DD)が直接入っているので、これを使って日付判定する。
TITLE_CARD_RE = re.compile(
    r'<a class="leaving-soon__title" href="(/titles/\d+[^"]*)"[^>]*?'
    r'data-expire="(\d{4}-\d{2}-\d{2})"[^>]*>\s*([^<]+?)\s*</a>'
)


def fetch_prime_expiring(target_days_ahead=1):
    """
    target_days_ahead: 今日から何日以内の終了予定を対象にするか
    戻り値: [{"title": str, "date": "MM/DD"}, ...]
    """
    resp = requests.get(URL, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    page_html = resp.text

    today = datetime.date.today()
    target_dates = {
        (today + datetime.timedelta(days=i)).strftime("%Y-%m-%d"):
            (today + datetime.timedelta(days=i)).strftime("%m/%d")
        for i in range(target_days_ahead + 1)
    }

    results = []
    seen_urls = set()
    for m in TITLE_CARD_RE.finditer(page_html):
        rel_url, iso_date, title_text = m.group(1), m.group(2), m.group(3)
        if iso_date not in target_dates:
            continue
        if rel_url in seen_urls:
            continue
        seen_urls.add(rel_url)
        results.append({"title": html.unescape(title_text), "date": target_dates[iso_date]})

    return results


if __name__ == "__main__":
    items = fetch_prime_expiring(target_days_ahead=1)
    for it in items:
        print(it["date"], it["title"])
    print(f"合計 {len(items)} 件")
