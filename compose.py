# -*- coding: utf-8 -*-
"""
取得した作品リストから、Xに投稿する文章を組み立てる。
Netflix / Prime Videoはそれぞれ別のツイートとして投稿する。
"""

NETFLIX_HASHTAGS = "#Netflix #NetflixJP #配信終了予定"
PRIME_HASHTAGS = "#AmazonPrimeVideo #プライムビデオ #配信終了予定"


def _format_titles(items, with_link=False):
    if not items:
        return None
    lines = []
    for it in items:
        line = f"・{it['title']}"
        if with_link and it.get("url"):
            line += f"\n{it['url']}"
        lines.append(line)
    return "\n".join(lines)


def build_netflix_tweet(netflix_items):
    nf_line = _format_titles(netflix_items, with_link=True)
    if not nf_line:
        return None
    today_str = _today_label()
    return f"🟥【本日〜明日 配信終了予定】{today_str}\n🟥Netflix\n{nf_line}\n\n{NETFLIX_HASHTAGS}"


def build_prime_tweet(prime_items):
    pv_line = _format_titles(prime_items, with_link=True)
    if not pv_line:
        return None
    today_str = _today_label()
    return f"🟦【本日〜明日 配信終了予定】{today_str}\n🟦Prime Video\n{pv_line}\n\n{PRIME_HASHTAGS}"


def _today_label():
    import datetime
    jst = datetime.timezone(datetime.timedelta(hours=9))
    return datetime.datetime.now(jst).date().strftime("%m/%d")


if __name__ == "__main__":
    sample_nf = [{"title": "サンプル作品A", "date": "08/22", "url": "https://www.netflix.com/jp/title/XXXX"}]
    sample_pv = [{"title": "サンプル作品B", "date": "08/22", "url": "https://www.amazon.co.jp/dp/XXXX?tag=nomissvod-22"}]
    print(build_netflix_tweet(sample_nf))
    print()
    print(build_prime_tweet(sample_pv))
