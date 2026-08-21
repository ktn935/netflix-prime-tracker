# -*- coding: utf-8 -*-
"""
Xへの投稿処理。
APIキー類は環境変数から読み込む(コードに直接書かない)。

必要な環境変数:
  X_API_KEY
  X_API_KEY_SECRET
  X_ACCESS_TOKEN
  X_ACCESS_TOKEN_SECRET
"""
import io
import os

import requests
import tweepy

MAX_IMAGES = 4


def _credentials():
    return (
        os.environ["X_API_KEY"].strip(),
        os.environ["X_API_KEY_SECRET"].strip(),
        os.environ["X_ACCESS_TOKEN"].strip(),
        os.environ["X_ACCESS_TOKEN_SECRET"].strip(),
    )


def get_client():
    api_key, api_secret, access_token, access_secret = _credentials()
    return tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_secret,
    )


def get_api_v1():
    """画像アップロードにはv1.1 APIが必要"""
    api_key, api_secret, access_token, access_secret = _credentials()
    auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
    return tweepy.API(auth)


def _upload_images(image_urls):
    api = get_api_v1()
    media_ids = []
    for url in image_urls[:MAX_IMAGES]:
        try:
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
            media = api.media_upload(filename="thumbnail.jpg", file=io.BytesIO(resp.content))
            media_ids.append(media.media_id)
        except Exception as e:
            print(f"[警告] 画像アップロードに失敗しました ({url}): {e}")
    return media_ids


def post_tweet(text: str, image_urls=None):
    client = get_client()
    media_ids = _upload_images(image_urls) if image_urls else None
    if media_ids:
        response = client.create_tweet(text=text, media_ids=media_ids)
    else:
        response = client.create_tweet(text=text)
    return response
