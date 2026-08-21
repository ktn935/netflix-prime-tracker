# -*- coding: utf-8 -*-
"""
取得した作品リストから、Xに投稿する文章を組み立てる。
"""

MAX_LEN = 270  # X上限(280)より少し余裕を持たせる
MAX_TITLES_PER_SERVICE = 5


def _format_titles(items, max_titles=MAX_TITLES_PER_SERVICE):
    if not items:
        return None
    titles = [it["title"] for it in items[:max_titles]]
    line = "・" + "\n・".join(titles)
    if len(items) > max_titles:
        line += f"\n他{len(items) - max_titles}作品"
    return line


def build_tweet(netflix_items, prime_items):
    today_str = _today_label()
    parts = [f"【本日〜明日 配信終了予定】{today_str}"]

    nf_line = _format_titles(netflix_items)
    if nf_line:
        parts.append(f"\n■Netflix\n{nf_line}")

    pv_line = _format_titles(prime_items)
    if pv_line:
        parts.append(f"\n■Prime Video\n{pv_line}")

    if not nf_line and not pv_line:
        return None  # 投稿すべき内容がない

    text = "".join(parts)

    if len(text) > MAX_LEN:
        text = text[: MAX_LEN - 1] + "…"

    return text


def _today_label():
    import datetime
    return datetime.date.today().strftime("%m/%d")


if __name__ == "__main__":
    sample_nf = [{"title": "サンプル作品A", "date": "08/22"}]
    sample_pv = [{"title": "サンプル作品B", "date": "08/22"}]
    print(build_tweet(sample_nf, sample_pv))
