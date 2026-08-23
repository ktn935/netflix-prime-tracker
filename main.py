# -*- coding: utf-8 -*-
"""
Netflix / Prime Videoの配信終了予定を取得し、Xに投稿するメインスクリプト。
Netflix・Prime Videoはそれぞれ別のツイートとして投稿する。

投稿モードは2種類:
  daily   = 本日(23:59まで)に配信終了する作品のみ(毎朝8時に投稿)
  weekend = 金曜(当日)〜日曜(23:59)までに配信終了する作品一覧(毎週金曜18:30に投稿)

ローカルでテストする場合:
  1. .env ファイルなどでAPIキーを環境変数に設定
  2. python main.py --dry-run              で投稿せず内容だけ確認(daily)
  3. python main.py --mode weekend --dry-run  で週末モードの内容を確認
  4. python main.py                        で実際に投稿
"""
import sys
import argparse
import datetime

from scrape_netflix import fetch_netflix_expiring
from scrape_prime import fetch_prime_expiring
from compose import build_netflix_tweet, build_prime_tweet, JST
from make_collage import make_collage
from make_text_card import make_text_card
from post_x import post_tweet


def _weekend_days_ahead():
    """今日(金曜想定)から日曜日までの日数(金曜に実行すれば2になる)"""
    today = datetime.datetime.now(JST).date()
    return (6 - today.weekday()) % 7


def _handle_post(label, text, items, service, mode, today, days_remaining, dry_run):
    if text is None:
        print(f"[{label}] 投稿対象の作品がありませんでした。投稿をスキップします。")
        return

    collage_bytes = make_collage(items, service)
    text_card = make_text_card(
        items, service, mode=mode, reference_date=today, days_remaining=days_remaining,
    )
    images = ([collage_bytes] if collage_bytes else []) + ([text_card] if text_card else [])

    print(f"----- {label} 投稿文 -----")
    print(text)
    print(f"文字数: {len(text)}")
    print(f"添付画像: {len(images)}枚(サムネ一覧{'あり' if collage_bytes else 'なし'}/文字カード{'あり' if text_card else 'なし'})")
    print("----------------------------")

    if dry_run:
        print("(--dry-run のため実際の投稿は行いません)")
        return

    response = post_tweet(text, images=images)
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
        choices=["daily", "weekend"],
        default="daily",
        help="daily=本日終了分のみ、weekend=金〜日曜までの一覧",
    )
    parser.add_argument(
        "--days-ahead",
        type=int,
        default=None,
        help="対象日数を直接指定する(動作確認用。指定時はmodeの自動計算より優先)",
    )
    args = parser.parse_args()

    today = datetime.datetime.now(JST).date()

    if args.days_ahead is not None:
        days_ahead = args.days_ahead
    else:
        days_ahead = 0 if args.mode == "daily" else _weekend_days_ahead()

    # 文字カード右上の「あと◯日」リボンバッジ用(0以下なら「本日ラスト」表記になる)
    deadline_date = today + datetime.timedelta(days=days_ahead)
    days_remaining = (deadline_date - today).days

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
        build_netflix_tweet(netflix_items, mode=args.mode, reference_date=today),
        netflix_items,
        "netflix",
        args.mode,
        today,
        days_remaining,
        args.dry_run,
    )
    _handle_post(
        "Prime Video",
        build_prime_tweet(prime_items, mode=args.mode, reference_date=today),
        prime_items,
        "prime",
        args.mode,
        today,
        days_remaining,
        args.dry_run,
    )


if __name__ == "__main__":
    main()
