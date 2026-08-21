# -*- coding: utf-8 -*-
"""
Netflix / Prime Videoの配信終了予定を取得し、Xに投稿するメインスクリプト。
Netflix・Prime Videoはそれぞれ別のツイートとして投稿する。

ローカルでテストする場合:
  1. .env ファイルなどでAPIキーを環境変数に設定
  2. python main.py --dry-run  で投稿せず内容だけ確認
  3. python main.py            で実際に投稿
"""
import sys
import argparse

from scrape_netflix import fetch_netflix_expiring
from scrape_prime import fetch_prime_expiring
from compose import build_netflix_tweet, build_prime_tweet
from post_x import post_tweet, MAX_IMAGES


def _thumbnails(items, max_images=MAX_IMAGES):
    return [it["thumbnail"] for it in items if it.get("thumbnail")][:max_images]


def _handle_post(label, text, image_urls, dry_run):
    if text is None:
        print(f"[{label}] 投稿対象の作品がありませんでした。投稿をスキップします。")
        return

    print(f"----- {label} 投稿文 -----")
    print(text)
    print(f"文字数: {len(text)}")
    print(f"添付画像: {len(image_urls)}枚")
    for u in image_urls:
        print("  -", u)
    print("----------------------------")

    if dry_run:
        print("(--dry-run のため実際の投稿は行いません)")
        return

    response = post_tweet(text, image_urls=image_urls)
    print(f"[{label}] 投稿しました:", response)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="投稿せず、生成される文章を表示するだけ",
    )
    args = parser.parse_args()

    try:
        netflix_items = fetch_netflix_expiring(target_days_ahead=1)
    except Exception as e:
        print(f"[警告] Netflix情報の取得に失敗しました: {e}", file=sys.stderr)
        netflix_items = []

    try:
        prime_items = fetch_prime_expiring(target_days_ahead=1)
    except Exception as e:
        print(f"[警告] Prime Video情報の取得に失敗しました: {e}", file=sys.stderr)
        prime_items = []

    _handle_post(
        "Netflix",
        build_netflix_tweet(netflix_items),
        _thumbnails(netflix_items),
        args.dry_run,
    )
    _handle_post(
        "Prime Video",
        build_prime_tweet(prime_items),
        _thumbnails(prime_items),
        args.dry_run,
    )


if __name__ == "__main__":
    main()
