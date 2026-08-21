# -*- coding: utf-8 -*-
"""
Netflix / Prime Videoの配信終了予定を取得し、Xに投稿するメインスクリプト。
Netflix・Prime Videoはそれぞれ別のツイートとして投稿する。

投稿モードは2種類:
  daily  = 本日(23:59まで)に配信終了する作品のみ(毎朝8時に投稿)
  weekly = 今週の土曜日(23:59)までに配信終了する作品一覧(毎週日曜0:01に投稿)

ローカルでテストする場合:
  1. .env ファイルなどでAPIキーを環境変数に設定
  2. python main.py --dry-run             で投稿せず内容だけ確認(daily)
  3. python main.py --mode weekly --dry-run  で週間モードの内容を確認
  4. python main.py                       で実際に投稿
"""
import sys
import argparse
import datetime

from scrape_netflix import fetch_netflix_expiring
from scrape_prime import fetch_prime_expiring
from compose import build_netflix_tweet, build_prime_tweet, JST
from post_x import post_tweet, MAX_IMAGES


def _weekly_days_ahead():
    """今日から今週土曜日までの日数(日曜に実行すれば6になる)"""
    today = datetime.datetime.now(JST).date()
    return (5 - today.weekday()) % 7


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
    parser.add_argument(
        "--mode",
        choices=["daily", "weekly"],
        default="daily",
        help="daily=本日終了分のみ、weekly=今週土曜までの一覧",
    )
    args = parser.parse_args()

    days_ahead = 0 if args.mode == "daily" else _weekly_days_ahead()

    try:
        netflix_items = fetch_netflix_expiring(target_days_ahead=days_ahead)
    except Exception as e:
        print(f"[警告] Netflix情報の取得に失敗しました: {e}", file=sys.stderr)
        netflix_items = []

    try:
        prime_items = fetch_prime_expiring(target_days_ahead=days_ahead)
    except Exception as e:
        print(f"[警告] Prime Video情報の取得に失敗しました: {e}", file=sys.stderr)
        prime_items = []

    _handle_post(
        "Netflix",
        build_netflix_tweet(netflix_items, mode=args.mode),
        _thumbnails(netflix_items),
        args.dry_run,
    )
    _handle_post(
        "Prime Video",
        build_prime_tweet(prime_items, mode=args.mode),
        _thumbnails(prime_items),
        args.dry_run,
    )


if __name__ == "__main__":
    main()
