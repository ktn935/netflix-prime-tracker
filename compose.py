# -*- coding: utf-8 -*-
"""
取得した作品リストから、Xに投稿する文章を組み立てる。
"""

HASHTAGS = "#Netflix #NetflixJP #AmazonPrimeVideo #プライムビデオ #配信終了予定"


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


def build_tweet(netflix_items, prime_items):
    today_str = _today_label()
    parts = [f"【本日〜明日 配信終了予定】{today_str}"]

    nf_line = _format_titles(netflix_items)
    if nf_line:
        parts.append(f"\n■Netflix\n{nf_line}")

    pv_line = _format_titles(prime_items, with_link=True)
    if pv_line:
        parts.append(f"\n■Prime Video\n{pv_line}")

    if not nf_line and not pv_line:
        return None  # 投稿すべき内容がない

    parts.append(f"\n\n{HASHTAGS}")

    return "".join(parts)


def _today_label():
    import datetime
    jst = datetime.timezone(datetime.timedelta(hours=9))
    return datetime.datetime.now(jst).date().strftime("%m/%d")


if __name__ == "__main__":
    sample_nf = [{"title": "サンプル作品A", "date": "08/22"}]
    sample_pv = [{"title": "サンプル作品B", "date": "08/22", "url": "https://www.amazon.co.jp/dp/XXXX?tag=nomissvod-22"}]
    print(build_tweet(sample_nf, sample_pv))
