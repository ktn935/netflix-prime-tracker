# -*- coding: utf-8 -*-
"""
Netflix / Prime Videoの配信終了予定を取得し、Xに投稿するメインスクリプト。

ローカルでテストする場合:
  1. .env ファイルなどでAPIキーを環境変数に設定
  2. python main.py --dry-run  で投稿せず内容だけ確認
  3. python main.py            で実際に投稿
"""
import sys
import argparse

from scrape_netflix import fetch_netflix_expiring
from scrape_prime import fetch_prime_expiring
from compose import build_tweet
from post_x import post_tweet


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

    text = build_tweet(netflix_items, prime_items)

    if text is None:
        print("投稿対象の作品がありませんでした。投稿をスキップします。")
        return

    print("----- 生成された投稿文 -----")
    print(text)
    print(f"文字数: {len(text)}")
    print("----------------------------")

    if args.dry_run:
        print("(--dry-run のため実際の投稿は行いません)")
        return

    response = post_tweet(text)
    print("投稿しました:", response)


if __name__ == "__main__":
    main()
